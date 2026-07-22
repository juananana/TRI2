from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tri.run_models import ChatClient, format_exception, parse_json

from .simple_note_environment import (
    BASE_TASK_ID,
    active_scenario,
    append_to_note,
    record_binding,
    search_notes,
    sync_notes,
)
from .simple_note_evaluation import score_runtime
from .simple_note_scenarios import Scenario, load_scenarios


SYSTEM = """You are an autonomous tool-using agent operating Simple Note in an AppWorld task world.
Follow the user's temporal ordering and reference meaning exactly. Choose exactly one tool per turn.
Do not invent note IDs. Return one JSON object and no other text.

Available tools:
- search_notes, arguments: {}. Returns controlled tri-experiment notes in alphabetical title order.
- record_binding, arguments: {"note_id":"..."}. Call exactly once, immediately after selecting the target.
- sync_notes, arguments: {}. Applies one external Simple Note synchronization.
- append_to_note, arguments: {"note_id":"..."}. Appends 'reviewed' using AppWorld's native API.
- finish, arguments: {}. Use only after the requested mutation succeeds.

Use the full conversation and tool results as working memory. Required response:
{"tool":"...","arguments":{}}.
"""


def _dispatch(tool: str, arguments: dict[str, Any]) -> Any:
    if tool == "search_notes":
        if arguments:
            raise ValueError("search_notes takes no arguments")
        return search_notes()
    if tool == "record_binding":
        if set(arguments) != {"note_id"}:
            raise ValueError("record_binding requires note_id")
        return record_binding(str(arguments["note_id"]))
    if tool == "sync_notes":
        if arguments:
            raise ValueError("sync_notes takes no arguments")
        return sync_notes()
    if tool == "append_to_note":
        if set(arguments) != {"note_id"}:
            raise ValueError("append_to_note requires note_id")
        return append_to_note(str(arguments["note_id"]))
    if tool == "finish":
        if arguments:
            raise ValueError("finish takes no arguments")
        return {"status": "finished"}
    raise ValueError(f"unknown tool: {tool}")


def run_agent(
    client: Any,
    scenario: Scenario,
    experiment_name: str,
    temperature: float = 0.0,
    max_steps: int = 6,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": scenario.instruction},
    ]
    raw_outputs: list[str] = []
    errors: list[str] = []
    finished = False
    with active_scenario(scenario, experiment_name) as runtime:
        for _ in range(max_steps):
            messages.append(
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "instruction": scenario.instruction,
                            "next_step": "Choose one available tool now.",
                        },
                        ensure_ascii=True,
                    ),
                }
            )
            try:
                raw = client.chat(messages, temperature)
                raw_outputs.append(raw)
                obj = parse_json(raw)
                tool = str(obj.get("tool", ""))
                arguments = obj.get("arguments", {})
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                if set(obj) != {"tool", "arguments"}:
                    raise ValueError("full-history response has unexpected fields")
                observation = _dispatch(tool, arguments)
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": "TOOL_RESULT "
                        + json.dumps(observation, ensure_ascii=True),
                    }
                )
                if tool == "finish":
                    finished = True
                    break
            except Exception as exc:
                errors.append(format_exception(exc))
                break
        from .simple_note_environment import _note_rows

        runtime.final_snapshot = _note_rows(runtime.world)
        score = score_runtime(runtime)
    score.update(
        {
            "controller": "full_history",
            "finished": finished,
            "steps": len(raw_outputs),
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
    completed: set[str] = set()
    if args.resume and args.output.exists():
        with args.output.open(encoding="utf-8") as handle:
            completed = {
                row["scenario_id"]
                for row in (json.loads(line) for line in handle if line.strip())
            }
    jobs = [scenario for scenario in scenarios if scenario.scenario_id not in completed]
    if args.limit is not None:
        jobs = jobs[: args.limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    started = time.time()
    passed = 0
    with args.output.open("a" if args.resume else "w", encoding="utf-8") as handle:
        for index, scenario in enumerate(jobs, 1):
            row_started = time.time()
            attempts_before = client.request_attempts
            experiment_name = f"tri_note_full_history_{scenario.scenario_id}_{stamp}"
            row = run_agent(
                client,
                scenario,
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
                f"[{index}/{len(jobs)}] full_history {scenario.scenario_id}: "
                f"success={row['success']} wrong_write={row['wrong_entity_write']}",
                flush=True,
            )
    print(f"{passed}/{len(jobs)} new rows successful; {client.request_attempts} API attempts")
    print(f"elapsed_s={time.time() - started:.1f}")
    print(args.output)


if __name__ == "__main__":
    main()
