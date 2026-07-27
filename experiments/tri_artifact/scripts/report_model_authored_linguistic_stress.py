#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tri.model_authored_linguistic_stress import (
    EVIDENCE_STATUS,
    MODEL_IDS,
    cluster_bootstrap_difference,
    conditional_substitution,
    exact_mcnemar,
    judge_accepts,
    load_jsonl,
    prediction_rows_from_run,
    run_rule,
    sha256_path,
    summarize_predictions,
    validate_tasks,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data/model_authored_linguistic_stress_v1.jsonl"
MANIFEST = ROOT / "reports/model_authored_linguistic_stress_freeze_manifest_v1.json"
OUTPUT_JSON = ROOT / "reports/model_authored_linguistic_stress_transport_repaired_v2.json"
OUTPUT_MD = ROOT / "reports/model_authored_linguistic_stress_transport_repaired_v2.md"
REPAIR_ADDENDUM = ROOT / "reports/TRI_model_authored_linguistic_stress_transport_repair_addendum.md"
REPAIR_SOURCE = ROOT / "tri/model_authored_linguistic_stress.py"


def run_path(model: str, controller: str) -> Path:
    return ROOT / f"runs/model_authored_linguistic_evaluate_{model}_{controller}_full_v1.jsonl"


def judge_path(model: str) -> Path:
    return ROOT / f"runs/model_authored_linguistic_judge_{model}_full_v1.jsonl"


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}%"


def validate_inventory(path: Path, expected_ids: set[str], expected_kind: str) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    ids = [row["task"]["id"] for row in rows]
    if len(rows) != 48 or len(set(ids)) != 48 or set(ids) != expected_ids:
        raise ValueError(f"{path}: expected exact 48-row task inventory")
    if any(row.get("kind") != expected_kind or row.get("run_scope") != "full" for row in rows):
        raise ValueError(f"{path}: run provenance mismatch")
    return rows


def mode_summary(tasks: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    output = {}
    for mode in ("preserve", "reevaluate"):
        subset = [task for task in tasks if task["reference_mode_gold"] == mode]
        correct = sum(predictions.get(task["id"], {}).get("predicted_target") == task["correct_target"] for task in subset)
        output[mode] = {"n": len(subset), "correct": correct, "accuracy": correct / len(subset)}
    return output


def pair_correctness(tasks: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], valid_ids: set[str] | None = None) -> dict[str, bool]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        if valid_ids is None or task["id"] in valid_ids:
            grouped[task["state_cluster_id"]].append(task)
    return {
        pair_id: all(predictions.get(task["id"], {}).get("predicted_target") == task["correct_target"] for task in pair)
        for pair_id, pair in grouped.items()
        if len(pair) == 2
    }


