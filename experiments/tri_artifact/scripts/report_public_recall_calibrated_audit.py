#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.public_recall_calibrated_audit import render_markdown, report_audit


def main() -> None:
    parser = argparse.ArgumentParser(description="Report the public recall-calibrated audit.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--population-size", action="append", required=True, metavar="DATASET=N")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args()
    sizes = {}
    for value in args.population_size:
        if "=" not in value:
            raise SystemExit("--population-size must be DATASET=N")
        dataset, raw = value.split("=", 1)
        sizes[dataset] = int(raw)
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = report_audit(rows, sizes, bootstrap_samples=args.bootstrap_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))


if __name__ == "__main__":
    main()
