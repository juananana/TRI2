#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from tri.binding_drift_tri_adapter import OFFICIAL_COMMIT, file_sha256, reverify_prompt, run_reverify
from tri.run_models import ChatClient


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--verifier-label", required=True)
    parser.add_argument("--data", default=str(ROOT / "data" / "binding_drift_tri_symmetric_smoke_v1.jsonl"))
    parser.add_argument("--output")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--expected-rows", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    data = Path(args.data)
    tasks = load(data)
    if args.limit:
        tasks = tasks[: args.limit]
    if len({task["id"] for task in tasks}) != len(tasks):
        raise SystemExit("Task IDs are not unique")
    if args.expected_rows is not None and len(tasks) != args.expected_rows:
        raise SystemExit(f"Expected {args.expected_rows} rows, found {len(tasks)}")
    for task in tasks:
        prompt = reverify_prompt(task)
        if any(field in prompt for field in ("correct_target", "reference_mode", '"binding"')):
            raise SystemExit(f"Evaluator-only field leaked into prompt for {task['id']}")
    if args.dry_run:
        print(json.dumps({
            "status": "dry_run_ok",
            "data": str(data),
            "sha256": file_sha256(data),
            "rows": len(tasks),
            "unique_state_clusters": len({task["state_cluster_id"] for task in tasks}),
            "bindings": {binding: sum(task["binding"] == binding for task in tasks) for binding in ("anchored", "dynamic")},
            "updates": {update: sum(task["update"] == update for task in tasks) for update in ("flip", "stable", "name_collision")},
        }, indent=2))
        return
    if not args.output:
        raise SystemExit("--output is required unless --dry-run is used")
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment")
    base_url = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    output = Path(args.output)
    if output.exists() and not args.resume:
        raise SystemExit(f"Refusing to overwrite existing run without --resume: {output}")
    completed = set()
    if args.resume and output.exists():
        for row in load(output):
            completed.add(row["task"]["id"])
    tasks = [task for task in tasks if task["id"] not in completed]
    client = ChatClient(args.model, base_url, key, timeout=args.timeout, max_retries=3, max_tokens=300, enable_thinking=False)
    with output.open("a" if args.resume else "w", encoding="utf-8") as handle:
        for index, task in enumerate(tasks, 1):
            started = time.time()
            attempts = client.request_attempts
            retries = client.retry_events
            usage = len(client.usage_records)
            result = run_reverify(client, task)
            row = {
                "run_timestamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "method": "binding_drift_reverify_author_adaptation",
                "official_source_commit": OFFICIAL_COMMIT,
                "verifier_model": args.model,
                "verifier_label": args.verifier_label,
                "temperature": 0.0,
                "enable_thinking": False,
                "api_request_attempts": client.request_attempts - attempts,
                "api_retries": client.retry_events - retries,
                "usage": client.usage_records[usage:],
                "latency_s": round(time.time() - started, 3),
                "task": task,
                "result": result,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"[{index}/{len(tasks)}] {task['id']} success={result['success']}")


if __name__ == "__main__":
    main()
