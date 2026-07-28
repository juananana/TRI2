#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.public_recall_calibrated_audit import build_sampling_frame


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a frozen public-audit sampling frame.")
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--controls", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-dataset", type=int, default=100)
    args = parser.parse_args()
    frame = build_sampling_frame(read(args.population), read(args.candidates), read(args.controls) if args.controls else [], args.per_dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in frame), encoding="utf-8")
    print(json.dumps({"rows": len(frame), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
