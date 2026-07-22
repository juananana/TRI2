from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from .v2_model_report import short_model


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXACT = (
    ROOT / "runs/v3_exact_predecessor_qwen_full.jsonl",
    ROOT / "runs/v3_exact_predecessor_glm_full.jsonl",
)
DEFAULT_UNTYPED = (
    ROOT / "runs/v3_prefrefresh_untyped_qwen_full.jsonl",
    ROOT / "runs/v3_prefrefresh_untyped_glm_full.jsonl",
)
DEFAULT_LIFECYCLE_FREE = (
    ROOT / "runs/v3_factorial_qwen_primary_lifecycle_free.jsonl",
    ROOT / "runs/v3_factorial_glm_primary_lifecycle_free.jsonl",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    task_ids = [row.get("task", {}).get("id") for row in rows]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError(f"duplicate task IDs in {path}")
    return rows


def cluster_id(row: dict[str, Any]) -> str:
    task = row.get("task", {})
    return str(task.get("template_id") or task.get("paraphrase") or "unknown")


def norm_binding_time(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    aliases = {
        "pre-refresh": "pre_refresh",
        "before_refresh": "pre_refresh",
        "before refresh": "pre_refresh",
        "post-refresh": "post_refresh",
        "after_refresh": "post_refresh",
        "after refresh": "post_refresh",
    }
    return aliases.get(text, text)


def is_api_error(row: dict[str, Any]) -> bool:
    if row.get("status") != "ok":
        return True
    result = row.get("result")
    if not isinstance(result, dict):
        return False
    errors = [str(error) for error in result.get("errors", [])]
    return any(
        "http error" in error.lower()
        or "urlerror" in error.lower()
        or "timed out" in error.lower()
        or error.lower().startswith("api_call_error:")
        for error in errors
    )


def is_parse_error(row: dict[str, Any]) -> bool:
    if is_api_error(row):
        return False
    result = row.get("result")
    if not isinstance(result, dict):
        return True
    return bool(result.get("errors", []))


def is_final_correct(row: dict[str, Any]) -> bool:
    return (
        not is_api_error(row)
        and not is_parse_error(row)
        and bool(row.get("result", {}).get("success"))
    )


def compiler_fields(row: dict[str, Any]) -> dict[str, bool | None]:
    task = row.get("task", {})
    result = row.get("result", {})
    ledger = result.get("compiled_ledger") if isinstance(result, dict) else None
    ledger = ledger if isinstance(ledger, dict) else {}
    expected = "pre_refresh" if task.get("binding") == "anchored" else "post_refresh"
    usable_compilation = not is_api_error(row) and not is_parse_error(row)
    binding_correct = usable_compilation and norm_binding_time(ledger.get("binding_time")) == expected
    anchored = task.get("binding") == "anchored"
    bound_id_correct = (
        (
            usable_compilation
            and ledger.get("bound_target_id") == task.get("pre_refresh_target")
        ) if anchored else None
    )
    compiler_correct = binding_correct and (not anchored or bool(bound_id_correct))
    final_correct = is_final_correct(row)
    return {
        "binding_correct": binding_correct,
        "bound_id_correct": bound_id_correct,
        "compiler_correct": compiler_correct,
        "final_correct": final_correct,
        "actor_failure": compiler_correct and not final_correct,
        "compiler_induced_failure": not compiler_correct and not final_correct,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "n_tasks": len(rows),
        "itt_correct": 0,
        "api_errors": 0,
        "parse_errors": 0,
        "compiler_binding_correct": 0,
        "anchored_n": 0,
        "anchored_bound_id_correct": 0,
        "final_failures": 0,
        "actor_failures": 0,
        "compiler_induced_failures": 0,
    }
    for row in rows:
        task = row.get("task", {})
        fields = compiler_fields(row)
        counts["itt_correct"] += int(bool(fields["final_correct"]))
        counts["api_errors"] += int(is_api_error(row))
        counts["parse_errors"] += int(is_parse_error(row))
        counts["compiler_binding_correct"] += int(bool(fields["binding_correct"]))
        if task.get("binding") == "anchored":
            counts["anchored_n"] += 1
            counts["anchored_bound_id_correct"] += int(bool(fields["bound_id_correct"]))
        counts["final_failures"] += int(not bool(fields["final_correct"]))
        counts["actor_failures"] += int(bool(fields["actor_failure"]))
        counts["compiler_induced_failures"] += int(bool(fields["compiler_induced_failure"]))
    n_tasks = counts["n_tasks"]
    counts["itt_accuracy"] = counts["itt_correct"] / n_tasks if n_tasks else None
    counts["api_error_rate"] = counts["api_errors"] / n_tasks if n_tasks else None
    counts["parse_error_rate"] = counts["parse_errors"] / n_tasks if n_tasks else None
    counts["compiler_binding_time_accuracy"] = (
        counts["compiler_binding_correct"] / n_tasks if n_tasks else None
    )
    counts["anchored_bound_id_accuracy"] = (
        counts["anchored_bound_id_correct"] / counts["anchored_n"]
        if counts["anchored_n"]
        else None
    )
    return counts


def bootstrap_clusters(
    clusters: dict[str, list[Any]],
    statistic: Callable[[list[Any]], float],
    samples: int,
    seed: int,
) -> tuple[float, float]:
    if not clusters:
        return (float("nan"), float("nan"))
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sampled: list[Any] = []
        for _ in names:
            sampled.extend(clusters[rng.choice(names)])
        values.append(statistic(sampled))
    values.sort()
    return percentile(values, 0.025), percentile(values, 0.975)


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return float("nan")
    position = (len(values) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def slices(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("task", {}).get(field, "unknown"))].append(row)
    return [
        {field: value, **summarize_rows(group)}
        for value, group in sorted(groups.items())
    ]


def summarize_run(path: Path, samples: int, seed: int) -> dict[str, Any]:
    rows = load_jsonl(path)
    if not rows:
        raise ValueError(f"no rows in {path}")
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        clusters[cluster_id(row)].append(row)
    lo, hi = bootstrap_clusters(
        clusters,
        lambda sample: sum(is_final_correct(row) for row in sample) / len(sample),
        samples,
        seed,
    )
    first = rows[0]
    return {
        "file": str(path),
        "model": short_model(str(first.get("model", ""))),
        "mode": first.get("result", {}).get("mode"),
        "n_template_clusters": len(clusters),
        "template_cluster_bootstrap_ci95": [lo, hi],
        **summarize_rows(rows),
        "binding_slices": slices(rows, "binding"),
        "explicitness_slices": slices(rows, "phenomenon"),
        "update_slices": slices(rows, "update"),
        "template_slices": slices(rows, "template_id"),
    }


def summarize_pair(
    exact_path: Path,
    comparator_path: Path,
    comparator_name: str,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    exact_by_id = {row["task"]["id"]: row for row in load_jsonl(exact_path)}
    comparator_by_id = {row["task"]["id"]: row for row in load_jsonl(comparator_path)}
    shared_ids = sorted(set(exact_by_id) & set(comparator_by_id))
    if not shared_ids:
        raise ValueError(f"no paired tasks for {exact_path} and {comparator_path}")
    clusters: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for task_id in shared_ids:
        exact = exact_by_id[task_id]
        clusters[cluster_id(exact)].append((exact, comparator_by_id[task_id]))

    def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
        return sum(is_final_correct(exact) - is_final_correct(other) for exact, other in sample) / len(sample)

    pairs = [pair for group in clusters.values() for pair in group]
    lo, hi = bootstrap_clusters(clusters, delta, samples, seed)
    exact_correct = sum(is_final_correct(exact) for exact, _ in pairs)
    comparator_correct = sum(is_final_correct(other) for _, other in pairs)
    return {
        "comparison": comparator_name,
        "exact_file": str(exact_path),
        "comparator_file": str(comparator_path),
        "exact_mode": pairs[0][0].get("result", {}).get("mode"),
        "comparator_mode": pairs[0][1].get("result", {}).get("mode"),
        "n_paired": len(pairs),
        "n_template_clusters": len(clusters),
        "unpaired_exact": len(exact_by_id) - len(shared_ids),
        "unpaired_comparator": len(comparator_by_id) - len(shared_ids),
        "exact_accuracy": exact_correct / len(pairs),
        "comparator_accuracy": comparator_correct / len(pairs),
        "delta_exact_minus_comparator": delta(pairs),
        "template_cluster_bootstrap_ci95": [lo, hi],
    }


def complete(run: dict[str, Any], expected_tasks: int, expected_clusters: int) -> bool:
    return (
        run["n_tasks"] == expected_tasks
        and run["n_template_clusters"] == expected_clusters
    )


def build_report(
    exact_paths: tuple[Path, Path],
    untyped_paths: tuple[Path, Path],
    lifecycle_free_paths: tuple[Path, Path],
    samples: int = 10000,
    seed: int = 20260717,
) -> dict[str, Any]:
    runs = [summarize_run(path, samples, seed) for path in exact_paths]
    pairs: list[dict[str, Any]] = []
    for exact, untyped, lifecycle_free in zip(exact_paths, untyped_paths, lifecycle_free_paths):
        pairs.append(summarize_pair(exact, untyped, "untyped_pre_refresh", samples, seed))
        pairs.append(summarize_pair(exact, lifecycle_free, "lifecycle_free", samples, seed))
    return {
        "bootstrap_samples": samples,
        "seed": seed,
        "runs": runs,
        "paired_comparisons": pairs,
    }


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v3 Exact Historical Compile-Then-Act Audit",
        "",
        "All accuracy metrics are intention-to-treat: API and parse failures count as incorrect.",
        f"Template-cluster bootstrap: {report['bootstrap_samples']} resamples; seed {report['seed']}.",
        "",
        "## Overall",
        "",
        "| Model | Controller | n | ITT Acc. | Cluster 95% CI | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Final failures | Actor failures | Compiler-induced failures |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["runs"]:
        lo, hi = row["template_cluster_bootstrap_ci95"]
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['n_tasks']} | {pct(row['itt_accuracy'])} | "
            f"[{pct(lo)}, {pct(hi)}] | {row['api_errors']} | {row['parse_errors']} | "
            f"{pct(row['compiler_binding_time_accuracy'])} | {pct(row['anchored_bound_id_accuracy'])} | "
            f"{row['final_failures']} | {row['actor_failures']} | {row['compiler_induced_failures']} |"
        )
    for title, key, label in (
        ("Binding Slices", "binding_slices", "Binding"),
        ("Explicitness Slices", "explicitness_slices", "Explicitness"),
        ("Update Slices", "update_slices", "Update"),
        ("Template-Cluster Slices", "template_slices", "Template"),
    ):
        lines.extend([
            "",
            f"## {title}",
            "",
            f"| Model | {label} | n | ITT Acc. | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Actor failures | Final failures |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        field = {"binding_slices": "binding", "explicitness_slices": "phenomenon", "update_slices": "update", "template_slices": "template_id"}[key]
        for run in report["runs"]:
            for row in run[key]:
                lines.append(
                    f"| {run['model']} | {row[field]} | {row['n_tasks']} | {pct(row['itt_accuracy'])} | "
                    f"{row['api_errors']} | {row['parse_errors']} | {pct(row['compiler_binding_time_accuracy'])} | "
                    f"{pct(row['anchored_bound_id_accuracy'])} | {row['actor_failures']} | {row['final_failures']} |"
                )
    lines.extend([
        "",
        "## Protocol-Frozen Audit Comparisons",
        "",
        "Delta is exact historical compile-then-act minus the named comparator.",
        "",
        "| Comparison | Exact controller | Comparator | Paired n | Templates | Exact Acc. | Comparator Acc. | Delta | Cluster 95% CI | Unpaired exact/comparator |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["paired_comparisons"]:
        lo, hi = row["template_cluster_bootstrap_ci95"]
        lines.append(
            f"| {row['comparison']} | {row['exact_mode']} | {row['comparator_mode']} | "
            f"{row['n_paired']} | {row['n_template_clusters']} | {pct(row['exact_accuracy'])} | "
            f"{pct(row['comparator_accuracy'])} | {pct(row['delta_exact_minus_comparator'])} | "
            f"[{pct(lo)}, {pct(hi)}] | {row['unpaired_exact']}/{row['unpaired_comparator']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exact", nargs=2, type=Path, default=DEFAULT_EXACT)
    parser.add_argument("--untyped", nargs=2, type=Path, default=DEFAULT_UNTYPED)
    parser.add_argument("--lifecycle-free", nargs=2, type=Path, default=DEFAULT_LIFECYCLE_FREE)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/v3_exact_predecessor_two_model.json")
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--expected-tasks", type=int, default=160)
    parser.add_argument("--expected-clusters", type=int, default=20)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    report = build_report(
        tuple(args.exact), tuple(args.untyped), tuple(args.lifecycle_free),
        args.bootstrap_samples, args.seed,
    )
    incomplete = [
        row["model"] for row in report["runs"]
        if not complete(row, args.expected_tasks, args.expected_clusters)
    ]
    if incomplete and not args.allow_incomplete:
        raise SystemExit(
            "refusing to write a two-model report before complete exact runs: "
            + ", ".join(incomplete)
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
