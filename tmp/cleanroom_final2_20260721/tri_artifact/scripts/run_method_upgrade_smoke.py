from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from tri.method_upgrade_smoke import METHODS, compile_task
from tri.run_models import ChatClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--methods", default=",".join(METHODS))
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-url", default=os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set LLM_API_KEY in the environment")
    methods = args.methods.split(",")
    if any(method not in METHODS for method in methods):
        raise SystemExit(f"methods must be from {METHODS}")
    payload = args.data.read_bytes()
    tasks = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
    if args.limit is not None:
        tasks = tasks[:args.limit]
    client = ChatClient(
        args.model, args.base_url, api_key, timeout=args.timeout,
        max_retries=args.max_retries, max_tokens=args.max_tokens, enable_thinking=False,
    )
    rows = []
    for method in methods:
        for task in tasks:
            row = compile_task(client, method, task)
            row.update({
                "model": args.model,
                "dataset_sha256": hashlib.sha256(payload).hexdigest(),
                "temperature": 0.0,
                "thinking": False,
                "max_tokens": args.max_tokens,
            })
            rows.append(row)
            print(json.dumps({
                "task": task["id"], "method": method,
                "schema_valid": row["schema_valid"], "errors": row["errors"],
            }, ensure_ascii=False), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output), "rows": len(rows),
        "request_attempts": client.request_attempts, "retry_events": client.retry_events,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
