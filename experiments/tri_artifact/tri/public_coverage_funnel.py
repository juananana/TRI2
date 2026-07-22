from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load(root: Path, name: str) -> dict[str, Any]:
    return json.loads((root / "reports" / name).read_text(encoding="utf-8"))


def build_report(root: Path) -> dict[str, Any]:
    """Build a descriptive funnel from the three already-completed source audits."""
    toolsandbox = _load(root, "official_toolsandbox_tri_prevalence_audit.json")
    appworld = _load(root, "appworld_public_trace_tri_audit.json")
    tau3 = _load(root, "official_tau3_native_tri_audit.json")

    excluded = toolsandbox["classification_counts"]
    total = toolsandbox["semantic_scenario_family_count"]
    after_mutation = total - excluded["excluded_no_entity_mutation"]
    after_transition = after_mutation - excluded["excluded_no_intervening_transition"]
    after_binding = after_transition - excluded["excluded_no_prior_entity_selection"]
    after_stable_id = after_binding - excluded["excluded_no_stable_mutation_id"]

    assert after_stable_id == toolsandbox["tri_like_eligible_count"]
    assert toolsandbox["strict_tri_eligible_count"] == 0
    assert appworld["strict_exogenous_tri_opportunity_count"] == 0
    assert tau3["strict_native_tri_opportunities_after_manual_semantic_audit"] == 0

    return {
        "study": "source-derived public-suite TRI coverage funnel",
        "status": "post-primary/descriptive; zero API; not an independent recall audit",
        "scope": (
            "This report summarizes existing official ToolSandbox, AppWorld, and tau3-bench "
            "audits. It makes their exclusion paths visible but does not establish candidate "
            "retrieval recall, inter-annotator agreement, or coverage outside the pinned versions."
        ),
        "suites": [
            {
                "benchmark": "ToolSandbox",
                "source": "reports/official_toolsandbox_tri_prevalence_audit.json",
                "unit": "semantic scenario families",
                "funnel": [
                    {"stage": "audited families", "count": total},
                    {"stage": "after entity-mutation exclusion", "count": after_mutation},
                    {"stage": "after independent-transition exclusion", "count": after_transition},
                    {"stage": "after prior-selection exclusion", "count": after_binding},
                    {"stage": "TRI-like after stable-ID exclusion", "count": after_stable_id},
                    {"stage": "strict native opportunities", "count": 0},
                ],
                "near_match_count": toolsandbox["tri_like_eligible_count"],
                "note": (
                    "These are sequential classification buckets from the source audit, not "
                    "independently measured marginal feature prevalences."
                ),
            },
            {
                "benchmark": "AppWorld",
                "source": "reports/appworld_public_trace_tri_audit.json",
                "unit": "generator families and released trajectories",
                "funnel": [
                    {"stage": "audited generator families", "count": appworld["public_generator_family_count"]},
                    {"stage": "TRI-like generator families", "count": appworld["tri_like_generator_family_count"]},
                    {"stage": "strict exogenous opportunities", "count": 0},
                    {"stage": "released trajectories in near-match family", "count": appworld["combined"]["released_trajectory_count"]},
                    {"stage": "observable post-binding operations", "count": appworld["combined"]["post_binding_opportunities"]},
                    {"stage": "observed post-binding substitutions", "count": appworld["combined"]["post_binding_substitutions"]},
                ],
                "near_match_count": appworld["tri_like_generator_family_count"],
                "note": (
                    "The released-trace rows describe an action-induced preservation near-match, "
                    "not an exogenous selector-flip TRI denominator."
                ),
            },
            {
                "benchmark": "tau3-bench",
                "source": "reports/official_tau3_native_tri_audit.json",
                "unit": "core task definitions",
                "funnel": [
                    {"stage": "audited tasks", "count": tau3["total_tasks"]},
                    {
                        "stage": "tasks with user-evaluation mutation",
                        "count": sum(domain["tasks_with_user_evaluation_mutation"] for domain in tau3["domains"].values()),
                    },
                    {
                        "stage": "tasks with stable ID in user mutation",
                        "count": sum(domain["tasks_with_user_mutation_carrying_stable_entity_id"] for domain in tau3["domains"].values()),
                    },
                    {
                        "stage": "metadata strict candidates",
                        "count": sum(domain["metadata_strict_candidates_before_manual_audit"] for domain in tau3["domains"].values()),
                    },
                    {"stage": "strict native opportunities", "count": 0},
                ],
                "near_match_count": tau3["natural_stateful_near_matches"]["telecom_overdue_payment_then_resume_line_tasks"],
                "note": (
                    "The listed near-matches use different bill and line roles, so they do not "
                    "provide a same-role target-transition comparison."
                ),
            },
        ],
        "interpretation": (
            "The funnel supports a scoped coverage statement for three pinned benchmark versions. "
            "It does not estimate deployed prevalence and does not replace the planned independent "
            "candidate-recall and double-review audit."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Public-Suite TRI Coverage Funnel",
        "",
        "**Status:** post-primary/descriptive; zero API; not an independent recall audit.",
        "",
        report["scope"],
        "",
    ]
    for suite in report["suites"]:
        lines.extend([f"## {suite['benchmark']}", "", f"Unit: {suite['unit']}.", ""])
        lines.extend(["| Stage | Count |", "|---|---:|"])
        lines.extend(f"| {row['stage']} | {row['count']} |" for row in suite["funnel"])
        lines.extend(["", f"Near-match count: {suite['near_match_count']}.", "", suite["note"], ""])
    lines.extend(["## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)
