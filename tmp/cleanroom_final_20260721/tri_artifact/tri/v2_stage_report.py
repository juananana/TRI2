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


def expected_mode(task: dict[str, Any], factorized: bool) -> str | None:
    if task.get("binding") == "anchored":
        return "preserve" if factorized else "pre_refresh"
    if task.get("binding") == "dynamic":
        return "reevaluate" if factorized else "post_refresh"
    return None


def row_stages(row: dict[str, Any]) -> dict[str, Any]:
    task = row.get("task", {})
    result = row.get("result", {})
    ledger = result.get("compiled_ledger") or {}
    factorized = "reference_mode" in ledger
    observed_mode = ledger.get("reference_mode" if factorized else "binding_time")
    expected = expected_mode(task, factorized)
    mode_correct = expected is not None and observed_mode == expected

    observed_id = ledger.get("bound_target_id")
    if task.get("binding") == "anchored":
        id_correct = observed_id == task.get("pre_refresh_target")
    elif task.get("binding") == "dynamic":
        id_correct = observed_id in (None, "", "null")
    else:
        id_correct = None

    policy_correct: bool | None = None
    if factorized and task.get("binding") == "anchored":
        policy_correct = ledger.get("invalidity_policy") == "reject"

    compiler_correct = bool(mode_correct and id_correct)
    if policy_correct is not None:
        compiler_correct = compiler_correct and policy_correct
    final_correct = bool(result.get("success")) and not is_api_failure(row)
    return {
        "factorized": factorized,
        "expected_mode": expected,
        "observed_mode": observed_mode,
        "mode_correct": mode_correct,
        "id_correct": id_correct,
        "policy_correct": policy_correct,
        "compiler_correct": compiler_correct,
        "final_correct": final_correct,
        "actor_only_failure": compiler_correct and not final_correct,
        "compiler_induced_failure": not compiler_correct and not final_correct,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    empty = lambda: defaultdict(int)
    groups: dict[tuple[str, ...], defaultdict[str, int]] = defaultdict(empty)
    details: list[dict[str, Any]] = []
    for row in rows:
        if "task" not in row or "result" not in row:
            continue
        task = row["task"]
        result = row["result"]
        ledger = result.get("compiled_ledger")
        if ledger is None:
            continue
        stages = row_stages(row)
        key = (
            short_model(row.get("model", "")),
            result.get("mode", "unknown"),
            task.get("split", "unknown"),
            task.get("phenomenon", "unknown"),
            task.get("binding", "unknown"),
        )
        stats = groups[key]
        stats["n"] += 1
        stats["api_errors"] += int(is_api_failure(row))
        for field in (
            "mode_correct",
            "id_correct",
            "policy_correct",
            "compiler_correct",
            "final_correct",
            "actor_only_failure",
            "compiler_induced_failure",
        ):
            value = stages[field]
            if value is not None:
                stats[f"{field}_eligible"] += 1
                stats[field] += int(value)
        if not stages["final_correct"]:
            details.append({
                "task_id": task.get("id"),
                "model": key[0],
                "mode": key[1],
                "split": key[2],
                "binding": key[4],
                "gold": task.get("correct_target"),
                "prediction": result.get("predicted_target"),
                **stages,
            })

    summary = []
    for key, counts in sorted(groups.items()):
        row = dict(zip(("model", "mode", "split", "phenomenon", "binding"), key))
        row.update(counts)
        for field in (
            "mode_correct",
            "id_correct",
            "policy_correct",
            "compiler_correct",
            "final_correct",
        ):
            eligible = counts.get(f"{field}_eligible", 0)
            row[f"{field}_rate"] = counts.get(field, 0) / eligible if eligible else None
        summary.append(row)
    return {"summary": summary, "failure_details": details}


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v2 Compiler Stage Report",
        "",
        "| Model | Mode | Split | Style | Binding | n | Mode | ID | Policy | Compiler | Final | Actor-only | Compiler-induced | API |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['split']} | {row['phenomenon']} | "
            f"{row['binding']} | {row['n']} | {pct(row['mode_correct_rate'])} | "
            f"{pct(row['id_correct_rate'])} | {pct(row['policy_correct_rate'])} | "
            f"{pct(row['compiler_correct_rate'])} | {pct(row['final_correct_rate'])} | "
            f"{row.get('actor_only_failure', 0)} | {row.get('compiler_induced_failure', 0)} | "
            f"{row.get('api_errors', 0)} |"
        )
    lines.extend(["", "## Failure Details", ""])
    for row in report["failure_details"]:
        lines.append(
            f"- `{row['task_id']}`: mode={row['observed_mode']} expected={row['expected_mode']}; "
            f"gold={row['gold']} prediction={row['prediction']}; "
            f"compiler_correct={row['compiler_correct']} actor_only={row['actor_only_failure']}"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default="reports/v2_stage_report.json")
    args = ap.parse_args()
    report = summarize(load_rows([Path(path) for path in args.input]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
