from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .run_models import (
    ChatClient,
    format_exception,
    has_internal_api_error,
    normalize_target,
    parse_json,
    target_satisfies_schema,
)
from .v3_sqlite_replay import SQLiteWriteEnvironment


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


GENERIC_LEDGER_SYSTEM = (
    "Create a generic structured task-state record for a later agent step. Record the "
    "entity selected by the target description in the current initial state, its complete "
    "snapshot, the selector, the requested action, and the action preconditions. Do not "
    "add specialized temporal-reference fields such as binding_time, reference_mode, or "
    "invalidity_policy. Return JSON only: {\"task_goal\":\"...\","
    "\"selected_entity_id\":\"...\",\"selected_entity_snapshot\":{},"
    "\"selector\":\"...\",\"action\":\"...\",\"action_preconditions\":{}}."
)

GENERIC_ACTOR_SYSTEM = (
    "You are the final step of a tool agent after an environment refresh. Use the original "
    "instruction, a generic structured task-state record, the refreshed state, and the "
    "action schema to decide the target. Reason normally about whether the old selected "
    "entity or the current selector result should be used. If the correct target cannot be "
    "acted on, return INVALID_BOUND_ENTITY. Return JSON only: "
    "{\"action\":\"process\",\"target_id\":\"...\"} or "
    "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)

LIFECYCLE_COMPILER_SYSTEM = (
    "Compile the user's instruction into a factorized reference lifecycle record. "
    "Keep reference identity semantics separate from invalid-target handling. "
    "Set reference_mode to preserve when the instruction commits to an entity selected "
    "before refresh; set it to reevaluate when the description must be evaluated after "
    "refresh. Infer commitment from discourse order, not from the time of the final action: "
    "an instruction that first asks to identify, check, or find an entity and later says "
    "refresh and act on it preserves that entity even without words such as same or previous. "
    "Use reevaluate only when the instruction says to refresh before deciding, finding, or "
    "selecting, or explicitly says to use the refreshed state. The mere fact that refresh "
    "precedes the final action does not license reevaluation. For preserve, include "
    "bound_target_id from the initial state. "
    "Set invalidity_policy to reject unless the instruction explicitly authorizes selecting "
    "a replacement when the preserved entity becomes invalid; only then use "
    "reevaluate_selector. Return JSON only: "
    "{\"reference_mode\":\"preserve or reevaluate\",\"selector\":\"...\","
    "\"bound_target_id\":\"id or null\","
    "\"invalidity_policy\":\"reject or reevaluate_selector\",\"reason\":\"...\"}."
)

LIFECYCLE_ACTOR_SYSTEM = (
    "Act using the factorized lifecycle record, refreshed state, and action schema. "
    "An entity is actionable only if it is present and satisfies every action precondition. "
    "For a preserved entity, do not reapply the selector after refresh: the selector was "
    "used to establish identity, and its descriptive property may legitimately change. "
    "Only action_schema.preconditions determine post-refresh validity. "
    "For reference_mode preserve, use bound_target_id when actionable. If it is not "
    "actionable, follow invalidity_policy: reject returns INVALID_BOUND_ENTITY, while "
    "reevaluate_selector selects an actionable refreshed entity matching the selector. "
    "For reference_mode reevaluate, evaluate the selector in refreshed_state regardless of "
    "the old bound_target_id. Return JSON only: {\"action\":\"process\","
    "\"target_id\":\"...\"} or {\"action\":\"invalid\","
    "\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)


def call_json(client: ChatClient, system: str, payload: dict[str, Any], temperature: float) -> tuple[str, dict[str, Any]]:
    text = client.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ], temperature)
    return text, parse_json(text)


def final_payload(
    mode: str,
    task: dict[str, Any],
    env: SQLiteWriteEnvironment,
    target: str | None,
    ledger: dict[str, Any] | None,
    raw: list[str],
    errors: list[str],
) -> dict[str, Any]:
    action = env.act(target)
    acted_ids = env.acted_ids()
    gold = task["correct_target"]
    final_success = (gold == INVALID and not acted_ids) or (gold != INVALID and acted_ids == [gold])
    return {
        "mode": mode,
        "compiled_ledger": ledger,
        "predicted_target": target,
        "correct_target": gold,
        "success": target == gold,
        "final_state_success": final_success,
        "action_status": action["status"],
        "acted_ids": acted_ids,
        "collateral_modifications": len([target_id for target_id in acted_ids if target_id != gold]),
        "errors": errors,
        "raw_outputs": raw,
        "tool_trace": env.trace,
    }


