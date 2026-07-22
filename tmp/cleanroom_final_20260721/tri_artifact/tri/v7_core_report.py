from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .v2_model_report import is_api_failure, short_model


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_id[row["task"]["id"]] = row
    return list(by_id.values())


def success(row: dict[str, Any]) -> bool:
    return not is_api_failure(row) and bool(row.get("result", {}).get("success"))


def initial_id(row: dict[str, Any]) -> str | None:
    ledger = row.get("result", {}).get("compiled_ledger") or {}
    mode = str(row.get("result", {}).get("mode", ""))
    if "generic" in mode:
        return ledger.get("selected_entity_id")
    return ledger.get("bound_target_id")


def initial_correct(row: dict[str, Any]) -> bool:
    return initial_id(row) == row["task"].get("pre_refresh_target")


def mode_correct(row: dict[str, Any]) -> bool | None:
    result = row.get("result", {})
    ledger = result.get("compiled_ledger") or {}
    mode = str(result.get("mode", ""))
    expected = "preserve" if row["task"].get("binding") == "anchored" else "reevaluate"
    if "factorized" in mode:
        return ledger.get("reference_mode") == expected
    if mode == "compile_then_act":
        expected_time = "pre_refresh" if expected == "preserve" else "post_refresh"
        return ledger.get("binding_time") == expected_time
    return None


def core_opportunity(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") in {"flip", "name_collision"}
        and task.get("bound_entity_present_after_refresh")
        and task.get("bound_entity_actionable_after_refresh")
        and initial_correct(row)
        and not is_api_failure(row)
    )


def core_drift(row: dict[str, Any]) -> bool:
    return bool(
        core_opportunity(row)
        and row.get("result", {}).get("predicted_target")
        == row["task"].get("post_refresh_target")
    )


