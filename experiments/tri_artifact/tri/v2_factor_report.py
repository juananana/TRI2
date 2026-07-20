from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from .v2_ablation import exact_match, wilson


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_run_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(load_jsonl(path))
    return [r for r in rows if "model" in r and "task" in r and "result" in r]


def short_model(name: str) -> str:
    if "GLM" in name:
        return "GLM-5.1"
    if "Qwen" in name:
        return "Qwen3.5"
    if "MiniMax" in name:
        return "MiniMax"
    return name.split("/")[-1]


def mode(row: dict[str, Any]) -> str:
    return row.get("result", {}).get("mode", "api_error")


def api_failure(row: dict[str, Any]) -> bool:
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


def success(row: dict[str, Any]) -> bool:
    return not api_failure(row) and bool(row.get("result", {}).get("success"))


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


def summarize_model_runs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_style: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    by_update: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    by_domain: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    validity_gap: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})

    for row in rows:
        task = row["task"]
        key_base = (short_model(row["model"]), mode(row))
        ok = success(row)
        _add(by_style, key_base + (task.get("phenomenon", "unknown"), task["binding"]), ok)
        _add(by_update, key_base + (task["update"], task["binding"]), ok)
        _add(by_domain, key_base + (task["domain"], task["binding"]), ok)
        bucket = "bound_valid" if task.get("bound_entity_actionable_after_refresh", True) else "bound_invalid"
        if task["binding"] == "anchored":
            _add(validity_gap, key_base + (bucket, task["update"]), ok)

    return {
        "by_style": [_row(k, v, ["model", "mode", "phenomenon", "binding"]) for k, v in sorted(by_style.items())],
        "by_update": [_row(k, v, ["model", "mode", "update", "binding"]) for k, v in sorted(by_update.items())],
        "by_domain": [_row(k, v, ["model", "mode", "domain", "binding"]) for k, v in sorted(by_domain.items())],
        "validity_gap": [_row(k, v, ["model", "mode", "bound_status", "update"]) for k, v in sorted(validity_gap.items())],
    }


def macro_domain(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    per_domain: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    counts: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0})
    for row in rows:
        task = row["task"]
        key = (short_model(row["model"]), mode(row), task["binding"], task["domain"])
        counts[key]["n"] += 1
        counts[key]["correct"] += int(success(row))
    for (model, m, binding, _domain), stats in counts.items():
        per_domain[(model, m, binding)].append(stats["correct"] / stats["n"])
    out = []
    for (model, m, binding), vals in sorted(per_domain.items()):
        out.append({
            "model": model,
            "mode": m,
            "binding": binding,
            "n_domains": len(vals),
            "macro_accuracy": sum(vals) / len(vals),
            "domain_min": min(vals),
            "domain_max": max(vals),
        })
    return out


def pct(x: float | None) -> str:
    return "NA" if x is None or math.isnan(x) else f"{100 * x:.1f}"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI-v2 Factor Report",
        "",
        "## Explicit vs Implicit",
        "",
        "| Model | Mode | Phenomenon | Binding | n | Acc. |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in report["by_style"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['phenomenon']} | {row['binding']} | "
            f"{row['n']} | {pct(row['accuracy'])} |"
        )
    lines.extend([
        "",
        "## Validity Gap for Anchored Cases",
        "",
        "| Model | Mode | Bound status | Update | n | Acc. |",
        "|---|---|---|---|---:|---:|",
    ])
    for row in report["validity_gap"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['bound_status']} | {row['update']} | "
            f"{row['n']} | {pct(row['accuracy'])} |"
        )
    lines.extend([
        "",
        "## Domain Macro Accuracy",
        "",
        "| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |",
        "|---|---|---|---:|---:|---:|---:|",
    ])
    for row in report["macro_domain"]:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['binding']} | {row['n_domains']} | "
            f"{pct(row['macro_accuracy'])} | {pct(row['domain_min'])} | {pct(row['domain_max'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default=str(REPORTS / "v2_factor_report.json"))
    args = ap.parse_args()
    rows = load_run_rows([Path(x) for x in args.input])
    report = summarize_model_runs(rows)
    report["macro_domain"] = macro_domain(rows)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
