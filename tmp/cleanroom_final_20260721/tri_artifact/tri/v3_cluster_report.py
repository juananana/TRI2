from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .v2_model_report import is_api_failure, short_model


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def success(row: dict[str, Any]) -> int:
    return int(not is_api_failure(row) and bool(row.get("result", {}).get("success")))


def cluster_id(row: dict[str, Any]) -> str:
    task = row["task"]
    return str(task.get("template_id") or task.get("paraphrase") or "unknown")


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bootstrap_clusters(
    clusters: dict[str, list[Any]],
    statistic: Callable[[list[Any]], float],
    samples: int,
    seed: int,
) -> tuple[float, float]:
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sampled: list[Any] = []
        for _ in names:
            sampled.extend(clusters[rng.choice(names)])
        values.append(statistic(sampled))
    return percentile(values, 0.025), percentile(values, 0.975)


def summarize_run(path: Path, samples: int, seed: int) -> dict[str, Any]:
    rows = load_jsonl(path)
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        clusters[cluster_id(row)].append(row)
    task_accuracy = sum(success(row) for row in rows) / len(rows)
    cluster_accuracies = [
        sum(success(row) for row in group) / len(group) for group in clusters.values()
    ]
    lo, hi = bootstrap_clusters(
        clusters,
        lambda sample: sum(success(row) for row in sample) / len(sample),
        samples,
        seed,
    )
    first = rows[0]
    binding_slices = []
    for binding in sorted({str(row["task"].get("binding", "unknown")) for row in rows}):
        group = [row for row in rows if str(row["task"].get("binding", "unknown")) == binding]
        binding_slices.append({
            "binding": binding,
            "n_tasks": len(group),
            "task_accuracy": sum(success(row) for row in group) / len(group),
        })
    return {
        "file": str(path),
        "model": short_model(first.get("model", "")),
        "mode": first.get("result", {}).get("mode"),
        "n_tasks": len(rows),
        "n_clusters": len(clusters),
        "task_accuracy": task_accuracy,
        "template_macro_accuracy": sum(cluster_accuracies) / len(cluster_accuracies),
        "cluster_bootstrap_ci95_low": lo,
        "cluster_bootstrap_ci95_high": hi,
        "api_errors": sum(is_api_failure(row) for row in rows),
        "binding_slices": binding_slices,
    }


def summarize_pair(path_a: Path, path_b: Path, samples: int, seed: int) -> dict[str, Any]:
    rows_a = {row["task"]["id"]: row for row in load_jsonl(path_a)}
    rows_b = {row["task"]["id"]: row for row in load_jsonl(path_b)}
    common = sorted(set(rows_a) & set(rows_b))
    clusters: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for task_id in common:
        clusters[cluster_id(rows_a[task_id])].append((rows_a[task_id], rows_b[task_id]))

    def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
        return sum(success(b) - success(a) for a, b in sample) / len(sample)

    pairs = [pair for group in clusters.values() for pair in group]
    cluster_deltas = [delta(group) for group in clusters.values()]
    lo, hi = bootstrap_clusters(clusters, delta, samples, seed)
    first_a, first_b = pairs[0]
    return {
        "file_a": str(path_a),
        "file_b": str(path_b),
        "model_a": short_model(first_a.get("model", "")),
        "model_b": short_model(first_b.get("model", "")),
        "mode_a": first_a.get("result", {}).get("mode"),
        "mode_b": first_b.get("result", {}).get("mode"),
        "n_tasks": len(pairs),
        "n_clusters": len(clusters),
        "delta_b_minus_a": delta(pairs),
        "cluster_bootstrap_ci95_low": lo,
        "cluster_bootstrap_ci95_high": hi,
        "template_wins_b": sum(value > 0 for value in cluster_deltas),
        "template_ties": sum(value == 0 for value in cluster_deltas),
        "template_wins_a": sum(value < 0 for value in cluster_deltas),
    }


def pct(value: float) -> str:
    return f"{100 * value:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v3 Cluster-Aware Report",
        "",
        f"Cluster bootstrap samples: {report['bootstrap_samples']}; seed: {report['seed']}.",
        "",
        "## Controllers",
        "",
        "| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['n_tasks']} | {row['n_clusters']} | "
            f"{pct(row['task_accuracy'])} | {pct(row['template_macro_accuracy'])} | "
            f"[{pct(row['cluster_bootstrap_ci95_low'])}, "
            f"{pct(row['cluster_bootstrap_ci95_high'])}] | {row['api_errors']} |"
        )
    if any(row["binding_slices"] for row in report["runs"]):
        lines.extend([
            "",
            "## Binding Slices",
            "",
            "| Model | Controller | Binding | Tasks | Task Acc. |",
            "|---|---|---|---:|---:|",
        ])
        for row in report["runs"]:
            for slice_row in row["binding_slices"]:
                lines.append(
                    f"| {row['model']} | {row['mode']} | {slice_row['binding']} | "
                    f"{slice_row['n_tasks']} | {pct(slice_row['task_accuracy'])} |"
                )
    if report["pairs"]:
        lines.extend([
            "",
            "## Pre-Specified Paired Comparisons",
            "",
            "| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI | B win / tie / A win |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for row in report["pairs"]:
            lines.append(
                f"| {row['model_a']} {row['mode_a']} | {row['model_b']} {row['mode_b']} | "
                f"{row['n_tasks']} | {row['n_clusters']} | {pct(row['delta_b_minus_a'])} | "
                f"[{pct(row['cluster_bootstrap_ci95_low'])}, "
                f"{pct(row['cluster_bootstrap_ci95_high'])}] | "
                f"{row['template_wins_b']} / {row['template_ties']} / {row['template_wins_a']} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--pair", nargs=2, action="append", default=[])
    ap.add_argument("--bootstrap-samples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260717)
    ap.add_argument("--output", default="reports/v3_cluster_report.json")
    args = ap.parse_args()
    report = {
        "bootstrap_samples": args.bootstrap_samples,
        "seed": args.seed,
        "runs": [
            summarize_run(Path(path), args.bootstrap_samples, args.seed)
            for path in args.input
        ],
        "pairs": [
            summarize_pair(Path(a), Path(b), args.bootstrap_samples, args.seed)
            for a, b in args.pair
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
