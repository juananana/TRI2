#!/usr/bin/env python3
"""Generate the frozen TRI-v3 crossed-dependence sensitivity report."""

import argparse
import json
from pathlib import Path

from tri.crossed_cluster_sensitivity import (
    DEFAULT_DRAWS,
    DEFAULT_SEED,
    build_report,
    markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "crossed_cluster_sensitivity_v1.json",
    )
    args = parser.parse_args()

    report = build_report(ROOT / "runs", draws=args.draws, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path = args.output.with_suffix(".md")
    markdown_path.write_text(markdown(report), encoding="utf-8")
    print(markdown_path)


if __name__ == "__main__":
    main()
