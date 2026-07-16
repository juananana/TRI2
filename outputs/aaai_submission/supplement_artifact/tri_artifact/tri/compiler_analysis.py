from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def norm_binding_time(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"pre_refresh", "pre-refresh", "before_refresh", "before refresh"}:
        return "pre_refresh"
    if text in {"post_refresh", "post-refresh", "after_refresh", "after refresh"}:
        return "post_refresh"
    return text


def load_rows(paths: list[Path], deduplicate_tasks: bool) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                result = row.get("result", {})
                if row.get("status") == "ok" and result.get("mode") == "compile_then_act":
                    rows.append(row)
    if deduplicate_tasks:
        seen: dict[tuple[str | None, str | None], dict] = {}
        for row in rows:
            seen[(row.get("model"), row.get("task", {}).get("id"))] = row
        rows = list(seen.values())
    return rows


def is_binding_correct(row: dict) -> bool:
    task = row["task"]
    ledger = row["result"].get("compiled_ledger") or {}
    expected = "pre_refresh" if task["binding"] == "anchored" else "post_refresh"
    return norm_binding_time(ledger.get("binding_time")) == expected


def is_bound_id_correct(row: dict) -> bool:
    task = row["task"]
    ledger = row["result"].get("compiled_ledger") or {}
    if task["binding"] != "anchored":
        return True
    return ledger.get("bound_target_id") == task["pre_refresh_target"]


def pct(numer: int, denom: int) -> str:
    return "NA" if denom == 0 else f"{100 * numer / denom:.1f}"


def summarize(rows: list[dict]) -> dict:
    groups = defaultdict(lambda: {
        "n": 0,
        "compile_binding_correct": 0,
        "compile_bound_id_correct": 0,
        "compile_bound_id_applicable": 0,
        "final_correct": 0,
        "drift": 0,
        "errors": 0,
    })
    for row in rows:
        task = row["task"]
        result = row["result"]
        key = (row["model"], task["binding"], task["update"])
        groups[key]["n"] += 1
        groups[key]["compile_binding_correct"] += int(is_binding_correct(row))
        if task["binding"] == "anchored":
            groups[key]["compile_bound_id_applicable"] += 1
            groups[key]["compile_bound_id_correct"] += int(is_bound_id_correct(row))
        groups[key]["final_correct"] += int(bool(result.get("success")))
        groups[key]["drift"] += int(bool(result.get("drift_to_new_leader")))
        groups[key]["errors"] += int(bool(result.get("errors")))
    return {
        "overall": [
            {
                "model": key[0],
                "binding": key[1],
                "update": key[2],
                **value,
                "compile_binding_accuracy": None if value["n"] == 0 else value["compile_binding_correct"] / value["n"],
                "compile_bound_id_accuracy": (
                    None
                    if value["compile_bound_id_applicable"] == 0
                    else value["compile_bound_id_correct"] / value["compile_bound_id_applicable"]
                ),
                "final_accuracy": None if value["n"] == 0 else value["final_correct"] / value["n"],
                "drift_rate": None if value["n"] == 0 else value["drift"] / value["n"],
            }
            for key, value in sorted(groups.items())
        ]
    }


def markdown(report: dict) -> str:
    lines = [
        "## Compile-Then-Act Analysis",
        "",
        "| Model | Binding | Update | n | Binding Compile Acc. | Bound-ID Compile Acc. | Final Acc. | Drift | Errors |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["overall"]:
        n = row["n"]
        id_denom = row["compile_bound_id_applicable"]
        id_acc = "NA" if id_denom == 0 else pct(row["compile_bound_id_correct"], id_denom)
        lines.append(
            f"| {row['model']} | {row['binding']} | {row['update']} | {n} | "
            f"{pct(row['compile_binding_correct'], n)} | "
            f"{id_acc} | "
            f"{pct(row['final_correct'], n)} | "
            f"{pct(row['drift'], n)} | {row['errors']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--deduplicate-tasks", action="store_true")
    args = ap.parse_args()
    report = summarize(load_rows([Path(p) for p in args.input], args.deduplicate_tasks))
    out = Path(args.output)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
