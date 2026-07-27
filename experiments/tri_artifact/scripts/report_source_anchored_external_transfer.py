#!/usr/bin/env python3
"""Generate the external transfer smoke or full report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.source_anchored_external_transfer_report import (
    build_report,
    render_latex_table,
    render_markdown,
)


def main() -> None:
    artifact = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=artifact / "runs/source_anchored_external_transfer_siliconflow_v1.jsonl",
    )
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    parser.add_argument("--latex-table-out", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    report = build_report(rows, expected_rows=32 if args.smoke else 320, smoke=args.smoke)
    json_path = args.report_json or artifact / "reports" / (
        "source_anchored_external_transfer_smoke_v1.json"
        if args.smoke
        else "source_anchored_external_transfer_v1.json"
    )
    md_path = args.report_md or json_path.with_suffix(".md")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    if args.latex_table_out:
        args.latex_table_out.parent.mkdir(parents=True, exist_ok=True)
        args.latex_table_out.write_text(render_latex_table(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
