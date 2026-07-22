from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable


def load_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def _rate(rows: list[dict[str, Any]], event: Callable[[dict[str, Any]], bool]) -> float | None:
    return sum(event(row) for row in rows) / len(rows) if rows else None


def cluster_bootstrap(
    rows: list[dict[str, Any]],
    event: Callable[[dict[str, Any]], bool],
    repetitions: int = 10_000,
    seed: int = 20260719,
) -> list[float] | None:
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        cluster = str(row.get("cluster_id", ""))
        if not cluster:
            return None
        by_cluster[cluster].append(row)
    clusters = sorted(by_cluster)
    if len(clusters) < 2:
        return None
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(repetitions):
        sampled = [rng.choice(clusters) for _ in clusters]
        replicate = [row for cluster in sampled for row in by_cluster[cluster]]
        value = _rate(replicate, event)
        if value is not None:
            samples.append(value)
    samples.sort()
    return samples


def percentile_interval(samples: list[float] | None) -> list[float] | None:
    if not samples:
        return None
    low = samples[int(0.025 * (len(samples) - 1))]
    high = samples[int(0.975 * (len(samples) - 1))]
    return [low, high]


def summarize(group: list[dict[str, Any]]) -> dict[str, Any]:
    opportunities = [row for row in group if row.get("tri_opportunity", False)]
    mechanism = lambda row: bool(
        row.get("unauthorized_rebinding", False) or row.get("premature_lock", False)
    )
    mechanism_samples = cluster_bootstrap(opportunities, mechanism)
    return {
        "n": len(group),
        "api_or_protocol_errors": sum(bool(row.get("errors")) for row in group),
        "binding_observed": sum(bool(row.get("binding_observed")) for row in group),
        "initial_binding_correct": sum(
            bool(row.get("initial_binding_correct")) for row in group
        ),
        "tri_opportunities": len(opportunities),
        "final_state_success": sum(bool(row.get("final_state_success")) for row in group),
        "wrong_entity_writes": sum(bool(row.get("wrong_entity_write")) for row in group),
        "unauthorized_rebindings": sum(
            bool(row.get("unauthorized_rebinding")) for row in group
        ),
        "premature_locks": sum(bool(row.get("premature_lock")) for row in group),
        "conditional_mechanism_error_rate": _rate(opportunities, mechanism),
        "cluster_bootstrap_95_ci": percentile_interval(mechanism_samples),
        "selector_clusters": sorted(
            {str(row.get("cluster_id")) for row in group if row.get("cluster_id")}
        ),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [(row["model"], row["controller"], row["scenario_id"]) for row in rows]
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[
            (
                str(row["model"]),
                str(row["controller"]),
                str(row["reference_mode"]),
                str(row["transition"]),
            )
        ].append(row)
    cells = [
        {
            "model": key[0],
            "controller": key[1],
            "reference_mode": key[2],
            "transition": key[3],
            **summarize(group),
        }
        for key, group in sorted(groups.items())
    ]
    return {
        "inventory": {
            "rows": len(rows),
            "duplicate_model_controller_task_keys": len(keys) - len(set(keys)),
            "models": sorted({str(row["model"]) for row in rows}),
            "controllers": sorted({str(row["controller"]) for row in rows}),
            "tasks": len({str(row["scenario_id"]) for row in rows}),
        },
        "cells": cells,
    }


def markdown(report: dict[str, Any]) -> str:
    inv = report["inventory"]
    lines = [
        "# ToolSandbox Single-Turn 2x2 Results",
        "",
        f"Rows: {inv['rows']}; tasks: {inv['tasks']}; duplicate keys: "
        f"{inv['duplicate_model_controller_task_keys']}.",
        "",
        "| Model | Controller | Mode | Transition | N | API/protocol errors | Correct binding | Opportunities | Mechanism errors | Conditional rate (95% cluster CI) | Wrong writes |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["cells"]:
        errors = row["unauthorized_rebindings"] + row["premature_locks"]
        rate = row["conditional_mechanism_error_rate"]
        interval = row["cluster_bootstrap_95_ci"]
        if rate is None:
            rate_text = "NA"
        elif interval is None:
            rate_text = f"{100 * rate:.1f}% (CI unavailable)"
        else:
            rate_text = f"{100 * rate:.1f}% [{100 * interval[0]:.1f}, {100 * interval[1]:.1f}]"
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['reference_mode']} | "
            f"{row['transition']} | {row['n']} | {row['api_or_protocol_errors']} | "
            f"{row['initial_binding_correct']} | {row['tri_opportunities']} | {errors} | "
            f"{rate_text} | {row['wrong_entity_writes']} |"
        )
    lines.extend(
        [
            "",
            "Mechanism errors are unauthorized rebinding in Preserve/Flip and premature locking "
            "in Reevaluate/Flip. The denominator includes only trajectories with an observed, "
            "correctly timed, correct binding and a completed refresh. Stable cells are negative "
            "controls. API and protocol errors are not counted as TRI evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    report = build_report(load_rows(args.inputs))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
