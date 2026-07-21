from __future__ import annotations

import json

from tri.qualitative_trace_cases import ROOT, build_report, markdown


def main() -> None:
    report = build_report()
    output = ROOT / "reports/qualitative_trace_cases.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
