from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .v3_sqlite_replay import SQLiteWriteEnvironment
from .v5_stress_report import cluster_delta_ci, exact_mcnemar


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def replay_cta(row: dict[str, Any]) -> dict[str, Any]:
    task = row["task"]
    target = row["result"].get("predicted_target")
    env = SQLiteWriteEnvironment(task)
    try:
        env.query()
        env.refresh()
        action = env.act(target)
        acted = env.acted_ids()
    finally:
        env.close()
    gold = task["correct_target"]
    return {
        "success": target == gold,
        "action_status": action["status"],
        "acted_ids": acted,
        "final_state_success": (gold == INVALID and not acted) or (gold != INVALID and acted == [gold]),
    }


def normalized(rows: list[dict[str, Any]], replay: bool) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        task = row["task"]
        result = replay_cta(row) if replay else row["result"]
        output[task["id"]] = {"task": task, "result": result, "raw": row}
    return output


def controller_summary(rows: dict[str, dict[str, Any]], label: str) -> dict[str, Any]:
    values = list(rows.values())
    statuses = Counter(row["result"]["action_status"] for row in values)
    slices: dict[str, dict[str, list[int]]] = {}
    for field in ("binding", "style", "update", "domain"):
        counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in values:
            key = str(row["task"][field])
            counts[key][0] += int(bool(row["result"]["success"]))
            counts[key][1] += 1
        slices[field] = dict(sorted(counts.items()))
    return {
        "label": label,
        "n": len(values),
        "success": sum(bool(row["result"]["success"]) for row in values),
        "final_state_success": sum(bool(row["result"]["final_state_success"]) for row in values),
        "action_status": dict(sorted(statuses.items())),
        "api_errors": sum(row["raw"].get("status") != "ok" for row in values),
        "internal_errors": sum(bool(row["raw"]["result"].get("errors")) for row in values),
        "error_rows": sum(
            row["raw"].get("status") != "ok" or bool(row["raw"]["result"].get("errors"))
            for row in values
        ),
        "requests": sum(int(row["raw"].get("api_request_attempts", 0)) for row in values),
        "retries": sum(int(row["raw"].get("api_retries", 0)) for row in values),
        "slices": slices,
    }


def report(baseline_rows: list[dict[str, Any]], role_rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = normalized(baseline_rows, replay=True)
    role = normalized(role_rows, replay=False)
    if set(baseline) != set(role):
        raise ValueError("Controller runs do not contain identical task IDs")
    ids = sorted(baseline)
    baseline_only = sum(baseline[i]["result"]["success"] and not role[i]["result"]["success"] for i in ids)
    role_only = sum(role[i]["result"]["success"] and not baseline[i]["result"]["success"] for i in ids)
    ci = cluster_delta_ci(baseline, role)
    return {
        "controllers": [
            controller_summary(baseline, "Historical Compile-then-act"),
            controller_summary(role, "Role-indexed lifecycle"),
        ],
        "paired": {
            "delta_percentage_points": 100.0 * (role_only - baseline_only) / len(ids),
            "cluster_ci95": list(ci),
            "baseline_only": baseline_only,
            "role_only": role_only,
            "mcnemar_exact_p": exact_mcnemar(baseline_only, role_only),
        },
    }


def ratio(pair: list[int]) -> str:
    return f"{pair[0]}/{pair[1]}"


def markdown(value: dict[str, Any]) -> str:
    lines = [
        "# TRI-v6 Role-Indexed Held-Out Validation",
        "",
        "Post-hoc held-out validation on 40 compositional tasks from four unseen schemas.",
        "Historical Compile-then-act predictions are replayed through the same SQLite mutation evaluator.",
        "",
        "| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in value["controllers"]:
        status = row["action_status"]
        lines.append(
            f"| {row['label']} | {row['success']}/{row['n']} | {row['final_state_success']}/{row['n']} | "
            f"{status.get('wrong_entity_write', 0)} | {status.get('invalid_target_attempt', 0)} | "
            f"{status.get('unnecessary_rejection', 0)} | {row['requests']} | "
            f"{row['error_rows']} |"
        )
    paired = value["paired"]
    lines.extend([
        "",
        f"Role-indexed minus historical CTA: {paired['delta_percentage_points']:+.1f} points, "
        f"template-cluster 95% CI [{paired['cluster_ci95'][0]:+.1f}, {paired['cluster_ci95'][1]:+.1f}].",
        f"Discordant pairs: {paired['role_only']} role-only and {paired['baseline_only']} CTA-only; "
        f"exact McNemar p={paired['mcnemar_exact_p']:.6g}.",
        "",
        "| Controller | Anchored | Dynamic | Explicit | Implicit |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in value["controllers"]:
        binding = row["slices"]["binding"]
        explicit = [0, 0]
        implicit = [0, 0]
        for style, pair in row["slices"]["style"].items():
            target = explicit if style.startswith("explicit") else implicit
            target[0] += pair[0]
            target[1] += pair[1]
        lines.append(
            f"| {row['label']} | {ratio(binding['anchored'])} | {ratio(binding['dynamic'])} | "
            f"{ratio(explicit)} | {ratio(implicit)} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="runs/v6_qwen_exact_cta_full.jsonl")
    parser.add_argument("--role", default="runs/v6_qwen_role_indexed_full.jsonl")
    parser.add_argument("--output-json", default="reports/v6_qwen_role_heldout_report.json")
    parser.add_argument("--output-md", default="reports/v6_qwen_role_heldout_report.md")
    args = parser.parse_args()
    value = report(load(Path(args.baseline)), load(Path(args.role)))
    Path(args.output_json).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(markdown(value), encoding="utf-8")
    print(args.output_json)
    print(args.output_md)


if __name__ == "__main__":
    main()
