"""Quantify policy-selection regret under non-identifying evaluation regimes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v3": ROOT / "reports/v3_identifiability_regimes_v1.json",
    "v7": ROOT / "reports/v7_identifiability_regimes_v1.json",
}
EXPECTED_SHA256 = {
    "v3": "f9acb0c9e7ba9028f1402dff31e7239f937e9267f73bd125653d2e9e845e67d7",
    "v7": "8aac36f5c4d18c3ed1d119d20886ee7c42c3ff1d584a7d2f76b34a1512e61ed4",
}
PROXY_REGIMES = {
    "aggregate_e2e": "Aggregate E2E",
    "preserve_only": "Preserve only",
    "reevaluate_only": "Reevaluate only",
    "stable_only": "Stable only",
}
EXTREMES = {"Always-Lock+validity", "Always-Reevaluate"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs(inputs: dict[str, Path] = INPUTS) -> dict[str, dict[str, Any]]:
    reports = {}
    for dataset, path in inputs.items():
        observed = sha256(path)
        expected = EXPECTED_SHA256[dataset]
        if observed != expected:
            raise ValueError(f"{dataset} input hash mismatch: {observed} != {expected}")
        reports[dataset] = json.loads(path.read_text(encoding="utf-8"))
    return reports


def model_families(runs: list[dict[str, Any]]) -> list[str]:
    families = {
        row["controller"].split("-", 1)[0]
        for row in runs
        if row["controller"] not in EXTREMES
    }
    return sorted(families)


def candidates_for_family(
    runs: list[dict[str, Any]], family: str
) -> list[dict[str, Any]]:
    prefix = family + "-"
    candidates = [
        row for row in runs
        if row["controller"] in EXTREMES or row["controller"].startswith(prefix)
    ]
    if not any(row["controller"].startswith(prefix) for row in candidates):
        raise ValueError(f"No model-specific candidates for {family}")
    if {row["controller"] for row in candidates} & EXTREMES != EXTREMES:
        raise ValueError(f"Missing deterministic extremes for {family}")
    return candidates


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-12


def summarize_candidate_set(
    dataset: str,
    family: str,
    candidates: list[dict[str, Any]],
    proxy_key: str,
) -> dict[str, Any]:
    proxy_scores = {
        row["controller"]: float(row["regimes"][proxy_key]["accuracy"])
        for row in candidates
    }
    pair_scores = {
        row["controller"]: float(row["changed_pairacc"]["pair_accuracy"])
        for row in candidates
    }
    maximum = max(proxy_scores.values())
    maximizers = sorted(
        controller for controller, score in proxy_scores.items() if _close(score, maximum)
    )
    maximizer_pairacc = [pair_scores[controller] for controller in maximizers]
    best_pairacc = max(pair_scores.values())
    minimum_selected = min(maximizer_pairacc)
    maximum_selected = max(maximizer_pairacc)
    return {
        "dataset": dataset,
        "model_family": family,
        "proxy_regime": proxy_key,
        "proxy_label": PROXY_REGIMES[proxy_key],
        "candidate_controllers": sorted(proxy_scores),
        "proxy_maximum": maximum,
        "proxy_maximizers": maximizers,
        "pairacc_among_maximizers": {
            "minimum": minimum_selected,
            "maximum": maximum_selected,
        },
        "best_pairacc_in_candidate_set": best_pairacc,
        "worst_case_selection_regret": best_pairacc - minimum_selected,
        "optimistic_selection_regret": best_pairacc - maximum_selected,
        "zero_pairacc_maximizer_exists": any(_close(value, 0.0) for value in maximizer_pairacc),
    }


def build_report(inputs: dict[str, Path] = INPUTS) -> dict[str, Any]:
    source_reports = load_inputs(inputs)
    rows = []
    source_meta = {}
    for dataset, report in source_reports.items():
        runs = report["runs"]
        source_meta[dataset] = {
            "path": str(inputs[dataset].relative_to(ROOT)),
            "sha256": EXPECTED_SHA256[dataset],
        }
        for family in model_families(runs):
            candidates = candidates_for_family(runs, family)
            for proxy_key in PROXY_REGIMES:
                rows.append(summarize_candidate_set(dataset, family, candidates, proxy_key))
    return {
        "status": "post-primary zero-API audit over frozen identifiability reports",
        "protocol": "reports/TRI_evaluation_selection_regret_protocol.md",
        "target_metric": "changed-winner matched PairAcc",
        "inputs": source_meta,
        "rows": rows,
        "summary": {
            "candidate_sets": len({(row["dataset"], row["model_family"]) for row in rows}),
            "proxy_evaluations": len(rows),
            "zero_pairacc_maximizer_rows": sum(
                row["zero_pairacc_maximizer_exists"] for row in rows
            ),
            "one_sided_or_stable_evaluations": sum(
                row["proxy_regime"] != "aggregate_e2e" for row in rows
            ),
            "one_sided_or_stable_zero_pairacc_rows": sum(
                row["proxy_regime"] != "aggregate_e2e"
                and row["zero_pairacc_maximizer_exists"]
                for row in rows
            ),
            "aggregate_suboptimal_rows": sum(
                row["proxy_regime"] == "aggregate_e2e"
                and row["worst_case_selection_regret"] > 1e-12
                for row in rows
            ),
            "maximum_worst_case_selection_regret": max(
                row["worst_case_selection_regret"] for row in rows
            ),
        },
        "boundaries": [
            "The candidate sets are concrete tested alternatives, not an exhaustive policy class.",
            "Worst-case tie handling means the proxy score licenses a poor policy; it does not claim users always choose it.",
            "PairAcc measures the balanced changed-winner authorization contrast, not general task utility or prevalence.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Evaluation-Selection Regret Audit",
        "",
        f"**Status:** {report['status']}.",
        "",
        "A proxy-score maximizer is any candidate tied for the highest score under that regime.",
        "Regret is measured against the best changed-winner PairAcc in the same model-family candidate set.",
        "",
        "| Dataset/model | Proxy | Maximizers | PairAcc range | Best PairAcc | Worst regret | Optimistic regret | Zero-PairAcc maximizer? |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        selected = row["pairacc_among_maximizers"]
        lines.append(
            f"| {row['dataset']} / {row['model_family']} | {row['proxy_label']} | "
            f"{', '.join(row['proxy_maximizers'])} | "
            f"{100 * selected['minimum']:.1f}--{100 * selected['maximum']:.1f} | "
            f"{100 * row['best_pairacc_in_candidate_set']:.1f} | "
            f"{100 * row['worst_case_selection_regret']:.1f} | "
            f"{100 * row['optimistic_selection_regret']:.1f} | "
            f"{'yes' if row['zero_pairacc_maximizer_exists'] else 'no'} |"
        )
    summary = report["summary"]
    lines.extend(
        [
            "",
            f"Across {summary['candidate_sets']} dataset/model candidate sets and "
            f"{summary['proxy_evaluations']} proxy evaluations, "
            f"all {summary['one_sided_or_stable_evaluations']} Stable-only or one-sided "
            "maximizer sets include a zero-PairAcc unconditional policy.",
            f"The maximum worst-case selection regret is "
            f"{100 * summary['maximum_worst_case_selection_regret']:.1f} points.",
            "",
            *[f"- {boundary}" for boundary in report["boundaries"]],
            "",
        ]
    )
    return "\n".join(lines)


def validate(report: dict[str, Any]) -> None:
    expected_rows = 5 * len(PROXY_REGIMES)
    if len(report["rows"]) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, found {len(report['rows'])}")
    for row in report["rows"]:
        if row["worst_case_selection_regret"] < -1e-12:
            raise ValueError("Negative worst-case selection regret")
        if row["optimistic_selection_regret"] < -1e-12:
            raise ValueError("Negative optimistic selection regret")
        if row["optimistic_selection_regret"] > row["worst_case_selection_regret"] + 1e-12:
            raise ValueError("Optimistic regret exceeds worst-case regret")