def stable_error(row: dict[str, Any]) -> bool:
    return bool(
        row["task"].get("binding") == "anchored"
        and row["task"].get("update") == "stable"
        and not success(row)
    )


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    position = (len(values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def cluster_interval(
    rows: list[Any], statistic: Callable[[list[Any]], float], seed: int, samples: int
) -> list[float]:
    clusters: dict[str, list[Any]] = defaultdict(list)
    for item in rows:
        row = item[0] if isinstance(item, tuple) else item
        clusters[row["task"]["state_cluster_id"]].append(item)
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sample = [item for _ in names for item in clusters[rng.choice(names)]]
        values.append(statistic(sample))
    return [percentile(values, 0.025), percentile(values, 0.975)]


def summarize_run(path: Path, seed: int, samples: int) -> dict[str, Any]:
    rows = load(path)
    core = [row for row in rows if core_opportunity(row)]
    stable = [
        row
        for row in rows
        if row["task"].get("binding") == "anchored" and row["task"].get("update") == "stable"
    ]
    first = rows[0]
    mode_values = [value for row in rows if (value := mode_correct(row)) is not None]
    slices = []
    for binding in ("anchored", "dynamic"):
        group = [row for row in rows if row["task"]["binding"] == binding]
        slices.append({"binding": binding, "n": len(group), "correct": sum(success(row) for row in group)})
    return {
        "file": str(path),
        "model": short_model(first.get("model", "")),
        "controller": first.get("result", {}).get("mode", "unknown"),
        "n": len(rows),
        "unique_state_clusters": len({row["task"]["state_cluster_id"] for row in rows}),
        "correct": sum(success(row) for row in rows),
        "accuracy_ci95_state_cluster": cluster_interval(
            rows, lambda sample: sum(success(row) for row in sample) / len(sample), seed, samples
        ),
        "api_errors": sum(is_api_failure(row) for row in rows),
        "parse_or_internal_errors": sum(
            bool(row.get("result", {}).get("errors")) and not is_api_failure(row) for row in rows
        ),
        "anchored_initial_correct": sum(
            row["task"]["binding"] == "anchored" and initial_correct(row) for row in rows
        ),
        "anchored_n": sum(row["task"]["binding"] == "anchored" for row in rows),
        "mode_correct": sum(mode_values),
        "mode_n": len(mode_values),
        "core_opportunities": len(core),
        "core_drifts": sum(core_drift(row) for row in core),
        "core_drift_ci95_state_cluster": cluster_interval(
            core,
            lambda sample: sum(core_drift(row) for row in sample) / len(sample),
            seed,
            samples,
        ),
        "stable_n": len(stable),
        "stable_errors": sum(stable_error(row) for row in stable),
        "binding_slices": slices,
    }


def summarize_pair(a: Path, b: Path, seed: int, samples: int) -> dict[str, Any]:
    rows_a = {row["task"]["id"]: row for row in load(a)}
    rows_b = {row["task"]["id"]: row for row in load(b)}
    pairs = [(rows_a[key], rows_b[key]) for key in sorted(set(rows_a) & set(rows_b))]

    def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
        return sum(int(success(right)) - int(success(left)) for left, right in sample) / len(sample)

    return {
        "a": str(a),
        "b": str(b),
        "mode_a": pairs[0][0]["result"].get("mode"),
        "mode_b": pairs[0][1]["result"].get("mode"),
        "model": short_model(pairs[0][0].get("model", "")),
        "n": len(pairs),
        "delta_b_minus_a": delta(pairs),
        "ci95_state_cluster": cluster_interval(pairs, delta, seed, samples),
    }


def build_report(
    inputs: list[Path], pairs: list[tuple[Path, Path]], seed: int = 20260720, samples: int = 10_000
) -> dict[str, Any]:
    return {
        "seed": seed,
        "bootstrap_samples": samples,
        "runs": [summarize_run(path, seed, samples) for path in inputs],
        "pairs": [summarize_pair(a, b, seed, samples) for a, b in pairs],
    }


def pct(count: int, total: int) -> str:
    return "NA" if not total else f"{100 * count / total:.1f}%"


def markdown(report: dict[str, Any]) -> str:
    cluster_counts = sorted({row["unique_state_clusters"] for row in report["runs"]})
    cluster_text = ", ".join(str(count) for count in cluster_counts)
    lines = [
        "# TRI-v7 Core Replication Report",
        "",
        f"Intervals resample each run's observed state-instance clusters ({cluster_text} in this report).",
        "",
        "| Model | Controller | n | Accuracy | Correct initial anchored | Core drift | Stable errors | API / parse errors |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        drift_lo, drift_hi = row["core_drift_ci95_state_cluster"]
        drift = (
            f"{row['core_drifts']}/{row['core_opportunities']} "
            f"[{100 * drift_lo:.1f}, {100 * drift_hi:.1f}]"
        )
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | "
            f"{pct(row['correct'], row['n'])} | "
            f"{row['anchored_initial_correct']}/{row['anchored_n']} | "
            f"{drift} | "
            f"{row['stable_errors']}/{row['stable_n']} | "
            f"{row['api_errors']} / {row['parse_or_internal_errors']} |"
        )
    if report["pairs"]:
        lines.extend([
            "",
            "| Model | A | B | n | Delta B-A | State-cluster 95% CI |",
            "|---|---|---|---:|---:|---:|",
        ])
        for row in report["pairs"]:
            lo, hi = row["ci95_state_cluster"]
            lines.append(
                f"| {row['model']} | {row['mode_a']} | {row['mode_b']} | {row['n']} | "
                f"{100 * row['delta_b_minus_a']:.1f} | [{100 * lo:.1f}, {100 * hi:.1f}] |"
            )
    lines.extend([
        "",
        "| Model | Controller | Reference mode | Anchored | Dynamic |",
        "|---|---|---:|---:|---:|",
    ])
    for row in report["runs"]:
        slices = {item["binding"]: item for item in row["binding_slices"]}
        mode = "NA" if not row["mode_n"] else pct(row["mode_correct"], row["mode_n"])
        anchored = slices["anchored"]
        dynamic = slices["dynamic"]
        lines.append(
            f"| {row['model']} | {row['controller']} | {mode} | "
            f"{pct(anchored['correct'], anchored['n'])} | "
            f"{pct(dynamic['correct'], dynamic['n'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--pair", nargs=2, action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, default=Path("reports/v7_core_replication.json"))
    parser.add_argument("--seed", type=int, default=20260720)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args()
    report = build_report(args.input, [tuple(pair) for pair in args.pair], args.seed, args.bootstrap_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
