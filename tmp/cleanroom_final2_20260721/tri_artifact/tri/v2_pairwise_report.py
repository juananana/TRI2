from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from .v2_model_report import is_api_failure, short_model


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ok(row: dict[str, Any]) -> bool:
    return not is_api_failure(row) and bool(row.get("result", {}).get("success"))


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired_rows(path_a: Path, path_b: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows_a = {row["task"]["id"]: row for row in load_jsonl(path_a) if "task" in row}
    rows_b = {row["task"]["id"]: row for row in load_jsonl(path_b) if "task" in row}
    ids = sorted(set(rows_a) & set(rows_b))
    return [rows_a[i] for i in ids], [rows_b[i] for i in ids]


def summarize(path_a: Path, path_b: Path) -> dict[str, Any]:
    rows_a, rows_b = paired_rows(path_a, path_b)
    both_ok = a_only = b_only = both_wrong = 0
    api_a = api_b = 0
    for a, b in zip(rows_a, rows_b):
        a_api = is_api_failure(a)
        b_api = is_api_failure(b)
        api_a += int(a_api)
        api_b += int(b_api)
        a_ok = ok(a)
        b_ok = ok(b)
        both_ok += int(a_ok and b_ok)
        a_only += int(a_ok and not b_ok)
        b_only += int(b_ok and not a_ok)
        both_wrong += int(not a_ok and not b_ok)
    acc_a = (both_ok + a_only) / len(rows_a) if rows_a else None
    acc_b = (both_ok + b_only) / len(rows_a) if rows_a else None
    first_a = rows_a[0] if rows_a else {}
    first_b = rows_b[0] if rows_b else {}
    return {
        "file_a": str(path_a),
        "file_b": str(path_b),
        "model_a": short_model(first_a.get("model", "")) if first_a else None,
        "model_b": short_model(first_b.get("model", "")) if first_b else None,
        "mode_a": first_a.get("result", {}).get("mode") if first_a else None,
        "mode_b": first_b.get("result", {}).get("mode") if first_b else None,
        "n_paired": len(rows_a),
        "accuracy_a": acc_a,
        "accuracy_b": acc_b,
        "delta_b_minus_a": None if acc_a is None or acc_b is None else acc_b - acc_a,
        "both_correct": both_ok,
        "a_only_correct": a_only,
        "b_only_correct": b_only,
        "both_wrong": both_wrong,
        "api_errors_a": api_a,
        "api_errors_b": api_b,
        "mcnemar_exact_p": exact_mcnemar_p(a_only, b_only),
    }


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{100 * x:.1f}"


def markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# TRI-v2 Paired Significance Report",
        "",
        "Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.",
        "",
        "| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        label_a = f"{row['model_a']} {row['mode_a']}"
        label_b = f"{row['model_b']} {row['mode_b']}"
        lines.append(
            f"| {label_a} | {label_b} | {row['n_paired']} | {pct(row['accuracy_a'])} | "
            f"{pct(row['accuracy_b'])} | {pct(row['delta_b_minus_a'])} | "
            f"{row['a_only_correct']} | {row['b_only_correct']} | "
            f"{row['api_errors_a']}/{row['api_errors_b']} | {row['mcnemar_exact_p']:.4g} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, action="append", required=True, metavar=("A", "B"))
    ap.add_argument("--output", default="reports/v2_pairwise_report.json")
    args = ap.parse_args()
    report = [summarize(Path(a), Path(b)) for a, b in args.pair]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
