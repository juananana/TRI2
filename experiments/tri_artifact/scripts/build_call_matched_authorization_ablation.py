#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tri.call_matched_authorization_ablation import (
    SOURCE_SHA256,
    TASK_FILE_SHA256,
    build_tasks,
    jsonl_bytes,
    sha256_bytes,
    sha256_path,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the frozen 40-pair flip inventory.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    tasks = build_tasks(args.source)
    payload = jsonl_bytes(tasks)
    if sha256_bytes(payload) != TASK_FILE_SHA256:
        raise SystemExit("Generated task bytes do not match the frozen task-file hash.")
    if args.output.exists() and args.output.read_bytes() != payload:
        raise SystemExit(f"Refusing to overwrite a different frozen task file: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"source={args.source}")
    print(f"source_sha256={sha256_path(args.source)}")
    print(f"expected_source_sha256={SOURCE_SHA256}")
    print(f"output={args.output}")
    print(f"output_sha256={sha256_bytes(payload)}")
    print(f"rows={len(tasks)}")
    print(f"state_clusters={len({task['state_cluster_id'] for task in tasks})}")


if __name__ == "__main__":
    main()
