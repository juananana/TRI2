#!/usr/bin/env python3
"""Build the model-assisted public recall triage queue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.model_assisted_public_recall_triage import (
    build_report,
    build_triage_rows,
    render_markdown,
    write_jsonl,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument(
        "--triage-jsonl",
        type=Path,
        default=Path(__file__).parents[1] / "data" / "model_assisted_public_recall_triage_v1.jsonl",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=Path(__file__).parents[1] / "reports" / "model_assisted_public_recall_triage_v1.json",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=Path(__file__).parents[1] / "reports" / "model_assisted_public_recall_triage_v1.md",
    )
    parser.add_argument("--no-controls", action="store_true")
    args = parser.parse_args()

    rows = build_triage_rows(args.artifact_root, include_controls=not args.no_controls)
    args.triage_jsonl.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.triage_jsonl, rows)
    report = build_report(args.artifact_root, rows, args.triage_jsonl)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.report_md.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))


if __name__ == "__main__":
    main()
