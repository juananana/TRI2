from __future__ import annotations

import json
from pathlib import Path

from tri.construct_validity_audit import build_report, markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = build_report(ROOT)
    json_path = ROOT / "reports/construct_validity_cue_overlap_v1.json"
    md_path = ROOT / "reports/construct_validity_cue_overlap_v1.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
