from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tri.independent_language_holdout import (
    build_assignments,
    load_jsonl,
    validate_writer_returns,
    write_annotation_wjx_forms,
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--writer-returns", type=Path, required=True)
    args = parser.parse_args()
    pairs = load_jsonl(args.packet / "private_scenario_key.jsonl")
    assignments = build_assignments(pairs)
    authored = validate_writer_returns(
        read_csv(args.writer_returns),
        assignments,
        {row["pair_id"]: row for row in pairs},
    )
    authored_path = args.packet / "locked_authored_instructions.jsonl"
    if authored_path.exists():
        raise SystemExit(f"Refusing to overwrite {authored_path}")
    authored_path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in authored),
        encoding="utf-8",
    )
    output = args.packet / "annotator_wjx_forms"
    write_annotation_wjx_forms(authored, pairs, assignments, output)
    print(json.dumps({"authored_rows": len(authored), "annotator_forms": 36, "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
