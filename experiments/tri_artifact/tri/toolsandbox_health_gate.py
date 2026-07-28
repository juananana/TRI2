from __future__ import annotations

import argparse
import json
from pathlib import Path


CELLS = {
    ("preserve", "stable"),
    ("preserve", "flip"),
    ("reevaluate", "stable"),
    ("reevaluate", "flip"),
}


def evaluate(path: Path, expected_rows: int = 8) -> dict:
    with path.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    keys = {(row["model"], row["controller"], row["scenario_id"]) for row in rows}
    api_or_protocol_errors = sum(bool(row.get("errors")) for row in rows)
    rows_by_cell = {
        cell: sum(
            1
            for row in rows
            if (row["reference_mode"], row["transition"]) == cell
        )
        for cell in CELLS
    }
    opportunities = {
        cell: sum(
            bool(row.get("tri_opportunity"))
            for row in rows
            if (row["reference_mode"], row["transition"]) == cell
        )
        for cell in CELLS
    }
    passed = bool(
        len(rows) == expected_rows
        and len(keys) == expected_rows
        and api_or_protocol_errors == 0
        # Opportunity formation is a model outcome, not interface health.
        and all(count > 0 for count in rows_by_cell.values())
    )
    return {
        "passed": passed,
        "rows": len(rows),
        "unique_keys": len(keys),
        "api_or_protocol_errors": api_or_protocol_errors,
        "rows_by_cell": {
            f"{mode}_{transition}": rows_by_cell[(mode, transition)]
            for mode, transition in sorted(CELLS)
        },
        "opportunities_by_cell": {
            f"{mode}_{transition}": opportunities[(mode, transition)]
            for mode, transition in sorted(CELLS)
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--expected-rows", type=int, default=8)
    args = parser.parse_args()
    result = evaluate(args.input, args.expected_rows)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
