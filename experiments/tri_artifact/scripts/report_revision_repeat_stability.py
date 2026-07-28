#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.revision_matched_audit import load_jsonl
from tri.revision_repeat_stability import build_repeat_report, render_markdown


ROOT = Path(__file__).resolve().parents[1]


def _labeled(values: list[str]) -> list[tuple[str, list[dict]]]:
    result = []
    for value in values:
        if "=" not in value:
            raise SystemExit("Pass inputs must be LABEL=/absolute/or/relative/path.jsonl")
        label, raw_path = value.split("=", 1)
        path = Path(raw_path)
        result.append((label, load_jsonl(path)))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Report source-derived repeat stability.")
    parser.add_argument("--historical", nargs="+", required=True)
    parser.add_argument("--new", nargs="+", required=True)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "reports" / "revision_source_grounded_repeat_v1.json"
    )
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args()
    report = build_repeat_report(
        _labeled(args.historical), _labeled(args.new), samples=args.bootstrap_samples
    )
    markdown = render_markdown(report)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()

