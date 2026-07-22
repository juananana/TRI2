#!/usr/bin/env python3
"""Audit released AppWorld trajectories for a natural TRI-like task family."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CANDIDATE_GENERATOR_ID = "8ce6779"
ASSIGN_RE = re.compile(r"^/todoist/tasks/(\d+)/assign$")
COMMENT_RE = re.compile(r"^/todoist/tasks/(\d+)/comments$")


def _decode_int_key(value: str) -> int:
    return int(value.rsplit(":", 1)[-1])


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_task(data_root: Path, output_task_dir: Path) -> dict[str, Any]:
    task_id = output_task_dir.name
    task_root = data_root / "tasks" / task_id
    instruction = _load_json(task_root / "specs.json")["instruction"]
    private = _load_json(task_root / "ground_truth/private_data.json")
    expected_ids = {
        _decode_int_key(value) for value in private["task_id_to_assignee_id"].keys()
    }
    calls_path = output_task_dir / "logs/api_calls.jsonl"
    calls = [
        json.loads(line)
        for line in calls_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assigned_sequence: list[int] = []
    commented_sequence: list[int] = []
    for call in calls:
        if call.get("method", "").lower() != "post":
            continue
        url = call.get("url", "")
        match = ASSIGN_RE.match(url)
        if match:
            assigned_sequence.append(int(match.group(1)))
            continue
        match = COMMENT_RE.match(url)
        if match:
            commented_sequence.append(int(match.group(1)))

    assigned = set(assigned_sequence)
    commented = set(commented_sequence)
    correct_binding_ids = expected_ids & assigned
    preserved_ids = correct_binding_ids & commented
    report_path = output_task_dir / "evaluation/report.md"
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    all_tests_passed = "Num Failed Tests : 0" in report_text
    return {
        "task_id": task_id,
        "instruction": instruction,
        "expected_target_count": len(expected_ids),
        "assignment_operation_count": len(assigned_sequence),
        "comment_operation_count": len(commented_sequence),
        "assigned_wrong_count": len(assigned - expected_ids),
        "commented_wrong_count": len(commented - expected_ids),
        "expected_targets_not_assigned_count": len(expected_ids - assigned),
        "correct_bindings_without_comment_count": len(correct_binding_ids - commented),
        "comments_without_prior_assignment_count": len(commented - assigned),
        "post_binding_opportunities": len(correct_binding_ids),
        "same_id_preservations": len(preserved_ids),
        "post_binding_substitutions": len((commented - assigned) & expected_ids),
        "all_official_tests_passed": all_tests_passed,
    }


def build_audit(runtime_root: Path) -> dict[str, Any]:
    data_root = runtime_root / "data"
    outputs_root = runtime_root / "experiments/outputs"
    task_ids = [f"{CANDIDATE_GENERATOR_ID}_{index}" for index in (1, 2, 3)]
    trajectories: list[dict[str, Any]] = []
    for experiment_dir in sorted(path for path in outputs_root.iterdir() if path.is_dir()):
        if experiment_dir.name.startswith(("tri_", "verification")):
            continue
        for task_id in task_ids:
            output_task_dir = experiment_dir / "tasks" / task_id
            if not (output_task_dir / "logs/api_calls.jsonl").exists():
                continue
            row = audit_task(data_root, output_task_dir)
            row["experiment"] = experiment_dir.name
            trajectories.append(row)

    generators = Counter(
        task_dir.name.split("_", 1)[0]
        for task_dir in (data_root / "tasks").iterdir()
        if task_dir.is_dir() and "_" in task_dir.name
    )
    combined = {
        "released_trajectory_count": len(trajectories),
        "experiment_configuration_count": len(
            {row["experiment"] for row in trajectories}
        ),
        "post_binding_opportunities": sum(
            row["post_binding_opportunities"] for row in trajectories
        ),
        "same_id_preservations": sum(row["same_id_preservations"] for row in trajectories),
        "post_binding_substitutions": sum(
            row["post_binding_substitutions"] for row in trajectories
        ),
        "correct_bindings_without_comment": sum(
            row["correct_bindings_without_comment_count"] for row in trajectories
        ),
        "expected_targets_not_assigned": sum(
            row["expected_targets_not_assigned_count"] for row in trajectories
        ),
        "wrong_assignment_targets": sum(
            row["assigned_wrong_count"] for row in trajectories
        ),
        "wrong_comment_targets": sum(
            row["commented_wrong_count"] for row in trajectories
        ),
        "fully_passing_trajectories": sum(
            row["all_official_tests_passed"] for row in trajectories
        ),
    }
    experiment_names = sorted({row["experiment"] for row in trajectories})
    return {
        "source": "official AppWorld 0.1.3.post1 released experiment outputs",
        "candidate_generator_id": CANDIDATE_GENERATOR_ID,
        "public_task_instance_count": sum(generators.values()),
        "public_generator_family_count": len(generators),
        "strict_exogenous_tri_opportunity_count": 0,
        "tri_like_generator_family_count": 1,
        "candidate_interpretation": (
            "The instruction binds tasks selected as assigned-to-me and incomplete. Reassignment "
            "changes the assignee field so those tasks no longer satisfy the initial selector; "
            "'leave a comment there' nevertheless refers to the same stable task IDs. This is a "
            "natural post-binding preservation trace, but not an exogenous refresh or selector-flip pair."
        ),
        "experiment_configurations": experiment_names,
        "combined": combined,
        "trajectories": trajectories,
    }


def render_markdown(audit: dict[str, Any]) -> str:
    combined = audit["combined"]
    lines = [
        "# AppWorld Released-Trajectory TRI Audit",
        "",
        "## Coverage",
        "",
        f"The downloaded AppWorld release contains {audit['public_task_instance_count']} task instances "
        f"from {audit['public_generator_family_count']} generator families. The unmodified task format "
        "has an initial world and Agent-driven actions but no independently scheduled post-binding",
        "external transition. Therefore the strict exogenous-refresh TRI opportunity count is **0**.",
        "",
        "One public task family, `8ce6779` (three instances), is a natural TRI-like trace. The",
        "Agent selects incomplete Todoist tasks assigned to the user, reassigns them, and then",
        "must resolve `leave a comment there` to the same task IDs. Reassignment makes those IDs",
        "fail the original assigned-to-me selector, while their discourse identity persists.",
        "",
        "## Released Trace Audit",
        "",
        "| Quantity | Count |",
        "|---|---:|",
        f"| Public Agent trajectories containing the family | {combined['released_trajectory_count']} |",
        f"| Released experiment configurations | {combined['experiment_configuration_count']} |",
        f"| Correct target-binding operations | {combined['post_binding_opportunities']} |",
        f"| Same-ID comments after reassignment | {combined['same_id_preservations']} |",
        f"| Post-binding target substitutions | {combined['post_binding_substitutions']} |",
        f"| Expected task targets never reassigned | {combined['expected_targets_not_assigned']} |",
        f"| Correct assignments lacking the required comment | {combined['correct_bindings_without_comment']} |",
        f"| Assignments to non-gold task IDs | {combined['wrong_assignment_targets']} |",
        f"| Comments on non-gold task IDs | {combined['wrong_comment_targets']} |",
        f"| Trajectories passing every official evaluator test | {combined['fully_passing_trajectories']} |",
        "",
        "## Interpretation",
        "",
        "This public trace establishes that post-binding reference persistence across a",
        "selector-invalidating state mutation occurs naturally in an independent benchmark.",
        "It does not establish TRI failure prevalence: the family has no Stable/Flip or",
        "Preserve/Reevaluate counterpart and no concurrent external update. In these released",
        "traces, the dominant failure is failure to bind/reassign expected tasks, not substitution of a",
        "different task after a correct binding. The result therefore supports problem realism",
        "while preserving the paper's model/controller-conditional failure claim.",
        "",
        "Per-experiment aggregate counts and official evaluator outcomes are stored in",
        "`appworld_public_trace_tri_audit.json`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    audit = build_audit(args.runtime_root)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(audit), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
