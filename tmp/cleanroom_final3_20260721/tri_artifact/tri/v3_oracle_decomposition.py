from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .run_models import target_satisfies_schema


def load(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return {row["task"]["id"]: row for row in map(json.loads, handle) if row}


def gold_mode(task: dict[str, Any]) -> str:
    return "preserve" if task["binding"] == "anchored" else "reevaluate"


def oracle_preserve_target(task: dict[str, Any]) -> str:
    target = task["pre_refresh_target"]
    return target if target_satisfies_schema(target, task) else INVALID


def summarize(gated_path: Path, free_path: Path) -> dict[str, Any]:
    gated = load(gated_path)
    free = load(free_path)
    ids = sorted(set(gated) & set(free))
    counts = {
        "n": len(ids),
        "mode_correct": 0,
        "bound_id_correct_on_preserve": 0,
        "n_preserve": 0,
        "learned_free_correct": 0,
        "learned_gated_correct": 0,
        "oracle_mode_learned_id_correct": 0,
        "learned_mode_oracle_id_correct": 0,
        "oracle_mode_oracle_id_correct": 0,
    }
    for task_id in ids:
        gated_row = gated[task_id]
        free_row = free[task_id]
        task = gated_row["task"]
        ledger = gated_row["result"].get("compiled_ledger") or {}
        learned_mode = ledger.get("reference_mode")
        expected_mode = gold_mode(task)
        counts["mode_correct"] += learned_mode == expected_mode
        if expected_mode == "preserve":
            counts["n_preserve"] += 1
            counts["bound_id_correct_on_preserve"] += (
                ledger.get("bound_target_id") == task["pre_refresh_target"]
            )

        gold = task["correct_target"]
        free_target = free_row["result"].get("predicted_target")
        gated_target = gated_row["result"].get("predicted_target")
        counts["learned_free_correct"] += free_target == gold
        counts["learned_gated_correct"] += gated_target == gold

        if expected_mode == "preserve":
            learned_id = ledger.get("bound_target_id")
            mode_oracle_target = (
                learned_id if target_satisfies_schema(learned_id, task) else INVALID
            )
            both_oracle_target = oracle_preserve_target(task)
        else:
            mode_oracle_target = free_target
            both_oracle_target = free_target

        if learned_mode == "preserve":
            id_oracle_target = oracle_preserve_target(task)
        else:
            id_oracle_target = free_target

        counts["oracle_mode_learned_id_correct"] += mode_oracle_target == gold
        counts["learned_mode_oracle_id_correct"] += id_oracle_target == gold
        counts["oracle_mode_oracle_id_correct"] += both_oracle_target == gold

    rates = {
        key.replace("_correct", "_accuracy"): value / counts["n"]
        for key, value in counts.items()
        if key.endswith("_correct") and key != "bound_id_correct_on_preserve"
    }
    rates["bound_id_accuracy_on_preserve"] = (
        counts["bound_id_correct_on_preserve"] / counts["n_preserve"]
    )
    return {
        "gated_source": str(gated_path),
        "free_source": str(free_path),
        "counts": counts,
        "rates": rates,
        "interpretation_note": (
            "Oracle interventions replace only mode and/or pre-refresh bound ID. "
            "Reevaluate branches retain the observed lifecycle-free actor output."
        ),
    }


def markdown(report: dict[str, Any]) -> str:
    rates = report["rates"]
    return "\n".join([
        "# TRI-v3 Oracle Component Decomposition",
        "",
        f"Tasks: {report['counts']['n']}; preserve tasks: {report['counts']['n_preserve']}.",
        "",
        "| Component condition | Accuracy |",
        "|---|---:|",
        f"| Learned mode + learned ID + free actor | {100 * rates['learned_free_accuracy']:.1f} |",
        f"| Learned mode + learned ID + gate | {100 * rates['learned_gated_accuracy']:.1f} |",
        f"| Oracle mode + learned ID + gate | {100 * rates['oracle_mode_learned_id_accuracy']:.1f} |",
        f"| Learned mode + oracle ID + gate | {100 * rates['learned_mode_oracle_id_accuracy']:.1f} |",
        f"| Oracle mode + oracle ID + gate | {100 * rates['oracle_mode_oracle_id_accuracy']:.1f} |",
        "",
        f"Mode accuracy: {100 * rates['mode_accuracy']:.1f}%.",
        f"Bound-ID accuracy on preserve tasks: {100 * rates['bound_id_accuracy_on_preserve']:.1f}%.",
        "",
        report["interpretation_note"],
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gated", required=True)
    parser.add_argument("--free", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = summarize(Path(args.gated), Path(args.free))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
