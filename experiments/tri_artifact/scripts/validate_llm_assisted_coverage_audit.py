#!/usr/bin/env python3
"""Validate the shipped non-evidential LLM-assisted coverage-audit template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.llm_assisted_coverage_audit import build_framework_report, render_markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).parents[1]
        / "data"
        / "llm_assisted_public_coverage_audit_template.jsonl",
    )
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    report = build_framework_report(args.artifact_root, args.template)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
