from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any, Callable

from .policy_extreme_controls import predictions as extreme_predictions


ROOT = Path(__file__).resolve().parents[1]
PAIR_STYLES = {
    "explicit_anchor": "implicit_dynamic",
    "implicit_anchor": "explicit_dynamic",
}
SIGNATURE_FIELDS = (
    "domain",
    "initial_state",
    "refreshed_state",
    "selector",
    "action",
    "action_schema",
    "update",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def transition_signature(task: dict[str, Any]) -> str:
    payload = {field: task.get(field) for field in SIGNATURE_FIELDS}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_pairs(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for task in tasks:
        signature = transition_signature(task)
        style = str(task.get("style"))
        if style in groups[signature]:
            raise ValueError(f"duplicate style {style} for transition {task.get('id')}")
        groups[signature][style] = task

    pairs: list[dict[str, Any]] = []
    for signature, styles in groups.items():
        for anchor_style, dynamic_style in PAIR_STYLES.items():
            if anchor_style not in styles and dynamic_style not in styles:
                continue
            if anchor_style not in styles or dynamic_style not in styles:
                raise ValueError(
                    f"incomplete pair for {anchor_style}/{dynamic_style}: {sorted(styles)}"
                )
            preserve = styles[anchor_style]
            reevaluate = styles[dynamic_style]
            if preserve.get("binding") != "anchored" or reevaluate.get("binding") != "dynamic":
                raise ValueError("pair does not contain anchored and dynamic tasks")
            pairs.append({
                "pair_id": f"{preserve['id']}::{reevaluate['id']}",
                "signature": signature,
                "update": preserve.get("update"),
                "preserve_id": preserve["id"],
                "reevaluate_id": reevaluate["id"],
            })
    expected_tasks = {task["id"] for task in tasks}
    paired_tasks = {
        task_id
        for pair in pairs
        for task_id in (pair["preserve_id"], pair["reevaluate_id"])
    }
    if paired_tasks != expected_tasks:
        missing = sorted(expected_tasks - paired_tasks)
        extra = sorted(paired_tasks - expected_tasks)
        raise ValueError(f"pair coverage mismatch; missing={missing[:3]}, extra={extra[:3]}")
    return sorted(pairs, key=lambda pair: pair["pair_id"])


def pair_slice(update: str) -> str:
    if update in {"flip", "name_collision"}:
        return "changed_winner_core"
    if update == "stable":
        return "stable_control"
    if update in {"remove", "invalidate"}:
        return "invalidity_policy"
    return "other"


def result_success(row: dict[str, Any]) -> bool:
    if row.get("status", "ok") != "ok":
        return False
    result = row.get("result")
    if not isinstance(result, dict):
        return False
    if result.get("errors"):
        return False
    if result.get("error") is not None:
        return False
    if "success" in result:
        return bool(result["success"])
    task = row.get("task", {})
    return result.get("predicted_target") == task.get("correct_target")


def run_outcomes(path: Path) -> tuple[dict[str, bool], dict[str, int]]:
    rows = load_jsonl(path)
    outcomes: dict[str, bool] = {}
    failures = {"api_or_status_errors": 0, "parse_or_protocol_errors": 0}
    for row in rows:
        task = row.get("task", {})
        task_id = task.get("id")
        if not task_id:
            raise ValueError(f"row without task.id in {path}")
        if task_id in outcomes:
            raise ValueError(f"duplicate task {task_id} in {path}")
        outcomes[task_id] = result_success(row)
        if row.get("status", "ok") != "ok":
            failures["api_or_status_errors"] += 1
        elif not isinstance(row.get("result"), dict) or row.get("result", {}).get("errors"):
            failures["parse_or_protocol_errors"] += 1
        elif row.get("result", {}).get("error") is not None:
            failures["parse_or_protocol_errors"] += 1
    return outcomes, failures


def deterministic_outcomes(
    tasks: list[dict[str, Any]], predictor: Callable[[dict[str, Any]], str]
) -> dict[str, bool]:
    return {task["id"]: predictor(task) == task.get("correct_target") for task in tasks}


def summarize_pairs(
    pairs: list[dict[str, Any]], outcomes: dict[str, bool]
) -> tuple[dict[str, dict[str, Any]], int]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        grouped["all"].append(pair)
        grouped[pair_slice(str(pair["update"]))].append(pair)

    summaries: dict[str, dict[str, Any]] = {}
    for name in ("all", "changed_winner_core", "stable_control", "invalidity_policy"):
        rows = grouped.get(name, [])
        preserve_correct = sum(outcomes.get(pair["preserve_id"], False) for pair in rows)
        reevaluate_correct = sum(outcomes.get(pair["reevaluate_id"], False) for pair in rows)
        both = sum(
            outcomes.get(pair["preserve_id"], False)
            and outcomes.get(pair["reevaluate_id"], False)
            for pair in rows
        )
        summaries[name] = {
            "pairs": len(rows),
            "preserve_correct": preserve_correct,
            "preserve_accuracy": preserve_correct / len(rows) if rows else None,
            "reevaluate_correct": reevaluate_correct,
            "reevaluate_accuracy": reevaluate_correct / len(rows) if rows else None,
            "both_correct": both,
            "pair_accuracy": both / len(rows) if rows else None,
        }
    expected_ids = {
        task_id
        for pair in pairs
        for task_id in (pair["preserve_id"], pair["reevaluate_id"])
    }
    return summaries, len(expected_ids - outcomes.keys())


def run_entry(
    dataset: str,
    model: str,
    controller: str,
    pairs: list[dict[str, Any]],
    outcomes: dict[str, bool],
    source: str,
    failures: dict[str, int] | None = None,
) -> dict[str, Any]:
    slices, missing = summarize_pairs(pairs, outcomes)
    return {
        "dataset": dataset,
        "model": model,
        "controller": controller,
        "source": source,
        "missing_outputs_itt_incorrect": missing,
        **(failures or {"api_or_status_errors": 0, "parse_or_protocol_errors": 0}),
        "slices": slices,
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    datasets = {
        "v3": load_jsonl(root / "data/temporal_referent_v3_language_clusters.jsonl"),
        "v7": load_jsonl(root / "data/temporal_referent_v7_core_replication.jsonl"),
    }
    pairs = {name: build_pairs(tasks) for name, tasks in datasets.items()}
    entries: list[dict[str, Any]] = []

    run_specs = (
        ("v3", "Qwen3.5", "Generic", "runs/20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl"),
        ("v3", "GLM-5.1", "Generic", "runs/20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl"),
        ("v3", "Qwen3.5", "CTA", "runs/v3_exact_predecessor_qwen_full.jsonl"),
        ("v3", "GLM-5.1", "CTA", "runs/v3_exact_predecessor_glm_full.jsonl"),
        ("v3", "Qwen3.5", "Lifecycle-free", "runs/v3_factorial_qwen_primary_lifecycle_free.jsonl"),
        ("v3", "GLM-5.1", "Lifecycle-free", "runs/v3_factorial_glm_primary_lifecycle_free.jsonl"),
        ("v3", "Qwen3.5", "Lifecycle-gated", "runs/20260717T030034Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl"),
        ("v3", "GLM-5.1", "Lifecycle-gated", "runs/20260717T034201Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl"),
        ("v7", "Qwen3.5", "Generic", "runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl"),
        ("v7", "GLM-5.1", "Generic", "runs/v7_glm_generic_structured_ledger_then_act_full.jsonl"),
        ("v7", "DeepSeek-V4-Pro", "Generic", "runs/v7_deepseek_generic_structured_ledger_then_act_full_v1.jsonl"),
        ("v7", "Qwen3.5", "CTA", "runs/v7_qwen_compile_then_act_full.jsonl"),
        ("v7", "GLM-5.1", "CTA", "runs/v7_glm_compile_then_act_full.jsonl"),
        ("v7", "DeepSeek-V4-Pro", "CTA", "runs/v7_deepseek_compile_then_act_full_v1.jsonl"),
        ("v7", "Qwen3.5", "Lifecycle-gated", "runs/v7_qwen_factorized_hybrid_compile_then_act_full.jsonl"),
        ("v7", "GLM-5.1", "Lifecycle-gated", "runs/v7_glm_factorized_hybrid_compile_then_act_full.jsonl"),
    )
    for dataset, model, controller, relative in run_specs:
        path = root / relative
        outcomes, failures = run_outcomes(path)
        entries.append(run_entry(dataset, model, controller, pairs[dataset], outcomes, relative, failures))

    for dataset in ("v3", "v7"):
        tasks = datasets[dataset]
        for controller, key in (
            ("Always-Lock+validity", "always_lock_with_validity"),
            ("Always-Reevaluate", "always_reevaluate"),
        ):
            outcomes = deterministic_outcomes(tasks, lambda task, k=key: extreme_predictions(task)[k])
            entries.append(run_entry(dataset, "model-independent", controller, pairs[dataset], outcomes, "deterministic control"))
        rule_path = root / f"runs/deterministic_discourse_rule_v2_{dataset}.jsonl"
        outcomes, failures = run_outcomes(rule_path)
        entries.append(run_entry(dataset, "model-independent", "Rule v2 (post-hoc)", pairs[dataset], outcomes, str(rule_path.relative_to(root)), failures))

    return {
        "definition": (
            "PairAcc is the fraction of complete dataset-matched Preserve/Reevaluate pairs for "
            "which both task outcomes are correct. Pairs hold S0, S1, selector, action, schema, "
            "and update fixed. Preserve and Reevaluate marginal accuracy are also reported to "
            "expose one-sided policies. Missing outputs and API/parse/protocol failures are "
            "incorrect under ITT."
        ),
        "pairing": (
            "explicit_anchor is paired with implicit_dynamic; implicit_anchor is paired with "
            "explicit_dynamic when both occur. Stable is a control slice; changed-winner core "
            "contains flip and name_collision; remove/invalidate form a separate policy slice."
        ),
        "inventory": {
            name: {
                "tasks": len(tasks),
                "pairs": len(pairs[name]),
                "slice_pairs": {
                    slice_name: block["pairs"]
                    for slice_name, block in summarize_pairs(pairs[name], {})[0].items()
                },
            }
            for name, tasks in datasets.items()
        },
        "results": entries,
        "availability_note": (
            "v7 Lifecycle-gated outputs exist for Qwen and GLM, but not DeepSeek; no value is imputed."
        ),
    }


def percentage(correct: int, total: int) -> str:
    value = (Decimal(correct * 100) / Decimal(total)).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_EVEN
    )
    return f"{value:.1f}"


def pct(block: dict[str, Any]) -> str:
    if not block["pairs"]:
        return "NA"
    correct = block["both_correct"]
    total = block["pairs"]
    return f"{correct}/{total} ({percentage(correct, total)}%)"


def marginal_pct(block: dict[str, Any], mode: str) -> str:
    if not block["pairs"]:
        return "NA"
    correct = block[f"{mode}_correct"]
    total = block["pairs"]
    return f"{correct}/{total} ({percentage(correct, total)}%)"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Matched-Pair Consistency Audit",
        "",
        report["definition"],
        "",
        report["pairing"],
        "",
        "| Dataset | Model | Controller | All pairs | Changed PairAcc | Changed Preserve | Changed Reevaluate | Stable | Invalidity policy | Missing | API/status | Parse/protocol |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        slices = row["slices"]
        lines.append(
            f"| {row['dataset']} | {row['model']} | {row['controller']} | "
            f"{pct(slices['all'])} | {pct(slices['changed_winner_core'])} | "
            f"{marginal_pct(slices['changed_winner_core'], 'preserve')} | "
            f"{marginal_pct(slices['changed_winner_core'], 'reevaluate')} | "
            f"{pct(slices['stable_control'])} | {pct(slices['invalidity_policy'])} | "
            f"{row['missing_outputs_itt_incorrect']} | {row['api_or_status_errors']} | "
            f"{row['parse_or_protocol_errors']} |"
        )
    lines.extend(["", report["availability_note"], ""])
    return "\n".join(lines)
