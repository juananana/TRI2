from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from .reference_lifecycle import REPRESENTATIONS, predict


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def load_tasks(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def exact_match(pred: str | list[str], gold: str | list[str]) -> bool:
    if isinstance(pred, list) or isinstance(gold, list):
        return list(pred) == list(gold) if isinstance(pred, list) and isinstance(gold, list) else False
    return pred == gold


def wilson(correct: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    p = correct / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return center - margin, center + margin


def _add(groups: dict[tuple[str, ...], dict[str, int]], key: tuple[str, ...], ok: bool) -> None:
    groups[key]["n"] += 1
    groups[key]["correct"] += int(ok)


def _row(key: tuple[str, ...], stats: dict[str, int], fields: list[str]) -> dict[str, Any]:
    lo, hi = wilson(stats["correct"], stats["n"])
    return {
        **dict(zip(fields, key)),
        **stats,
        "accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
        "ci95_low": lo,
        "ci95_high": hi,
    }


def error_type(task: dict[str, Any], pred: str | list[str]) -> str:
    if pred == task.get("post_refresh_target") and task["binding"] == "anchored":
        return "temporal_rebinding"
    if pred == task.get("pre_refresh_target") and task["binding"] == "dynamic":
        return "premature_binding"
    if task["correct_target"] == "INVALID_BOUND_ENTITY" and pred != "INVALID_BOUND_ENTITY":
        return "invalid_but_processed"
    if pred == "INVALID_BOUND_ENTITY" and task["correct_target"] != "INVALID_BOUND_ENTITY":
        return "unnecessary_invalidation"
    if task.get("update") == "name_collision":
        return "alias_collision"
    if task.get("task_type") == "collection":
        return "collection_mismatch"
    if task.get("task_type") == "nested":
        return "nested_mismatch"
    return "other"


def summarize(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    overall: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    by_type: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    by_update: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    by_phenomenon: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    errors: dict[tuple[str, ...], int] = defaultdict(int)
    examples: list[dict[str, Any]] = []

    for task in tasks:
        for rep in REPRESENTATIONS:
            pred = predict(task, rep)
            ok = exact_match(pred, task["correct_target"])
            _add(overall, (rep,), ok)
            _add(by_type, (rep, task["task_type"], task["binding"]), ok)
            _add(by_update, (rep, task.get("update", "none"), task["binding"]), ok)
            _add(by_phenomenon, (rep, task["phenomenon"], task["binding"]), ok)
            if not ok:
                et = error_type(task, pred)
                errors[(rep, et)] += 1
                if len(examples) < 80:
                    examples.append({
                        "representation": rep,
                        "error_type": et,
                        "task_id": task["id"],
                        "task_type": task["task_type"],
                        "phenomenon": task["phenomenon"],
                        "binding": task["binding"],
                        "update": task.get("update"),
                        "prediction": pred,
                        "correct": task["correct_target"],
                    })

    return {
        "n_tasks": len(tasks),
        "representations": REPRESENTATIONS,
        "overall": [_row(k, v, ["representation"]) for k, v in sorted(overall.items())],
        "by_type": [_row(k, v, ["representation", "task_type", "binding"]) for k, v in sorted(by_type.items())],
        "by_update": [_row(k, v, ["representation", "update", "binding"]) for k, v in sorted(by_update.items())],
        "by_phenomenon": [
            _row(k, v, ["representation", "phenomenon", "binding"])
            for k, v in sorted(by_phenomenon.items())
        ],
        "error_counts": [
            {"representation": rep, "error_type": et, "count": count}
            for (rep, et), count in sorted(errors.items())
        ],
        "error_examples": examples,
    }


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{100 * x:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v2 Representation Ablation",
        "",
        f"Tasks: {report['n_tasks']}",
        "",
        "## Overall",
        "",
        "| Representation | n | Accuracy | 95% CI |",
        "|---|---:|---:|---:|",
    ]
    for row in report["overall"]:
        lines.append(
            f"| {row['representation']} | {row['n']} | {pct(row['accuracy'])} | "
            f"[{pct(row['ci95_low'])}, {pct(row['ci95_high'])}] |"
        )
    lines.extend([
        "",
        "## By Task Type",
        "",
        "| Representation | Task type | Binding | n | Accuracy |",
        "|---|---|---|---:|---:|",
    ])
    for row in report["by_type"]:
        lines.append(
            f"| {row['representation']} | {row['task_type']} | {row['binding']} | "
            f"{row['n']} | {pct(row['accuracy'])} |"
        )
    lines.extend([
        "",
        "## Error Counts",
        "",
        "| Representation | Error type | Count |",
        "|---|---|---:|",
    ])
    for row in report["error_counts"]:
        lines.append(f"| {row['representation']} | {row['error_type']} | {row['count']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DATA / "temporal_referent_v2.jsonl"))
    ap.add_argument("--output", default=str(REPORTS / "v2_ablation.json"))
    args = ap.parse_args()
    report = summarize(load_tasks(Path(args.input)))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
