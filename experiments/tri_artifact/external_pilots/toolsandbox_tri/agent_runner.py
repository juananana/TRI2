from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal

from tri.run_models import ChatClient, format_exception, parse_json

from .environment import (
    active_scenario,
    current_runtime,
    observe_state_binding,
    postpone_reminder,
    record_binding,
    search_all_reminders,
    sync_reminders,
)
from .evaluation import score_runtime
from .scenarios import Scenario, build_frozen_scenarios, build_pilot_scenarios, load_scenarios


Controller = Literal[
    "full_history", "generic", "generic_state_observed", "untyped", "lifecycle"
]

COMMON_SYSTEM = """You are an autonomous tool-using agent in a stateful reminder environment.
Follow the user's temporal ordering and reference meaning exactly. At each turn choose exactly
one tool. Do not invent reminder IDs. Return one JSON object and no other text.

Available tools:
- search_reminder, arguments: {}. Returns all reminders ordered from earliest due time.
- record_binding, arguments: {"reminder_id":"..."}. Records the selected identity without
  changing state. Call it exactly once, immediately after selecting the target.
- sync_reminders, arguments: {}. Applies the requested external synchronization once.
- postpone_reminder, arguments: {"reminder_id":"...","seconds":86400}.
- finish, arguments: {}. Use after the requested mutation succeeds, or when the instruction
  requires no mutation because the established reminder is absent or not editable.
"""

MODE_SYSTEM = {
    "full_history": """Use the complete conversation and tool results as the only working
memory. Do not emit a persistent state field or specialized lifecycle fields. Required output:
{"tool":"...","arguments":{}}.""",
    "generic": """Use ordinary reasoning over the full transcript. Include a `state` JSON object
with any generic task notes useful for the next turn. Do not use the field names reference_mode,
bound_target_id, binding_time, or invalidity_policy.
Required output: {"tool":"...","arguments":{},"state":{}}.""",
    "generic_state_observed": """Use ordinary reasoning over the full transcript. Include a
`state` JSON object with any generic task notes useful for the next turn. Do not use the field
names reference_mode, bound_target_id, binding_time, or invalidity_policy. Required output:
{"tool":"...","arguments":{},"state":{}}.""",
    "untyped": """Maintain a concise free-form plan for the next turn, but do not use a typed
reference schema or the field names reference_mode, bound_target_id, binding_time, or
invalidity_policy. Required output:
{"tool":"...","arguments":{},"state":"free-form plan"}.""",
    "lifecycle": """Maintain a typed lifecycle state. Infer preserve when an entity is selected
before sync and later referred to as that selected entity; infer reevaluate when sync occurs
before selection. A selector establishes identity but does not authorize changing that identity.
For preserve, retain the concrete bound target ID. If it is removed or non-editable and the user
did not authorize fallback, finish without modifying another reminder. Required output:
{"tool":"...","arguments":{},"state":{"reference_mode":"preserve|reevaluate|unknown",
"selector":"copy the user's selector","bound_target_id":"ID or null",
"invalidity_policy":"reject"}}.""",
}


def _validate_state(controller: Controller, state: Any) -> Any:
    forbidden = {"reference_mode", "bound_target_id", "binding_time", "invalidity_policy"}
    if controller == "full_history":
        if state is not None:
            raise ValueError("full_history must not emit persistent state")
    elif controller in {"generic", "generic_state_observed"}:
        if not isinstance(state, dict):
            raise ValueError("generic state must be an object")
        if forbidden & state.keys():
            raise ValueError("generic state used prohibited lifecycle fields")
    elif controller == "untyped":
        if not isinstance(state, str):
            raise ValueError("untyped state must be a string")
        if any(name in state.lower() for name in forbidden):
            raise ValueError("untyped state used prohibited lifecycle field names")
    else:
        if not isinstance(state, dict):
            raise ValueError("lifecycle state must be an object")
        required = {"reference_mode", "selector", "bound_target_id", "invalidity_policy"}
        if set(state) != required:
            raise ValueError("lifecycle state has the wrong fields")
        if state["reference_mode"] not in {"preserve", "reevaluate", "unknown"}:
            raise ValueError("invalid reference_mode")
        if state["invalidity_policy"] != "reject":
            raise ValueError("pilot supports reject invalidity policy only")
    return state


def _state_reminder_id(state: Any) -> str | None:
    values: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str) and value.startswith("REM-"):
            values.add(value)

    visit(state)
    return next(iter(values)) if len(values) == 1 else None


def _observe_generic_binding(tool: str, state: Any) -> None:
    runtime = current_runtime()
    if any(
        event["tool"] in {"record_binding", "observe_binding"}
        and event.get("status") == "ok"
        for event in runtime.trace
    ):
        return
    target_id = _state_reminder_id(state)
    if target_id is None or tool == "record_binding":
        return
    should_observe = bool(
        (runtime.scenario.reference_mode == "preserve" and tool == "sync_reminders")
        or (
            runtime.scenario.reference_mode == "reevaluate"
            and runtime.synced
            and tool == "postpone_reminder"
        )
    )
    if should_observe:
        observe_state_binding(target_id)


