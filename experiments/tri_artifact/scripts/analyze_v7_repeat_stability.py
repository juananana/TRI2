#!/usr/bin/env python3
"""Generate the frozen v7 repeat-stability report."""

import json
from pathlib import Path

from tri.v7_repeat_stability_report import build_report, markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = build_report(
        ROOT / "runs", ROOT / "data" / "temporal_referent_v7_repeat_stability_v1.jsonl"
    )
    json_path = ROOT / "reports" / "v7_repeat_stability_v1.json"
    md_path = ROOT / "reports" / "v7_repeat_stability_v1.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
