from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .v2_model_report import is_api_failure, short_model


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def row_stages(row: dict[str, Any]) -> dict[str, Any]:
    task = row["task"]
    result = row.get("result", {})
    ledger = result.get("compiled_ledger") or {}
    api_error = is_api_failure(row)
    lifecycle_mode = result.get("mode") == "guarded_lifecycle_then_act"
    guard_correct = lifecycle_mode and ledger.get("guard_type") == task["guard_type"]
    id_correct = lifecycle_mode and ledger.get("bound_target_id") == task["pre_refresh_target"]
    compiler_correct = guard_correct and id_correct and not api_error
    final_correct = bool(result.get("success")) and not api_error
    return {
        "api_error": api_error,
        "guard_correct": guard_correct,
        "id_correct": id_correct,
        "compiler_correct": compiler_correct,
        "final_correct": final_correct,
        "actor_only_failure": compiler_correct and not final_correct,
        "compiler_induced_failure": lifecycle_mode and not compiler_correct and not final_correct,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        result = row.get("result", {})
        groups[(
            short_model(str(row.get("model", "unknown"))),
            str(result.get("mode", "unknown")),
            str(row["task"]["guard_type"]),
            str(row["task"]["update"]),
        )].append(row)
    table = []
    failures = []
    for (model, mode, guard, update), group in sorted(groups.items()):
        stages = [row_stages(row) for row in group]
        lifecycle_mode = mode == "guarded_lifecycle_then_act"
        table.append({
            "model": model,
            "mode": mode,
            "guard_type": guard,
            "update": update,
            "n": len(group),
            "guard_accuracy": sum(stage["guard_correct"] for stage in stages) / len(group) if lifecycle_mode else None,
            "id_accuracy": sum(stage["id_correct"] for stage in stages) / len(group) if lifecycle_mode else None,
            "final_accuracy": sum(stage["final_correct"] for stage in stages) / len(group),
            "actor_only_failures": sum(stage["actor_only_failure"] for stage in stages),
            "compiler_induced_failures": sum(stage["compiler_induced_failure"] for stage in stages),
            "api_errors": sum(stage["api_error"] for stage in stages),
        })
        for row, stage in zip(group, stages):
            if not stage["final_correct"]:
                failures.append({
                    "task_id": row["task"]["id"],
                    "model": model,
                    "mode": mode,
                    "guard_type": guard,
                    "update": update,
                    "prediction": row.get("result", {}).get("predicted_target"),
                    "gold": row["task"]["correct_target"],
                    **stage,
                })
    return {"table": table, "failures": failures}


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v4 Guarded Policy Stage Report",
        "",
        "| Model | Controller | Guard | Update | n | Guard | Bound ID | Final | Actor-only | Compiler-induced | API err. |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["table"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['guard_type']} | {row['update']} | "
            f"{row['n']} | {pct(row['guard_accuracy'])} | {pct(row['id_accuracy'])} | "
            f"{pct(row['final_accuracy'])} | {row['actor_only_failures']} | "
            f"{row['compiler_induced_failures']} | {row['api_errors']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default="reports/v4_policy_report.json")
    args = ap.parse_args()
    report = summarize(load_rows([Path(path) for path in args.input]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
