from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from tri.rssa_smoke import run_rssa_task
from tri.run_models import ChatClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"
EXPECTED_SHA256 = "e651f4db45275877ca09a5e70187baca6d5ee8901bf983bb1ecc3885ef879181"


def _client(args: argparse.Namespace, api_key: str, max_tokens: int) -> ChatClient:
    return ChatClient(
        args.model,
        args.base_url,
        api_key,
        timeout=args.timeout,
        max_retries=args.max_retries,
        max_tokens=max_tokens,
        enable_thinking=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--base-url", default=os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    )
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=3)
    args = parser.parse_args()
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set LLM_API_KEY in the environment")

    payload = args.data.read_bytes()
    dataset_sha256 = hashlib.sha256(payload).hexdigest()
    if args.data.resolve() == DEFAULT_DATA.resolve() and dataset_sha256 != EXPECTED_SHA256:
        raise SystemExit(f"frozen manifest hash mismatch: {dataset_sha256}")
    tasks = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
    if len(tasks) != 20 or len({task["id"] for task in tasks}) != 20:
        raise SystemExit("R-SSA smoke requires exactly 20 unique tasks")

    compiler = _client(args, api_key, 500)
    grounder = _client(args, api_key, 300)
    actor = _client(args, api_key, 300)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for task in tasks:
            row = run_rssa_task(compiler, grounder, actor, task)
            row.update({
                "model": args.model,
                "dataset_sha256": dataset_sha256,
                "temperature": 0.0,
                "thinking": False,
                "endpoint": args.base_url,
                "timeout": args.timeout,
                "max_retries": args.max_retries,
                "max_tokens": {"compiler": 500, "grounder": 300, "actor": 300},
            })
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            print(json.dumps({
                "task": task["id"],
                "schema": row["schema_valid"],
                "epoch": row["action_binding_epoch_correct"],
                "edge": row["producer_edge_correct"],
                "free": row["free"]["success"],
                "enforced": row["enforced"]["success"],
                "errors": row["errors"],
            }, ensure_ascii=False), flush=True)

    print(json.dumps({
        "output": str(args.output),
        "rows": len(tasks),
        "dataset_sha256": dataset_sha256,
        "request_attempts": {
            "compiler": compiler.request_attempts,
            "grounder": grounder.request_attempts,
            "actor": actor.request_attempts,
        },
        "retry_events": {
            "compiler": compiler.retry_events,
            "grounder": grounder.retry_events,
            "actor": actor.retry_events,
        },
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
