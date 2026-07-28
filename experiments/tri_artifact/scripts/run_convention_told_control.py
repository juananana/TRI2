#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.run_call_matched_authorization_ablation import RecordingChatClient, run_component
from tri.convention_told_control import (
    CONDITIONS,
    EVIDENCE_STATUS,
    RUN_VERSION,
    SYSTEM_PROMPTS,
    build_payload,
    canonical_json,
    load_frozen_inventory,
    load_jsonl,
    parse_output,
    payload_sha256,
    sha256_path,
    validate_resume_prefix,
    validate_run_row,
    validate_smoke,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_convention_told_natural_history_protocol.md"
ADDENDUM = ROOT / "reports" / "TRI_submission_critical_replication_addendum_20260728.md"
ENDPOINT = "https://api.siliconflow.cn/v1"
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
    "deepseek": "deepseek-ai/DeepSeek-V4-Pro",
    "minimax": "Pro/MiniMaxAI/MiniMax-M2.5",
}
TEMPERATURE = 0.0
MAX_TOKENS = 1200
TIMEOUT = 180
MAX_RETRIES = 2
RETRY_BACKOFF = 2.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"unknown model: {value}")


def run_task(
    client: RecordingChatClient,
    task: dict[str, Any],
    task_index: int,
    run_scope: str,
    task_hash: str,
    protocol_hash: str,
    addendum_hash: str,
) -> dict[str, Any]:
    payload = build_payload(task)
    order = CONDITIONS if task_index % 2 == 0 else tuple(reversed(CONDITIONS))
    conditions: dict[str, dict[str, Any]] = {}
    for condition in order:
        conditions[condition] = run_component(
            client,
            condition,
            SYSTEM_PROMPTS[condition],
            payload,
            parse_output,
        )
    outcomes = {
        condition: (conditions[condition].get("parsed") or {}).get("target_id")
        for condition in CONDITIONS
    }
    components = [conditions[condition] for condition in CONDITIONS]
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": run_scope,
        "timestamp_utc": utc_now(),
        "model": client.model,
        "endpoint": ENDPOINT,
        "api_settings": {
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "timeout_seconds": TIMEOUT,
            "max_retries": MAX_RETRIES,
            "retry_backoff_seconds": RETRY_BACKOFF,
            "thinking_parameter": "disabled",
        },
        "task_file_sha256": task_hash,
        "protocol_sha256": protocol_hash,
        "addendum_sha256": addendum_hash,
        "task": task,
        "task_index": task_index,
        "condition_order": list(order),
        "user_payload_sha256": payload_sha256(task),
        "conditions": conditions,
        "outcomes": outcomes,
        "logical_calls_planned": 2,
        "logical_calls_attempted": sum(bool(component.get("attempts")) for component in components),
        "logical_calls_completed": sum(
            bool(component.get("attempts"))
            and component["attempts"][-1].get("status") == "success"
            for component in components
        ),
        "complete": all(component.get("parsed") is not None for component in components),
    }
    validate_run_row(row)
    return row


def dry_run(tasks: list[dict[str, Any]], model: str, stage: str) -> dict[str, Any]:
    selected = tasks[:16] if stage == "smoke" else tasks
    payload = build_payload(selected[0])
    return {
        "dry_run": True,
        "network_calls": 0,
        "model": model,
        "stage": stage,
        "rows": len(selected),
        "pairs": len({task["pair_id"] for task in selected}),
        "logical_calls": 2 * len(selected),
        "conditions": list(CONDITIONS),
        "payload_keys": sorted(payload),
        "payload_sha256": payload_sha256(selected[0]),
        "condition_payloads_byte_matched": canonical_json(payload) == canonical_json(build_payload(selected[0])),
        "first_task_ids": [task["id"] for task in selected[:4]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the frozen Convention-told control.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--smoke-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    alias, model = resolve_model(args.model)
    tasks = load_frozen_inventory(TASKS)
    selected = tasks[:16] if args.stage == "smoke" else tasks
    output = args.output or ROOT / "runs" / f"convention_told_{alias}_{args.stage}_v1.jsonl"
    if args.dry_run:
        print(json.dumps(dry_run(tasks, model, args.stage), indent=2, ensure_ascii=False))
        return
    if args.stage == "full":
        if args.smoke_file is None:
            raise SystemExit("A full run requires --smoke-file.")
        validate_smoke(load_jsonl(args.smoke_file), tasks, model)

    api_key = (os.environ.get("LLM_API_KEY") or os.environ.get("SILICONFLOW_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("Set LLM_API_KEY or SILICONFLOW_API_KEY; credentials are never serialized.")
    output.parent.mkdir(parents=True, exist_ok=True)
    task_hash = sha256_path(TASKS)
    protocol_hash = sha256_path(PROTOCOL)
    addendum_hash = sha256_path(ADDENDUM)
    existing: list[dict[str, Any]] = []
    if args.resume:
        if not output.exists():
            raise SystemExit("--resume requires an existing output file")
        existing = load_jsonl(output)
        validate_resume_prefix(
            existing,
            selected,
            model,
            args.stage,
            task_hash,
            protocol_hash,
            addendum_hash,
        )
    elif output.exists():
        raise SystemExit(f"Refusing to overwrite raw output: {output}")

    client = RecordingChatClient(
        model=model,
        base_url=ENDPOINT,
        api_key=api_key,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
        retry_backoff=RETRY_BACKOFF,
        max_tokens=MAX_TOKENS,
        enable_thinking=False,
    )
    with output.open("a" if args.resume else "x", encoding="utf-8") as handle:
        for index, task in enumerate(selected[len(existing) :], start=len(existing)):
            row = run_task(
                client,
                task,
                index,
                args.stage,
                task_hash,
                protocol_hash,
                addendum_hash,
            )
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")
            handle.flush()
    rows = load_jsonl(output)
    if args.stage == "smoke":
        validate_smoke(rows, tasks, model)
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha256_path(output),
                "model": model,
                "rows": len(rows),
                "complete_rows": sum(row["complete"] for row in rows),
                "http_attempts": client.request_attempts,
                "retries": client.retry_events,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

