from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return [r for r in rows if r.get("status") == "ok"]


def mean(xs: list[bool]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def summarize(rows: list[dict]) -> dict:
    buckets = defaultdict(list)
    errors = defaultdict(int)
    for row in rows:
        task = row["task"]
        result = row["result"]
        key = (
            row["model"],
            result.get("mode"),
            task["split"],
            task["paraphrase"],
            task["binding"],
            task["update"],
        )
        buckets[key].append(bool(result.get("success")))
        if result.get("drift_to_new_leader"):
            errors[(row["model"], result.get("mode"), task["binding"], task["update"], "drift_to_new_leader")] += 1

    table = []
    for (model, mode, split, para, binding, update), vals in sorted(buckets.items()):
        table.append({
            "model": model,
            "mode": mode,
            "split": split,
            "paraphrase": para,
            "binding": binding,
            "update": update,
            "n": len(vals),
            "accuracy": mean(vals),
        })
    return {"valid_rows": len(rows), "table": table, "error_counts": {str(k): v for k, v in errors.items()}}


def markdown_table(report: dict) -> str:
    lines = [
        "| Model | Mode | Split | Para | Binding | Update | n | Acc |",
        "|---|---|---|---|---|---:|---:|---:|",
    ]
    for row in report["table"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['split']} | {row['paraphrase']} | "
            f"{row['binding']} | {row['update']} | {row['n']} | {row['accuracy']:.2f} |"
        )
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    report = summarize(load([Path(x) for x in args.input]))
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        Path(args.output).with_suffix(".md").write_text(markdown_table(report) + "\n", encoding="utf-8")
    print(text)
    print(markdown_table(report))


if __name__ == "__main__":
    main()

