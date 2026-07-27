#!/usr/bin/env python3
"""Generate machine-readable and Markdown reports for external AI annotations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.external_public_annotation_report import (
    build_annotation_report,
    render_annotation_markdown,
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_args() -> argparse.Namespace:
    artifact_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        type=Path,
        default=artifact_root / "data" / "external_public_annotation_candidates_v1.jsonl",
    )
    parser.add_argument(
        "--runs",
        type=Path,
        default=artifact_root / "runs" / "external_public_annotation_siliconflow_v1.jsonl",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=artifact_root / "reports" / "external_public_annotation_v1.json",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=artifact_root / "reports" / "external_public_annotation_v1.md",
    )
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_jsonl(args.candidates)
    if args.smoke:
        selected = []
        for dataset in sorted({row["dataset"] for row in candidates}):
            selected.extend([row for row in candidates if row["dataset"] == dataset][:2])
        candidates = selected
    candidate_ids = {row["candidate_id"] for row in candidates}
    rows = [row for row in load_jsonl(args.runs) if row.get("candidate_id") in candidate_ids]
    report = build_annotation_report(candidates, rows)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_md.write_text(render_annotation_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.smoke and not report["smoke_pass"]:
        raise SystemExit("smoke gate failed")


if __name__ == "__main__":
    main()
