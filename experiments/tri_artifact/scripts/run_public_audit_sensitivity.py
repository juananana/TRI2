#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from tri.public_audit_sensitivity import build_controls, build_report, render_markdown
from tri.revision_matched_audit import jsonl_bytes


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "reports" / "benchmark_coverage_checklist.json"
STRUCTURAL = ROOT / "reports" / "external_public_opportunity_audit_v1.json"
DATA = ROOT / "data" / "public_audit_injected_controls_v1.jsonl"
JSON_REPORT = ROOT / "reports" / "public_audit_injected_sensitivity_v1.json"
MD_REPORT = ROOT / "reports" / "public_audit_injected_sensitivity_v1.md"


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise SystemExit(f"Refusing to overwrite a different sensitivity artifact: {path}")
    path.write_bytes(payload)


def main() -> None:
    controls = build_controls(CHECKLIST, STRUCTURAL)
    report = build_report(controls, CHECKLIST, STRUCTURAL)
    write_frozen(DATA, jsonl_bytes(controls))
    write_frozen(JSON_REPORT, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_frozen(MD_REPORT, render_markdown(report).encode("utf-8"))
    print(
        json.dumps(
            {
                "controls": len(controls),
                "strict_positive_recall": report["strict_positive_recall"],
                "hard_negative_exclusion": report["hard_negative_exclusion"],
                "report": str(JSON_REPORT),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
