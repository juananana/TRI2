"""Validation and reporting for frozen external public-dataset annotations."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


EXPECTED_MODELS = ["Qwen/Qwen3.5-122B-A10B", "Pro/zai-org/GLM-5.1"]
ALLOWED_TRI = {"yes", "no", "unclear"}
ALLOWED_TIMING = {"preserve", "reevaluate", "ambiguous", "absent"}
LABEL_FIELDS = {
    "prior_selector_or_selection",
    "observable_stable_id_before_update",
    "binding_before_update",
    "independent_update_after_binding",
    "same_role_competing_entity",
    "distinct_refreshed_winner",
    "old_target_survives",
    "old_target_action_valid",
    "later_target_mutation",
    "timing_authorization",
    "target_level_outcome_observable",
    "source_anchored_eligible",
    "strict_native_tri_opportunity",
}


def valid_annotation(row: dict[str, Any]) -> bool:
    if row.get("status") != "ok" or not isinstance(row.get("annotation"), dict):
        return False
    labels = row["annotation"].get("labels")
    if not isinstance(labels, dict) or set(labels) != LABEL_FIELDS:
        return False
    for field, value in labels.items():
        allowed = ALLOWED_TIMING if field == "timing_authorization" else ALLOWED_TRI
        if value not in allowed:
            return False
    return row["annotation"].get("candidate_id") == row.get("candidate_id")


def build_annotation_report(
    candidates: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    candidate_ids = {row["candidate_id"] for row in candidates}
    dataset_by_candidate = {row["candidate_id"]: row.get("dataset", "unknown") for row in candidates}
    expected_pairs = {(model, candidate_id) for model in EXPECTED_MODELS for candidate_id in candidate_ids}
    latest_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    repeated_pairs: Counter[tuple[str, str]] = Counter()
    attempted_rows = 0
    failed_attempt_rows = 0
    raw_failed_rows = 0
    per_model: dict[str, Counter[str]] = defaultdict(Counter)
    valid_by_model_dataset: Counter[tuple[str, str]] = Counter()
    labels_by_candidate: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    for row in rows:
        pair = (row.get("model"), row.get("candidate_id"))
        if pair in expected_pairs and not valid_annotation(row):
            raw_failed_rows += 1
        if pair in latest_by_pair:
            repeated_pairs[pair] += 1
        latest_by_pair[pair] = row

    for pair, row in latest_by_pair.items():
        if pair not in expected_pairs:
            continue
        attempted_rows += 1
        model = str(row.get("model"))
        if valid_annotation(row):
            per_model[model]["valid"] += 1
            valid_by_model_dataset[(model, dataset_by_candidate.get(row["candidate_id"], "unknown"))] += 1
            labels_by_candidate[row["candidate_id"]][model] = row["annotation"]["labels"]
        else:
            per_model[model]["failed_or_invalid"] += 1
            failed_attempt_rows += 1

    strict_yes_union: set[str] = set()
    strict_yes_intersection: set[str] = set()
    source_yes_union: set[str] = set()
    source_yes_intersection: set[str] = set()
    complete_candidates = 0
    disagreements = 0
    for candidate_id in sorted(candidate_ids):
        model_labels = labels_by_candidate.get(candidate_id, {})
        if set(model_labels) != set(EXPECTED_MODELS):
            continue
        complete_candidates += 1
        strict_values = {
            model: model_labels[model]["strict_native_tri_opportunity"]
            for model in EXPECTED_MODELS
        }
        source_values = {
            model: model_labels[model]["source_anchored_eligible"]
            for model in EXPECTED_MODELS
        }
        if "yes" in strict_values.values():
            strict_yes_union.add(candidate_id)
        if all(value == "yes" for value in strict_values.values()):
            strict_yes_intersection.add(candidate_id)
        if "yes" in source_values.values():
            source_yes_union.add(candidate_id)
        if all(value == "yes" for value in source_values.values()):
            source_yes_intersection.add(candidate_id)
        if len(set(strict_values.values())) > 1 or len(set(source_values.values())) > 1:
            disagreements += 1

    seen_pairs = set(latest_by_pair)
    missing_pairs = sorted(f"{model}::{candidate}" for model, candidate in expected_pairs - seen_pairs)
    completed = len(seen_pairs & expected_pairs)
    status = (
        "post-primary model-assisted annotation; candidate labels only"
        if not missing_pairs
        else "incomplete post-primary model-assisted annotation; candidate labels only"
    )
    smoke_expected = len(candidate_ids) == 4
    if smoke_expected:
        smoke_datasets = set(dataset_by_candidate.values())
        smoke_pass = (
            completed == 8
            and sum(counts["valid"] for counts in per_model.values()) >= 6
            and all(valid_by_model_dataset[(model, dataset)] >= 1 for model in EXPECTED_MODELS for dataset in smoke_datasets)
        )
    else:
        smoke_pass = None

    return {
        "study": "SiliconFlow external public-dataset candidate annotation",
        "status": status,
        "candidate_count": len(candidate_ids),
        "expected_rows": len(expected_pairs),
        "observed_unique_rows": completed,
        "attempted_latest_rows": attempted_rows,
        "failed_latest_rows": failed_attempt_rows,
        "total_raw_rows_supplied": len(rows),
        "raw_failed_rows": raw_failed_rows,
        "complete_two_model_candidates": complete_candidates,
        "per_model": {model: dict(per_model.get(model, Counter())) for model in EXPECTED_MODELS},
        "valid_by_model_dataset": {
            f"{model}::{dataset}": count
            for (model, dataset), count in sorted(valid_by_model_dataset.items())
        },
        "repeated_attempt_pairs": [
            f"{model}::{candidate}" for (model, candidate), count in sorted(repeated_pairs.items()) if count
        ],
        "missing_pairs": missing_pairs,
        "strict_yes_union": sorted(strict_yes_union),
        "strict_yes_intersection": sorted(strict_yes_intersection),
        "source_eligible_yes_union": sorted(source_yes_union),
        "source_eligible_yes_intersection": sorted(source_yes_intersection),
        "two_model_disagreement_candidates": disagreements,
        "smoke_mode": smoke_expected,
        "smoke_pass": smoke_pass,
        "claim_boundary": (
            "These are fallible model candidate labels. A strict-yes label nominates a case for "
            "source verification; it is not itself a native opportunity, independent review, "
            "behavioral result, or prevalence estimate."
        ),
    }


def render_annotation_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SiliconFlow External Public-Dataset Candidate Annotation",
        "",
        f"**Status:** {report['status']}",
        "",
        f"- Frozen candidates: {report['candidate_count']}",
        f"- Expected model rows: {report['expected_rows']}",
        f"- Observed unique rows: {report['observed_unique_rows']}",
        f"- Missing model--candidate pairs: {len(report['missing_pairs'])}",
        f"- Raw attempted rows supplied: {report['total_raw_rows_supplied']}",
        f"- Raw failed rows retained: {report['raw_failed_rows']}",
        f"- Complete two-model candidates: {report['complete_two_model_candidates']}",
        f"- Two-model label disagreements: {report['two_model_disagreement_candidates']}",
        "",
        "| Model | Valid | Failed/invalid |",
        "|---|---:|---:|",
    ]
    for model, counts in report["per_model"].items():
        lines.append(
            f"| {model} | {counts.get('valid', 0)} | {counts.get('failed_or_invalid', 0)} |"
        )
    lines += [
        "",
        f"- Strict-positive candidate union: {len(report['strict_yes_union'])}",
        f"- Strict-positive candidate intersection: {len(report['strict_yes_intersection'])}",
        f"- Source-eligible candidate union: {len(report['source_eligible_yes_union'])}",
        f"- Source-eligible candidate intersection: {len(report['source_eligible_yes_intersection'])}",
    ]
    if report["smoke_mode"]:
        lines += ["", f"**Smoke pass:** {report['smoke_pass']}"]
    lines += ["", "## Boundary", "", report["claim_boundary"], ""]
    return "\n".join(lines)
