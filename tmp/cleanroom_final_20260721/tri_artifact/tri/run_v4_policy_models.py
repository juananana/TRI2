from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .run_models import (
    ChatClient,
    format_exception,
    has_internal_api_error,
    is_success,
    load_tasks,
    normalize_target,
    parse_json,
    run_generic_structured_ledger_then_act,
    target_satisfies_schema,
)


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


COMPILER_SYSTEM = (
    "Compile the instruction into a guarded reference lifecycle record. The target is chosen "
    "before refresh, but the instruction gives a condition for whether that identity remains "
    "committed afterward. Use guard_type action_validity when the same entity should be kept "
    "whenever it still satisfies the requested action's preconditions, even if the descriptive "
    "selector now prefers another entity. Use guard_type selector_match when the same entity "
    "should be kept only while the selector still chooses it. In both cases, fallback_policy is "
    "reevaluate_selector. Resolve bound_target_id from the initial state. Return JSON only: "
    "{\"reference_mode\":\"conditional\","
    "\"guard_type\":\"action_validity or selector_match\","
    "\"selector\":\"...\",\"bound_target_id\":\"...\","
    "\"fallback_policy\":\"reevaluate_selector\",\"reason\":\"...\"}."
)

ACTOR_SYSTEM = (
    "Execute the guarded reference lifecycle record on the refreshed state. For guard_type "
    "action_validity, preserve bound_target_id if it is present and satisfies every action "
    "precondition; otherwise reevaluate the selector. For guard_type selector_match, preserve "
    "bound_target_id only if it remains the entity chosen by the selector; otherwise reevaluate "
    "the selector. The final target must satisfy action preconditions. Return JSON only: "
    "{\"action\":\"process\",\"target_id\":\"...\"}."
)


def run_guarded_lifecycle(
    client: ChatClient, task: dict[str, Any], temperature: float
) -> dict[str, Any]:
    raw: list[str] = []
    errors: list[str] = []
    ledger = None
    target = None
    gate_used = False
    try:
        text = client.chat([
            {"role": "system", "content": COMPILER_SYSTEM},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
                "action_schema": task.get("action_schema", {}),
                "future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        ledger = parse_json(text)
        bound_id = normalize_target(ledger.get("bound_target_id"))
        if (
            ledger.get("guard_type") == "action_validity"
            and target_satisfies_schema(bound_id, task)
        ):
            target = bound_id
            gate_used = True
        else:
            text = client.chat([
                {"role": "system", "content": ACTOR_SYSTEM},
                {"role": "user", "content": json.dumps({
                    "lifecycle_record": ledger,
                    "refreshed_state": task["refreshed_state"],
                    "action_schema": task.get("action_schema", {}),
                }, ensure_ascii=False)},
            ], temperature)
            raw.append(text)
            target = normalize_target(parse_json(text).get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
    return {
        "mode": "guarded_lifecycle_then_act",
        "compiled_ledger": ledger,
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "guard_gate_used": gate_used,
        "errors": errors,
        "raw_outputs": raw,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=["generic", "guarded_lifecycle"], required=True)
    ap.add_argument("--data", default="data/temporal_referent_v4_policy.jsonl")
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
    tasks = load_tasks("all", "all", None, "all", "all", args.data)
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
    output = Path(args.output) if args.output else RUNS / f"{stamp}_{safe_model}_{args.mode}_v4_policy.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    runner = (
        run_generic_structured_ledger_then_act
        if args.mode == "generic"
        else run_guarded_lifecycle
    )
    with output.open("w", encoding="utf-8") as f:
        for index, task in enumerate(tasks, 1):
            started = time.time()
            attempts_before = client.request_attempts
            retries_before = client.retry_events
            try:
                result = runner(client, task, args.temperature)
                status = "api_error" if has_internal_api_error(result) else "ok"
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                result, status = {"error": format_exception(exc), "success": False}, "api_error"
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
                f"success={result.get('success')} target={result.get('predicted_target')}"
            )
    print(output)


if __name__ == "__main__":
    main()
