from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .run_models import ChatClient, format_exception, has_internal_api_error, normalize_target, target_satisfies_schema
from .run_v3_sqlite_trajectories import (
    GENERIC_LEDGER_SYSTEM,
    LIFECYCLE_ACTOR_SYSTEM,
    LIFECYCLE_COMPILER_SYSTEM,
    call_json,
)
from .v3_sqlite_replay import SQLiteWriteEnvironment


GENERIC_STRESS_ACTOR_SYSTEM = (
    "You are the final step of a tool agent after two environment refreshes and an unrelated "
    "count call. Use the original instruction, generic task-state record, intermediate monitoring "
    "observation, and final state to choose the mutation target. A monitoring-only selector result "
    "does not automatically replace an earlier action target. If no entity should be acted on, "
    "return INVALID_BOUND_ENTITY. Return JSON only: {\"action\":\"process\",\"target_id\":\"...\"} "
    "or {\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)

ROLE_INDEXED_COMPILER_SYSTEM = (
    "Compile the instruction into role-indexed reference records. Distinct discourse roles must "
    "remain distinct: action_target is the only referent that may be mutated; "
    "monitoring_reference is observation-only and must never replace action_target. For each "
    "role, set reference_mode to preserve only when that role is resolved before the relevant "
    "refresh, and reevaluate when its selection is explicitly deferred. A dynamic action_target "
    "that is selected after the second refresh has bound_target_id null even if a monitoring "
    "reference is selected earlier. For a preserved action_target, bind its ID from initial_state. "
    "Use invalidity_policy reject unless replacement is explicitly authorized. Return JSON only: "
    "{\"references\":[{\"role\":\"action_target\",\"reference_mode\":\"preserve or reevaluate\","
    "\"selector\":\"...\",\"bound_target_id\":\"id or null\","
    "\"invalidity_policy\":\"reject or reevaluate_selector\"},"
    "{\"role\":\"monitoring_reference\",\"reference_mode\":\"reevaluate\","
    "\"selector\":\"...\",\"bound_target_id\":null,\"invalidity_policy\":\"reject\"}]} ."
)


def action_reference(ledger: dict[str, Any]) -> dict[str, Any]:
    references = ledger.get("references")
    if not isinstance(references, list):
        raise ValueError("role-indexed ledger must contain a references list")
    matches = [reference for reference in references if reference.get("role") == "action_target"]
    if len(matches) != 1:
        raise ValueError("role-indexed ledger must contain exactly one action_target")
    reference = matches[0]
    if reference.get("reference_mode") not in {"preserve", "reevaluate"}:
        raise ValueError("action_target has invalid reference_mode")
    if reference.get("invalidity_policy") not in {"reject", "reevaluate_selector"}:
        raise ValueError("action_target has invalid invalidity_policy")
    return reference


class MultiRefreshEnvironment(SQLiteWriteEnvironment):
    def __init__(self, task: dict[str, Any]):
        super().__init__(task)
        self.refresh_index = 0

    def refresh_next(self) -> list[dict[str, Any]]:
        states = [self.task["intermediate_state"], self.task["final_state"]]
        state = states[self.refresh_index]
        self.refresh_index += 1
        self._replace(state)
        rows = self.query()
        self.trace.append({"tool": "refresh_database", "refresh_index": self.refresh_index, "result_count": len(rows)})
        return rows

    def count_entities(self) -> int:
        count = self.db.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        self.trace.append({"tool": "count_entities", "result": count})
        return int(count)


def finish(
    mode: str,
    task: dict[str, Any],
    env: MultiRefreshEnvironment,
    target: str | None,
    ledger: dict[str, Any] | None,
    raw: list[str],
    errors: list[str],
) -> dict[str, Any]:
    action = env.act(target)
    acted = env.acted_ids()
    gold = task["correct_target"]
    return {
        "mode": mode,
        "compiled_ledger": ledger,
        "predicted_target": target,
        "correct_target": gold,
        "success": target == gold,
        "final_state_success": (gold == INVALID and not acted) or (gold != INVALID and acted == [gold]),
        "action_status": action["status"],
        "acted_ids": acted,
        "collateral_modifications": len([entity_id for entity_id in acted if entity_id != gold]),
        "errors": errors,
        "raw_outputs": raw,
        "tool_trace": env.trace,
    }


def run_generic(client: ChatClient, task: dict[str, Any], temperature: float) -> dict[str, Any]:
    env = MultiRefreshEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    ledger = None
    target = None
    try:
        initial = env.query()
        text, ledger = call_json(client, GENERIC_LEDGER_SYSTEM, {
            "instruction": task["instruction"],
            "initial_state": initial,
            "action_schema": task.get("action_schema", {}),
            "future_event": "two refreshes, a monitoring query, and a count call precede mutation",
        }, temperature)
        raw.append(text)
        intermediate = env.refresh_next()
        count = env.count_entities()
        final = env.refresh_next()
        text, obj = call_json(client, GENERIC_STRESS_ACTOR_SYSTEM, {
            "original_instruction": task["instruction"],
            "generic_ledger": ledger,
            "intermediate_monitoring_observation": intermediate,
            "unrelated_count_result": count,
            "final_state": final,
            "action_schema": task.get("action_schema", {}),
        }, temperature)
        raw.append(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    try:
        return finish("sqlite_multirefresh_generic", task, env, target, ledger, raw, errors)
    finally:
        env.close()


def run_lifecycle(client: ChatClient, task: dict[str, Any], temperature: float) -> dict[str, Any]:
    env = MultiRefreshEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    ledger = None
    target = None
    try:
        initial = env.query()
        text, ledger = call_json(client, LIFECYCLE_COMPILER_SYSTEM, {
            "instruction": task["instruction"],
            "initial_state": initial,
            "action_schema": task.get("action_schema", {}),
            "available_future_update": "two refreshes and unrelated monitoring/count calls precede mutation",
        }, temperature)
        raw.append(text)
        env.refresh_next()
        env.count_entities()
        final = env.refresh_next()
        use_gate = ledger.get("reference_mode") == "preserve"
        if use_gate:
            bound_id = normalize_target(ledger.get("bound_target_id"))
            # target_satisfies_schema reads task.refreshed_state, which equals final_state.
            if target_satisfies_schema(bound_id, task):
                target = bound_id
            elif ledger.get("invalidity_policy") == "reject":
                target = INVALID
            else:
                use_gate = False
        if not use_gate:
            text, obj = call_json(client, LIFECYCLE_ACTOR_SYSTEM, {
                "ledger": ledger,
                "refreshed_state": final,
                "action_schema": task.get("action_schema", {}),
            }, temperature)
            raw.append(text)
            target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    try:
        return finish("sqlite_multirefresh_lifecycle", task, env, target, ledger, raw, errors)
    finally:
        env.close()


def run_role_indexed(client: ChatClient, task: dict[str, Any], temperature: float) -> dict[str, Any]:
    env = MultiRefreshEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    ledger = None
    target = None
    try:
        initial = env.query()
        text, ledger = call_json(client, ROLE_INDEXED_COMPILER_SYSTEM, {
            "instruction": task["instruction"],
            "initial_state": initial,
            "action_schema": task.get("action_schema", {}),
            "trajectory": "refresh-monitor-count-refresh-mutate",
        }, temperature)
        raw.append(text)
        action_ledger = action_reference(ledger)
        env.refresh_next()
        env.count_entities()
        final = env.refresh_next()
        use_gate = action_ledger["reference_mode"] == "preserve"
        if use_gate:
            bound_id = normalize_target(action_ledger.get("bound_target_id"))
            if target_satisfies_schema(bound_id, task):
                target = bound_id
            elif action_ledger["invalidity_policy"] == "reject":
                target = INVALID
            else:
                use_gate = False
        if not use_gate:
            text, obj = call_json(client, LIFECYCLE_ACTOR_SYSTEM, {
                "ledger": action_ledger,
                "refreshed_state": final,
                "action_schema": task.get("action_schema", {}),
            }, temperature)
            raw.append(text)
            target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    try:
        return finish("sqlite_multirefresh_role_indexed", task, env, target, ledger, raw, errors)
    finally:
        env.close()


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--mode", choices=["generic", "lifecycle", "role_indexed"], required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-api-retries", type=int, default=1)
    parser.add_argument("--retry-backoff", type=float, default=5.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--disable-thinking", action="store_true")
    args = parser.parse_args()
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")
    client = ChatClient(
        args.model,
        os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
        key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False if args.disable_thinking else None,
    )
    runners = {
        "generic": run_generic,
        "lifecycle": run_lifecycle,
        "role_indexed": run_role_indexed,
    }
    runner = runners[args.mode]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    tasks = load(Path(args.data))
    with output.open("w", encoding="utf-8") as handle:
        for index, task in enumerate(tasks, 1):
            started = time.time()
            attempts_before = client.request_attempts
            retries_before = client.retry_events
            result = runner(client, task, args.temperature)
            status = "api_error" if has_internal_api_error(result) else "ok"
            row = {
                "run_timestamp": stamp,
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "enable_thinking": False if args.disable_thinking else None,
                "status": status,
                "latency_s": round(time.time() - started, 3),
                "api_request_attempts": client.request_attempts - attempts_before,
                "api_retries": client.retry_events - retries_before,
                "task": task,
                "result": result,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"[{index}/{len(tasks)}] {task['id']}: {status} success={result['success']} write={result['action_status']}")
    print(output)


if __name__ == "__main__":
    main()
