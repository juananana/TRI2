from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def load_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def summarize(group: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(group)
    opportunities = sum(bool(row.get("tri_opportunity", False)) for row in group)
    mechanism_errors = sum(
        bool(row.get("unauthorized_rebinding", False) or row.get("premature_lock", False))
        for row in group
    )
    return {
        "n": count,
        "success": sum(row["success"] for row in group),
        "accuracy": sum(row["success"] for row in group) / count if count else None,
        "final_state_success": sum(row["final_state_success"] for row in group),
        "wrong_entity_writes": sum(row["wrong_entity_write"] for row in group),
        "invalid_attempts": sum(int(row["invalid_attempts"]) for row in group),
        "unnecessary_rejections": sum(row["unnecessary_rejection"] for row in group),
        "execution_or_protocol_errors": sum(bool(row["errors"]) for row in group),
        "binding_observed": sum(bool(row.get("binding_observed", False)) for row in group),
        "initial_binding_correct": sum(
            bool(row.get("initial_binding_correct", False)) for row in group
        ),
        "tri_opportunities": opportunities,
        "mechanism_errors": mechanism_errors,
        "conditional_mechanism_error_rate": (
            mechanism_errors / opportunities if opportunities else None
        ),
        "api_request_attempts": sum(int(row.get("api_request_attempts", 0)) for row in group),
    }


def grouped(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in fields)].append(row)
    return [
        {**dict(zip(fields, key)), **summarize(group)}
        for key, group in sorted(groups.items())
    ]


def paired(rows: list[dict[str, Any]], left: str, right: str) -> list[dict[str, Any]]:
    by_model_task = {
        (row["model"], row["scenario_id"], row["controller"]): row for row in rows
    }
    pairs: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    for model, scenario_id, controller in by_model_task:
        if controller != left:
            continue
        other = by_model_task.get((model, scenario_id, right))
        if other is not None:
            pairs[model].append(
                (bool(by_model_task[(model, scenario_id, left)]["success"]), bool(other["success"]))
            )
    output = []
    for model, values in sorted(pairs.items()):
        right_wins = sum(not a and b for a, b in values)
        left_wins = sum(a and not b for a, b in values)
        output.append(
            {
                "model": model,
                "left": left,
                "right": right,
                "n": len(values),
                "delta_accuracy": (
                    sum(b for _, b in values) - sum(a for a, _ in values)
                ) / len(values),
                "right_wins": right_wins,
                "ties": len(values) - right_wins - left_wins,
                "left_wins": left_wins,
            }
        )
    return output


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    duplicate_keys = len(rows) - len(
        {(row["model"], row["controller"], row["scenario_id"]) for row in rows}
    )
    comparisons = [
        ("generic", "untyped"),
        ("untyped", "lifecycle"),
        ("matched_generic", "matched_untyped"),
        ("matched_untyped", "matched_lifecycle"),
        ("matched_lifecycle", "matched_lifecycle_gate_replay"),
    ]
    return {
        "inventory": {
            "rows": len(rows),
            "models": sorted({row["model"] for row in rows}),
            "controllers": sorted({row["controller"] for row in rows}),
            "tasks": len({row["scenario_id"] for row in rows}),
            "duplicate_keys": duplicate_keys,
        },
        "by_model_controller": grouped(rows, ("model", "controller")),
        "by_model_controller_mode": grouped(
            rows, ("model", "controller", "reference_mode")
        ),
        "by_model_controller_transition": grouped(
            rows, ("model", "controller", "transition")
        ),
        "paired_generic_to_untyped": paired(rows, "generic", "untyped"),
        "paired_untyped_to_lifecycle": paired(rows, "untyped", "lifecycle"),
        "paired_comparisons": [
            result
            for left, right in comparisons
            for result in paired(rows, left, right)
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = ["# ToolSandbox-Based TRI External Pilot", ""]
    inventory = report["inventory"]
    lines.append(
        f"Rows: {inventory['rows']}; tasks: {inventory['tasks']}; "
        f"models: {', '.join(inventory['models'])}; duplicate keys: {inventory['duplicate_keys']}."
    )
    lines.extend(
        [
            "",
            "## Main Results",
            "",
            "| Model | Controller | N | Success | Accuracy | Wrong writes | TRI opportunities | Mechanism errors | API/protocol errors |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["by_model_controller"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | {row['success']} | "
            f"{100 * row['accuracy']:.1f} | {row['wrong_entity_writes']} | "
            f"{row['tri_opportunities']} | {row['mechanism_errors']} | "
            f"{row['execution_or_protocol_errors']} |"
        )
    lines.extend(["", "## Paired Descriptive Contrasts", ""])
    for row in report["paired_comparisons"]:
        lines.append(
            f"- {row['model']}: {row['left']} -> {row['right']} "
            f"{100 * row['delta_accuracy']:+.1f} points; wins/ties/losses "
            f"{row['right_wins']}/{row['ties']}/{row['left_wins']} over {row['n']} tasks."
        )
    lines.extend(
        [
            "",
            "This is a custom ToolSandbox-based TRI extension, not an official ToolSandbox score. "
            "The original 24-task pilot is exploratory. The frozen 96-task set uses four paraphrases "
            "of six selector clusters; conditional mechanism rates must therefore be accompanied by "
            "cluster-aware uncertainty rather than treating all paraphrases as independent.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(load_rows(args.inputs))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
