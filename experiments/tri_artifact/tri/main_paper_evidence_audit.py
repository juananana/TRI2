"""Rebuild and cross-check the manuscript's critical evidence chain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .identifiability_regimes import load_jsonl, summarize
from .v7_leave_group_out import RUNS
from .v7_shared_eligible_pairacc import shared_eligible


ROOT = Path(__file__).resolve().parents[1]


def default_paper_path(root: Path = ROOT) -> Path:
    """Locate the manuscript in either the archive or development layout."""
    archive_path = root / "paper" / "AnonymousSubmission2027.tex"
    repository_path = root.parents[1] / "paper" / "AnonymousSubmission2027.tex"
    return archive_path if archive_path.is_file() else repository_path


PAPER = default_paper_path()

EXTERNAL_EXTENSION_REPORTS = (
    "toolsandbox_single_turn_qwen_full_history_full_v1.json",
    "toolsandbox_single_turn_glm_full_history_full_v1.json",
    "toolsandbox_single_turn_matched_generic_qwen_full_v1.json",
    "toolsandbox_single_turn_matched_generic_glm_full_v1.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_audit_rows(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    reports = [
        load_json(root / "reports/v7_write_audit.json"),
        load_json(root / "reports/v7_deepseek_write_audit_v1.json"),
    ]
    rows = {}
    for report in reports:
        for row in report["summary"]:
            rows[(row["model"], row["controller"])] = row
    return rows


def v7_rows(root: Path, paper_text: str) -> list[dict[str, Any]]:
    writes = write_audit_rows(root)
    output = []
    for model, (generic_name, cta_name) in RUNS.items():
        generic_rows = load_jsonl(root / "runs" / generic_name)
        cta_rows = load_jsonl(root / "runs" / cta_name)
        shared = shared_eligible(generic_rows, cta_rows)
        for label, rows, write_controller in (
            ("Generic", generic_rows, "generic_structured_ledger_then_act"),
            ("CTA", cta_rows, "compile_then_act"),
        ):
            summary = summarize(rows)
            pair = summary["changed_pairacc"]
            conditional = summary["conditional_changed_winner"]
            write = writes[(model, write_controller)]
            paper_model = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM"}.get(model, model)
            paper_controller = label
            latex_row = (
                f"{paper_model} / {paper_controller} & {pair['both_correct']}/{pair['pairs']} & "
                f"{conditional['drift_to_refreshed_winner']}/{conditional['eligible']} & "
                f"{write['core_tri_writes']}/{write['all_wrong_writes']} \\\\"
            )
            output.append(
                {
                    "model": model,
                    "controller": label,
                    "pairacc": [pair["both_correct"], pair["pairs"]],
                    "conditional_substitution": [
                        conditional["drift_to_refreshed_winner"],
                        conditional["eligible"],
                    ],
                    "core_substitution_writes": write["core_tri_writes"],
                    "all_wrong_writes": write["all_wrong_writes"],
                    "shared_eligible": shared["eligible"],
                    "shared_generic_substitutions": shared["generic_substitutions"],
                    "shared_cta_substitutions": shared["cta_substitutions"],
                    "latex_row": latex_row,
                    "latex_row_present": latex_row in paper_text,
                }
            )
    return output


def primary_summary(root: Path) -> dict[str, Any]:
    output = {}
    for model, name in (
        ("Qwen3.5", "v3_qwen_language_cluster.json"),
        ("GLM-5.1", "v3_glm_language_cluster.json"),
    ):
        report = load_json(root / "reports" / name)
        generic = next(row for row in report["runs"] if row["mode"] == "generic_structured_ledger_then_act")
        gated = next(row for row in report["runs"] if row["mode"] == "factorized_hybrid_compile_then_act")
        pair = report["pairs"][0]
        output[model] = {
            "generic_accuracy": generic["task_accuracy"],
            "gated_accuracy": gated["task_accuracy"],
            "delta": pair["delta_b_minus_a"],
            "cluster_bootstrap_ci95": [
                pair["cluster_bootstrap_ci95_low"],
                pair["cluster_bootstrap_ci95_high"],
            ],
        }
    return output


def external_extension_summary(root: Path) -> list[dict[str, Any]]:
    output = []
    for name in EXTERNAL_EXTENSION_REPORTS:
        report = load_json(root / "reports" / name)
        output.append(
            {
                "report": name,
                "rows": report["inventory"]["rows"],
                "opportunities": sum(cell["tri_opportunities"] for cell in report["cells"]),
                "mechanism_errors": sum(
                    cell["unauthorized_rebindings"] + cell["premature_locks"]
                    for cell in report["cells"]
                ),
                "wrong_writes": sum(cell["wrong_entity_writes"] for cell in report["cells"]),
            }
        )
    return output


def build_report(root: Path = ROOT, paper_path: Path = PAPER) -> dict[str, Any]:
    paper_text = paper_path.read_text(encoding="utf-8")
    normalized_paper = " ".join(paper_text.split())
    supplement_text = (paper_path.parent / "supplementary_material.tex").read_text(encoding="utf-8")
    rows = v7_rows(root, paper_text)
    primary = primary_summary(root)
    human = load_json(root / "human_validation/analysis.json")["groups"]
    coverage = load_json(root / "reports/public_suite_coverage_funnel_v1.json")
    external_extension = external_extension_summary(root)
    selection_regret = load_json(root / "reports/evaluation_selection_regret_v1.json")
    selection_summary = selection_regret["summary"]
    call_matched = load_json(root / "reports/call_matched_authorization_ablation_v2.json")
    call_models = {row["model"]: row for row in call_matched["models"]}
    call_qwen = call_models["Qwen/Qwen3.5-122B-A10B"]
    call_glm = call_models["Pro/zai-org/GLM-5.1"]
    revision_full = load_json(root / "reports/revision_full_diagnostic_v2.json")
    revision_models = {row["model"]: row for row in revision_full["models"]}
    revision_qwen = revision_models["Qwen/Qwen3.5-122B-A10B"]
    revision_glm = revision_models["Pro/zai-org/GLM-5.1"]
    revision_source = load_json(root / "reports/revision_source_grounded_v2.json")
    revision_source_models = {row["model"]: row for row in revision_source["models"]}
    source_qwen = revision_source_models["Qwen/Qwen3.5-122B-A10B"]
    source_glm = revision_source_models["Pro/zai-org/GLM-5.1"]
    source_deepseek = revision_source_models["deepseek-ai/DeepSeek-V4-Pro"]
    binding_drift = load_json(root / "reports/binding_drift_tri_glm_v7_full_v1.json")
    binding_summaries = binding_drift["summaries"]
    rule_residual = load_json(root / "reports/rule_hard_residual_v1.json")
    source_transfer = load_json(root / "reports/source_anchored_external_transfer_v1.json")
    source_cells = source_transfer["conditional_cells_by_repository_model_controller"]
    qwen_history_agentdojo = source_cells[
        "AgentDojo | Qwen/Qwen3.5-122B-A10B | ordinary_full_history"
    ]

    figure_paths = [
        paper_path.parent / "Figures" / "fig_resolution_policy_phase_space_compact.pdf",
        paper_path.parent / "Figures" / "fig_shared_eligible_target_flow_compact.pdf",
        paper_path.parent / "Figures" / "fig_wrong_write_decomposition_compact.pdf",
        paper_path.parent / "Figures" / "fig_source_model_transfer_fingerprints_compact.pdf",
        paper_path.parent / "Figures" / "fig_decision_visibility_effect_sizes_compact.pdf",
        paper_path.parent / "Figures" / "fig_enforcement_repairs_harms_compact.pdf",
    ]
    checks = {
        "split_result_figures_match_frozen_sources": (
            all(path.is_file() for path in figure_paths)
            and "Figures/fig_resolution_policy_phase_space_singlecolumn.pdf" in paper_text
            and "Figures/fig_controller_transition.pdf" in paper_text
            and "Figures/fig_wrong_write_decomposition_compact.pdf" in paper_text
            and "Figures/fig_source_model_transfer_fingerprints_compact.pdf" in supplement_text
            and "Figures/fig_decision_visibility_effect_sizes_compact.pdf" in paper_text
            and "Figures/fig_enforcement_repairs_harms_compact.pdf" in supplement_text
            and "Figures/tri_comprehensive_results.pdf" in supplement_text
            and "Post-primary audits from frozen \\PrimaryDiagnostic{} and \\NewSchemaReplication{} outputs" in supplement_text
            and "Policy marginals and matched discrimination" in paper_text
            and "Cross-schema paired controller transitions" in paper_text
            and "Wrong-target writes under fixed-executor replay" in paper_text
            and "Decision-visible minus History-only effects" in paper_text
            and "Source-derived controlled-contrast fingerprints" in supplement_text
            and "Row-level repairs and harms" in supplement_text
            and all(token in paper_text for token in ("43/72", "38/80", "59/79", "41/66", "30/70", "50/69"))
            and all(
                row["core_substitution_writes"] == row["conditional_substitution"][0]
                for row in rows
                if row["controller"] == "Generic"
            )
        ),
        "shared_qwen_claim_present": "41/66 versus 0/66" in paper_text,
        "shared_glm_claim_present": "30/70 versus 0/70" in paper_text,
        "shared_deepseek_claim_present": "50/69 versus 0/69" in paper_text,
        "qwen_primary_claim_present": all(
            token in paper_text
            for token in ("95/128", "125/128", "74.2\\%", "97.7\\%")
        ),
        "glm_primary_claim_present": all(
            token in paper_text for token in ("93/128", "127/128", "72.7\\%", "99.2\\%", "100.0\\%")
        ),
        "human_agreement_claim_present": (
            "Fleiss' $\\kappa=.708$" in paper_text
            and "Krippendorff's $\\alpha=.709$" in paper_text
        ),
        "coverage_scope_present": (
            "ToolSandbox (129 families)" in paper_text
            and "AppWorld (244 families)" in paper_text
            and "$\\tau^3$-Bench (2,449 tasks" in paper_text
        ),
        "external_extension_four_condition_scope_matches_sources": (
            len(external_extension) == 4
            and [row["rows"] for row in external_extension] == [96, 96, 96, 96]
            and [row["opportunities"] for row in external_extension] == [70, 73, 64, 87]
            and [row["mechanism_errors"] for row in external_extension] == [0, 0, 0, 0]
            and [row["wrong_writes"] for row in external_extension] == [6, 13, 5, 4]
            and "four-condition, 96-task extension" in normalized_paper
            and "64--87 eligible opportunities" in paper_text
        ),
        "source_anchored_transfer_claim_matches_report": (
            source_transfer["unique_rows"] == 320
            and source_transfer["valid_rows"] == 306
            and source_transfer["parse_or_schema_failures"] == 14
            and source_transfer["changed_condition"]["preserve_unauthorized_substitutions"] == 2
            and source_transfer["changed_condition"]["preserve_changed_rows"] == 64
            and source_transfer["changed_by_repository"]["STATE-Bench"]["preserve_unauthorized_substitutions"] == 0
            and source_transfer["changed_by_repository"]["STATE-Bench"]["preserve_changed_rows"] == 34
            and qwen_history_agentdojo["preserve_changed_to_refreshed_winner"] == 2
            and qwen_history_agentdojo["preserve_changed_rows"] == 7
            and qwen_history_agentdojo["preserve_stable_exact"] == 7
            and qwen_history_agentdojo["preserve_stable_rows"] == 7
            and "2/7 eligible AgentDojo" in paper_text
            and "0/7 matched Stable" in paper_text
            and "connect the controlled" in paper_text
            and "diagnostic to source\ninterfaces" in paper_text
        ),
        "selection_regret_claim_matches_report": (
            selection_summary["proxy_evaluations"] == 20
            and selection_summary["one_sided_or_stable_evaluations"] == 15
            and selection_summary["one_sided_or_stable_zero_pairacc_rows"] == 15
            and selection_summary["aggregate_suboptimal_rows"] == 0
            and selection_summary["aggregate_pairacc_optimal_rows"] == 5
            and abs(selection_summary["maximum_worst_case_selection_regret"] - 1.0) < 1e-12
            and "all 15 maximizer sets under Stable-only or one-sided scoring contain a zero-PairAcc policy" in normalized_paper
            and "worst-case PairAcc regret of 100 points" in normalized_paper
            and "Aggregate end-to-end (E2E) scoring selects a PairAcc-optimal candidate in all five candidate sets" in normalized_paper
        ),
        "call_matched_claim_matches_report": (
            call_matched["report_version"] == "TRI-call-matched-authorization-ablation-report-v2"
            and call_qwen["rows"] == 80
            and call_glm["rows"] == 80
            and call_qwen["metrics"]["history_only"]["changed_pairacc"]["count"] == 12
            and call_qwen["metrics"]["decision_visible"]["changed_pairacc"]["count"] == 20
            and call_glm["metrics"]["history_only"]["changed_pairacc"]["count"] == 12
            and call_glm["metrics"]["decision_visible"]["changed_pairacc"]["count"] == 24
            and call_qwen["metrics"]["history_only"]["preserve_conditional_substitution"]["numerator"] == 16
            and call_qwen["metrics"]["history_only"]["preserve_conditional_substitution"]["denominator"] == 28
            and call_qwen["metrics"]["decision_visible"]["preserve_conditional_substitution"]["numerator"] == 4
            and call_glm["metrics"]["history_only"]["preserve_conditional_substitution"]["numerator"] == 12
            and call_glm["metrics"]["history_only"]["preserve_conditional_substitution"]["denominator"] == 24
            and call_glm["metrics"]["decision_visible"]["preserve_conditional_substitution"]["numerator"] == 0
            and call_qwen["enforcement"]["harms"] == 8
            and call_qwen["enforcement"]["repairs"] == 4
            and call_glm["enforcement"]["changed"] == 0
            and revision_full["report_version"] == "TRI-revision-matched-audit-report-v2"
            and revision_qwen["rows"] == 160
            and revision_glm["rows"] == 160
            and revision_qwen["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 5
            and revision_qwen["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 13
            and revision_glm["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 8
            and revision_glm["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 25
            and revision_qwen["metrics"]["history_only"]["preserve_substitution"]["numerator"] == 22
            and revision_qwen["metrics"]["history_only"]["preserve_substitution"]["denominator"] == 28
            and revision_qwen["metrics"]["decision_visible"]["preserve_substitution"]["numerator"] == 13
            and revision_glm["metrics"]["history_only"]["preserve_substitution"]["numerator"] == 16
            and revision_glm["metrics"]["history_only"]["preserve_substitution"]["denominator"] == 25
            and revision_glm["metrics"]["decision_visible"]["preserve_substitution"]["numerator"] == 0
            and revision_qwen["enforcement"] == {"repairs": 18, "harms": 8}
            and revision_glm["enforcement"] == {"repairs": 4, "harms": 0}
            and all(
                token in normalized_paper
                for token in (
                    "5/32 to 13/32 for Qwen",
                    "8/32 to 25/32 for GLM",
                    "22/28 to 13/28",
                    "16/25 to 0/25",
                    "PairAcc to 24/32, with 18 repairs and eight row-level harms",
                )
            )
        ),
        "source_grounded_matched_claim_matches_report": (
            revision_source["report_version"] == "TRI-revision-matched-audit-report-v2"
            and revision_source["evidence_status"] == "post-primary; protocol frozen before own calls"
            and all(model["rows"] == 60 for model in revision_source["models"])
            and all(model["logical_calls"]["completed"] == 180 for model in revision_source["models"])
            and source_qwen["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 12
            and source_qwen["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 13
            and source_glm["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 11
            and source_glm["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 20
            and source_deepseek["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 19
            and source_deepseek["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 22
            and source_qwen["metrics"]["history_only"]["preserve_substitution"]["numerator"] == 7
            and source_qwen["metrics"]["decision_visible"]["preserve_substitution"]["numerator"] == 7
            and source_glm["metrics"]["history_only"]["preserve_substitution"]["numerator"] == 10
            and source_glm["metrics"]["decision_visible"]["preserve_substitution"]["numerator"] == 1
            and source_deepseek["metrics"]["history_only"]["preserve_substitution"]["numerator"] == 6
            and source_deepseek["metrics"]["decision_visible"]["preserve_substitution"]["numerator"] == 2
            and source_qwen["metrics"]["history_only"]["fixed_executor_wrong_writes"]["numerator"] == 16
            and source_qwen["metrics"]["decision_visible"]["fixed_executor_wrong_writes"]["numerator"] == 17
            and source_glm["metrics"]["history_only"]["fixed_executor_wrong_writes"]["numerator"] == 16
            and source_glm["metrics"]["decision_visible"]["fixed_executor_wrong_writes"]["numerator"] == 5
            and source_deepseek["metrics"]["history_only"]["fixed_executor_wrong_writes"]["numerator"] == 11
            and source_deepseek["metrics"]["decision_visible"]["fixed_executor_wrong_writes"]["numerator"] == 9
            and all(
                token in normalized_paper
                for token in (
                    "12/30 to 13/30 for Qwen",
                    "11/30 to 20/30",
                    "19/30 to 22/30",
                    "unchanged at 7/26",
                    "10/30 to 1/30",
                    "6/27 to 2/27",
                    "16 to 17, 16 to 5, and 11 to 9",
                    "controlled interventions over source-derived states and schemas",
                    "public-suite audit below",
                )
            )
        ),
        "binding_drift_author_adaptation_matches_report": (
            binding_drift["status"] == "post_primary_author_adaptation"
            and binding_drift["n_tasks"] == 240
            and binding_drift["interpretation_gate"] == "complementary_policy_result"
            and binding_summaries["entity_lock_analogue"]["correct"] == 160
            and binding_summaries["entity_lock_analogue"]["anchored"]["correct"] == 120
            and binding_summaries["entity_lock_analogue"]["dynamic"]["correct"] == 40
            and binding_summaries["entity_lock_analogue"]["paired_authorization"]["both_correct"] == 40
            and binding_summaries["glm_self_reverify_author_adaptation"]["correct"] == 155
            and binding_summaries["glm_self_reverify_author_adaptation"]["anchored"]["correct"] == 39
            and binding_summaries["glm_self_reverify_author_adaptation"]["dynamic"]["correct"] == 116
            and binding_summaries["glm_self_reverify_author_adaptation"]["paired_authorization"]["both_correct"] == 38
            and binding_summaries["exact_cta_frozen"]["correct"] == 226
            and binding_summaries["exact_cta_frozen"]["paired_authorization"]["both_correct"] == 106
            and binding_drift["post_run_information_audit"]["status"] == "not_information_matched_to_cta"
            and all(
                token in normalized_paper
                for token in (
                    "\\cite{babu2026bindingdrift}",
                    "Entity lock favors Preserve and self-reverification favors Reevaluate",
                    "without $S_0$ or the pre-refresh bound",
                    "not an official reproduction or an information-matched performance comparison",
                )
            )
            and "tab:supp-binding-drift-adaptation" in supplement_text
        ),
        "rule_hard_residual_matches_report": (
            rule_residual["status"] == "post_hoc_residual_audit_zero_api"
            and rule_residual["rule_hard_rows"] == 20
            and rule_residual["preserve_rows"] == 10
            and rule_residual["reevaluate_rows"] == 10
            and rule_residual["complete_rule_hard_pairs"] == 0
            and rule_residual["results"]["Qwen / Timing-reminder"]["correct"] == 13
            and rule_residual["results"]["Qwen / CTA"]["correct"] == 13
            and rule_residual["results"]["GLM / Timing-reminder"]["correct"] == 20
            and rule_residual["results"]["GLM / CTA"]["correct"] == 20
            and rule_residual["results"]["DeepSeek / Timing-reminder"]["correct"] == 18
            and rule_residual["results"]["DeepSeek / CTA"]["correct"] == 16
            and "The residual and component analyses are supplementary" in paper_text
            and "tab:supp-rule-hard-residual" in supplement_text
        ),
        "generic_core_writes_equal_conditional_substitutions": all(
            row["core_substitution_writes"] == row["conditional_substitution"][0]
            for row in rows
            if row["controller"] == "Generic"
        ),
        "cta_core_writes_zero_but_all_wrong_reported": all(
            row["core_substitution_writes"] == 0 and row["all_wrong_writes"] > 0
            for row in rows
            if row["controller"] == "CTA"
        ),
    }
    try:
        displayed_paper_path = paper_path.relative_to(root)
    except ValueError:
        displayed_paper_path = paper_path.relative_to(root.parents[1])
    return {
        "status": "zero-API audit rebuilt from frozen outputs and source reports",
        "paper": str(displayed_paper_path),
        "v7_diagnostic_table": rows,
        "v3_primary": primary,
        "human_validation": {
            "n": human["all"]["n_items"],
            "fleiss_kappa": human["all"]["fleiss_kappa"],
            "krippendorff_alpha": human["all"]["krippendorff_alpha_nominal"],
            "majority_gold_accuracy": human["all"]["majority_gold_accuracy"],
            "reject_majority_gold_accuracy": human["anchored_reject"]["majority_gold_accuracy"],
        },
        "public_coverage": coverage["suites"],
        "external_extension": external_extension,
        "source_anchored_external_transfer": {
            "rows": source_transfer["unique_rows"],
            "valid": source_transfer["valid_rows"],
            "preserve_changed_substitutions": [
                source_transfer["changed_condition"]["preserve_unauthorized_substitutions"],
                source_transfer["changed_condition"]["preserve_changed_rows"],
            ],
            "state_bench_substitutions": [
                source_transfer["changed_by_repository"]["STATE-Bench"]["preserve_unauthorized_substitutions"],
                source_transfer["changed_by_repository"]["STATE-Bench"]["preserve_changed_rows"],
            ],
        },
        "selection_regret": selection_summary,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "boundaries": [
            "The audit checks numerical and provenance consistency, not natural prevalence.",
            "Human and public-suite classifications retain the limitations stated in the paper.",
            "Provider inference cannot be reproduced exactly because immutable serving revisions are unavailable.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Main-Paper Evidence Audit",
        "",
        f"**Status:** {report['status']}.",
        "",
        "| Check | Pass |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {name.replace('_', ' ')} | {'yes' if passed else 'NO'} |"
        for name, passed in report["checks"].items()
    )
    lines.extend(
        [
            "",
            "| Model/controller | PairAcc | Conditional substitution | Core writes | All wrong writes | Shared G/CTA |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["v7_diagnostic_table"]:
        pair = row["pairacc"]
        conditional = row["conditional_substitution"]
        lines.append(
            f"| {row['model']} / {row['controller']} | {pair[0]}/{pair[1]} | "
            f"{conditional[0]}/{conditional[1]} | {row['core_substitution_writes']} | "
            f"{row['all_wrong_writes']} | {row['shared_generic_substitutions']}/"
            f"{row['shared_cta_substitutions']} of {row['shared_eligible']} |"
        )
    lines.extend(
        [
            "",
            "| 96-task paper-facing condition | Rows | Opportunities | Mechanism errors | Wrong writes |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["external_extension"]:
        lines.append(
            f"| {row['report']} | {row['rows']} | {row['opportunities']} | "
            f"{row['mechanism_errors']} | {row['wrong_writes']} |"
        )
    lines.extend(["", *[f"- {item}" for item in report["boundaries"]], ""])
    return "\n".join(lines)


def validate(report: dict[str, Any]) -> None:
    failed = [name for name, passed in report["checks"].items() if not passed]
    if failed:
        raise ValueError(f"main-paper evidence audit failed: {', '.join(failed)}")
