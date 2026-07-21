"""Cluster-level precision and subsampling stability for matched v7 runs."""

from __future__ import annotations

import random
from collections import defaultdict
from pathlib import Path

from .v7_core_report import cluster_interval, percentile, success
from .v7_leave_group_out import RUNS, index_rows, load_jsonl


DEFAULT_CLUSTER_SIZES = (5, 10, 20, 30, 40)
PRIMARY_RUNS = {
    "Qwen3.5": (
        "20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
        "20260717T030034Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
    ),
    "GLM-5.1": (
        "20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
        "20260717T034201Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
    ),
}


def matched_pairs(
    generic_path: Path, cta_path: Path, expected_tasks: int = 240
) -> list[tuple[dict, dict]]:
    generic = index_rows(load_jsonl(generic_path))
    cta = index_rows(load_jsonl(cta_path))
    if set(generic) != set(cta):
        raise ValueError("Matched runs have different task IDs")
    pairs = [(generic[task_id], cta[task_id]) for task_id in sorted(generic)]
    if len(pairs) != expected_tasks:
        raise ValueError(f"Expected {expected_tasks} matched tasks, found {len(pairs)}")
    return pairs


def delta(pairs: list[tuple[dict, dict]]) -> float:
    return sum(int(success(cta)) - int(success(generic)) for generic, cta in pairs) / len(pairs)


def group_by_cluster(
    pairs: list[tuple[dict, dict]], field: str = "state_cluster_id", expected_clusters: int = 40
) -> dict[str, list[tuple[dict, dict]]]:
    clusters: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for pair in pairs:
        generic, cta = pair
        generic_cluster = generic["task"][field]
        cta_cluster = cta["task"][field]
        if generic_cluster != cta_cluster:
            raise ValueError("Matched task has inconsistent state cluster")
        clusters[generic_cluster].append(pair)
    if len(clusters) != expected_clusters:
        raise ValueError(f"Expected {expected_clusters} clusters, found {len(clusters)}")
    return clusters


def bootstrap_interval(
    pairs: list[tuple[dict, dict]], field: str, expected_clusters: int, trials: int, seed: int
) -> list[float]:
    clusters = group_by_cluster(pairs, field, expected_clusters)
    names = sorted(clusters)
    rng = random.Random(seed)
    values = []
    for _ in range(trials):
        sample = [pair for _ in names for pair in clusters[rng.choice(names)]]
        values.append(delta(sample))
    return [percentile(values, 0.025), percentile(values, 0.975)]


def subsample_curve(
    pairs: list[tuple[dict, dict]], sizes: tuple[int, ...], trials: int, seed: int,
    cluster_field: str = "state_cluster_id", expected_clusters: int = 40,
) -> list[dict]:
    clusters = group_by_cluster(pairs, cluster_field, expected_clusters)
    names = sorted(clusters)
    rng = random.Random(seed)
    curve = []
    for size in sizes:
        if size <= 0 or size > len(names):
            raise ValueError(f"Invalid cluster sample size: {size}")
        values = []
        draws = 1 if size == len(names) else trials
        for _ in range(draws):
            selected = names if size == len(names) else rng.sample(names, size)
            sample = [pair for name in selected for pair in clusters[name]]
            values.append(delta(sample))
        curve.append(
            {
                "clusters": size,
                "tasks": sum(len(clusters[name]) for name in names[:size]),
                "draws": draws,
                "median_delta": percentile(values, 0.5),
                "subsample_interval_95": [percentile(values, 0.025), percentile(values, 0.975)],
                "positive_fraction": sum(value > 0 for value in values) / len(values),
                "at_least_10_points_fraction": sum(value >= 0.10 for value in values) / len(values),
            }
        )
    return curve


