"""Model-assisted public benchmark recall triage.

This module builds a non-independent review queue from already frozen public
coverage audits. The labels are candidate labels for reviewer triage only; they
do not adjudicate benchmark coverage and do not establish recall.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from tri.public_audit_sensitivity import FEATURES, build_controls, strict_label
from tri.revision_matched_audit import canonical_json, sha256_bytes, sha256_path


TRIAGE_VERSION = "TRI-model-assisted-public-recall-triage-v1"
EVIDENCE_STATUS = "post-primary zero-API model-assisted triage; not independent review"
SUITES = ("ToolSandbox", "AppWorld", "tau3-bench", "API-Bank", "BFCL", "ToolTalk")
PROMPT_TEXT = """You are helping audit benchmark coverage for Temporal Referent Integrity (TRI).

For each record, label these features as yes/no/partial using only the supplied
source excerpt: stable_entity_id, observable_pre_refresh_binding,
independent_post_binding_transition, competing_same_role_entity,
changed_selector_winner, old_entity_remains_actionable, later_target_mutation,
and evaluable_authorized_target.

Return JSON only. Treat partial as non-strict. Do not infer missing pre/post
states, independent refreshes, or changed selector winners from general task
descriptions. The output is candidate_labels for human review, not adjudication.
"""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("\n".join(canonical_json(row) for row in rows) + "\n", encoding="utf-8")


def _feature(status: str, evidence: str) -> dict[str, str]:
    if status not in {"yes", "no", "partial"}:
        raise ValueError(f"invalid feature status: {status}")
    return {"status": status, "evidence": evidence}


def _strict_from_candidate(features: dict[str, dict[str, str]]) -> bool:
    return all(features[name]["status"] == "yes" for name in FEATURES)


def _review_priority(features: dict[str, dict[str, str]], source_kind: str) -> str:
    statuses = [features[name]["status"] for name in FEATURES]
    yes_count = statuses.count("yes")
    partial_count = statuses.count("partial")
    if _strict_from_candidate(features) or source_kind in {"closest_case", "injected_control"}:
        return "highest"
    if source_kind == "external_structural_candidate" and (yes_count >= 2 or partial_count):
        return "high"
    if yes_count >= 5 or partial_count >= 2:
        return "high"
    if yes_count >= 3 or partial_count:
        return "medium"
    return "low"


def _base_record(
    record_id: str,
    suite: str,
    source_kind: str,
    source_path: str,
    source_sha256: str,
    case_id: str,
    excerpt: dict[str, Any],
    features: dict[str, dict[str, str]],
) -> dict[str, Any]:
    if set(features) != set(FEATURES):
        missing = sorted(set(FEATURES) - set(features))
        raise ValueError(f"missing feature labels for {record_id}: {missing}")
    return {
        "triage_version": TRIAGE_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "record_id": record_id,
        "suite": suite,
        "source_kind": source_kind,
        "source": {"path": source_path, "sha256": source_sha256},
        "case_id": case_id,
        "source_excerpt": excerpt,
        "candidate_labels": features,
        "candidate_strict": _strict_from_candidate(features),
        "review_priority": _review_priority(features, source_kind),
        "publication_status": "candidate_labels_only_not_independent_review",
    }


def _labels_from_checklist(row: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        name: _feature(cell["status"], cell["evidence"])
        for name, cell in row["features"].items()
    }


def _closest_case_records(root: Path) -> list[dict[str, Any]]:
    checklist_path = root / "reports" / "benchmark_coverage_checklist.json"
    checklist = load_json(checklist_path)
    rows = []
    for row in checklist["benchmarks"]:
        suite = row["benchmark"]
        rows.append(
            _base_record(
                f"closest-{suite.lower().replace('-', '')}",
                suite,
                "closest_case",
                "reports/benchmark_coverage_checklist.json",
                sha256_path(checklist_path),
                row["closest_case"],
                {
                    "closest_case": row["closest_case"],
                    "inventory": row["inventory"],
                    "source": row["source"],
                },
                _labels_from_checklist(row),
            )
        )
    return rows


def _toolsandbox_records(root: Path) -> list[dict[str, Any]]:
    path = root / "reports" / "official_toolsandbox_tri_prevalence_audit.json"
    report = load_json(path)
    source_sha = sha256_path(path)
    rows: list[dict[str, Any]] = []
    chosen = []
    tri_like = [s for s in report["scenarios"] if s["tri_like_eligible"]]
    chosen.extend(tri_like)
    for classification in sorted({s["classification"] for s in report["scenarios"]}):
        matches = [s for s in report["scenarios"] if s["classification"] == classification]
        chosen.extend(matches[:2])
    seen = set()
    for scenario in chosen:
        name = scenario["scenario_name"]
        if name in seen:
            continue
        seen.add(name)
        features = {
            "stable_entity_id": _feature(
                "yes" if scenario["has_stable_entity_id_in_mutation_gold"] else "no",
                f"mutation entity id fields: {scenario['mutation_entity_id_fields']}",
            ),
            "observable_pre_refresh_binding": _feature(
                "yes" if scenario["entity_selection_milestone_indices"] else "no",
                f"selection milestones: {scenario['entity_selection_milestone_indices']}",
            ),
            "independent_post_binding_transition": _feature(
                "yes" if scenario["has_external_or_user_side_transition"] else "no",
                "audit field has_external_or_user_side_transition",
            ),
            "competing_same_role_entity": _feature(
                "yes" if scenario["has_competing_selector_winner"] else "no",
                "audit field has_competing_selector_winner",
            ),
            "changed_selector_winner": _feature(
                "yes" if scenario["has_competing_selector_winner"] else "no",
                "no frozen refreshed-winner contrast in ToolSandbox audit",
            ),
            "old_entity_remains_actionable": _feature(
                "partial" if scenario["tri_like_eligible"] else "no",
                scenario["classification_note"],
            ),
            "later_target_mutation": _feature(
                "yes" if scenario["entity_mutation_milestone_indices"] else "no",
                f"mutation milestones: {scenario['entity_mutation_milestone_indices']}",
            ),
            "evaluable_authorized_target": _feature(
                "yes" if scenario["entity_mutation_milestone_indices"] else "no",
                "official milestone target is available only for mutation rows",
            ),
        }
        rows.append(
            _base_record(
                f"toolsandbox-{name}",
                "ToolSandbox",
                "stratified_official_audit",
                "reports/official_toolsandbox_tri_prevalence_audit.json",
                source_sha,
                name,
                {
                    "classification": scenario["classification"],
                    "official_user_task": scenario["official_user_task"],
                    "tool_allow_list": scenario["tool_allow_list"],
                    "classification_note": scenario["classification_note"],
                },
                features,
            )
        )
    return rows


def _appworld_records(root: Path) -> list[dict[str, Any]]:
    path = root / "reports" / "appworld_public_trace_tri_audit.json"
    report = load_json(path)
    source_sha = sha256_path(path)
    rows = []
    selected = [
        row
        for row in report["trajectories"]
        if row["post_binding_opportunities"] or row["comment_operation_count"] or row["assigned_wrong_count"]
    ][:12]
    if not selected:
        selected = report["trajectories"][:6]
    for index, item in enumerate(selected, start=1):
        features = {
            "stable_entity_id": _feature("yes", "Todoist task IDs persist across assignment/comment audit"),
            "observable_pre_refresh_binding": _feature(
                "yes" if item["assignment_operation_count"] else "partial",
                f"assignment operations: {item['assignment_operation_count']}",
            ),
            "independent_post_binding_transition": _feature(
                "no",
                "assignment is agent-induced in the released trace, not an exogenous refresh",
            ),
            "competing_same_role_entity": _feature(
                "partial",
                "other Todoist tasks exist but no controlled competing-winner intervention is exposed",
            ),
            "changed_selector_winner": _feature(
                "partial" if item["assignment_operation_count"] else "no",
                "assigned-to-me membership can change, but no replacement winner is measured",
            ),
            "old_entity_remains_actionable": _feature(
                "yes" if item["post_binding_opportunities"] else "partial",
                f"post-binding opportunities: {item['post_binding_opportunities']}",
            ),
            "later_target_mutation": _feature(
                "yes" if item["comment_operation_count"] else "no",
                f"comment operations: {item['comment_operation_count']}",
            ),
            "evaluable_authorized_target": _feature("yes", "official expected task IDs are available"),
        }
        rows.append(
            _base_record(
                f"appworld-{item['experiment']}-{item['task_id']}-{index}",
                "AppWorld",
                "released_trace_sample",
                "reports/appworld_public_trace_tri_audit.json",
                source_sha,
                f"{item['experiment']}::{item['task_id']}",
                {
                    "instruction": item["instruction"],
                    "assignment_operation_count": item["assignment_operation_count"],
                    "comment_operation_count": item["comment_operation_count"],
                    "post_binding_opportunities": item["post_binding_opportunities"],
                    "post_binding_substitutions": item["post_binding_substitutions"],
                },
                features,
            )
        )
    return rows


def _tau3_records(root: Path) -> list[dict[str, Any]]:
    path = root / "reports" / "official_tau3_native_tri_audit.json"
    report = load_json(path)
    source_sha = sha256_path(path)
    rows = []
    for domain, info in sorted(report["domains"].items()):
        features = {
            "stable_entity_id": _feature(
                "yes" if info["tasks_with_user_mutation_carrying_stable_entity_id"] else "no",
                f"user mutations carrying stable ID: {info['tasks_with_user_mutation_carrying_stable_entity_id']}",
            ),
            "observable_pre_refresh_binding": _feature(
                "partial" if domain == "telecom" else "no",
                "telecom has bill identification near-matches but no scored same-role commitment",
            ),
            "independent_post_binding_transition": _feature(
                "yes" if info["tasks_with_user_evaluation_mutation"] else "no",
                f"user-evaluation mutations: {info['tasks_with_user_evaluation_mutation']}",
            ),
            "competing_same_role_entity": _feature("no", "audit found no competing same-role candidate"),
            "changed_selector_winner": _feature("no", "audit found no same-role selector flip"),
            "old_entity_remains_actionable": _feature("no", "near-match changes role from bill to line"),
            "later_target_mutation": _feature(
                "no" if domain == "telecom" else "no",
                "later resume_line is not a mutation of the bound bill",
            ),
            "evaluable_authorized_target": _feature(
                "partial" if domain == "telecom" else "no",
                "actions are scored, but not a same-role referent transition",
            ),
        }
        rows.append(
            _base_record(
                f"tau3-{domain}",
                "tau3-bench",
                "domain_summary",
                "reports/official_tau3_native_tri_audit.json",
                source_sha,
                domain,
                {
                    "tasks": info["tasks"],
                    "tasks_with_user_evaluation_mutation": info["tasks_with_user_evaluation_mutation"],
                    "near_match_interpretation": report["natural_stateful_near_matches"]["interpretation"],
                },
                features,
            )
        )
    return rows


def _external_candidate_features(row: dict[str, Any]) -> dict[str, dict[str, str]]:
    strict = row["strict_fields"]
    stable = "yes" if row.get("stable_id_keys") else "no"
    return {
        "stable_entity_id": _feature(stable, f"stable id keys: {row.get('stable_id_keys', [])}"),
        "observable_pre_refresh_binding": _feature(
            "yes" if row.get("query_before_mutation") else "no",
            "query-before-mutation structural detector",
        ),
        "independent_post_binding_transition": _feature(
            "partial" if row.get("native_update_language") else "no",
            f"native update language: {row.get('native_update_language')}",
        ),
        "competing_same_role_entity": _feature(
            "yes" if row.get("eligible_classes") else "no",
            f"eligible executable classes: {row.get('eligible_classes', [])}",
        ),
        "changed_selector_winner": _feature(
            "yes" if strict.get("distinct_refreshed_winner") else "no",
            "strict audit field distinct_refreshed_winner",
        ),
        "old_entity_remains_actionable": _feature(
            "yes" if strict.get("old_target_action_valid_after_refresh") else "no",
            "strict audit field old_target_action_valid_after_refresh",
        ),
        "later_target_mutation": _feature(
            "yes" if row.get("tool_sequence") and any("API." in name or "api." in name for name in row["tool_sequence"]) else "partial",
            f"tool sequence: {row.get('tool_sequence', [])}",
        ),
        "evaluable_authorized_target": _feature(
            "yes" if strict.get("target_level_outcome_observable") else "no",
            "strict audit field target_level_outcome_observable",
        ),
    }


def _external_records(root: Path) -> list[dict[str, Any]]:
    path = root / "data" / "external_public_opportunity_candidates_v1.jsonl"
    rows = load_jsonl(path)
    source_sha = sha256_path(path)
    selected: list[dict[str, Any]] = []
    for dataset in ("API-Bank", "BFCL", "ToolTalk"):
        subset = [row for row in rows if row["dataset"] == dataset]
        high = [
            row for row in subset
            if row.get("source_anchored_eligible")
            or row.get("timing_label") != "absent"
            or row.get("native_update_language")
        ]
        selected.extend(high[:18])
        selected.extend(subset[:4])
    dedup: dict[str, dict[str, Any]] = {}
    for row in selected:
        dedup.setdefault(f"{row['dataset']}::{row['unit_id']}", row)
    output = []
    for key, row in sorted(dedup.items()):
        suite = row["dataset"]
        output.append(
            _base_record(
                f"external-{suite.lower().replace('-', '')}-{row['unit_id']}",
                suite,
                "external_structural_candidate",
                "data/external_public_opportunity_candidates_v1.jsonl",
                source_sha,
                str(row["unit_id"]),
                {
                    "cluster_id": row["cluster_id"],
                    "source_path": row["source_path"],
                    "eligibility_basis": row["eligibility_basis"],
                    "timing_label": row.get("timing_label"),
                    "tool_sequence": row.get("tool_sequence", []),
                },
                _external_candidate_features(row),
            )
        )
    return output


def _injected_control_records(root: Path) -> list[dict[str, Any]]:
    checklist = root / "reports" / "benchmark_coverage_checklist.json"
    structural = root / "reports" / "external_public_opportunity_audit_v1.json"
    controls = build_controls(checklist, structural)
    source_sha = sha256_bytes(("\n".join(canonical_json(row) for row in controls) + "\n").encode("utf-8"))
    rows = []
    for row in controls:
        features = {
            name: _feature("yes" if value else "no", "known-label injected control")
            for name, value in row["features"].items()
        }
        observed = strict_label(row["features"])
        rows.append(
            _base_record(
                f"control-{row['control_id']}",
                row["suite"],
                "injected_control",
                "generated from tri.public_audit_sensitivity.build_controls",
                source_sha,
                row["control_id"],
                {
                    "control_kind": row["control_kind"],
                    "expected_strict": row["expected_strict"],
                    "observed_strict": observed,
                    "missing_feature": row.get("missing_feature"),
                },
                features,
            )
        )
    return rows


def build_triage_rows(root: Path, include_controls: bool = True) -> list[dict[str, Any]]:
    rows = []
    rows.extend(_closest_case_records(root))
    rows.extend(_toolsandbox_records(root))
    rows.extend(_appworld_records(root))
    rows.extend(_tau3_records(root))
    rows.extend(_external_records(root))
    if include_controls:
        rows.extend(_injected_control_records(root))
    ids = [row["record_id"] for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = [key for key, value in Counter(ids).items() if value > 1]
        raise ValueError(f"duplicate triage ids: {duplicates}")
    return rows


def build_report(root: Path, rows: list[dict[str, Any]], output_jsonl: Path) -> dict[str, Any]:
    natural = [row for row in rows if row["source_kind"] != "injected_control"]
    controls = [row for row in rows if row["source_kind"] == "injected_control"]
    by_suite = {}
    for suite in SUITES:
        subset = [row for row in natural if row["suite"] == suite]
        by_suite[suite] = {
            "natural_records": len(subset),
            "highest_priority": sum(row["review_priority"] == "highest" for row in subset),
            "high_priority": sum(row["review_priority"] == "high" for row in subset),
            "candidate_strict": sum(row["candidate_strict"] for row in subset),
        }
    priority_queue = [
        {
            "record_id": row["record_id"],
            "suite": row["suite"],
            "case_id": row["case_id"],
            "source_kind": row["source_kind"],
            "review_priority": row["review_priority"],
            "candidate_strict": row["candidate_strict"],
            "missing_or_partial_features": [
                name
                for name in FEATURES
                if row["candidate_labels"][name]["status"] != "yes"
            ],
        }
        for row in natural
        if row["review_priority"] in {"highest", "high"}
    ]
    try:
        triage_jsonl = str(output_jsonl.relative_to(root))
    except ValueError:
        triage_jsonl = str(output_jsonl)
    return {
        "report_version": TRIAGE_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "decision": "MODEL-ASSISTED TRIAGE ONLY / NOT INDEPENDENT CALIBRATION",
        "created_for": "rapid reviewer-facing recall sensitivity and human review queue",
        "prompt_sha256": hashlib.sha256(PROMPT_TEXT.encode("utf-8")).hexdigest(),
        "triage_jsonl": triage_jsonl,
        "triage_jsonl_sha256": sha256_path(output_jsonl),
        "natural_records": len(natural),
        "injected_controls": len(controls),
        "natural_candidate_strict": sum(row["candidate_strict"] for row in natural),
        "control_strict_positive_recall": {
            "numerator": sum(row["candidate_strict"] for row in controls if row["source_excerpt"]["expected_strict"]),
            "denominator": sum(1 for row in controls if row["source_excerpt"]["expected_strict"]),
        },
        "control_hard_negative_exclusion": {
            "numerator": sum(
                not row["candidate_strict"]
                for row in controls
                if not row["source_excerpt"]["expected_strict"]
            ),
            "denominator": sum(1 for row in controls if not row["source_excerpt"]["expected_strict"]),
        },
        "by_suite": by_suite,
        "priority_queue": priority_queue,
        "boundary": (
            "These candidate labels are produced from existing frozen audits and structured source excerpts. "
            "They can prioritize human review and probe whether the deterministic audit missed obvious "
            "near cases, but they cannot be reported as independent human recall calibration or as a "
            "new public benchmark result."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Model-Assisted Public Recall Triage",
        "",
        f"**Decision:** {report['decision']}.",
        "",
        f"Natural records triaged: {report['natural_records']}.",
        f"Injected controls: {report['injected_controls']}.",
        f"Natural candidate strict opportunities: {report['natural_candidate_strict']}.",
        "",
        "## Suite Summary",
        "",
        "| Suite | Natural records | Highest | High | Candidate strict |",
        "|---|---:|---:|---:|---:|",
    ]
    for suite, row in report["by_suite"].items():
        lines.append(
            f"| {suite} | {row['natural_records']} | {row['highest_priority']} | "
            f"{row['high_priority']} | {row['candidate_strict']} |"
        )
    pos = report["control_strict_positive_recall"]
    neg = report["control_hard_negative_exclusion"]
    lines.extend(
        [
            "",
            "## Injected Controls",
            "",
            f"- Strict-positive controls recovered: {pos['numerator']}/{pos['denominator']}.",
            f"- One-feature-missing controls excluded: {neg['numerator']}/{neg['denominator']}.",
            "",
            "## Human Review Queue",
            "",
            "| Record | Suite | Case | Priority | Candidate strict | Missing or partial features |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for item in report["priority_queue"][:80]:
        missing = ", ".join(item["missing_or_partial_features"]) or "none"
        lines.append(
            f"| `{item['record_id']}` | {item['suite']} | `{item['case_id']}` | "
            f"{item['review_priority']} | {item['candidate_strict']} | {missing} |"
        )
    lines.extend(["", "## Boundary", "", report["boundary"], ""])
    return "\n".join(lines)
