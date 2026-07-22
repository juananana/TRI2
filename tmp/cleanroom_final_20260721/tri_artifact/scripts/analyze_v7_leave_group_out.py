#!/usr/bin/env python3
"""Generate v7 leave-domain/template-out sensitivity artifacts."""

import json
from pathlib import Path

from tri.v7_leave_group_out import build_report, markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = build_report(ROOT / "runs")
    json_path = ROOT / "reports" / "v7_leave_group_out_sensitivity_v1.json"
    md_path = ROOT / "reports" / "v7_leave_group_out_sensitivity_v1.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
