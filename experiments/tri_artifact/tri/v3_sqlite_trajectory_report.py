from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from .v2_ablation import wilson
from .v2_model_report import is_api_failure, short_model
from .v3_cluster_report import bootstrap_clusters, cluster_id


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(
            short_model(str(row.get("model", "unknown"))),
            str(row.get("result", {}).get("mode", "unknown")),
        )].append(row)

    table = []
    for (model, mode), group in sorted(groups.items()):
        results = [row.get("result", {}) for row in group]
        final_count = sum(bool(result.get("final_state_success")) for result in results)
        lo, hi = wilson(final_count, len(group))
        latencies = [float(row.get("latency_s", 0.0)) for row in group]
        table.append({
            "model": model,
            "mode": mode,
            "n": len(group),
            "resolution_success": sum(bool(result.get("success")) for result in results),
            "final_state_success": final_count,
            "final_state_ci95_low": lo,
            "final_state_ci95_high": hi,
            "wrong_entity_write": sum(result.get("action_status") == "wrong_entity_write" for result in results),
            "invalid_target_attempt": sum(result.get("action_status") == "invalid_target_attempt" for result in results),
            "unnecessary_rejection": sum(result.get("action_status") == "unnecessary_rejection" for result in results),
            "safe_rejection": sum(result.get("action_status") == "safe_rejection" for result in results),
            "collateral_modifications": sum(int(result.get("collateral_modifications", 0)) for result in results),
            "api_errors": sum(is_api_failure(row) for row in group),
            "api_requests": sum(int(row.get("api_request_attempts", 0)) for row in group),
            "api_retries": sum(int(row.get("api_retries", 0)) for row in group),
            "mean_latency_s": sum(latencies) / len(latencies),
            "median_latency_s": median(latencies),
        })
    return {"n_episodes": len(rows), "table": table}


def summarize_pair(path_a: Path, path_b: Path, samples: int, seed: int) -> dict[str, Any]:
    rows_a = {row["task"]["id"]: row for row in load_rows([path_a])}
    rows_b = {row["task"]["id"]: row for row in load_rows([path_b])}
    common = sorted(set(rows_a) & set(rows_b))
    clusters: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for task_id in common:
        clusters[cluster_id(rows_a[task_id])].append((rows_a[task_id], rows_b[task_id]))

    def endpoint(row: dict[str, Any]) -> int:
        return int(bool(row.get("result", {}).get("final_state_success")))

    def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
        return sum(endpoint(b) - endpoint(a) for a, b in sample) / len(sample)

    pairs = [pair for group in clusters.values() for pair in group]
    lo, hi = bootstrap_clusters(clusters, delta, samples, seed)
    first_a, first_b = pairs[0]
    return {
        "model": short_model(str(first_a.get("model", "unknown"))),
        "mode_a": first_a.get("result", {}).get("mode"),
        "mode_b": first_b.get("result", {}).get("mode"),
        "n": len(pairs),
        "n_clusters": len(clusters),
        "delta_final_state_b_minus_a": delta(pairs),
        "cluster_bootstrap_ci95_low": lo,
        "cluster_bootstrap_ci95_high": hi,
    }


def pct(count: int, n: int) -> str:
    return f"{100 * count / n:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v3 Model-Facing SQLite Trajectories",
        "",
        f"Episodes: {report['n_episodes']}",
        "",
        "| Model | Controller | n | Resolution | Final state | Final 95% CI | Wrong write | Invalid attempt | Unneeded reject | Collateral | Requests | Retries | API err. |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["table"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['n']} | "
            f"{pct(row['resolution_success'], row['n'])} | "
            f"{pct(row['final_state_success'], row['n'])} | "
            f"[{100 * row['final_state_ci95_low']:.1f}, {100 * row['final_state_ci95_high']:.1f}] | "
            f"{pct(row['wrong_entity_write'], row['n'])} | "
            f"{pct(row['invalid_target_attempt'], row['n'])} | "
            f"{pct(row['unnecessary_rejection'], row['n'])} | "
            f"{row['collateral_modifications']} | {row['api_requests']} | "
            f"{row['api_retries']} | {row['api_errors']} |"
        )
    if report.get("pairs"):
        lines.extend([
            "",
            "## Paired Final-State Effects",
            "",
            "| Model | A | B | n | Templates | Delta B-A | Cluster 95% CI |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for row in report["pairs"]:
            lines.append(
                f"| {row['model']} | {row['mode_a']} | {row['mode_b']} | {row['n']} | "
                f"{row['n_clusters']} | {100 * row['delta_final_state_b_minus_a']:.1f} | "
                f"[{100 * row['cluster_bootstrap_ci95_low']:.1f}, "
                f"{100 * row['cluster_bootstrap_ci95_high']:.1f}] |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--pair", nargs=2, action="append", default=[])
    ap.add_argument("--bootstrap-samples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260717)
    ap.add_argument("--output", default="reports/v3_sqlite_trajectory_report.json")
    args = ap.parse_args()
    report = summarize(load_rows([Path(path) for path in args.input]))
    report["bootstrap_samples"] = args.bootstrap_samples
    report["seed"] = args.seed
    report["pairs"] = [
        summarize_pair(Path(a), Path(b), args.bootstrap_samples, args.seed)
        for a, b in args.pair
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
