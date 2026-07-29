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
    generated_dir = paper_path.parent / "generated"
    generated_text = "\n".join(
        path.read_text(encoding="utf-8") for path in generated_dir.glob("*.tex")
    ) if generated_dir.is_dir() else ""
    searchable_paper = paper_text + "\n" + generated_text
    normalized_paper = " ".join(searchable_paper.split())
    supplement_text = (paper_path.parent / "supplementary_material.tex").read_text(encoding="utf-8")
    normalized_supplement = " ".join(supplement_text.split())
    rows = v7_rows(root, paper_text)
    primary = primary_summary(root)
    human = load_json(root / "human_validation/analysis.json")["groups"]
    coverage = load_json(root / "reports/public_suite_coverage_funnel_v1.json")
    external_extension = external_extension_summary(root)
    selection_regret = load_json(root / "reports/evaluation_selection_regret_v1.json")
    selection_summary = selection_regret["summary"]
    call_matched = load_json(root / "reports/call_matched_authorization_ablation_v2.json")
    decision_block = load_json(root / "reports/decision_block_stratification_v1.json")
    decision_pooled = decision_block["interface_redundancy_pooled"]
    decision_qwen = decision_block["authored_stratification"]["Qwen"]
    decision_glm = decision_block["authored_stratification"]["GLM"]
    call_models = {row["model"]: row for row in call_matched["models"]}
    call_qwen = call_models["Qwen/Qwen3.5-122B-A10B"]
    call_glm = call_models["Pro/zai-org/GLM-5.1"]
    revision_full = load_json(root / "reports/revision_full_diagnostic_v3.json")
    revision_models = {row["model"]: row for row in revision_full["models"]}
    revision_qwen = revision_models["Qwen/Qwen3.5-122B-A10B"]
    revision_glm = revision_models["Pro/zai-org/GLM-5.1"]
    revision_source = load_json(root / "reports/revision_source_grounded_v3.json")
    revision_source_models = {row["model"]: row for row in revision_source["models"]}
    source_qwen = revision_source_models["Qwen/Qwen3.5-122B-A10B"]
    source_glm = revision_source_models["Pro/zai-org/GLM-5.1"]
    source_deepseek = revision_source_models["deepseek-ai/DeepSeek-V4-Pro"]
    revision_four = load_json(root / "reports/revision_full_diagnostic_four_model_v2.json")
    revision_four_models = {row["model"]: row for row in revision_four["models"]}
    binding_drift = load_json(root / "reports/binding_drift_tri_glm_v7_full_v1.json")
    binding_summaries = binding_drift["summaries"]
    rule_residual = load_json(root / "reports/rule_hard_residual_v1.json")
    source_transfer = load_json(root / "reports/source_anchored_external_transfer_v1.json")
    source_cells = source_transfer["conditional_cells_by_repository_model_controller"]
    qwen_history_agentdojo = source_cells[
        "AgentDojo | Qwen/Qwen3.5-122B-A10B | ordinary_full_history"
    ]
    oracle_qwen_primary = load_json(root / "reports/v3_oracle_qwen_primary.json")["counts"]
    oracle_glm_primary = load_json(root / "reports/v3_oracle_glm_primary.json")["counts"]
    oracle_qwen_unseen = load_json(root / "reports/v3_oracle_qwen_unseen.json")["counts"]
    repeat_stability = load_json(root / "reports/v7_repeat_stability_v1.json")
    repeat_models = {row["model"]: row for row in repeat_stability["models"]}
    repeat_qwen = repeat_models["Qwen3.5"]
    repeat_glm = repeat_models["GLM-5.1"]
    full_history = load_json(root / "reports/v7_matched_full_history_three_model_final_v1.json")
    full_history_pairs = {
        (row["model"], row["controller_a"], row["controller_b"]): row
        for row in full_history["pairs"]
    }
    full_history_cta = {
        model: full_history_pairs[(model, "full_history_once", "compile_then_act")]
        for model in ("Qwen3.5", "GLM-5.1", "DeepSeek")
    }

    figure_paths = [
        paper_path.parent / "Figures" / "fig1_shared_transition.pdf",
        paper_path.parent / "Figures" / "fig2_diagnostic_workflow.pdf",
        paper_path.parent / "Figures" / "result_policy_discrimination.pdf",
        paper_path.parent / "Figures" / "fig3_substitution_flow.pdf",
        paper_path.parent / "Figures" / "fig4_sqlite_outcome_tree.pdf",
        paper_path.parent / "Figures" / "fig_submission_critical_pairacc_effects.pdf",
        paper_path.parent / "Figures" / "fig_s2_changed_calibration_round5.pdf",
        paper_path.parent / "Figures" / "fig_s8_external_boundary_round5.pdf",
        paper_path.parent / "Figures" / "fig4_wrong_write_mirror_round3.pdf",
        paper_path.parent / "Figures" / "fig_source_model_transfer_fingerprints_compact.pdf",
        paper_path.parent / "Figures" / "fig_enforcement_repairs_harms_compact.pdf",
    ]
    checks = {
        "split_result_figures_match_frozen_sources": (
            all(path.is_file() for path in figure_paths)
            and "Figures/fig1_shared_transition.pdf" in paper_text
            and "Figures/fig2_diagnostic_workflow.pdf" in paper_text
            and "Figures/result_policy_discrimination.pdf" in paper_text
            and "Figures/fig3_substitution_flow.pdf" in paper_text
            and "Figures/fig4_sqlite_outcome_tree.pdf" in paper_text
            and (
                "Figures/result_decision_transfer.pdf" in paper_text
                or "Figures/fig_submission_critical_pairacc_effects.pdf" in normalized_paper
            )
            and "Figures/fig4_sqlite_outcome_tree.pdf" in supplement_text
            and "Figures/fig4_wrong_write_mirror_round3.pdf" in supplement_text
            and "Figures/fig_source_model_transfer_fingerprints_compact.pdf" in supplement_text
            and "Figures/fig_s2_changed_calibration_round5.pdf" in supplement_text
            and "Figures/fig_s8_external_boundary_round5.pdf" in supplement_text
            and "Figures/fig_enforcement_repairs_harms_compact.pdf" in supplement_text
            and "Figures/tri_comprehensive_results.pdf" in supplement_text
            and "Post-primary audits from frozen \\PrimaryDiagnostic{} and \\NewSchemaReplication{} outputs" in supplement_text
            and "Evidence boundary. Each row separates the completed evidence from the strongest"
            in supplement_text
            and "TRI diagnostic construction and observable endpoints" in normalized_paper
            and "it is an evaluation workflow, not a controller architecture" in normalized_paper
            and "Figures/fig2_policy_rulers.pdf" not in paper_text
            and "Figures/fig5_paired_transfer_matrix.pdf" not in paper_text
            and (
                "Ten-schema conditional outcomes after correct initial binding" in normalized_paper
                or "Ten-schema outcomes after correct initial binding" in normalized_paper
            )
            and (
                "Strict SQLite opportunities for Generic after correct pre-refresh binding to A"
                in normalized_paper
                or "Secondary/frozen SQLite consequence test for Generic" in normalized_paper
                or "Secondary/frozen 40-task SQLite outcomes for Generic" in normalized_paper
                or "Complete 40-task SQLite outcomes and strict refreshed-winner writes for Generic"
                in normalized_paper
            )
            and "Source-derived controlled-contrast fingerprints" in supplement_text
            and "Row-level repairs and harms" in supplement_text
            and all(token in paper_text for token in ("41/66", "30/70", "50/69", "8/8", "6/8"))
            and all(
                row["core_substitution_writes"] == row["conditional_substitution"][0]
                for row in rows
                if row["controller"] == "Generic"
            )
        ),
        "shared_qwen_claim_present": "41/66" in paper_text and "CTA substitutes on none" in normalized_paper,
        "shared_glm_claim_present": "30/70" in paper_text and "CTA substitutes on none" in normalized_paper,
        "shared_deepseek_claim_present": "50/69" in paper_text and "CTA substitutes on none" in normalized_paper,
        "qwen_primary_claim_present": all(
            token in paper_text
            for token in (
                "103/160",
                "157/160",
                "+33.8 points",
                "[18.1, 50.0]",
                "Qwen Lifecycle-Gated reaches 125/128 versus Generic 95/128",
            )
        ),
        "glm_primary_claim_present": all(
            token in paper_text
            for token in (
                "115/160",
                "160/160",
                "+28.1 points",
                "[18.1, 38.1]",
                "GLM CTA reaches 128/128 versus Generic",
                "93/128",
            )
        ),
        "human_agreement_claim_present": (
            "majority--gold agreement is 98.0\\% on 50 dynamic items" in normalized_paper
            and "86.7\\% on 30 anchored actionable items" in normalized_paper
            and "55.0\\% on 20 action-invalid \\textsc{Reject} items" in normalized_paper
            and "We therefore center actionable referent identity and treat fallback policy separately"
            in normalized_paper
            and "All & 100 & 86.0 & 72.0 & .708 & .709" in supplement_text
            and "Blinded Human Agreement Audit" in supplement_text
            and "Post-primary descriptive construct audit" in supplement_text
            and "human construct evidence" not in normalized_paper
            and "Blind Human Construct Validation" not in supplement_text
        ),
        "replication_structure_and_denominator_present": all(
            token in normalized_paper
            for token in (
                "40 state clusters across ten schemas",
                "two reference modes crossed with Stable, Flip, and name-collision transitions",
                "yielding 80 changed pairs",
                "PairAcc denominator of 80",
            )
        ),
        "coverage_scope_present": (
            "no case meeting all eligibility conditions in six public benchmarks"
            in normalized_paper
        ),
        "external_extension_four_condition_scope_matches_sources": (
            len(external_extension) == 4
            and [row["rows"] for row in external_extension] == [96, 96, 96, 96]
            and [row["opportunities"] for row in external_extension] == [70, 73, 64, 87]
            and [row["mechanism_errors"] for row in external_extension] == [0, 0, 0, 0]
            and [row["wrong_writes"] for row in external_extension] == [6, 13, 5, 4]
            and "finds zero substitutions in four Qwen/GLM controller conditions over 64--87 eligible rows each"
            in normalized_paper
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
            and "2/7 changed rows" in normalized_paper
            and "0/7 matched Stable" in normalized_paper
            and "no method consistently improves execution accuracy" in normalized_paper
        ),
        "selection_regret_claim_matches_report": (
            selection_summary["proxy_evaluations"] == 20
            and selection_summary["one_sided_or_stable_evaluations"] == 15
            and selection_summary["one_sided_or_stable_zero_pairacc_rows"] == 15
            and selection_summary["aggregate_suboptimal_rows"] == 0
            and selection_summary["aggregate_pairacc_optimal_rows"] == 5
            and abs(selection_summary["maximum_worst_case_selection_regret"] - 1.0) < 1e-12
            and "Across five tested controller candidate sets, aggregate E2E and PairAcc choose the same policy; there is no ranking reversal"
            in normalized_paper
            and "All 15" in normalized_supplement
            and "Maximum worst-case regret is 100 points" in normalized_supplement
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
            and revision_full["report_version"] == "TRI-revision-matched-audit-report-v3"
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
                    "PairAcc rises from 5/32 to 13/32 for Qwen and from 8/32 to 25/32 for GLM",
                    "estimates the complete block rather than any field",
                    "RQ3: Does Decision Visibility Change Outcomes under Equal Calls?",
                    "using the same base payloads, states, tool schemas, and call count",
                    "The visible block jointly contains the predicted reference mode, bound ID, and selector restatement",
                    "Decision-enforced applies it offline",
                    "No predeclared field-level contrast met the cross-model promotion gate",
                    "supported intervention remains composite rather than attributable to one field",
                )
            )
            and "Qwen & History-only & 5/32 & 100/128 & 21/32 & 22/28" in supplement_text
            and "Qwen & Decision-visible & 13/32 & 106/128 & 25/32 & 13/28" in supplement_text
            and "GLM & History-only & 8/32 & 102/128 & 11/32 & 16/25" in supplement_text
            and "GLM & Decision-visible & 25/32 & 120/128 & 21/32 & 0/25" in supplement_text
            and "Offline enforcement produces 18 repairs and eight harms for Qwen"
            in normalized_supplement
        ),
        "four_model_pairacc_interval_repair_matches_report": (
            revision_four["report_version"] == "TRI-revision-matched-audit-report-v3"
            and len(revision_four["report_amendments"]) == 2
            and revision_four_models["Qwen/Qwen3.5-122B-A10B"]
            ["decision_visible_minus_history"]["changed_pairacc"]["ci95_cluster"]
            == [0.09375, 0.40625]
            and revision_four_models["Pro/zai-org/GLM-5.1"]
            ["decision_visible_minus_history"]["changed_pairacc"]["ci95_cluster"]
            == [0.34375, 0.6875]
            and revision_four_models["deepseek-ai/DeepSeek-V4-Pro"]
            ["decision_visible_minus_history"]["changed_pairacc"]["ci95_cluster"]
            == [0.25, 0.625]
            and revision_four_models["Pro/MiniMaxAI/MiniMax-M2.5"]
            ["decision_visible_minus_history"]["changed_pairacc"]["ci95_cluster"]
            == [0.1875, 0.5]
            and all(
                token in generated_text
                for token in (
                    "+25.0 [9.4,40.6]",
                    "+53.1 [34.4,68.8]",
                    "+43.8 [25.0,62.5]",
                    "+34.4 [18.8,50.0]",
                    "pair-cluster-resampling 95\\% CIs",
                )
            )
        ),
        "decision_block_stratification_matches_report": (
            decision_block["evidence_status"] == "post-primary zero-API descriptive audit"
            and decision_pooled["rows"] == 760
            and all(
                value["numerator"] == 760 and value["denominator"] == 760
                for value in decision_pooled["checks"].values()
            )
            and decision_qwen["by_compiler_mode_correctness"]["correct"]["exact_target"]
            ["history_only"]["numerator"] == 105
            and decision_qwen["by_compiler_mode_correctness"]["correct"]["exact_target"]
            ["decision_visible"]["numerator"] == 119
            and decision_qwen["by_compiler_mode_correctness"]["wrong"]["exact_target"]
            ["history_only"]["numerator"] == 16
            and decision_qwen["by_compiler_mode_correctness"]["wrong"]["exact_target"]
            ["decision_visible"]["numerator"] == 12
            and decision_glm["by_compiler_mode_correctness"]["correct"]["exact_target"]
            ["history_only"]["numerator"] == 110
            and decision_glm["by_compiler_mode_correctness"]["correct"]["exact_target"]
            ["decision_visible"]["numerator"] == 136
            and (
                "Across nine audited matched-call inventories, both actors receive the same initial ID"
                in normalized_paper
                or "initial-ID values are exact repetitions in 760/760 audited records" in normalized_paper
            )
            and "Compiler-output strata are supplementary and descriptive" in normalized_paper
            and "Qwen & Mode correct & 137 & 105 & 119 & 16 / 2" in supplement_text
            and "GLM & Preserve ID correct & 61 & 32 & 57 & 25 / 0" in supplement_text
            and "post-treatment stratum" in normalized_supplement
        ),
        "oracle_stage_decomposition_matches_report": (
            oracle_qwen_primary["mode_correct"] == 160
            and oracle_qwen_primary["bound_id_correct_on_preserve"] == 80
            and oracle_glm_primary["mode_correct"] == 160
            and oracle_glm_primary["bound_id_correct_on_preserve"] == 80
            and oracle_qwen_unseen["mode_correct"] == 80
            and oracle_qwen_unseen["bound_id_correct_on_preserve"] == 21
            and oracle_qwen_unseen["learned_gated_correct"] == 66
            and oracle_qwen_unseen["learned_mode_oracle_id_correct"] == 78
            and oracle_qwen_unseen["oracle_mode_learned_id_correct"] == 66
            and all(
                token in normalized_paper
                for token in (
                    "Qwen mode is 80/80 but the Preserve bound ID is 21/40",
                    "Replacing the ID raises gated accuracy from 66/80 to 78/80",
                    "replacing mode does not",
                    "In this Qwen 80-row stress set, the remaining loss is concentrated in selector grounding",
                )
            )
            and "mode accuracy and Preserve bound-ID accuracy are 160/160 and 80/80"
            in normalized_supplement
        ),
        "temperature_zero_repeat_matches_report": (
            repeat_stability["decision"] == "mixed"
            and repeat_stability["expected_tasks"] == 40
            and [round(100 * row["cta_minus_generic"], 1) for row in repeat_qwen["paired"]]
            == [25.0, 12.5, 22.5]
            and [round(100 * row["cta_minus_generic"], 1) for row in repeat_glm["paired"]]
            == [30.0, 20.0, 25.0]
            and [
                (row["core_drifts"], row["core_opportunities"])
                for row in repeat_qwen["controllers"]["generic"]["runs"]
            ] == [(5, 10), (5, 11), (7, 11)]
            and [
                (row["core_drifts"], row["core_opportunities"])
                for row in repeat_glm["controllers"]["generic"]["runs"]
            ] == [(4, 12), (5, 12), (6, 12)]
            and all(
                row["core_drifts"] == 0
                for model in (repeat_qwen, repeat_glm)
                for row in model["controllers"]["cta"]["runs"]
            )
            and all(
                token in normalized_paper
                for token in (
                    "Across three temperature-zero passes, CTA remains above Generic and records no substitutions",
                    "Full results are supplementary",
                )
            )
            and "conditional substitution is 5/10, 5/11, and 7/11 for Qwen and 4/12, 5/12, and 6/12 for GLM"
            in normalized_supplement
        ),
        "full_history_baseline_claim_matches_report": (
            full_history_cta["Qwen3.5"]["delta_b_minus_a"] == 0.0125
            and full_history_cta["Qwen3.5"]["ci95_state_cluster"]
            == [-0.06666666666666667, 0.09166666666666666]
            and full_history_cta["GLM-5.1"]["delta_b_minus_a"] == 0.13333333333333333
            and full_history_cta["GLM-5.1"]["ci95_state_cluster"]
            == [0.0875, 0.17916666666666667]
            and full_history_cta["DeepSeek"]["delta_b_minus_a"] == 0.15416666666666667
            and full_history_cta["DeepSeek"]["ci95_state_cluster"]
            == [0.09166666666666666, 0.21666666666666667]
            and all(
                token in normalized_paper
                for token in (
                    "Against final-step-aware full history on the same 240 rows",
                    "$+1.2$ [$-6.7,9.2$] points for Qwen",
                    "$+13.3$ [$8.8,17.9$] for GLM",
                    "$+15.4$ [$9.2,21.7$] for DeepSeek",
                    "the Qwen interval includes zero",
                )
            )
        ),
        "source_grounded_matched_claim_matches_report": (
            revision_source["report_version"] == "TRI-revision-matched-audit-report-v3"
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
                    ("the Qwen estimate is null, DeepSeek intervals cross zero, and only GLM has an actionable-E2E interval excluding zero"
                     if "the Qwen estimate is null, DeepSeek intervals cross zero, and only GLM has an actionable-E2E interval excluding zero" in normalized_paper
                     else "The 30-pair test uses states and tool schemas from STATE-Bench, AgentDojo, and ToolSandbox"),
                    "The 30-pair test uses states and tool schemas from STATE-Bench, AgentDojo, and ToolSandbox",
                    ("neither native tasks nor prevalence evidence"
                     if "neither native tasks nor prevalence evidence" in normalized_paper
                     else "native behavior, or prevalence"),
                )
            )
            and "Qwen & History-only & 12/30" in supplement_text
            and "GLM & History-only & 11/30" in supplement_text
            and "DeepSeek & History-only & 19/30" in supplement_text
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
                    "neither an official reproduction nor an information-matched CTA baseline",
                    "it receives $S_1$ but neither $S_0$ nor the resolved old ID",
                    "Detailed counts are supplementary",
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
            and "Rule*, written after error inspection" in normalized_paper
            and "15/60 exact targets and 2/30 PairAcc" in normalized_paper
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
        "full_history_cta_deltas": {
            model: {
                "delta": row["delta_b_minus_a"],
                "ci95": row["ci95_state_cluster"],
            }
            for model, row in full_history_cta.items()
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "boundaries": [
            "The audit checks numerical and provenance consistency, not natural prevalence.",
            "Human agreement and public-suite classifications retain the limitations stated in the paper.",
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