def run_generic(
    client: ChatClient,
    task: dict[str, Any],
    temperature: float,
    validity_gate: bool = False,
) -> dict[str, Any]:
    env = SQLiteWriteEnvironment(task)
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
            "future_event": "the database will refresh before the final mutation",
        }, temperature)
        raw.append(text)
        refreshed = env.refresh()
        text, obj = call_json(client, GENERIC_ACTOR_SYSTEM, {
            "original_instruction": task["instruction"],
            "generic_ledger": ledger,
            "refreshed_state": refreshed,
            "action_schema": task.get("action_schema", {}),
        }, temperature)
        raw.append(text)
        target = normalize_target(obj.get("target_id"))
        if validity_gate and target != INVALID and not target_satisfies_schema(target, task):
            target = INVALID
    except Exception as exc:
        errors.append(format_exception(exc))
    try:
        mode = (
            "sqlite_generic_validity_gated"
            if validity_gate else "sqlite_generic_structured_ledger"
        )
        return final_payload(mode, task, env, target, ledger, raw, errors)
    finally:
        env.close()


def run_lifecycle(
    client: ChatClient,
    task: dict[str, Any],
    temperature: float,
    hybrid_gate: bool = True,
) -> dict[str, Any]:
    env = SQLiteWriteEnvironment(task)
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
            "available_future_update": "the database will refresh before the final mutation",
        }, temperature)
        raw.append(text)
        refreshed = env.refresh()
        use_gate = hybrid_gate and ledger.get("reference_mode") == "preserve"
        if use_gate:
            bound_id = normalize_target(ledger.get("bound_target_id"))
            if target_satisfies_schema(bound_id, task):
                target = bound_id
            elif ledger.get("invalidity_policy") == "reject":
                target = INVALID
            else:
                use_gate = False
        if not use_gate:
            text, obj = call_json(client, LIFECYCLE_ACTOR_SYSTEM, {
                "ledger": ledger,
                "refreshed_state": refreshed,
                "action_schema": task.get("action_schema", {}),
            }, temperature)
            raw.append(text)
            target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    try:
        mode = "sqlite_lifecycle_gated" if hybrid_gate else "sqlite_lifecycle_free_actor"
        return final_payload(mode, task, env, target, ledger, raw, errors)
    finally:
        env.close()


def load_tasks(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument(
        "--mode",
        choices=["generic", "generic_gate", "lifecycle_free", "lifecycle_gate", "lifecycle"],
        required=True,
    )
    ap.add_argument("--data", default="data/temporal_referent_v3_sqlite_trajectory.jsonl")
    ap.add_argument("--output")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--max-api-retries", type=int, default=3)
    ap.add_argument("--retry-backoff", type=float, default=5.0)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--disable-thinking", action="store_true")
    args = ap.parse_args()

    key = os.environ.get("LLM_API_KEY")
    base = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")
    tasks = load_tasks(Path(args.data))
    client = ChatClient(
        args.model,
        base,
        key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False if args.disable_thinking else None,
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = args.model.replace("/", "_").replace(":", "_")
    output = Path(args.output) if args.output else RUNS / f"{stamp}_{safe_model}_sqlite_{args.mode}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    runners = {
        "generic": lambda c, t, temp: run_generic(c, t, temp, validity_gate=False),
        "generic_gate": lambda c, t, temp: run_generic(c, t, temp, validity_gate=True),
        "lifecycle_free": lambda c, t, temp: run_lifecycle(c, t, temp, hybrid_gate=False),
        "lifecycle_gate": lambda c, t, temp: run_lifecycle(c, t, temp, hybrid_gate=True),
        "lifecycle": lambda c, t, temp: run_lifecycle(c, t, temp, hybrid_gate=True),
    }
    runner = runners[args.mode]
    with output.open("w", encoding="utf-8") as f:
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
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(
                f"[{index}/{len(tasks)}] {task['id']}: {status} "
                f"success={result['success']} write={result['action_status']}"
            )
    print(output)


if __name__ == "__main__":
    main()
