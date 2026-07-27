#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.call_matched_authorization_ablation import build_report, load_jsonl, render_markdown


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "call_matched_authorization_ablation_v2.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Report the post-primary matched authorization ablation.")
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20260725)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow smoke/limited inputs for debugging; do not use them as the v2 evidence report.",
    )
    args = parser.parse_args()
    rows = [row for path in args.input for row in load_jsonl(path)]
    if not args.allow_partial:
        by_model: dict[str, list[dict]] = {}
        for row in rows:
            by_model.setdefault(row.get("model", ""), []).append(row)
        invalid = {
            model: len(group)
            for model, group in by_model.items()
            if len(group) != 80 or any(row.get("run_scope") != "full" for row in group)
        }
        if invalid:
            raise SystemExit(
                "Default v2 reporting requires 80 full-scope rows per model; "
                f"invalid inputs: {invalid}. Use --allow-partial only for debugging."
            )
    report = build_report(rows, seed=args.seed, samples=args.bootstrap_samples)
    markdown = render_markdown(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
