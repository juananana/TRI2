from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.evaluation_selection_regret import ROOT, build_report, markdown, validate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "reports/evaluation_selection_regret_v1.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "reports/evaluation_selection_regret_v1.md",
    )
    args = parser.parse_args()
    report = build_report()
    validate(report)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(
        "evaluation-selection regret audit: "
        f"{report['summary']['proxy_evaluations']} rows; "
        f"max worst regret={100 * report['summary']['maximum_worst_case_selection_regret']:.1f}"
    )


if __name__ == "__main__":
    main()

