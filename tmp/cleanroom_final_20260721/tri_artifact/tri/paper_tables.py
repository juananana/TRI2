from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load(
    paths: list[Path],
    exclude_result_errors: bool = False,
    deduplicate_tasks: bool = False,
) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    rows = [r for r in rows if r.get("status") == "ok"]
    if exclude_result_errors:
        rows = [r for r in rows if not r.get("result", {}).get("errors")]
    if deduplicate_tasks:
        seen = {}
        for row in rows:
            result = row.get("result", {})
            task = row.get("task", {})
            key = (row.get("model"), result.get("mode"), task.get("id"))
            seen[key] = row
        rows = list(seen.values())
    return rows


def pct(numer: int, denom: int) -> str:
    return "NA" if denom == 0 else f"{100 * numer / denom:.1f}"


def summarize(rows: list[dict]) -> dict:
    groups = defaultdict(lambda: {"n": 0, "correct": 0, "drift": 0})
    by_para = defaultdict(lambda: {"n": 0, "correct": 0, "drift": 0})
    for row in rows:
        task = row["task"]
        result = row["result"]
        mode = result.get("mode")
        key = (row["model"], mode, task["binding"], task["update"])
        groups[key]["n"] += 1
        groups[key]["correct"] += int(bool(result.get("success")))
        groups[key]["drift"] += int(bool(result.get("drift_to_new_leader")))
        pkey = (row["model"], mode, task["paraphrase"], task["binding"], task["update"])
        by_para[pkey]["n"] += 1
        by_para[pkey]["correct"] += int(bool(result.get("success")))
        by_para[pkey]["drift"] += int(bool(result.get("drift_to_new_leader")))
    return {
        "overall": [
            {
                "model": k[0],
                "mode": k[1],
                "binding": k[2],
                "update": k[3],
                **v,
                "accuracy": None if v["n"] == 0 else v["correct"] / v["n"],
                "drift_rate": None if v["n"] == 0 else v["drift"] / v["n"],
            }
            for k, v in sorted(groups.items())
        ],
        "by_paraphrase": [
            {
                "model": k[0],
                "mode": k[1],
                "paraphrase": k[2],
                "binding": k[3],
                "update": k[4],
                **v,
                "accuracy": None if v["n"] == 0 else v["correct"] / v["n"],
                "drift_rate": None if v["n"] == 0 else v["drift"] / v["n"],
            }
            for k, v in sorted(by_para.items())
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "## Overall",
        "",
        "| Model | Mode | Binding | Update | n | Accuracy | Drift |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for r in report["overall"]:
        lines.append(
            f"| {r['model']} | {r['mode']} | {r['binding']} | {r['update']} | "
            f"{r['n']} | {pct(r['correct'], r['n'])} | {pct(r['drift'], r['n'])} |"
        )
    lines.extend([
        "",
        "## By Paraphrase",
        "",
        "| Model | Mode | Para | Binding | Update | n | Accuracy | Drift |",
        "|---|---|---|---|---|---:|---:|---:|",
    ])
    for r in report["by_paraphrase"]:
        lines.append(
            f"| {r['model']} | {r['mode']} | {r['paraphrase']} | {r['binding']} | {r['update']} | "
            f"{r['n']} | {pct(r['correct'], r['n'])} | {pct(r['drift'], r['n'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--exclude-result-errors", action="store_true")
    ap.add_argument("--deduplicate-tasks", action="store_true")
    args = ap.parse_args()
    report = summarize(load(
        [Path(p) for p in args.input],
        exclude_result_errors=args.exclude_result_errors,
        deduplicate_tasks=args.deduplicate_tasks,
    ))
    out = Path(args.output)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
