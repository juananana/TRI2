from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.main_paper_evidence_audit import ROOT, build_report, markdown, validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=ROOT)
    parser.add_argument("--paper", type=Path)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "reports/main_paper_evidence_audit_v1.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "reports/main_paper_evidence_audit_v1.md",
    )
    args = parser.parse_args()
    paper = args.paper or args.artifact_root.parents[1] / "paper/AnonymousSubmission2027.tex"
    report = build_report(args.artifact_root, paper)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    validate(report)
    print(f"main-paper evidence audit: {len(report['checks'])}/{len(report['checks'])} checks passed")


if __name__ == "__main__":
    main()
