from __future__ import annotations

import argparse
import copy
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .run_models import (
    ChatClient,
    drifted_to_new_leader,
    format_exception,
    has_internal_api_error,
    normalize_target,
    parse_json,
    target_satisfies_schema,
)


REMINDER_SYSTEM = (
    "You are the final step of a tool agent after an environment refresh. A refreshed world "
    "state does not by itself change an entity already selected before the refresh. Determine "
    "from the original instruction whether the target was fixed before refresh or selection was "
    "deliberately deferred until afterward. Use the generic task record and action schema; do not "
    "create a lifecycle record. If no entity should be acted on, return INVALID_BOUND_ENTITY. "
    "Return JSON only: {\"action\":\"process\",\"target_id\":\"...\"} or "
    "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)

LATE_COMPILER_SYSTEM = (
    "At the final action step, reinterpret the original instruction using the generic task record "
    "and refreshed state. Set reference_mode to preserve only if the instruction selected its "
    "action target before refresh; set it to reevaluate only if selection was deliberately deferred "
    "until after refresh. For reevaluate, also resolve the selector in the refreshed state. Return "
    "JSON only: {\"reference_mode\":\"preserve or reevaluate\","
    "\"dynamic_target_id\":\"id or null\",\"reason\":\"...\"}."
)

UNTYPED_PLAN_COMPILER_SYSTEM = (
    "Before the environment refresh, write a concise natural-language action contract for a "
    "later executor. Resolve anything that must be resolved from the current state, and explain "
    "what the executor should do after refresh, including what to do if the intended entity can "
    "no longer receive the action. Do not use a lifecycle schema or fields named reference_mode, "
    "bound_target_id, invalidity_policy, guard, or fallback_policy. Return JSON only: "
    "{\"plan\":\"free-form natural-language contract\"}."
)

UNTYPED_PLAN_ACTOR_SYSTEM = (
    "Execute the pre-refresh natural-language action contract against the refreshed state and "
    "action schema. Do not reinterpret an unavailable original instruction; follow the contract. "
    "If no entity should be acted on, return INVALID_BOUND_ENTITY. Return JSON only: "
    "{\"action\":\"process or invalid\",\"target_id\":\"id or INVALID_BOUND_ENTITY\"}."
)


def actor_payload(row: dict[str, Any]) -> dict[str, Any]:
    task = row["task"]
    return {
        "original_instruction": task["instruction"],
        "generic_ledger": row["result"].get("compiled_ledger"),
        "refreshed_state": task["refreshed_state"],
        "action_schema": task.get("action_schema", {}),
    }


def reminder_result(client: ChatClient, source: dict[str, Any], temperature: float) -> dict[str, Any]:
    task = source["task"]
    errors: list[str] = []
    raw: list[str] = []
    target = None
    try:
        text = client.chat([
            {"role": "system", "content": REMINDER_SYSTEM},
            {"role": "user", "content": json.dumps(actor_payload(source), ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        target = normalize_target(parse_json(text).get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    return {
        "mode": "generic_ledger_tri_reminder_actor",
        "compiled_ledger": copy.deepcopy(source["result"].get("compiled_ledger")),
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "correct_target": task["correct_target"],
        "success": target == task["correct_target"],
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def late_compiler_result(
    client: ChatClient, source: dict[str, Any], temperature: float
) -> dict[str, Any]:
    task = source["task"]
    generic = source["result"].get("compiled_ledger") or {}
    errors: list[str] = []
    raw: list[str] = []
    decision = None
    target = None
    try:
        text = client.chat([
            {"role": "system", "content": LATE_COMPILER_SYSTEM},
            {"role": "user", "content": json.dumps(actor_payload(source), ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        decision = parse_json(text)
        if decision.get("reference_mode") == "preserve":
            bound_id = normalize_target(generic.get("selected_entity_id"))
            target = bound_id if target_satisfies_schema(bound_id, task) else INVALID
        elif decision.get("reference_mode") == "reevaluate":
            dynamic_id = normalize_target(decision.get("dynamic_target_id"))
            target = dynamic_id if target_satisfies_schema(dynamic_id, task) else INVALID
        else:
            raise ValueError("invalid reference_mode")
    except Exception as exc:
        errors.append(format_exception(exc))
    return {
        "mode": "generic_ledger_action_time_semantic_gate",
        "compiled_ledger": copy.deepcopy(generic),
        "action_time_decision": decision,
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "correct_target": task["correct_target"],
        "success": target == task["correct_target"],
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def pre_refresh_untyped_plan_result(
    client: ChatClient, source: dict[str, Any], temperature: float
) -> dict[str, Any]:
    task = source["task"]
    errors: list[str] = []
    raw: list[str] = []
    plan = None
    target = None
    try:
        text = client.chat([
            {"role": "system", "content": UNTYPED_PLAN_COMPILER_SYSTEM},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
                "action_schema": task.get("action_schema", {}),
                "known_future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        if set(obj) != {"plan"} or not isinstance(obj["plan"], str) or not obj["plan"].strip():
            raise ValueError("untyped compiler must return one non-empty plan string")
        plan = obj["plan"].strip()

        text = client.chat([
            {"role": "system", "content": UNTYPED_PLAN_ACTOR_SYSTEM},
            {"role": "user", "content": json.dumps({
                "pre_refresh_plan": plan,
                "refreshed_state": task["refreshed_state"],
                "action_schema": task.get("action_schema", {}),
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        target = normalize_target(parse_json(text).get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    return {
        "mode": "pre_refresh_untyped_compile_then_act",
        "compiled_plan": plan,
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "correct_target": task["correct_target"],
        "success": target == task["correct_target"],
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--mode", choices=["reminder", "late_compiler", "pre_refresh_untyped"], required=True
    )
    parser.add_argument("--limit", type=int)
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
    rows = load(Path(args.input))
    if args.limit:
        rows = rows[: args.limit]
    client = ChatClient(
        rows[0]["model"],
        os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
        key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False if args.disable_thinking else None,
    )
    runners = {
        "reminder": reminder_result,
        "late_compiler": late_compiler_result,
        "pre_refresh_untyped": pre_refresh_untyped_plan_result,
    }
    runner = runners[args.mode]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as sink:
        for index, source in enumerate(rows, 1):
            started = time.time()
            attempts_before = client.request_attempts
            retries_before = client.retry_events
            result = runner(client, source, args.temperature)
            new_attempts = client.request_attempts - attempts_before
            row = copy.deepcopy(source)
            conceptual_attempts = new_attempts if args.mode == "pre_refresh_untyped" else 1 + new_attempts
            row.update({
                "run_timestamp": stamp,
                "status": "api_error" if has_internal_api_error(result) else "ok",
                "latency_s": round(time.time() - started, 3),
                "api_request_attempts": conceptual_attempts,
                "api_retries": client.retry_events - retries_before,
                "result": result,
                "alternative_baseline_source": args.input,
            })
            sink.write(json.dumps(row, ensure_ascii=False) + "\n")
            sink.flush()
            print(
                f"[{index}/{len(rows)}] {row['task']['id']}: {row['status']} "
                f"success={result['success']} target={result['predicted_target']}"
            )
    print(output)


if __name__ == "__main__":
    main()
