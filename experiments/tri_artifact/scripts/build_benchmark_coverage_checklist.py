from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))


def cell(status: str, evidence: str) -> dict[str, str]:
    return {"status": status, "evidence": evidence}


def build_report() -> dict[str, Any]:
    toolsandbox = load("official_toolsandbox_tri_prevalence_audit.json")
    appworld = load("appworld_public_trace_tri_audit.json")
    tau3 = load("official_tau3_native_tri_audit.json")
    assert toolsandbox["strict_tri_eligible_count"] == 0
    assert toolsandbox["tri_like_eligible_count"] == 1
    assert appworld["strict_exogenous_tri_opportunity_count"] == 0
    assert appworld["combined"]["post_binding_opportunities"] == 16
    assert tau3["strict_native_tri_opportunities_after_manual_semantic_audit"] == 0

    return {
        "scope": (
            "Feature audit of each benchmark's closest released natural near-match, not a claim "
            "that every task in the benchmark has the marked feature. 'Partial' means the trace "
            "has a related structure but not the strict same-role controlled condition."
        ),
        "strict_condition": (
            "All features are required to estimate conditional TRI on an observable, correctly "
            "bound target. No audited public benchmark contains a strict native opportunity."
        ),
        "benchmarks": [
            {
                "benchmark": "ToolSandbox",
                "closest_case": "update_contact_relationship_with_relationship_twice_multiple_user_turn",
                "inventory": "129 semantic families; 0 strict; 1 TRI-like",
                "source": "reports/official_toolsandbox_tri_prevalence_audit.json",
                "features": {
                    "stable_entity_id": cell("yes", "mutation gold exposes person_id"),
                    "observable_pre_refresh_binding": cell("yes", "search_contacts precedes mutation"),
                    "independent_post_binding_transition": cell("no", "first mutation is the requested agent action, not exogenous"),
                    "competing_same_role_entity": cell("no", "reviewed case introduces no competing friend"),
                    "changed_selector_winner": cell("no", "no replacement selector winner or Flip control"),
                    "old_entity_remains_actionable": cell("yes", "same person_ids are legally changed back"),
                    "later_target_mutation": cell("yes", "second modify_contact mutation targets the prior IDs"),
                    "evaluable_authorized_target": cell("yes", "official mutation gold exposes target person_ids"),
                },
            },
            {
                "benchmark": "AppWorld",
                "closest_case": "generator family 8ce6779",
                "inventory": "244 generator families; 0 strict; 1 TRI-like family",
                "source": "reports/appworld_public_trace_tri_audit.json",
                "features": {
                    "stable_entity_id": cell("yes", "Todoist task IDs persist across assignment and comment"),
                    "observable_pre_refresh_binding": cell("yes", "correct assignment operations expose 16 bound IDs"),
                    "independent_post_binding_transition": cell("no", "assignment is agent-induced; no scheduled external refresh"),
                    "competing_same_role_entity": cell("partial", "other tasks exist, but no controlled competing-winner intervention"),
                    "changed_selector_winner": cell("partial", "old tasks leave assigned-to-me selector; no measured replacement winner"),
                    "old_entity_remains_actionable": cell("yes", "the same IDs accept later comments"),
                    "later_target_mutation": cell("yes", "16 comments follow correct assignments"),
                    "evaluable_authorized_target": cell("yes", "official expected task IDs permit same-ID scoring"),
                },
            },
            {
                "benchmark": "tau3-bench",
                "closest_case": "8 telecom overdue-payment/resume-line definitions",
                "inventory": "2,449 tasks; 0 strict; 8 dual-control near-matches",
                "source": "reports/official_tau3_native_tri_audit.json",
                "features": {
                    "stable_entity_id": cell("no", "user-side mutation carries no bill/line stable ID"),
                    "observable_pre_refresh_binding": cell("partial", "agent identifies a bill, but no scored same-role commitment"),
                    "independent_post_binding_transition": cell("yes", "user pays through a user-side tool"),
                    "competing_same_role_entity": cell("no", "no competing bill or line selector candidate"),
                    "changed_selector_winner": cell("no", "no same-role selector flip"),
                    "old_entity_remains_actionable": cell("no", "subsequent action targets a different role: line, not bill"),
                    "later_target_mutation": cell("no", "resume_line is not a later mutation of the bound bill"),
                    "evaluable_authorized_target": cell("partial", "actions are scored, but not a same-role referent transition"),
                },
            },
        ],
        "interpretation": (
            "Missing strict opportunities can make a benchmark unable to measure TRI. It does "
            "not imply that TRI is common in deployed traffic or absent from agents."
        ),
    }


LABELS = {
    "stable_entity_id": "Stable ID",
    "observable_pre_refresh_binding": "Observed prior binding",
    "independent_post_binding_transition": "Independent transition",
    "competing_same_role_entity": "Competing same-role entity",
    "changed_selector_winner": "Changed winner",
    "old_entity_remains_actionable": "Old remains actionable",
    "later_target_mutation": "Later mutation",
    "evaluable_authorized_target": "Scorable authorized target",
}


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Public-Benchmark TRI Coverage Checklist",
        "",
        report["scope"],
        "",
        "| Strict feature | ToolSandbox | AppWorld | tau3-bench |",
        "|---|---|---|---|",
    ]
    by_name = {row["benchmark"]: row for row in report["benchmarks"]}
    for key, label in LABELS.items():
        lines.append(
            f"| {label} | {by_name['ToolSandbox']['features'][key]['status']} | "
            f"{by_name['AppWorld']['features'][key]['status']} | "
            f"{by_name['tau3-bench']['features'][key]['status']} |"
        )
    lines.extend(["", "## Evidence", ""])
    for row in report["benchmarks"]:
        lines.append(f"### {row['benchmark']}")
        lines.append("")
        lines.append(f"Closest case: `{row['closest_case']}`. {row['inventory']}.")
        lines.append("")
        for key, label in LABELS.items():
            item = row["features"][key]
            lines.append(f"- {label} ({item['status']}): {item['evidence']}.")
        lines.extend(["", f"Source: `{row['source']}`.", ""])
    lines.extend([report["interpretation"], ""])
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    output = ROOT / "reports/benchmark_coverage_checklist.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
