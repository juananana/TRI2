from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from tri.run_models import ChatClient, format_exception, parse_json

from .environment import (
    BASE_TASK_ID,
    active_scenario,
    current_runtime,
    postpone_task,
    record_binding,
    search_tasks,
    sync_tasks,
)
from .evaluation import score_runtime
from .scenarios import Scenario, load_scenarios


Controller = Literal["full_history", "generic", "lifecycle"]

COMMON_SYSTEM = """You are an autonomous tool-using agent operating Todoist in an AppWorld task world.
Follow the user's temporal ordering and reference meaning exactly. Choose exactly one tool per turn.
Do not invent task IDs. Return one JSON object and no other text.

Available tools:
- search_tasks, arguments: {}. Returns the controlled incomplete Todoist tasks ordered by due date.
- record_binding, arguments: {"task_id":"..."}. Call exactly once, immediately after selecting the target.
- sync_tasks, arguments: {}. Applies one external Todoist synchronization.
- postpone_task, arguments: {"task_id":"..."}. Moves that task one day later using AppWorld's native API.
- finish, arguments: {}. Use only after the requested mutation succeeds.
"""

MODE_SYSTEM = {
    "full_history": (
        "Use the full conversation and tool results as working memory. Required response: "
        '{"tool":"...","arguments":{}}.'
    ),
    "generic": (
        "Maintain an ordinary JSON state object with useful task notes, but do not use fields named "
        "reference_mode, bound_target_id, binding_time, or invalidity_policy. Required response: "
        '{"tool":"...","arguments":{},"state":{}}.'
    ),
    "lifecycle": (
        "Maintain typed lifecycle state. Preserve means selection happens before sync and the concrete "
        "ID remains the action referent; reevaluate means selection happens after sync. Required response: "
        '{"tool":"...","arguments":{},"state":{"reference_mode":"preserve|reevaluate|unknown",'
        '"selector":"...","bound_target_id":"ID or null"}}.'
    ),
}


def _validate_state(controller: Controller, state: Any) -> Any:
    forbidden = {"reference_mode", "bound_target_id", "binding_time", "invalidity_policy"}
    if controller == "full_history":
        if state is not None:
            raise ValueError("full_history must not emit state")
    elif controller == "generic":
        if not isinstance(state, dict) or forbidden & state.keys():
            raise ValueError("generic state is invalid")
    else:
        if not isinstance(state, dict):
            raise ValueError("lifecycle state must be an object")
        if set(state) != {"reference_mode", "selector", "bound_target_id"}:
            raise ValueError("lifecycle state has wrong fields")
        if state["reference_mode"] not in {"preserve", "reevaluate", "unknown"}:
            raise ValueError("invalid lifecycle reference mode")
    return state


def _dispatch(tool: str, arguments: dict[str, Any]) -> Any:
    if tool == "search_tasks":
        if arguments:
            raise ValueError("search_tasks takes no arguments")
        return search_tasks()
    if tool == "record_binding":
        if set(arguments) != {"task_id"}:
            raise ValueError("record_binding requires task_id")
        return record_binding(str(arguments["task_id"]))
    if tool == "sync_tasks":
        if arguments:
            raise ValueError("sync_tasks takes no arguments")
        return sync_tasks()
    if tool == "postpone_task":
        if set(arguments) != {"task_id"}:
            raise ValueError("postpone_task requires task_id")
        return postpone_task(str(arguments["task_id"]))
    if tool == "finish":
        if arguments:
            raise ValueError("finish takes no arguments")
        return {"status": "finished"}
    raise ValueError(f"unknown tool: {tool}")


