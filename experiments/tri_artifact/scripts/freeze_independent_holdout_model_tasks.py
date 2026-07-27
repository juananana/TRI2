from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tri.independent_language_holdout import (
    build_model_tasks,
    clear_complete_pairs,
    jsonl_bytes,
    load_jsonl,
    sha256_path,
    validate_annotation_returns,
)


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--annotation-returns", type=Path, required=True)
    parser.add_argument(
        "--tasks",
        type=Path,
        default=ROOT / "data" / "independent_language_holdout_v1.jsonl",
    )
    args = parser.parse_args()
    pairs = load_jsonl(args.packet / "private_scenario_key.jsonl")
    authored_path = args.packet / "locked_authored_instructions.jsonl"
    authored = load_jsonl(authored_path)
    annotations = validate_annotation_returns(read_csv(args.annotation_returns), authored)
    clarity = clear_complete_pairs(authored, annotations)
    tasks = build_model_tasks(authored, pairs, clarity)
    if args.tasks.exists():
        raise SystemExit(f"Refusing to overwrite {args.tasks}")
    args.tasks.write_bytes(jsonl_bytes(tasks))
    report = {
        "evidence_status": "post-primary human audit; model experiment not yet run",
        **{key: value for key, value in clarity.items() if key != "item_clear"},
        "all_rows": len(tasks),
        "task_sha256": sha256_path(args.tasks),
        "authored_sha256": sha256_path(authored_path),
        "annotation_returns_sha256": sha256_path(args.annotation_returns),
    }
    report_path = ROOT / "reports" / "independent_language_holdout_clarity_v1.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
