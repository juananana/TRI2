"""Post-run repair for changed-pair bootstrap intervals in revision audits."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any

from .revision_matched_audit import BOOTSTRAP_SAMPLES, BOOTSTRAP_SEED, exact_target


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _pair_correct(pair: list[dict[str, Any]], condition: str) -> bool:
    return all(
        exact_target(row.get("outcomes", {}).get(condition))
        == exact_target(row["task"]["correct_target"])
        for row in pair
    )


def eligible_changed_pairs(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["task"]["pair_id"]].append(row)
    return [
        pair
        for _, pair in sorted(grouped.items())
        if len(pair) == 2
        and {row["task"]["reference_mode_gold"] for row in pair}
        == {"preserve", "reevaluate"}
        and all(row["task"]["actionable_core"] for row in pair)
        and pair[0]["task"]["pre_refresh_target"]
        != pair[0]["task"]["post_refresh_target"]
    ]


def corrected_changed_pair_difference(
    rows: list[dict[str, Any]],
    seed: int = BOOTSTRAP_SEED,
    samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    pairs = eligible_changed_pairs(rows)
    effects = [
        int(_pair_correct(pair, "decision_visible"))
        - int(_pair_correct(pair, "history_only"))
        for pair in pairs
    ]
    estimate = sum(effects) / len(effects) if effects else None
    rng = random.Random(seed)
    draws = [
        sum(rng.choice(effects) for _ in effects) / len(effects)
        for _ in range(samples)
    ] if effects else []
    return {
        "left": "history_only",
        "right": "decision_visible",
        "difference": estimate,
        "ci95_cluster": [_percentile(draws, 0.025), _percentile(draws, 0.975)],
    }


def apply_changed_pair_interval_repair(
    report: dict[str, Any],
    rows: list[dict[str, Any]],
    seed: int = BOOTSTRAP_SEED,
    samples: int = BOOTSTRAP_SAMPLES,
) -> None:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    report_models = {model["model"]: model for model in report["models"]}
    if set(report_models) != set(by_model):
        raise ValueError("report and raw rows have different model sets")
    for model, model_rows in by_model.items():
        corrected = corrected_changed_pair_difference(model_rows, seed, samples)
        observed = report_models[model]["decision_visible_minus_history"]["changed_pairacc"]
        observed_difference = observed["difference"]
        corrected_difference = corrected["difference"]
        if (
            observed_difference is None
            or corrected_difference is None
            or not math.isclose(observed_difference, corrected_difference, abs_tol=1e-12)
        ):
            raise ValueError(f"changed-PairAcc point estimate changed for {model}")
        report_models[model]["decision_visible_minus_history"]["changed_pairacc"] = corrected
