"""Shared-denominator substitution and clustered PairAcc audit for frozen v7 runs."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .identifiability_regimes import changed_winner_task, initial_binding_correct, success
from .v7_core_report import percentile
from .v7_leave_group_out import RUNS, index_rows, load_jsonl


ROOT = Path(__file__).resolve().parents[1]


def protocol_valid(row: dict[str, Any]) -> bool:
    result = row.get("result")
    return bool(
        row.get("status", "ok") == "ok"
        and isinstance(result, dict)
        and not result.get("errors")
        and result.get("error") is None
        and isinstance(result.get("predicted_target"), str)
    )


def shared_eligible(
    generic_rows: list[dict[str, Any]], cta_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    generic = index_rows(generic_rows)
    cta = index_rows(cta_rows)
    if set(generic) != set(cta):
        raise ValueError("Matched runs have different task IDs")

    retained: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for task_id in sorted(generic):
        generic_row = generic[task_id]
        cta_row = cta[task_id]
        if generic_row["task"] != cta_row["task"]:
            raise ValueError(f"Task payload differs across controllers: {task_id}")
        if not changed_winner_task(generic_row):
            continue
        if not (protocol_valid(generic_row) and protocol_valid(cta_row)):
            continue
        if not (initial_binding_correct(generic_row) and initial_binding_correct(cta_row)):
            continue
        retained.append((generic_row, cta_row))

    def substitutions(position: int) -> int:
        return sum(
            pair[position]["result"]["predicted_target"]
            == pair[position]["task"]["post_refresh_target"]
            for pair in retained
        )

    return {
        "eligible": len(retained),
        "generic_substitutions": substitutions(0),
        "cta_substitutions": substitutions(1),
        "task_ids": [generic_row["task"]["id"] for generic_row, _ in retained],
    }


def _pair_signature(task: dict[str, Any]) -> str:
    return json.dumps(
        {
            key: task.get(key)
            for key in (
                "domain",
                "initial_state",
                "refreshed_state",
                "selector",
                "action",
                "action_schema",
                "update",
            )
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def pair_outcomes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        task = row["task"]
        if task.get("update") in {"flip", "name_collision"}:
            groups[_pair_signature(task)][str(task.get("style"))] = row

    pair_keys = (("explicit_anchor", "implicit_dynamic"), ("implicit_anchor", "explicit_dynamic"))
    outcomes: list[dict[str, Any]] = []
    for signature, group in groups.items():
        for preserve, reevaluate in pair_keys:
            if preserve not in group or reevaluate not in group:
                continue
            preserve_row = group[preserve]
            reevaluate_row = group[reevaluate]
            preserve_cluster = preserve_row["task"]["state_cluster_id"]
            if preserve_cluster != reevaluate_row["task"]["state_cluster_id"]:
                raise ValueError("Matched PairAcc members have different state clusters")
            outcomes.append(
                {
                    "pair_id": f"{signature}:{preserve}:{reevaluate}",
                    "state_cluster_id": preserve_cluster,
                    "both_correct": int(success(preserve_row) and success(reevaluate_row)),
                }
            )
    return sorted(outcomes, key=lambda item: item["pair_id"])


def cluster_bootstrap_interval(
    items: list[Any],
    cluster: Callable[[Any], str],
    statistic: Callable[[list[Any]], float],
    samples: int,
    seed: int,
) -> list[float]:
    clusters: dict[str, list[Any]] = defaultdict(list)
    for item in items:
        clusters[cluster(item)].append(item)
    names = sorted(clusters)
    if not names:
        raise ValueError("No clusters available for bootstrap")
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        sample = [item for _ in names for item in clusters[rng.choice(names)]]
        estimates.append(statistic(sample))
    return [percentile(estimates, 0.025), percentile(estimates, 0.975)]


def pairacc_summary(outcomes: list[dict[str, Any]], samples: int, seed: int) -> dict[str, Any]:
    estimate = sum(item["both_correct"] for item in outcomes) / len(outcomes)
    interval = cluster_bootstrap_interval(
        outcomes,
        lambda item: item["state_cluster_id"],
        lambda sample: sum(item["both_correct"] for item in sample) / len(sample),
        samples,
        seed,
    )
    return {
        "pairs": len(outcomes),
        "both_correct": sum(item["both_correct"] for item in outcomes),
        "estimate": estimate,
        "cluster_bootstrap_ci95": interval,
    }


def paired_pairacc_difference(
    generic_outcomes: list[dict[str, Any]],
    cta_outcomes: list[dict[str, Any]],
    samples: int,
    seed: int,
) -> dict[str, Any]:
    generic = {item["pair_id"]: item for item in generic_outcomes}
    cta = {item["pair_id"]: item for item in cta_outcomes}
    if set(generic) != set(cta):
        raise ValueError("Controllers have different PairAcc pairs")
    differences = []
    for pair_id in sorted(generic):
        if generic[pair_id]["state_cluster_id"] != cta[pair_id]["state_cluster_id"]:
            raise ValueError("Matched PairAcc pair has inconsistent state cluster")
        differences.append(
            {
                "state_cluster_id": generic[pair_id]["state_cluster_id"],
                "difference": cta[pair_id]["both_correct"] - generic[pair_id]["both_correct"],
            }
        )
    estimate = sum(item["difference"] for item in differences) / len(differences)
    interval = cluster_bootstrap_interval(
        differences,
        lambda item: item["state_cluster_id"],
        lambda sample: sum(item["difference"] for item in sample) / len(sample),
        samples,
        seed,
    )
    return {"pairs": len(differences), "estimate": estimate, "cluster_bootstrap_ci95": interval}


def build_report(run_dir: Path, samples: int = 10_000, seed: int = 20260722) -> dict[str, Any]:
    models = []
    for offset, (model, (generic_name, cta_name)) in enumerate(RUNS.items()):
        generic_rows = load_jsonl(run_dir / generic_name)
        cta_rows = load_jsonl(run_dir / cta_name)
        generic_pairs = pair_outcomes(generic_rows)
        cta_pairs = pair_outcomes(cta_rows)
        if len(generic_pairs) != 80 or len(cta_pairs) != 80:
            raise ValueError(f"{model}: expected 80 PairAcc pairs per controller")
        models.append(
            {
                "model": model,
                "sources": {"generic": generic_name, "cta": cta_name},
                "shared_eligible": shared_eligible(generic_rows, cta_rows),
                "generic_pairacc": pairacc_summary(generic_pairs, samples, seed + 3 * offset),
                "cta_pairacc": pairacc_summary(cta_pairs, samples, seed + 3 * offset + 1),
                "cta_minus_generic_pairacc": paired_pairacc_difference(
                    generic_pairs, cta_pairs, samples, seed + 3 * offset + 2
                ),
            }
        )
    return {
        "status": "post-primary zero-API audit of frozen outputs",
        "protocol": "reports/TRI_v7_shared_eligible_pairacc_protocol.md",
        "bootstrap": {
            "sampling_unit": "complete state-instance cluster with replacement",
            "clusters": 40,
            "samples": samples,
            "seed": seed,
        },
        "models": models,
        "interpretation_boundary": (
            "Shared eligibility removes controller-specific initial-binding selection only. "
            "Zero observed CTA substitutions do not establish zero population risk."
        ),
    }


def _fraction(value: float) -> str:
    return f"{100 * value:.1f}%"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# V7 Shared-Eligible and PairAcc Uncertainty Audit",
        "",
        f"**Status:** {report['status']}.",
        "",
        "| Model | Shared eligible | Generic substitutions | CTA substitutions |",
        "|---|---:|---:|---:|",
    ]
    for row in report["models"]:
        shared = row["shared_eligible"]
        lines.append(
            f"| {row['model']} | {shared['eligible']} | "
            f"{shared['generic_substitutions']} | {shared['cta_substitutions']} |"
        )
    lines.extend(
        [
            "",
            "The shared denominator requires both controllers to expose the correct initial ID on the",
            "same action-valid changed-winner task and excludes API, parse, and protocol failures.",
            "",
            "| Model | Generic PairAcc (95% CI) | CTA PairAcc (95% CI) | CTA-Generic (95% CI) |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in report["models"]:
        generic = row["generic_pairacc"]
        cta = row["cta_pairacc"]
        difference = row["cta_minus_generic_pairacc"]
        generic_ci = generic["cluster_bootstrap_ci95"]
        cta_ci = cta["cluster_bootstrap_ci95"]
        difference_ci = difference["cluster_bootstrap_ci95"]
        lines.append(
            f"| {row['model']} | {generic['both_correct']}/{generic['pairs']} "
            f"[{_fraction(generic_ci[0])}, {_fraction(generic_ci[1])}] | "
            f"{cta['both_correct']}/{cta['pairs']} "
            f"[{_fraction(cta_ci[0])}, {_fraction(cta_ci[1])}] | "
            f"{_fraction(difference['estimate'])} "
            f"[{_fraction(difference_ci[0])}, {_fraction(difference_ci[1])}] |"
        )
    lines.extend(
        [
            "",
            f"Bootstrap: {report['bootstrap']['samples']:,} resamples of all "
            f"{report['bootstrap']['clusters']} state clusters with replacement; base seed "
            f"{report['bootstrap']['seed']}.",
            "",
            report["interpretation_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=ROOT / "runs")
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.run_dir, args.samples, args.seed)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