def run_agent(
    client: Any,
    scenario: Scenario,
    controller: Controller,
    experiment_name: str,
    temperature: float = 0.0,
    max_steps: int = 6,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": COMMON_SYSTEM + "\n" + MODE_SYSTEM[controller]},
        {"role": "user", "content": scenario.instruction},
    ]
    raw_outputs: list[str] = []
    errors: list[str] = []
    state: Any = None if controller == "full_history" else (
        {} if controller == "generic" else {
            "reference_mode": "unknown",
            "selector": scenario.selector,
            "bound_target_id": None,
        }
    )
    finished = False
    with active_scenario(scenario, experiment_name) as runtime:
        for _ in range(max_steps):
            payload: dict[str, Any] = {
                "instruction": scenario.instruction,
                "next_step": "Choose one available tool now.",
            }
            if controller != "full_history":
                payload["persistent_state"] = state
            messages.append({"role": "user", "content": json.dumps(payload, ensure_ascii=True)})
            try:
                raw = client.chat(messages, temperature)
                raw_outputs.append(raw)
                obj = parse_json(raw)
                tool = str(obj.get("tool", ""))
                arguments = obj.get("arguments", {})
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                state = _validate_state(controller, obj.get("state"))
                observation = _dispatch(tool, arguments)
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": "TOOL_RESULT " + json.dumps(observation, ensure_ascii=True),
                    }
                )
                if tool == "finish":
                    finished = True
                    break
            except Exception as exc:
                errors.append(format_exception(exc))
                break
        # The context manager records final_snapshot while exiting, so query it now.
        from .environment import _task_rows

        runtime.final_snapshot = _task_rows(runtime.world)
        score = score_runtime(runtime)
    score.update(
        {
            "controller": controller,
            "finished": finished,
            "steps": len(raw_outputs),
            "persistent_state": state,
            "raw_outputs": raw_outputs,
            "errors": errors,
            "base_appworld_task_id": BASE_TASK_ID,
            "appworld_version": importlib.metadata.version("appworld"),
        }
    )
    score["success"] = bool(score["success"] and finished and not errors)
    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--controllers", default="full_history")
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-api-retries", type=int, default=1)
    parser.add_argument("--retry-backoff", type=float, default=5.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("LLM_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")
    controllers = [item.strip() for item in args.controllers.split(",") if item.strip()]
    if not controllers or any(item not in MODE_SYSTEM for item in controllers):
        raise SystemExit("invalid controller")
    scenarios = load_scenarios(args.data)
    client = ChatClient(
        model=args.model,
        base_url=os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
        api_key=key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False,
    )
    completed: set[tuple[str, str]] = set()
    if args.resume and args.output.exists():
        with args.output.open(encoding="utf-8") as handle:
            completed = {
                (row["controller"], row["scenario_id"])
                for row in (json.loads(line) for line in handle if line.strip())
            }
    jobs = [
        (controller, scenario)
        for controller in controllers
        for scenario in scenarios
        if (controller, scenario.scenario_id) not in completed
    ]
    if args.limit is not None:
        jobs = jobs[: args.limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    started = time.time()
    passed = 0
    with args.output.open("a" if args.resume else "w", encoding="utf-8") as handle:
        for index, (controller, scenario) in enumerate(jobs, 1):
            row_started = time.time()
            attempts_before = client.request_attempts
            experiment_name = f"tri_{controller}_{scenario.scenario_id}_{stamp}"
            row = run_agent(
                client,
                scenario,
                controller,  # type: ignore[arg-type]
                experiment_name,
                temperature=args.temperature,
            )
            row.update(
                {
                    "model": args.model,
                    "temperature": args.temperature,
                    "run_timestamp": stamp,
                    "latency_s": round(time.time() - row_started, 3),
                    "api_request_attempts": client.request_attempts - attempts_before,
                }
            )
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            handle.flush()
            passed += int(row["success"])
            print(
                f"[{index}/{len(jobs)}] {controller} {scenario.scenario_id}: "
                f"success={row['success']} wrong_write={row['wrong_entity_write']}",
                flush=True,
            )
    print(f"{passed}/{len(jobs)} new rows successful; {client.request_attempts} API attempts")
    print(f"elapsed_s={time.time() - started:.1f}")
    print(args.output)


if __name__ == "__main__":
    main()
