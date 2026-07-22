from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def load(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def short_model(name: str) -> str:
    if "GLM" in name:
        return "GLM-5.1"
    if "Qwen" in name:
        return "Qwen3.5"
    if "MiniMax" in name:
        return "MiniMax"
    if "DeepSeek" in name:
        return "DeepSeek"
    return name.split("/")[-1]


def wilson(correct: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    p = correct / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return center - margin, center + margin


def result_mode(row: dict[str, Any]) -> str:
    return row.get("result", {}).get("mode") or "api_error"


def is_api_failure(row: dict[str, Any]) -> bool:
    if row.get("status") != "ok":
        return True
    result = row.get("result", {})
    errors = [str(err) for err in result.get("errors", [])]
    if any(
        "HTTP Error" in err
        or "URLError" in err
        or "timed out" in err.lower()
        or err.startswith("api_call_error:")
        for err in errors
    ):
        return True
    return bool(errors) and not result.get("raw_outputs") and result.get("predicted_target") is None


def is_success_all(row: dict[str, Any]) -> bool:
    return not is_api_failure(row) and bool(row.get("result", {}).get("success"))


def error_type(row: dict[str, Any]) -> str | None:
    if is_api_failure(row):
        return "api_error"
    task = row["task"]
    result = row["result"]
    pred = result.get("predicted_target")
    gold = task["correct_target"]
    if pred == gold:
        return None
    if gold == "INVALID_BOUND_ENTITY" and pred != "INVALID_BOUND_ENTITY":
        return "invalid_but_processed"
    if pred == "INVALID_BOUND_ENTITY" and gold != "INVALID_BOUND_ENTITY":
        return "unnecessary_invalidation"
    if task["binding"] == "anchored" and pred == task["post_refresh_target"]:
        return "temporal_rebinding"
    if task["binding"] == "dynamic" and pred == task["pre_refresh_target"]:
        return "premature_binding"
    if task.get("update") == "name_collision":
        return "alias_collision"
    return "other"


def _add(groups: dict[tuple[str, ...], dict[str, int]], key: tuple[str, ...], row: dict[str, Any]) -> None:
    failed_api = is_api_failure(row)
    groups[key]["n"] += 1
    groups[key]["correct"] += int(is_success_all(row))
    groups[key]["api_errors"] += int(failed_api)
    groups[key]["completed"] += int(not failed_api)
    groups[key]["completed_correct"] += int(not failed_api and bool(row.get("result", {}).get("success")))


def _row(key: tuple[str, ...], stats: dict[str, int], fields: list[str]) -> dict[str, Any]:
    lo, hi = wilson(stats["correct"], stats["n"])
    completed_lo, completed_hi = wilson(stats["completed_correct"], stats["completed"])
    return {
        **dict(zip(fields, key)),
        **stats,
        "accuracy_all": stats["correct"] / stats["n"] if stats["n"] else None,
        "accuracy_completed": stats["completed_correct"] / stats["completed"] if stats["completed"] else None,
        "api_error_rate": stats["api_errors"] / stats["n"] if stats["n"] else None,
        "ci95_low": lo,
        "ci95_high": hi,
        "completed_ci95_low": completed_lo,
        "completed_ci95_high": completed_hi,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    empty = lambda: {"n": 0, "correct": 0, "api_errors": 0, "completed": 0, "completed_correct": 0}
    overall: dict[tuple[str, ...], dict[str, int]] = defaultdict(empty)
    by_binding: dict[tuple[str, ...], dict[str, int]] = defaultdict(empty)
    by_update: dict[tuple[str, ...], dict[str, int]] = defaultdict(empty)
    by_phenomenon: dict[tuple[str, ...], dict[str, int]] = defaultdict(empty)
    errors: dict[tuple[str, ...], int] = defaultdict(int)

    model_rows = [row for row in rows if "model" in row and "task" in row and "result" in row]
    for row in model_rows:
        model = short_model(row["model"])
        mode = result_mode(row)
        task = row["task"]
        _add(overall, (model, mode), row)
        _add(by_binding, (model, mode, task["binding"]), row)
        _add(by_update, (model, mode, task["binding"], task["update"]), row)
        _add(by_phenomenon, (model, mode, task.get("phenomenon", "unknown"), task["binding"]), row)
        et = error_type(row)
        if et:
            errors[(model, mode, et)] += 1

    return {
        "n_rows": len(model_rows),
        "n_input_rows": len(rows),
        "overall": [_row(k, v, ["model", "mode"]) for k, v in sorted(overall.items())],
        "by_binding": [_row(k, v, ["model", "mode", "binding"]) for k, v in sorted(by_binding.items())],
        "by_update": [_row(k, v, ["model", "mode", "binding", "update"]) for k, v in sorted(by_update.items())],
        "by_phenomenon": [
            _row(k, v, ["model", "mode", "phenomenon", "binding"])
            for k, v in sorted(by_phenomenon.items())
        ],
        "error_counts": [
            {"model": model, "mode": mode, "error_type": et, "count": count}
            for (model, mode, et), count in sorted(errors.items())
        ],
    }


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{100 * x:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v2 Model Report",
        "",
        f"Rows: {report['n_rows']}",
        "",
        "Accuracy counts API errors as failures.",
        "",
        "## Overall",
        "",
        "| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["overall"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['n']} | {pct(row['accuracy_all'])} | "
            f"[{pct(row['ci95_low'])}, {pct(row['ci95_high'])}] | "
            f"{pct(row['accuracy_completed'])} | {pct(row['api_error_rate'])} |"
        )
    lines.extend([
        "",
        "## By Binding",
        "",
        "| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |",
        "|---|---|---|---:|---:|---:|---:|",
    ])
    for row in report["by_binding"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['binding']} | {row['n']} | "
            f"{pct(row['accuracy_all'])} | {pct(row['accuracy_completed'])} | "
            f"{pct(row['api_error_rate'])} |"
        )
    lines.extend([
        "",
        "## Error Counts",
        "",
        "| Model | Mode | Error | Count |",
        "|---|---|---|---:|",
    ])
    for row in report["error_counts"]:
        lines.append(f"| {row['model']} | {row['mode']} | {row['error_type']} | {row['count']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default=str(REPORTS / "v2_model_report.json"))
    args = ap.parse_args()
    report = summarize(load([Path(p) for p in args.input]))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
