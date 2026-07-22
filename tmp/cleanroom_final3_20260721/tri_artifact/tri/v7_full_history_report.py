from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .v2_model_report import is_api_failure, short_model
from .v7_core_report import cluster_interval, load, success


def changed_winner(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task["pre_refresh_target"] != task["post_refresh_target"]
        and task["update"] in {"flip", "name_collision"}
    )


def anchored_substitution(row: dict[str, Any]) -> bool:
    return bool(
        row["task"]["binding"] == "anchored"
        and changed_winner(row)
        and row.get("result", {}).get("predicted_target")
        == row["task"]["post_refresh_target"]
    )


def dynamic_old_target(row: dict[str, Any]) -> bool:
    return bool(
        row["task"]["binding"] == "dynamic"
        and changed_winner(row)
        and row.get("result", {}).get("predicted_target")
        == row["task"]["pre_refresh_target"]
    )


def summarize_run(path: Path, seed: int, samples: int) -> dict[str, Any]:
    rows = load(path)
    first = rows[0]
    anchored_changed = [
        row for row in rows if row["task"]["binding"] == "anchored" and changed_winner(row)
    ]
    dynamic_changed = [
        row for row in rows if row["task"]["binding"] == "dynamic" and changed_winner(row)
    ]
    stable = [
        row for row in rows
        if row["task"]["binding"] == "anchored" and row["task"]["update"] == "stable"
    ]
    slices = {}
    for binding in ("anchored", "dynamic"):
        group = [row for row in rows if row["task"]["binding"] == binding]
        slices[binding] = {"n": len(group), "correct": sum(success(row) for row in group)}
    usage = [
        item
        for row in rows
        for item in row.get("api_usage", [])
        if isinstance(item, dict)
    ]
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
        "anchored_changed_n": len(anchored_changed),
        "anchored_substitutions": sum(anchored_substitution(row) for row in anchored_changed),
        "dynamic_changed_n": len(dynamic_changed),
        "dynamic_old_targets": sum(dynamic_old_target(row) for row in dynamic_changed),
        "stable_n": len(stable),
        "stable_errors": sum(not success(row) for row in stable),
        "binding_slices": slices,
        "api_errors": sum(is_api_failure(row) for row in rows),
        "parse_or_internal_errors": sum(
            bool(row.get("result", {}).get("errors")) and not is_api_failure(row) for row in rows
        ),
        "api_request_attempts": sum(int(row.get("api_request_attempts", 0)) for row in rows),
        "api_retries": sum(int(row.get("api_retries", 0)) for row in rows),
        "prompt_tokens": sum(int(item.get("prompt_tokens", 0)) for item in usage),
        "completion_tokens": sum(int(item.get("completion_tokens", 0)) for item in usage),
        "total_tokens": sum(int(item.get("total_tokens", 0)) for item in usage),
        "latency_seconds": sum(float(row.get("latency_s", 0.0)) for row in rows),
    }


def summarize_pair(a: Path, b: Path, seed: int, samples: int) -> dict[str, Any]:
    left = {row["task"]["id"]: row for row in load(a)}
    right = {row["task"]["id"]: row for row in load(b)}
    pairs = [(left[key], right[key]) for key in sorted(set(left) & set(right))]

    def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
        return sum(int(success(y)) - int(success(x)) for x, y in sample) / len(sample)

    return {
        "a": str(a),
        "b": str(b),
        "model": short_model(pairs[0][0].get("model", "")),
        "controller_a": pairs[0][0]["result"].get("mode"),
        "controller_b": pairs[0][1]["result"].get("mode"),
        "n": len(pairs),
        "only_a": sorted(set(left) - set(right)),
        "only_b": sorted(set(right) - set(left)),
        "a_wrong_b_right": sum(not success(x) and success(y) for x, y in pairs),
        "a_right_b_wrong": sum(success(x) and not success(y) for x, y in pairs),
        "delta_b_minus_a": delta(pairs),
        "ci95_state_cluster": cluster_interval(pairs, delta, seed, samples),
    }


def build_report(
    inputs: list[Path], pairs: list[tuple[Path, Path]], seed: int = 20260721,
    samples: int = 10_000,
) -> dict[str, Any]:
    return {
        "seed": seed,
        "bootstrap_samples": samples,
        "runs": [summarize_run(path, seed, samples) for path in inputs],
        "pairs": [summarize_pair(a, b, seed, samples) for a, b in pairs],
    }


def pct(value: int, total: int) -> str:
    return "NA" if not total else f"{100 * value / total:.1f}%"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# V7 Matched Full-History Baseline Report",
        "",
        "Full-history runs do not expose a separately scored pre-refresh binding. Anchored",
        "substitution is therefore unconditional and must not be called conditional TRI.",
        "",
        "| Model | Controller | n | Accuracy | Anchored | Dynamic | Anchored changed substitution | Dynamic old target | Stable errors | API / parse | Requests / retries | Tokens | Latency s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | "
            f"{pct(row['correct'], row['n'])} | "
            f"{pct(row['binding_slices']['anchored']['correct'], row['binding_slices']['anchored']['n'])} | "
            f"{pct(row['binding_slices']['dynamic']['correct'], row['binding_slices']['dynamic']['n'])} | "
            f"{row['anchored_substitutions']}/{row['anchored_changed_n']} | "
            f"{row['dynamic_old_targets']}/{row['dynamic_changed_n']} | "
            f"{row['stable_errors']}/{row['stable_n']} | "
            f"{row['api_errors']} / {row['parse_or_internal_errors']} | "
            f"{row['api_request_attempts']} / {row['api_retries']} | {row['total_tokens']} | "
            f"{row['latency_seconds']:.1f} |"
        )
    if report["pairs"]:
        lines.extend([
            "",
            "| Model | A | B | n | A wrong / B right | A right / B wrong | Delta B-A | State-cluster 95% CI | Missing A/B |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for row in report["pairs"]:
            lo, hi = row["ci95_state_cluster"]
            lines.append(
                f"| {row['model']} | {row['controller_a']} | {row['controller_b']} | "
                f"{row['n']} | {row['a_wrong_b_right']} | {row['a_right_b_wrong']} | "
                f"{100 * row['delta_b_minus_a']:.1f} | "
                f"[{100 * lo:.1f}, {100 * hi:.1f}] | "
                f"{len(row['only_a'])}/{len(row['only_b'])} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--pair", nargs=2, action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    args = parser.parse_args()
    report = build_report(
        args.input, [tuple(pair) for pair in args.pair], args.seed, args.bootstrap_samples
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
