from __future__ import annotations

import json
import random
from collections import defaultdict
from typing import Any

SEED = 20260729
ANNOTATORS = ("A1", "A2", "A3")
CONTROL_ROLE = "injected_control"


def unit_key(row: dict[str, Any]) -> str:
    dataset = str(row.get("dataset", ""))
    value = row.get("candidate_id") or row.get("unit_id") or row.get("cluster_id")
    if not dataset or value is None:
        raise ValueError("audit unit requires dataset and candidate_id/unit_id/cluster_id")
    return f"{dataset}::{value}"


def deduplicate_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        output.setdefault(unit_key(row), dict(row))
    return [output[key] for key in sorted(output)]


def build_sampling_frame(
    population: list[dict[str, Any]], candidates: list[dict[str, Any]],
    controls: list[dict[str, Any]] | None = None, per_dataset: int = 100, seed: int = SEED,
) -> list[dict[str, Any]]:
    if per_dataset <= 0:
        raise ValueError("per_dataset must be positive")
    population_by_key: dict[str, dict[str, Any]] = {}
    for row in population:
        key = unit_key(row)
        if key in population_by_key:
            raise ValueError(f"duplicate population unit: {key}")
        population_by_key[key] = row
    candidate_rows = deduplicate_candidates(candidates)
    candidate_keys = {unit_key(row) for row in candidate_rows}
    if not candidate_keys.issubset(population_by_key):
        raise ValueError("candidate units must exist in the population")
    frame = []
    for row in candidate_rows:
        item = dict(population_by_key[unit_key(row)])
        item.update({"audit_role": "retrieved_candidate", "inclusion_probability": 1.0, "sample_seed": seed})
        frame.append(item)
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in population_by_key.values():
        if unit_key(row) not in candidate_keys:
            by_dataset[str(row["dataset"])].append(row)
    for dataset, rows in sorted(by_dataset.items()):
        rows = sorted(rows, key=unit_key)
        sample_size = min(per_dataset, len(rows))
        rng = random.Random(seed + sum(ord(ch) for ch in dataset))
        probability = sample_size / len(rows) if rows else 0.0
        for row in sorted(rng.sample(rows, sample_size), key=unit_key):
            item = dict(row)
            item.update({"audit_role": "random_non_candidate", "inclusion_probability": probability, "sample_seed": seed})
            frame.append(item)
    for index, row in enumerate(controls or []):
        item = dict(row)
        item.update({"audit_role": CONTROL_ROLE, "inclusion_probability": 1.0, "sample_seed": seed, "control_index": index})
        frame.append(item)
    return frame


def majority_label(adjudications: dict[str, Any]) -> bool:
    if set(adjudications) != set(ANNOTATORS):
        raise ValueError("exactly three annotator labels are required")
    values = [value if isinstance(value, bool) else str(value).lower() in {"true", "yes", "positive", "1"} for value in adjudications.values()]
    return sum(values) >= 2


def attach_adjudication(row: dict[str, Any]) -> dict[str, Any]:
    majority = majority_label(row.get("adjudications", {}))
    values = [value if isinstance(value, bool) else str(value).lower() in {"true", "yes", "positive", "1"} for value in row["adjudications"].values()]
    agreement = max(sum(values), len(values) - sum(values)) / 3
    return {**row, "majority_strict_positive": majority, "item_agreement": agreement}


def _bootstrap_rate(units: list[tuple[float, bool]], seed: int, samples: int) -> list[float]:
    if not units:
        return []
    rng = random.Random(seed)
    values = []
    for _ in range(samples):
        draws = [units[rng.randrange(len(units))] for _ in units]
        denominator = sum(weight for weight, _ in draws)
        values.append(sum(weight for weight, positive in draws if positive) / denominator if denominator else 0.0)
    return values


def report_audit(rows: list[dict[str, Any]], population_sizes: dict[str, int], seed: int = SEED, bootstrap_samples: int = 10_000) -> dict[str, Any]:
    labeled = [attach_adjudication(row) for row in rows]
    natural = [row for row in labeled if row.get("audit_role") != CONTROL_ROLE]
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in natural:
        by_dataset[str(row["dataset"])].append(row)
    datasets = {}
    for dataset, dataset_rows in sorted(by_dataset.items()):
        units = []
        candidate_positive = 0.0
        for row in dataset_rows:
            weight = 1.0 / float(row.get("inclusion_probability", 1.0))
            positive = bool(row["majority_strict_positive"])
            units.append((weight, positive))
            if positive and row.get("audit_role") == "retrieved_candidate":
                candidate_positive += weight
        denominator = sum(weight for weight, _ in units)
        numerator = sum(weight for weight, positive in units if positive)
        bootstrap = sorted(_bootstrap_rate(units, seed + sum(ord(ch) for ch in dataset), bootstrap_samples))
        ci = [bootstrap[int(0.025 * len(bootstrap))], bootstrap[min(len(bootstrap) - 1, int(0.975 * len(bootstrap)))] ] if bootstrap else [None, None]
        population_size = int(population_sizes.get(dataset, 0))
        datasets[dataset] = {
            "population_size": population_size, "labeled_units": len(dataset_rows),
            "weighted_denominator": denominator, "weighted_positive": numerator,
            "prevalence": numerator / denominator if denominator else None,
            "bootstrap_ci95": ci,
            "zero_positive_upper_bound_95": min(1.0, 3.0 / population_size) if population_size and numerator == 0 else None,
            "candidate_positive_weight": candidate_positive,
            "retrieval_sensitivity": candidate_positive / numerator if numerator else None,
            "retrieval_sensitivity_identifiable": bool(numerator),
        }
    controls = [row for row in labeled if row.get("audit_role") == CONTROL_ROLE]
    return {
        "audit_version": "TRI-public-recall-calibrated-audit-v1",
        "evidence_status": "planned/unverified", "seed": seed, "bootstrap_samples": bootstrap_samples,
        "natural_rows": len(natural), "control_rows": len(controls), "datasets": datasets,
        "natural_positive_found": any(item["weighted_positive"] > 0 for item in datasets.values()),
        "recall_claim_allowed": any(item["retrieval_sensitivity_identifiable"] for item in datasets.values()),
        "controls": {
            "positive_correct": sum(row.get("expected_strict_positive") is True and row["majority_strict_positive"] for row in controls),
            "positive_total": sum(row.get("expected_strict_positive") is True for row in controls),
            "negative_correct": sum(row.get("expected_strict_positive") is False and not row["majority_strict_positive"] for row in controls),
            "negative_total": sum(row.get("expected_strict_positive") is False for row in controls),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Public Recall-Calibrated Audit", "", "| Dataset | Population | Labeled | Weighted positive | Prevalence | Zero-positive upper bound | Recall identifiable |", "|---|---:|---:|---:|---:|---:|---|"]
    for dataset, item in report["datasets"].items():
        prevalence = "NA" if item["prevalence"] is None else f"{100 * item['prevalence']:.3f}%"
        upper = "NA" if item["zero_positive_upper_bound_95"] is None else f"{100 * item['zero_positive_upper_bound_95']:.3f}%"
        lines.append(f"| {dataset} | {item['population_size']} | {item['labeled_units']} | {item['weighted_positive']:.2f} | {prevalence} | {upper} | {item['retrieval_sensitivity_identifiable']} |")
    lines.extend(["", f"Natural positives found: `{report['natural_positive_found']}`.", f"Recall claim allowed: `{report['recall_claim_allowed']}`.", "", "Injected controls are excluded from natural estimates."])
    return "\n".join(lines)
