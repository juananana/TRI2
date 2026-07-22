"""Recompute how evaluation regimes expose or hide referent-policy behavior."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .policy_extreme_controls import predictions as extreme_predictions


ROOT = Path(__file__).resolve().parents[1]
REGIMES = (
    "aggregate_e2e",
    "preserve_only",
    "reevaluate_only",
    "stable_only",
    "changed_winner_only",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def success(row: dict[str, Any]) -> bool:
    result = row.get("result")
    return bool(
        row.get("status", "ok") == "ok"
        and isinstance(result, dict)
        and not result.get("errors")
        and result.get("error") is None
        and result.get("predicted_target") == row["task"].get("correct_target")
    )


def initial_binding_id(row: dict[str, Any]) -> str | None:
    ledger = row.get("result", {}).get("compiled_ledger") or {}
    return ledger.get("selected_entity_id") or ledger.get("bound_target_id")


def initial_binding_correct(row: dict[str, Any]) -> bool:
    return initial_binding_id(row) == row["task"].get("pre_refresh_target")


def changed_winner_task(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") in {"flip", "name_collision"}
        and task.get("pre_refresh_target") != task.get("post_refresh_target")
        and task.get("bound_entity_present_after_refresh", True)
        and task.get("bound_entity_actionable_after_refresh", True)
    )


def eligible_changed(row: dict[str, Any]) -> bool:
    return changed_winner_task(row) and initial_binding_correct(row)


def regime_rows(rows: Iterable[dict[str, Any]], regime: str) -> list[dict[str, Any]]:
    rows = list(rows)
    if regime == "aggregate_e2e":
        return rows
    if regime == "preserve_only":
        return [row for row in rows if row["task"].get("binding") == "anchored"]
    if regime == "reevaluate_only":
        return [row for row in rows if row["task"].get("binding") == "dynamic"]
    if regime == "stable_only":
        return [row for row in rows if row["task"].get("update") == "stable"]
    if regime == "changed_winner_only":
        return [row for row in rows if changed_winner_task(row)]
    raise ValueError(f"unknown regime: {regime}")


def pair_accuracy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, bool]] = defaultdict(dict)
    for row in rows:
        task = row["task"]
        if task.get("update") not in {"flip", "name_collision"}:
            continue
        signature = json.dumps(
            {
                key: task.get(key)
                for key in ("domain", "initial_state", "refreshed_state", "selector", "action", "action_schema", "update")
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        groups[signature][str(task.get("style"))] = success(row)
    pair_keys = (("explicit_anchor", "implicit_dynamic"), ("implicit_anchor", "explicit_dynamic"))
    pairs: list[bool] = []
    for group in groups.values():
        for preserve, reevaluate in pair_keys:
            if preserve in group and reevaluate in group:
                pairs.append(group[preserve] and group[reevaluate])
    return {"pairs": len(pairs), "both_correct": sum(pairs), "pair_accuracy": (sum(pairs) / len(pairs) if pairs else None)}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"n": len(rows), "regimes": {}}
    for regime in REGIMES:
        subset = regime_rows(rows, regime)
        correct = sum(success(row) for row in subset)
        result["regimes"][regime] = {
            "n": len(subset),
            "correct": correct,
            "accuracy": correct / len(subset) if subset else None,
        }
    changed = [row for row in rows if eligible_changed(row)]
    drifts = sum(
        row.get("result", {}).get("predicted_target") == row["task"].get("post_refresh_target")
        for row in changed
    )
    result["conditional_changed_winner"] = {
        "eligible": len(changed),
        "drift_to_refreshed_winner": drifts,
        "drift_rate": drifts / len(changed) if changed else None,
    }
    result["changed_pairacc"] = pair_accuracy(rows)
    return result


def deterministic_control(tasks: list[dict[str, Any]], method: str) -> dict[str, Any]:
    outcomes = [extreme_predictions(task)[method] == task.get("correct_target") for task in tasks]
    rows = [{"task": task, "result": {"predicted_target": extreme_predictions(task)[method]}, "status": "ok"} for task in tasks]
    summary = summarize(rows)
    summary["overall"] = {"n": len(outcomes), "correct": sum(outcomes), "accuracy": sum(outcomes) / len(outcomes)}
    return summary


def analyze(run_specs: list[tuple[str, str, Path]], tasks_path: Path) -> dict[str, Any]:
    tasks_path = tasks_path if tasks_path.is_absolute() else ROOT / tasks_path
    tasks = load_jsonl(tasks_path)
    dataset_names = {dataset for dataset, _, _ in run_specs}
    if len(dataset_names) != 1:
        raise ValueError(f"one dataset per report is required, got {sorted(dataset_names)}")
    dataset_name = next(iter(dataset_names))
    runs = []
    for dataset, controller, path in run_specs:
        path = path if path.is_absolute() else ROOT / path
        rows = load_jsonl(path)
        if len(rows) != len(tasks):
            raise ValueError(f"{path} has {len(rows)} rows; expected {len(tasks)}")
        runs.append({"dataset": dataset, "controller": controller, "source": str(path.relative_to(ROOT)), **summarize(rows)})
    runs.append({"dataset": dataset_name, "controller": "Always-Lock+validity", "source": "deterministic control", **deterministic_control(tasks, "always_lock_with_validity")})
    runs.append({"dataset": dataset_name, "controller": "Always-Reevaluate", "source": "deterministic control", **deterministic_control(tasks, "always_reevaluate")})
    return {
        "purpose": "Show which evaluation regimes identify selective authorization and which hide it.",
        "definitions": {
            "preserve_only": "All anchored rows, including stable and changed-winner rows.",
            "reevaluate_only": "All dynamic rows, including stable and changed-winner rows.",
            "stable_only": "State updates with an unchanged selector winner.",
            "changed_winner_only": "Anchored, action-valid rows whose selector winner changes.",
            "conditional_changed_winner": "Changed-winner rows with correct observable initial binding and an action-valid old target; the numerator counts substitution to the refreshed winner.",
            "pairacc": "Both members of a matched Preserve/Reevaluate pair correct under the same state transition.",
        },
        "task_inventory": {"path": str(tasks_path.relative_to(ROOT)), "n": len(tasks)},
        "runs": runs,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Evaluation-Regime Identifiability Audit",
        "",
        report["purpose"],
        "",
        "## Regime definitions",
        "",
        *[f"- `{key}`: {value}" for key, value in report["definitions"].items()],
        "",
        "## Results",
        "",
        "| Dataset | Controller | Aggregate | Preserve-only | Reevaluate-only | Stable-only | Changed-only | PairAcc | Conditional substitution |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for run in report["runs"]:
        regimes = run["regimes"]
        pct = lambda name: "NA" if regimes[name]["accuracy"] is None else f"{100 * regimes[name]['accuracy']:.1f}% ({regimes[name]['correct']}/{regimes[name]['n']})"
        pair = run["changed_pairacc"]
        pair_text = "NA" if pair["pair_accuracy"] is None else f"{100 * pair['pair_accuracy']:.1f}% ({pair['both_correct']}/{pair['pairs']})"
        drift = run["conditional_changed_winner"]
        drift_text = "NA" if drift["drift_rate"] is None else f"{100 * drift['drift_rate']:.1f}% ({drift['drift_to_refreshed_winner']}/{drift['eligible']})"
        lines.append(f"| {run['dataset']} | {run['controller']} | {pct('aggregate_e2e')} | {pct('preserve_only')} | {pct('reevaluate_only')} | {pct('stable_only')} | {pct('changed_winner_only')} | {pair_text} | {drift_text} |")
    lines.extend([
        "",
        "The audit is descriptive and reuses frozen runs; it does not add model calls. Aggregate accuracy is not an identifiability test: Always-Lock and Always-Reevaluate can be equally accurate overall while failing opposite authorization modes.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--run", action="append", nargs=3, metavar=("DATASET", "CONTROLLER", "PATH"), required=True)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    args = parser.parse_args()
    specs = [(dataset, controller, Path(path)) for dataset, controller, path in args.run]
    report = analyze(specs, args.dataset)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