def build_report(
    run_dir: Path,
    sizes: tuple[int, ...] = DEFAULT_CLUSTER_SIZES,
    trials: int = 10_000,
    seed: int = 20260721,
) -> dict:
    models = []
    for offset, (model, (generic_name, cta_name)) in enumerate(RUNS.items()):
        pairs = matched_pairs(run_dir / generic_name, run_dir / cta_name)
        full_delta = delta(pairs)
        ci = cluster_interval(pairs, delta, seed + offset, trials)
        models.append(
            {
                "model": model,
                "matched_tasks": len(pairs),
                "state_clusters": len(group_by_cluster(pairs)),
                "tasks_per_cluster": sorted({
                    len(group) for group in group_by_cluster(pairs).values()
                }),
                "full_delta": full_delta,
                "cluster_bootstrap_ci95": ci,
                "curve": subsample_curve(pairs, sizes, trials, seed + 100 + offset),
            }
        )
    return {
        "estimand": "CTA minus Generic paired exact-target accuracy",
        "seed": seed,
        "subsample_draws": trials,
        "title": "TRI-v7 Replication Sample Sufficiency Audit",
        "dataset": "TRI-v7 independent state replication",
        "sampling_unit": "complete state cluster without replacement",
        "models": models,
    }


def build_primary_report(
    run_dir: Path,
    sizes: tuple[int, ...] = (5, 10, 15, 20),
    trials: int = 10_000,
    seed: int = 20260721,
) -> dict:
    models = []
    for offset, (model, (generic_name, cta_name)) in enumerate(PRIMARY_RUNS.items()):
        pairs = matched_pairs(run_dir / generic_name, run_dir / cta_name, expected_tasks=160)
        clusters = group_by_cluster(pairs, "template_id", expected_clusters=20)

        ci = bootstrap_interval(pairs, "template_id", 20, trials, seed + offset)
        models.append(
            {
                "model": model,
                "matched_tasks": len(pairs),
                "state_clusters": len(clusters),
                "tasks_per_cluster": sorted({len(group) for group in clusters.values()}),
                "full_delta": delta(pairs),
                "cluster_bootstrap_ci95": ci,
                "curve": subsample_curve(
                    pairs, sizes, trials, seed + 200 + offset,
                    cluster_field="template_id", expected_clusters=20,
                ),
            }
        )
    return {
        "estimand": "Lifecycle-Gated minus Generic paired exact-target accuracy",
        "seed": seed,
        "subsample_draws": trials,
        "title": "TRI-v3 Primary Sample Sufficiency Audit",
        "dataset": "TRI-v3 primary language-template inventory",
        "sampling_unit": "complete language-template cluster without replacement",
        "models": models,
    }


def markdown(report: dict) -> str:
    lines = [
        f"# {report['title']}",
        "",
        "This is a retrospective precision and stability analysis, not post-hoc power.",
        "Each draw samples complete independent clusters without replacement and retains all tasks",
        "inside each selected cluster. The full-sample confidence interval instead uses paired",
        "paired cluster bootstrap with replacement.",
        "",
        "| Model | Full delta | Cluster-bootstrap 95% CI | Clusters | Tasks |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["models"]:
        lo, hi = row["cluster_bootstrap_ci95"]
        lines.append(
            f"| {row['model']} | {100 * row['full_delta']:.1f} | "
            f"[{100 * lo:.1f}, {100 * hi:.1f}] | {row['state_clusters']} | "
            f"{row['matched_tasks']} |"
        )
    lines.extend([
        "",
        "| Model | Sampled clusters | Tasks | Positive draws | >=10-point draws | Median delta | 95% subsample interval |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["models"]:
        for point in row["curve"]:
            lo, hi = point["subsample_interval_95"]
            lines.append(
                f"| {row['model']} | {point['clusters']} | {point['tasks']} | "
                f"{100 * point['positive_fraction']:.1f}% | "
                f"{100 * point['at_least_10_points_fraction']:.1f}% | "
                f"{100 * point['median_delta']:.1f} | [{100 * lo:.1f}, {100 * hi:.1f}] |"
            )
    lines.extend([
        "",
        "The curve diagnoses effective cluster-level information rather than treating templated",
        "rows as independent observations. It does not establish natural-world",
        "prevalence or replace evaluation on externally sourced TRI opportunities.",
    ])
    return "\n".join(lines) + "\n"
