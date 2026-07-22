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
    is_success,
    normalize_target,
    run_factorized_actor_from_ledger,
    target_satisfies_schema,
)
from .run_v3_sqlite_trajectories import LIFECYCLE_ACTOR_SYSTEM, call_json
from .v2_model_report import is_api_failure
from .v3_sqlite_replay import SQLiteWriteEnvironment


def complete_language(
    client: ChatClient,
    source: dict[str, Any],
    temperature: float,
) -> tuple[dict[str, Any], int, int]:
    row = copy.deepcopy(source)
    result = row["result"]
    result["mode"] = "factorized_schema_compile_then_act"
    result["symbolic_preserve_gate"] = False
    if is_api_failure(source):
        return row, 0, 0

    ledger = result.get("compiled_ledger") or {}
    if ledger.get("reference_mode") != "preserve":
        result["factorial_actor_source"] = "reused_from_gated_dynamic_branch"
        return row, 0, 0

    attempts_before = client.request_attempts
    retries_before = client.retry_events
    try:
        actor_text, target = run_factorized_actor_from_ledger(
            client, row["task"], ledger, temperature
        )
        result.setdefault("raw_outputs", []).append(actor_text)
        result["predicted_target"] = target
        result["target_schema_valid"] = target_satisfies_schema(target, row["task"])
        result["success"] = is_success(target, row["task"])
        result["drift_to_new_leader"] = drifted_to_new_leader(target, row["task"])
        result["factorial_actor_source"] = "new_actor_call_on_frozen_compilation"
    except Exception as exc:
        result.setdefault("errors", []).append(format_exception(exc))
        result["predicted_target"] = None
        result["success"] = False
    return (
        row,
        client.request_attempts - attempts_before,
        client.retry_events - retries_before,
    )


def complete_sqlite(
    client: ChatClient,
    source: dict[str, Any],
    temperature: float,
) -> tuple[dict[str, Any], int, int]:
    row = copy.deepcopy(source)
    result = row["result"]
    result["mode"] = "sqlite_lifecycle_free_actor"
    if is_api_failure(source):
        return row, 0, 0

    ledger = result.get("compiled_ledger") or {}
    if ledger.get("reference_mode") != "preserve":
        result["factorial_actor_source"] = "reused_from_gated_dynamic_branch"
        return row, 0, 0

    attempts_before = client.request_attempts
    retries_before = client.retry_events
    task = row["task"]
    target = None
    try:
        actor_text, obj = call_json(client, LIFECYCLE_ACTOR_SYSTEM, {
            "ledger": ledger,
            "refreshed_state": task["refreshed_state"],
            "action_schema": task.get("action_schema", {}),
        }, temperature)
        result.setdefault("raw_outputs", []).append(actor_text)
        target = normalize_target(obj.get("target_id"))
        result["factorial_actor_source"] = "new_actor_call_on_frozen_compilation"
    except Exception as exc:
        result.setdefault("errors", []).append(format_exception(exc))

    env = SQLiteWriteEnvironment(task)
    try:
        env.query()
        env.refresh()
        action = env.act(target)
        acted_ids = env.acted_ids()
        gold = task["correct_target"]
        result.update({
            "predicted_target": target,
            "success": target == gold,
            "final_state_success": (
                (gold == INVALID and not acted_ids)
                or (gold != INVALID and acted_ids == [gold])
            ),
            "action_status": action["status"],
            "acted_ids": acted_ids,
            "collateral_modifications": len(
                [target_id for target_id in acted_ids if target_id != gold]
            ),
            "tool_trace": env.trace,
        })
    finally:
        env.close()
    return (
        row,
        client.request_attempts - attempts_before,
        client.retry_events - retries_before,
    )


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sqlite", action="store_true")
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
    rows = load_rows(Path(args.input))
    if args.limit:
        rows = rows[:args.limit]
    if not rows:
        raise SystemExit("No source rows found.")

    model = rows[0]["model"]
    client = ChatClient(
        model,
        os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
        key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False if args.disable_thinking else None,
    )
    transform = complete_sqlite if args.sqlite else complete_language
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as sink:
        for index, source in enumerate(rows, 1):
            started = time.time()
            completed, new_attempts, new_retries = transform(
                client, source, args.temperature
            )
            completed["factorial_completion_timestamp"] = stamp
            completed["latency_s"] = round(float(source.get("latency_s", 0.0)) + time.time() - started, 3)
            completed["api_request_attempts"] = int(source.get("api_request_attempts", 0)) + new_attempts
            completed["api_retries"] = int(source.get("api_retries", 0)) + new_retries
            completed["status"] = (
                "api_error" if has_internal_api_error(completed.get("result", {})) else "ok"
            )
            sink.write(json.dumps(completed, ensure_ascii=False) + "\n")
            sink.flush()
            result = completed["result"]
            print(
                f"[{index}/{len(rows)}] {completed['task']['id']}: {completed['status']} "
                f"success={result.get('success')} source={result.get('factorial_actor_source')}"
            )
    print(output)


if __name__ == "__main__":
    main()
