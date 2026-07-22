from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


INVALID_TARGET = "INVALID_BOUND_ENTITY"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            required = {
                "id",
                "binding",
                "update",
                "pre_refresh_target",
                "post_refresh_target",
                "correct_target",
                "bound_entity_actionable_after_refresh",
            }
            missing = required.difference(row)
            if missing:
                raise ValueError(f"{path}:{line_number} missing {sorted(missing)}")
            rows.append(row)
    return rows


def predictions(row: dict[str, Any]) -> dict[str, str]:
    locked = (
        row["pre_refresh_target"]
        if row["bound_entity_actionable_after_refresh"]
        else INVALID_TARGET
    )
    return {
        "always_lock_with_validity": locked,
        "always_reevaluate": row["post_refresh_target"],
    }


def score(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    methods = ("always_lock_with_validity", "always_reevaluate")
    result: dict[str, Any] = {"n": len(materialized), "methods": {}}
    for method in methods:
        correct = sum(
            predictions(row)[method] == row["correct_target"] for row in materialized
        )
        result["methods"][method] = {
            "correct": correct,
            "accuracy": 100.0 * correct / len(materialized) if materialized else 0.0,
        }
    return result


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_binding: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_update: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_binding[row["binding"]].append(row)
        by_update[row["update"]].append(row)
    return {
        "definitions": {
            "always_lock_with_validity": (
                "Retain the pre-refresh bound ID; reject only when that ID is no longer "
                "action-valid in the refreshed state."
            ),
            "always_reevaluate": (
                "Discard the pre-refresh binding decision and apply the selector to the "
                "refreshed state."
            ),
        },
        "scope_note": (
            "These are deterministic policy extremes, not reproductions of any named "
            "prompting method or agent architecture."
        ),
        "overall": score(rows),
        "by_binding": {key: score(value) for key, value in sorted(by_binding.items())},
        "by_update": {key: score(value) for key, value in sorted(by_update.items())},
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Always-Lock and Always-Reevaluate Policy Controls",
        "",
        report["scope_note"],
        "",
        "| Slice | n | Always lock + validity | Always reevaluate |",
        "|---|---:|---:|---:|",
    ]

    def add_row(label: str, block: dict[str, Any]) -> None:
        lock = block["methods"]["always_lock_with_validity"]
        reeval = block["methods"]["always_reevaluate"]
        lines.append(
            f"| {label} | {block['n']} | {lock['correct']}/{block['n']} "
            f"({lock['accuracy']:.1f}%) | {reeval['correct']}/{block['n']} "
            f"({reeval['accuracy']:.1f}%) |"
        )

    add_row("Overall", report["overall"])
    for binding, block in report["by_binding"].items():
        add_row(binding.capitalize(), block)
    lines.extend(
        [
            "",
            "Always lock and always reevaluate are complementary: each solves one reference "
            "mode and fails the changed-winner cases in the other. Their identical aggregate "
            "accuracy therefore does not imply behavioral equivalence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze(load_jsonl(args.input))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
