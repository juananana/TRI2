from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .v2_ablation import wilson
from .v2_model_report import short_model


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def exact_mcnemar(a_only: int, b_only: int) -> float:
    n = a_only + b_only
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(a_only, b_only) + 1))
    return min(1.0, 2.0 * tail / (2**n))


def cluster_delta_ci(
    a: dict[str, dict[str, Any]],
    b: dict[str, dict[str, Any]],
    samples: int = 10_000,
    seed: int = 20260717,
) -> tuple[float, float]:
    clusters: dict[str, list[str]] = defaultdict(list)
    for task_id, row in a.items():
        clusters[row["task"]["template_id"]].append(task_id)
    names = sorted(clusters)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(samples):
        ids = [task_id for _ in names for task_id in clusters[rng.choice(names)]]
        score_a = sum(bool(a[i]["result"]["success"]) for i in ids)
        score_b = sum(bool(b[i]["result"]["success"]) for i in ids)
        deltas.append(100.0 * (score_b - score_a) / len(ids))
    deltas.sort()
    return deltas[int(0.025 * samples)], deltas[int(0.975 * samples)]


def summarize_controller(rows: list[dict[str, Any]]) -> dict[str, Any]:
    results = [row["result"] for row in rows]
    n = len(rows)
    success = sum(bool(result["success"]) for result in results)
    lo, hi = wilson(success, n)
    slices: dict[str, dict[str, dict[str, int]]] = {}
    for field in ("binding", "style", "update", "domain"):
        counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in rows:
            value = str(row["task"][field])
            counts[value][0] += int(bool(row["result"]["success"]))
            counts[value][1] += 1
        slices[field] = {
            value: {"success": count[0], "n": count[1]}
            for value, count in sorted(counts.items())
        }

    lifecycle = [row for row in rows if row["result"]["mode"].endswith("lifecycle")]
    anchored = [row for row in lifecycle if row["task"]["binding"] == "anchored"]
    mode_correct = sum(
        (row["result"].get("compiled_ledger") or {}).get("reference_mode")
        == ("preserve" if row["task"]["binding"] == "anchored" else "reevaluate")
        for row in lifecycle
    ) if lifecycle else None
    bound_id_correct = sum(
        (row["result"].get("compiled_ledger") or {}).get("bound_target_id")
        == row["task"]["pre_refresh_target"]
        for row in anchored
    ) if anchored else None
    statuses = Counter(result["action_status"] for result in results)
    return {
        "model": short_model(str(rows[0]["model"])),
        "mode": results[0]["mode"],
        "n": n,
        "success": success,
        "accuracy": success / n,
        "ci95": [lo, hi],
        "action_status": dict(sorted(statuses.items())),
        "collateral_modifications": sum(int(r["collateral_modifications"]) for r in results),
        "api_errors": sum(
            row.get("status") != "ok"
            or any(str(error).startswith("api_call_error:") for error in row["result"].get("errors", []))
            for row in rows
        ),
        "internal_errors": sum(bool(result.get("errors")) for result in results),
        "api_requests": sum(int(row.get("api_request_attempts", 0)) for row in rows),
        "api_retries": sum(int(row.get("api_retries", 0)) for row in rows),
        "mode_correct": mode_correct,
        "mode_n": len(lifecycle) or None,
        "bound_id_correct": bound_id_correct,
        "bound_id_n": len(anchored) or None,
        "slices": slices,
    }


def summarize(generic: list[dict[str, Any]], lifecycle: list[dict[str, Any]]) -> dict[str, Any]:
    a = {row["task"]["id"]: row for row in generic}
    b = {row["task"]["id"]: row for row in lifecycle}
    if set(a) != set(b):
        raise ValueError("Generic and lifecycle runs do not contain the same task IDs")
    ids = sorted(a)
    a_only = sum(a[i]["result"]["success"] and not b[i]["result"]["success"] for i in ids)
    b_only = sum(b[i]["result"]["success"] and not a[i]["result"]["success"] for i in ids)
    score_a = sum(bool(a[i]["result"]["success"]) for i in ids)
    score_b = sum(bool(b[i]["result"]["success"]) for i in ids)
    ci = cluster_delta_ci(a, b)
    return {
        "controllers": [summarize_controller(generic), summarize_controller(lifecycle)],
        "paired": {
            "delta_percentage_points": 100.0 * (score_b - score_a) / len(ids),
            "cluster_ci95": list(ci),
            "generic_only": a_only,
            "lifecycle_only": b_only,
            "mcnemar_exact_p": exact_mcnemar(a_only, b_only),
        },
    }


def pct(count: int, n: int) -> str:
    return f"{100.0 * count / n:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v5 Multi-Refresh, Multi-Referent SQLite Stress",
        "",
        "Frozen secondary stress test: two refreshes, a monitoring-only referent, an unrelated",
        "tool call, and a real SQLite mutation. It is not pooled with the primary experiment.",
        "",
        "| Controller | n | Accuracy | 95% CI | Anchored | Dynamic | Wrong writes | Unneeded reject | Requests | API err. | Parse/internal err. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["controllers"]:
        anchored = row["slices"]["binding"]["anchored"]
        dynamic = row["slices"]["binding"]["dynamic"]
        status = row["action_status"]
        lines.append(
            f"| {row['mode']} | {row['n']} | {pct(row['success'], row['n'])} | "
            f"[{100*row['ci95'][0]:.1f}, {100*row['ci95'][1]:.1f}] | "
            f"{pct(anchored['success'], anchored['n'])} | {pct(dynamic['success'], dynamic['n'])} | "
            f"{status.get('wrong_entity_write', 0)} | {status.get('unnecessary_rejection', 0)} | "
            f"{row['api_requests']} | {row['api_errors']} | {row['internal_errors']} |"
        )
    paired = report["paired"]
    lifecycle = report["controllers"][1]
    lines.extend([
        "",
        f"Lifecycle minus generic: {paired['delta_percentage_points']:+.1f} points, "
        f"template-cluster 95% CI [{paired['cluster_ci95'][0]:+.1f}, {paired['cluster_ci95'][1]:+.1f}].",
        f"Discordant pairs: {paired['generic_only']} generic-only and "
        f"{paired['lifecycle_only']} lifecycle-only; exact McNemar p={paired['mcnemar_exact_p']:.6g}.",
        "",
        f"Lifecycle mode accuracy: {lifecycle['mode_correct']}/{lifecycle['mode_n']}; anchored "
        f"bound-ID accuracy: {lifecycle['bound_id_correct']}/{lifecycle['bound_id_n']}.",
        "",
        "| Controller | Update slice | Success |",
        "|---|---|---:|",
    ])
    for row in report["controllers"]:
        for value, count in row["slices"]["update"].items():
            lines.append(f"| {row['mode']} | {value} | {count['success']}/{count['n']} |")
    lines.extend([
        "",
        "The scalar lifecycle record was designed for one action referent. Failure to separate the",
        "monitoring referent from the action referent is a compositional reference-scope boundary,",
        "not evidence that post-binding temporal authorization is unnecessary.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generic", required=True)
    parser.add_argument("--lifecycle", required=True)
    parser.add_argument("--output", default="reports/v5_qwen_multirefresh_report.json")
    args = parser.parse_args()
    report = summarize(load(Path(args.generic)), load(Path(args.lifecycle)))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
