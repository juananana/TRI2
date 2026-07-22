from __future__ import annotations

import json
from pathlib import Path

from tri.public_coverage_funnel import build_report, render_markdown


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = build_report(root)
    (root / "reports" / "public_suite_coverage_funnel_v1.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (root / "reports" / "public_suite_coverage_funnel_v1.md").write_text(
        render_markdown(report), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