def build_report(tasks_path: Path = TASKS) -> dict[str, Any]:
    tasks = load_jsonl(tasks_path)
    validate_tasks(tasks)
    expected_ids = {task["id"] for task in tasks}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["task_inventory"]["sha256"] != sha256_path(tasks_path):
        raise ValueError("task inventory no longer matches the second-stage freeze manifest")

    judge_rows = {
        model: validate_inventory(judge_path(model), expected_ids, "judge")
        for model in MODEL_IDS
    }
    judge_maps = {
        model: {row["task"]["id"]: row for row in rows}
        for model, rows in judge_rows.items()
    }
    task_map = {task["id"]: task for task in tasks}
    judge_acceptance = {
        model: {task_id for task_id, row in rows.items() if judge_accepts(task_map[task_id], row)}
        for model, rows in judge_maps.items()
    }
    dual_valid_rows = set.intersection(*judge_acceptance.values())
    by_pair: dict[str, set[str]] = defaultdict(set)
    for task in tasks:
        if task["id"] in dual_valid_rows:
            by_pair[task["state_cluster_id"]].add(task["id"])
    dual_valid_pairs = {pair_id for pair_id, ids in by_pair.items() if len(ids) == 2}
    dual_pair_ids = {task["id"] for task in tasks if task["state_cluster_id"] in dual_valid_pairs}

    report: dict[str, Any] = {
        "evidence_status": EVIDENCE_STATUS + "; post-primary transport-repaired",
        "claim_boundary": "frozen model-authored linguistic distribution; not independent human or native-workflow evidence",
        "transport_repair": {
            "reason": "two-hyphen generated IDs were truncated by the pre-existing normalizer",
            "method": "exact actor target and compiled-ID match against serialized state IDs",
            "new_api_calls": 0,
            "invalid_report_retained": "reports/model_authored_linguistic_stress_v1.json",
            "addendum": str(REPAIR_ADDENDUM.relative_to(ROOT)),
            "addendum_sha256": sha256_path(REPAIR_ADDENDUM),
            "source": str(REPAIR_SOURCE.relative_to(ROOT)),
            "source_sha256": sha256_path(REPAIR_SOURCE),
        },
        "inventory": {
            "tasks": len(tasks),
            "pairs": len({task["state_cluster_id"] for task in tasks}),
            "domains": len({task["domain"] for task in tasks}),
            "generation_valid_rows": sum(task["generation_valid"] for task in tasks),
            "generation_failed_rows": sum(not task["generation_valid"] for task in tasks),
            "task_sha256": sha256_path(tasks_path),
            "manifest_sha256": sha256_path(MANIFEST),
        },
        "model_assisted_validation": {
            "judges": {},
            "dual_valid_rows": len(dual_valid_rows),
            "dual_valid_complete_pairs": len(dual_valid_pairs),
        },
        "runs": {},
        "comparisons": {},
    }
    for model, rows in judge_rows.items():
        statuses = Counter(row["status"] for row in rows)
        report["model_assisted_validation"]["judges"][model] = {
            "model_id": MODEL_IDS[model],
            "accepted": len(judge_acceptance[model]),
            "statuses": dict(statuses),
            "path": str(judge_path(model).relative_to(ROOT)),
            "sha256": sha256_path(judge_path(model)),
        }

    prediction_sets: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    run_rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for model in MODEL_IDS:
        for controller in ("generic", "cta"):
            path = run_path(model, controller)
            rows = validate_inventory(path, expected_ids, "evaluate")
            predictions = prediction_rows_from_run(path, controller, transport_repair=True)
            prediction_sets[(model, controller)] = predictions
            run_rows[(model, controller)] = rows
            statuses = Counter(row["status"] for row in rows)
            attempts = sum(len(call.get("attempts", [])) for row in rows for call in row.get("calls", []))
            retries = sum(max(0, len(call.get("attempts", [])) - 1) for row in rows for call in row.get("calls", []))
            report["runs"][f"{model}_{controller}"] = {
                "model_id": MODEL_IDS[model],
                "controller": controller,
                "all_generated_itt": summarize_predictions(tasks, predictions),
                "dual_judge_valid": summarize_predictions(tasks, predictions, dual_valid_rows),
                "by_mode": mode_summary(tasks, predictions),
                "conditional_substitution": conditional_substitution(tasks, predictions),
                "statuses": dict(statuses),
                "http_attempts": attempts,
                "retries": retries,
                "transport_recovered_targets": sum(row["predicted_target"] is not None for row in predictions.values()),
                "transport_unresolved_targets": sum(row["predicted_target"] is None for row in predictions.values()),
                "transport_recovered_initial_bindings": sum(row["initial_binding"] is not None for row in predictions.values()),
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256_path(path),
            }

    for model in MODEL_IDS:
        generic = prediction_sets[(model, "generic")]
        cta = prediction_sets[(model, "cta")]
        generic_pairs = pair_correctness(tasks, generic)
        cta_pairs = pair_correctness(tasks, cta)
        paired = {pair_id: (generic_pairs[pair_id], cta_pairs[pair_id]) for pair_id in sorted(generic_pairs)}
        row_generic = [generic[task["id"]]["predicted_target"] == task["correct_target"] for task in tasks]
        row_cta = [cta[task["id"]]["predicted_target"] == task["correct_target"] for task in tasks]
        dual_generic = pair_correctness(tasks, generic, dual_pair_ids)
        dual_cta = pair_correctness(tasks, cta, dual_pair_ids)
        dual_paired = {pair_id: (dual_generic[pair_id], dual_cta[pair_id]) for pair_id in sorted(dual_generic)}
        report["comparisons"][model] = {
            "all_generated_pairacc_difference": cluster_bootstrap_difference(paired),
            "dual_judge_valid_pairacc_difference": cluster_bootstrap_difference(dual_paired),
            "row_exact_mcnemar": exact_mcnemar(row_generic, row_cta),
        }

    rule_predictions = {
        task_id: {"predicted_target": row.get("predicted_target"), "status": "ok" if row.get("error") is None else "rule_unresolved"}
        for task_id, row in run_rule(tasks).items()
    }
    report["rule_star"] = {
        "status": "post-hoc benchmark-aware frozen rule",
        "all_generated_itt": summarize_predictions(tasks, rule_predictions),
        "dual_judge_valid": summarize_predictions(tasks, rule_predictions, dual_valid_rows),
        "by_mode": mode_summary(tasks, rule_predictions),
        "conditional_substitution": conditional_substitution(tasks, rule_predictions),
        "unresolved": sum(row["status"] != "ok" for row in rule_predictions.values()),
    }
    return report


