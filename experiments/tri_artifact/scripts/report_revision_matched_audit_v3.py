#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from scripts.report_revision_matched_audit_v2 import corrected_substitution
from tri.revision_matched_audit import CONDITIONS, build_report, load_jsonl, render_markdown
from tri.revision_matched_interval_repair import apply_changed_pair_interval_repair


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the amended revision matched-audit report.")
    parser.add_argument(
        "--audit", required=True, choices=("full_diagnostic", "human_rewrite", "source_grounded")
    )
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    args = parser.parse_args()

    rows = [row for path in args.inputs for row in load_jsonl(path)]
    report = build_report(rows)
    if report["audit_id"] != args.audit:
        raise SystemExit("Input rows do not match --audit")

    by_model: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    for model in report["models"]:
        corrected = corrected_substitution(by_model[model["model"]])
        for condition in CONDITIONS:
            model["metrics"][condition]["preserve_substitution"] = corrected[condition]
    apply_changed_pair_interval_repair(report, rows)

    report["report_version"] = "TRI-revision-matched-audit-report-v3"
    report["report_amendments"] = [
        {
            "status": "post-run zero-API denominator repair retained from v2",
            "change": "Preserve substitution requires actionable_core eligibility.",
        },
        {
            "status": "post-run zero-API interval repair",
            "change": (
                "Changed-PairAcc differences resample eligible pair/workflow clusters directly; "
                "repeated cluster draws remain separate bootstrap units."
            ),
            "unchanged": [
                "raw outputs",
                "tasks and gold",
                "point estimates and denominators",
                "failure accounting",
            ],
        },
    ]

    json_output = args.json_output or ROOT / "reports" / f"revision_{args.audit}_v3.json"
    md_output = args.md_output or ROOT / "reports" / f"revision_{args.audit}_v3.md"
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(report)
    markdown += (
        "\n## Report amendments\n\n"
        "V2 restricted Preserve-substitution eligibility to the actionable core. V3 additionally "
        "repairs the changed-PairAcc difference interval: the earlier reporter merged repeated "
        "bootstrap draws by their original pair ID and dropped merged four-or-more-row groups. "
        "V3 directly resamples eligible pairs with replacement. Point estimates, denominators, "
        "raw outputs, tasks, gold labels, and failure accounting are unchanged.\n"
    )
    md_output.write_text(markdown, encoding="utf-8")
    print(json.dumps({"audit": args.audit, "rows": len(rows), "json": str(json_output), "markdown": str(md_output)}, indent=2))


if __name__ == "__main__":
    main()

