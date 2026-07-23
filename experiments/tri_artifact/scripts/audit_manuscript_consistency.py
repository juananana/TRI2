from __future__ import annotations

import json
from pathlib import Path

from tri.manuscript_consistency_audit import ROOT, build_report, markdown, validate


def main() -> None:
    report = build_report()
    validate(report)
    json_path = ROOT / "reports/manuscript_consistency_audit_v1.json"
    md_path = ROOT / "reports/manuscript_consistency_audit_v1.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    passed = sum(report["checks"].values())
    print(f"manuscript consistency audit: {passed}/{len(report['checks'])} checks passed")


if __name__ == "__main__":
    main()