def markdown(report: dict[str, Any]) -> str:
    inv = report["inventory"]
    validation = report["model_assisted_validation"]
    lines = [
        "# Model-Authored Linguistic Stress Test",
        "",
        f"**Evidence status:** {report['evidence_status']}.",
        "",
        "This result is scoped to a frozen model-authored linguistic distribution. It is not",
        "independent human, naturally occurring workflow, benchmark-prevalence, or primary evidence.",
        "The original all-zero v1 aggregate was an identifier-normalization failure. This report",
        "uses the frozen exact-ID, zero-request transport repair and retains the invalid report.",
        "",
        "## Inventory and model-assisted validity",
        "",
        f"The ITT inventory contains {inv['tasks']} rows, {inv['pairs']} opposite-gold pairs, and {inv['domains']} workflow schemas. "
        f"Generation succeeded for {inv['generation_valid_rows']}/{inv['tasks']} rows. Both model judges accepted "
        f"{validation['dual_valid_rows']}/{inv['tasks']} rows forming {validation['dual_valid_complete_pairs']}/{inv['pairs']} complete pairs.",
        "",
        "| Judge | Accepted | Status counts |",
        "|---|---:|---|",
    ]
    for model, block in validation["judges"].items():
        lines.append(f"| {model} | {block['accepted']}/{inv['tasks']} | `{json.dumps(block['statuses'], sort_keys=True)}` |")
    lines += [
        "",
        "## Controller results",
        "",
        "| Model / controller | ITT row acc. | ITT PairAcc | Dual-valid row acc. | Dual-valid PairAcc | Preserve substitution | Failures |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, block in report["runs"].items():
        all_result, valid = block["all_generated_itt"], block["dual_judge_valid"]
        sub = block["conditional_substitution"]
        failures = sum(count for status, count in block["statuses"].items() if status != "ok")
        lines.append(
            f"| {name} | {all_result['correct_rows']}/{all_result['n_rows']} ({pct(all_result['accuracy'])}) | "
            f"{all_result['correct_pairs']}/{all_result['n_complete_pairs']} ({pct(all_result['pair_accuracy'])}) | "
            f"{valid['correct_rows']}/{valid['n_rows']} ({pct(valid['accuracy'])}) | "
            f"{valid['correct_pairs']}/{valid['n_complete_pairs']} ({pct(valid['pair_accuracy'])}) | "
            f"{sub['substitutions']}/{sub['eligible']} ({pct(sub['rate'])}) | {failures} |"
        )
    rule = report["rule_star"]
    all_rule, valid_rule = rule["all_generated_itt"], rule["dual_judge_valid"]
    lines.append(
        f"| Rule* (post-hoc) | {all_rule['correct_rows']}/{all_rule['n_rows']} ({pct(all_rule['accuracy'])}) | "
        f"{all_rule['correct_pairs']}/{all_rule['n_complete_pairs']} ({pct(all_rule['pair_accuracy'])}) | "
        f"{valid_rule['correct_rows']}/{valid_rule['n_rows']} ({pct(valid_rule['accuracy'])}) | "
        f"{valid_rule['correct_pairs']}/{valid_rule['n_complete_pairs']} ({pct(valid_rule['pair_accuracy'])}) | NA | {rule['unresolved']} |"
    )
    lines += ["", "## Paired comparisons", "", "| Model | CTA - Generic PairAcc | 95% cluster interval | Dual-valid difference | 95% interval | Row discordance G-only / CTA-only |", "|---|---:|---:|---:|---:|---:|"]
    for model, block in report["comparisons"].items():
        all_diff = block["all_generated_pairacc_difference"]
        valid_diff = block["dual_judge_valid_pairacc_difference"]
        mcnemar = block["row_exact_mcnemar"]
        lines.append(
            f"| {model} | {pct(all_diff['difference'])} | [{pct(all_diff['interval'][0])}, {pct(all_diff['interval'][1])}] | "
            f"{pct(valid_diff['difference'])} | [{pct(valid_diff['interval'][0])}, {pct(valid_diff['interval'][1])}] | "
            f"{mcnemar['baseline_only']} / {mcnemar['treatment_only']} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "The all-generated ITT result remains primary for this post-primary addendum; the dual-judge subset is a model-assisted sensitivity analysis. Rule* is retained as the strongest post-hoc baseline. Zero observed failures in any cell would not establish zero risk or natural prevalence.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=Path, default=TASKS)
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=OUTPUT_MD)
    args = parser.parse_args()
    report = build_report(args.tasks)
    args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.output_md.write_text(markdown(report), encoding="utf-8")
    print({"json": str(args.output_json), "markdown": str(args.output_md), "task_sha256": report["inventory"]["task_sha256"]})


if __name__ == "__main__":
    main()
