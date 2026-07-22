from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .reference_lifecycle import REPRESENTATIONS, predict
from .v2_ablation import exact_match, wilson
from .v2_tool_env import AppStyleEnvironment


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
RUNS = ROOT / "runs"


def load_tasks(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_episode(task: dict[str, Any], controller: str) -> dict[str, Any]:
    env = AppStyleEnvironment(task)
    env.open_app()
    env.refresh_app()
    target = predict(task, controller)
    action_result = env.perform_action(target)
    return {
        "status": "ok",
        "controller": controller,
        "task": task,
        "prediction": target,
        "success": exact_match(target, task["correct_target"]),
        "action_result": action_result,
        "trace": env.trace,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    for row in rows:
        task = row["task"]
        key = (row["controller"], task["task_type"], task["binding"])
        groups[key]["n"] += 1
        groups[key]["correct"] += int(row["success"])
    table = []
    for key, stats in sorted(groups.items()):
        lo, hi = wilson(stats["correct"], stats["n"])
        table.append({
            "controller": key[0],
            "task_type": key[1],
            "binding": key[2],
            **stats,
            "accuracy": stats["correct"] / stats["n"],
            "ci95_low": lo,
            "ci95_high": hi,
        })
    return {"n_episodes": len(rows), "table": table}


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v2 App-Style Tool Ablation",
        "",
        f"Episodes: {report['n_episodes']}",
        "",
        "| Controller | Task type | Binding | n | Accuracy | 95% CI |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in report["table"]:
        lines.append(
            f"| {row['controller']} | {row['task_type']} | {row['binding']} | {row['n']} | "
            f"{pct(row['accuracy'])} | [{pct(row['ci95_low'])}, {pct(row['ci95_high'])}] |"
        )
    return "\n".join(lines) + "\n"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DATA / "temporal_referent_v2.jsonl"))
    ap.add_argument("--runs-output", default=str(RUNS / "v2_tool_ablation.jsonl"))
    ap.add_argument("--report-output", default=str(REPORTS / "v2_tool_ablation.json"))
    args = ap.parse_args()

    tasks = load_tasks(Path(args.input))
    rows = [run_episode(task, controller) for task in tasks for controller in REPRESENTATIONS]
    write_jsonl(Path(args.runs_output), rows)
    report = summarize(rows)
    out = Path(args.report_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