def _dispatch(tool: str, arguments: dict[str, Any]) -> Any:
    if tool == "search_reminder":
        if arguments:
            raise ValueError("search_reminder takes no arguments in this pilot")
        return search_all_reminders()
    if tool == "record_binding":
        if set(arguments) != {"reminder_id"}:
            raise ValueError("record_binding requires exactly reminder_id")
        return record_binding(str(arguments["reminder_id"]))
    if tool == "sync_reminders":
        if arguments:
            raise ValueError("sync_reminders takes no arguments")
        return sync_reminders()
    if tool == "postpone_reminder":
        allowed = {"reminder_id", "seconds"}
        if not set(arguments) <= allowed or "reminder_id" not in arguments:
            raise ValueError("postpone_reminder requires reminder_id and optional seconds")
        return postpone_reminder(
            str(arguments["reminder_id"]), float(arguments.get("seconds", 86_400.0))
        )
    if tool == "finish":
        if arguments:
            raise ValueError("finish takes no arguments")
        return {"status": "finished"}
    raise ValueError(f"unknown tool: {tool}")


def run_agent(
    client: Any,
    scenario: Scenario,
    controller: Controller,
    temperature: float = 0.0,
    max_steps: int = 6,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": COMMON_SYSTEM + "\n" + MODE_SYSTEM[controller]},
        {"role": "user", "content": scenario.instruction},
    ]
    raw_outputs: list[str] = []
    errors: list[str] = []
    state: Any = None if controller == "full_history" else ({} if controller in {"generic", "generic_state_observed"} else ("" if controller == "untyped" else {
        "reference_mode": "unknown",
        "selector": scenario.selector,
        "bound_target_id": None,
        "invalidity_policy": "reject",
    }))
    finished = False
    with active_scenario(scenario) as runtime:
        for _ in range(max_steps):
            payload = {
                "instruction": scenario.instruction,
                "next_step": "Choose one available tool now.",
            }
            if controller != "full_history":
                payload["persistent_state"] = state
            messages.append({"role": "user", "content": json.dumps(payload, ensure_ascii=False)})
            try:
                raw = client.chat(messages, temperature)
                raw_outputs.append(raw)
                obj = parse_json(raw)
                tool = str(obj.get("tool", ""))
                arguments = obj.get("arguments", {})
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                state = _validate_state(controller, obj.get("state"))
                if controller == "generic_state_observed":
                    _observe_generic_binding(tool, state)
                observation = _dispatch(tool, arguments)
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": "TOOL_RESULT " + json.dumps(observation, ensure_ascii=False),
                    }
                )
                if tool == "finish":
                    finished = True
                    break
            except Exception as exc:
                errors.append(format_exception(exc))
                break
        score = score_runtime(runtime)
    score.update(
        {
            "controller": controller,
            "finished": finished,
            "steps": len(raw_outputs),
            "persistent_state": state,
            "raw_outputs": raw_outputs,
            "errors": errors,
        }
    )
    score["success"] = bool(score["success"] and finished and not errors)
    return score


def run_suite(
    client: Any,
    controllers: list[Controller],
    scenarios: list[Scenario] | None = None,
    temperature: float = 0.0,
) -> list[dict[str, Any]]:
    scenarios = scenarios or build_pilot_scenarios()
    return [
        run_agent(client, scenario, controller, temperature=temperature)
        for controller in controllers
        for scenario in scenarios
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--controllers", default="full_history,generic,untyped,lifecycle",
        help="comma-separated subset of full_history,generic,generic_state_observed,untyped,lifecycle",
    )
    parser.add_argument("--output")
    parser.add_argument("--split", choices=["smoke", "frozen"], default="smoke")
    parser.add_argument("--data", help="frozen scenario JSONL; required for paper runs")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-api-retries", type=int, default=1)
    parser.add_argument("--retry-backoff", type=float, default=5.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--protocol-addendum")
    args = parser.parse_args()
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")
    controllers = [item.strip() for item in args.controllers.split(",") if item.strip()]
    if not controllers or any(item not in MODE_SYSTEM for item in controllers):
        raise SystemExit("controllers must be from generic,untyped,lifecycle")
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
    if args.split == "frozen" and not args.data:
        raise SystemExit("--data is required for frozen runs")
    scenarios = (
        load_scenarios(Path(args.data))
        if args.data
        else build_pilot_scenarios()
    )
    addendum_sha256 = None
    if args.protocol_addendum:
        addendum_sha256 = hashlib.sha256(Path(args.protocol_addendum).read_bytes()).hexdigest()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = args.model.replace("/", "_").replace(":", "_")
    output = Path(args.output) if args.output else Path("runs") / (
        f"{stamp}_{safe_model}_toolsandbox_tri_{args.split}.jsonl"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    completed: set[tuple[str, str]] = set()
    if args.resume and output.exists():
        with output.open(encoding="utf-8") as handle:
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
    started = time.time()
    passed = 0
    with output.open("a" if args.resume else "w", encoding="utf-8") as handle:
        for index, (controller, scenario) in enumerate(jobs, 1):
            row_started = time.time()
            attempts_before = client.request_attempts
            row = run_agent(
                client,
                scenario,
                controller,  # type: ignore[arg-type]
                temperature=args.temperature,
            )
            row.update(
                {
                    "model": args.model,
                    "temperature": args.temperature,
                    "run_timestamp": stamp,
                    "latency_s": round(time.time() - row_started, 3),
                    "api_request_attempts": client.request_attempts - attempts_before,
                    "protocol_addendum_sha256": addendum_sha256,
                }
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            passed += int(row["success"])
            print(
                f"[{index}/{len(jobs)}] {controller} {scenario.scenario_id}: "
                f"success={row['success']} wrong_write={row['wrong_entity_write']}",
                flush=True,
            )
    print(f"{passed}/{len(jobs)} new rows successful; {client.request_attempts} API attempts")
    print(f"elapsed_s={time.time() - started:.1f}")
    print(output)


if __name__ == "__main__":
    main()
