from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def load_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def initial_binding_id(row: dict[str, Any]) -> str | None:
    ledger = row.get("result", {}).get("compiled_ledger") or {}
    return ledger.get("selected_entity_id")


def initial_binding_correct(row: dict[str, Any]) -> bool:
    task = row["task"]
    return initial_binding_id(row) == task.get("pre_refresh_target")


def is_core_opportunity(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") in {"flip", "name_collision"}
        and task.get("bound_entity_present_after_refresh")
        and task.get("bound_entity_actionable_after_refresh")
        and initial_binding_correct(row)
    )


def _percentile(values: list[float], q: float) -> float:
    pos = (len(values) - 1) * q
    lower = int(pos)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (pos - lower)


def cluster_ci(rows: list[dict[str, Any]], event: str, repetitions: int = 10_000) -> list[float] | None:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        clusters[str(row["task"].get("template_id", "unknown"))].append(row)
    names = sorted(clusters)
    if len(names) < 2:
        return None
    rng = random.Random(20260719)
    values = []
    for _ in range(repetitions):
        sample = [row for _ in names for row in clusters[rng.choice(names)]]
        values.append(sum(bool(row["result"].get(event)) for row in sample) / len(sample))
    values.sort()
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [row for row in rows if is_core_opportunity(row)]
    return {
        "n": len(rows),
        "initial_binding_correct": sum(initial_binding_correct(row) for row in rows),
        "opportunities": len(eligible),
        "drift_to_new_leader": sum(
            row["result"].get("predicted_target") == row["task"].get("post_refresh_target")
            for row in eligible
        ),
        "final_wrong_target": sum(
            row["result"].get("predicted_target") != row["task"].get("correct_target")
            for row in eligible
        ),
        "drift_rate_ci95_cluster": cluster_ci(eligible, "drift_to_new_leader"),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row.get("model", "")), str(row["task"].get("update", "unknown")))].append(row)
    summary = [
        {"model": model, "update": update, **summarize_group(group)}
        for (model, update), group in sorted(groups.items())
    ]
    core = [row for row in rows if is_core_opportunity(row)]
    return {
        "inventory": {
            "rows": len(rows),
            "models": sorted({str(row.get("model", "")) for row in rows}),
            "core_opportunities": len(core),
        },
        "summary": summary,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Corrected Generic Ledger TRI Audit",
        "",
        "This audit reads Generic Ledger's `selected_entity_id`; the older stage report incorrectly",
        "looked for lifecycle-only `bound_target_id` and therefore undercounted correct initial bindings.",
        "",
        f"Rows: {report['inventory']['rows']}; core opportunities: {report['inventory']['core_opportunities']}.",
        "",
        "| Model | Update | N | Initial binding correct | Opportunities | Drift to refreshed leader | Drift rate | Final wrong target |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        ci = row["drift_rate_ci95_cluster"]
        rate = (
            "NA"
            if not row["opportunities"]
            else f"{100 * row['drift_to_new_leader'] / row['opportunities']:.1f}%"
        )
        if ci is not None:
            rate += f" [{100 * ci[0]:.1f}, {100 * ci[1]:.1f}]"
        lines.append(
            f"| {row['model']} | {row['update']} | {row['n']} | {row['initial_binding_correct']} | "
            f"{row['opportunities']} | {row['drift_to_new_leader']} | {rate} | "
            f"{row['final_wrong_target']} |"
        )
    lines.extend(
        [
            "",
            "Core opportunities are anchored tasks with flip or name-collision updates where the",
            "pre-refresh selected_entity_id is correct and the old entity remains present and actionable.",
            "Remove/invalidate cases are excluded because they test invalidity policy rather than",
            "the referential-core TRI transition.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    report = build_report(load_rows(args.inputs))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
