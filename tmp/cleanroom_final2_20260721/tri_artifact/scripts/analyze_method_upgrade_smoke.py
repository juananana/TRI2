from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = (
    "schema_valid", "mode_correct", "bound_id_correct",
    "selector_initial_correct", "selector_final_correct", "authorized_target_correct",
)


def load(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["method"])].append(row)
    output = []
    for (model, method), group in sorted(groups.items()):
        metrics = {}
        for metric in METRICS:
            eligible = [row[metric] for row in group if row.get(metric) is not None]
            metrics[metric] = {
                "correct": sum(value is True for value in eligible),
                "eligible": len(eligible),
                "rate": (sum(value is True for value in eligible) / len(eligible) if eligible else None),
            }
        usage = [record for row in group for record in row.get("usage", [])]
        output.append({
            "model": model,
            "method": method,
            "tasks": len(group),
            "tasks_with_errors": sum(bool(row.get("errors")) for row in group),
            "request_attempts": sum(row.get("request_attempts", 0) for row in group),
            "prompt_tokens": sum(record.get("prompt_tokens", 0) for record in usage),
            "completion_tokens": sum(record.get("completion_tokens", 0) for record in usage),
            "metrics": metrics,
        })
    hashes = sorted({row.get("dataset_sha256") for row in rows if row.get("dataset_sha256")})
    return {"dataset_sha256": hashes, "groups": output}


def decision(report: dict[str, Any]) -> dict[str, Any]:
    expected_methods = {"exact_cta", "event_graph", "event_graph_selector"}
    by_model: dict[str, set[str]] = defaultdict(set)
    for group in report["groups"]:
        if (
            group["tasks"] >= 1
            and group["tasks_with_errors"] == 0
            and group["metrics"]["schema_valid"]["rate"] == 1.0
        ):
            by_model[group["model"]].add(group["method"])
    preflight_closed_loop = (
        len(by_model) >= 2
        and all(methods == expected_methods for methods in by_model.values())
    )
    m2 = [group for group in report["groups"] if group["method"] == "event_graph_selector"]
    complete = len(m2) >= 2 and all(group["tasks"] == 20 for group in m2)
    gates = {
        "two_complete_models": complete,
        "schema_valid_at_least_95pct": complete and all(
            group["metrics"]["schema_valid"]["rate"] >= 0.95 for group in m2
        ),
        "selector_equivalence_at_least_95pct": complete and all(
            group["metrics"]["selector_initial_correct"]["rate"] >= 0.95
            and group["metrics"]["selector_final_correct"]["rate"] >= 0.95
            for group in m2
        ),
        "api_parse_failure_at_most_5pct": complete and all(
            group["tasks_with_errors"] / group["tasks"] <= 0.05 for group in m2
        ),
    }
    return {
        "preflight_closed_loop": preflight_closed_loop,
        "gates": gates,
        "go_to_v7": all(gates.values()),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Method Upgrade Compiler Smoke",
        "",
        "| Model | Method | N | Schema | Mode | Bound ID | Selector initial | Selector final | Authorized target | Errors |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in report["groups"]:
        def cell(metric: str) -> str:
            item = group["metrics"][metric]
            return "NA" if not item["eligible"] else f"{item['correct']}/{item['eligible']}"
        lines.append(
            f"| {group['model']} | {group['method']} | {group['tasks']} | "
            f"{cell('schema_valid')} | {cell('mode_correct')} | {cell('bound_id_correct')} | "
            f"{cell('selector_initial_correct')} | {cell('selector_final_correct')} | "
            f"{cell('authorized_target_correct')} | {group['tasks_with_errors']} |"
        )
    lines.extend(["", "## Go/No-Go", ""])
    lines.append(f"- preflight_closed_loop: {report['decision']['preflight_closed_loop']}")
    for gate, value in report["decision"]["gates"].items():
        lines.append(f"- {gate}: {value}")
    lines.append(f"- go_to_v7: {report['decision']['go_to_v7']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    args = parser.parse_args()
    report = summarize(load(args.inputs))
    report["decision"] = decision(report)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["decision"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
