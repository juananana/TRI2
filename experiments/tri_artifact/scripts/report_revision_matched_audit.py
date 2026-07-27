#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.revision_matched_audit import build_report, load_jsonl, render_markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Report one frozen revision matched audit.")
    parser.add_argument("--audit", required=True, choices=("full_diagnostic", "human_rewrite", "source_grounded"))
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    args = parser.parse_args()
    rows = [row for path in args.inputs for row in load_jsonl(path)]
    report = build_report(rows)
    if report["audit_id"] != args.audit:
        raise SystemExit("Input rows do not match --audit")
    json_output = args.json_output or ROOT / "reports" / f"revision_{args.audit}_v1.json"
    md_output = args.md_output or ROOT / "reports" / f"revision_{args.audit}_v1.md"
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"audit": args.audit, "rows": len(rows), "json": str(json_output), "markdown": str(md_output)}, indent=2))


if __name__ == "__main__":
    main()
