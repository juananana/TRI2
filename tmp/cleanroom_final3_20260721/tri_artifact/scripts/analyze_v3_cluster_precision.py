#!/usr/bin/env python3
"""Generate the v3 primary cluster-level sample sufficiency audit."""

import json
from pathlib import Path

from tri.v7_cluster_precision import build_primary_report, markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = build_primary_report(ROOT / "runs")
    json_path = ROOT / "reports" / "v3_cluster_sample_sufficiency_v1.json"
    md_path = ROOT / "reports" / "v3_cluster_sample_sufficiency_v1.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
