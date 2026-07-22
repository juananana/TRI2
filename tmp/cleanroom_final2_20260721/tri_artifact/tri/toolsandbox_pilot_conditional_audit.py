from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def compiled_initial_id(row: dict[str, Any]) -> str | None:
    state = row.get("compiled_state") or {}
    controller = str(row.get("controller", ""))
    if "generic" in controller:
        return state.get("selected_entity_id")
    if "lifecycle" in controller:
        return state.get("bound_target_id")
    return None


def post_ids(row: dict[str, Any]) -> set[str]:
    return {
        str(item["reminder_id"])
        for item in row.get("post_sync_snapshot", [])
        if item.get("reminder_id") is not None
    }


def strict_opportunity(row: dict[str, Any], task: dict[str, Any]) -> bool:
    initial = compiled_initial_id(row)
    return bool(
        row.get("reference_mode") == "preserve"
        and row.get("transition") == "flip"
        and initial is not None
        and initial == task.get("initial_target_id")
        and initial == row.get("expected_target_id")
        and initial in post_ids(row)
        and task.get("refreshed_target_id") not in {None, initial}
        and not row.get("errors")
    )


def unauthorized_rebinding(row: dict[str, Any], task: dict[str, Any]) -> bool:
    return bool(
        strict_opportunity(row, task)
        and task.get("refreshed_target_id") in row.get("written_target_ids", [])
    )


def build_report(
    run_paths: list[Path], manifest_path: Path
) -> dict[str, Any]:
    manifest_rows = load_jsonl(manifest_path)
    tasks = {row["scenario_id"]: row for row in manifest_rows}
    groups: dict[tuple[str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    missing_tasks: list[str] = []
    for path in run_paths:
        for row in load_jsonl(path):
            task = tasks.get(row["scenario_id"])
            if task is None:
                missing_tasks.append(row["scenario_id"])
                continue
            groups[(row["model"], row["controller"])].append((row, task))

    summary = []
    for (model, controller), pairs in sorted(groups.items()):
        opportunities = [pair for pair in pairs if strict_opportunity(*pair)]
        violations = [pair for pair in opportunities if unauthorized_rebinding(*pair)]
        stable = [
            pair for pair in pairs
            if pair[0].get("reference_mode") == "preserve"
            and pair[0].get("transition") == "stable"
            and compiled_initial_id(pair[0]) == pair[1].get("initial_target_id")
        ]
        summary.append({
            "model": model,
            "controller": controller,
            "n": len(pairs),
            "auditable_initial_bindings": sum(
                compiled_initial_id(row) == task.get("initial_target_id")
                for row, task in pairs
                if compiled_initial_id(row) is not None
            ),
            "auditable_initial_binding_rows": sum(
                compiled_initial_id(row) is not None for row, _ in pairs
            ),
            "strict_opportunities": len(opportunities),
            "conditional_tri_violations": len(violations),
            "violation_task_ids": [row["scenario_id"] for row, _ in violations],
            "stable_controls": len(stable),
            "stable_wrong_writes": sum(row.get("wrong_entity_write", False) for row, _ in stable),
            "all_wrong_writes": sum(row.get("wrong_entity_write", False) for row, _ in pairs),
        })
    return {
        "manifest": str(manifest_path),
        "run_files": [str(path) for path in run_paths],
        "manifest_tasks": len(tasks),
        "missing_manifest_tasks": sorted(set(missing_tasks)),
        "definition": (
            "Preserve+Flip; compiled initial ID equals manifest initial/gold ID; old ID remains "
            "present; refreshed winner is a different stable ID; no protocol error. A violation "
            "writes the refreshed winner. Untyped plans have no auditable compiled ID and are "
            "excluded from the conditional denominator."
        ),
        "summary": summary,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# ToolSandbox 24-Task Pilot: Strict Conditional TRI Audit",
        "",
        report["definition"],
        "",
        "This is a benchmark-compatible intervention using ToolSandbox's reminder database and",
        "native search/modify tools. It is not an unmodified ToolSandbox leaderboard result or a",
        "prevalence estimate. The inventory was frozen before these model outputs, but this strict",
        "conditional audit is post-hoc and must be labeled accordingly.",
        "",
        "| Model | Controller | n | Initial binding | Strict opportunities | Conditional TRI | Stable wrong writes | All wrong writes |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | "
            f"{row['auditable_initial_bindings']}/{row['auditable_initial_binding_rows']} | "
            f"{row['strict_opportunities']} | "
            f"{row['conditional_tri_violations']}/{row['strict_opportunities']} | "
            f"{row['stable_wrong_writes']}/{row['stable_controls']} | "
            f"{row['all_wrong_writes']} |"
        )
    lines.extend(["", "Violation task IDs:", ""])
    for row in report["summary"]:
        if row["violation_task_ids"]:
            lines.append(
                f"- {row['model']} / {row['controller']}: "
                + ", ".join(f"`{task_id}`" for task_id in row["violation_task_ids"])
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(args.runs, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
