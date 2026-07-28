from __future__ import annotations

import tempfile
import unittest
import zipfile
import re
from pathlib import Path

from scripts.build_current_supplement import TASK_EMAIL_CONTENT_FILES, build


class CurrentSupplementTest(unittest.TestCase):
    def test_builds_complete_key_free_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "artifact.zip"
            build(output)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                self.assertIn(
                    "tri_artifact/data/temporal_referent_v3_language_clusters.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/external_public_annotation_candidates_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/TRI_external_public_siliconflow_annotation_addendum.md",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/external_public_annotation_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/external_public_annotation_siliconflow_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/source_anchored_external_transfer_tasks_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/source_anchored_external_transfer_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/source_anchored_external_transfer_siliconflow_repaired_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/data/model_authored_linguistic_stress_v1.jsonl",
                    names,
                )
                self.assertIn(
                    "tri_artifact/reports/model_authored_linguistic_stress_transport_repaired_v2.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/model_authored_linguistic_evaluate_glm_cta_full_v1.jsonl",
                    names,
                )
                self.assertIn("tri_artifact/paper/AnonymousSubmission2027.tex", names)
                self.assertIn("tri_artifact/paper/aaai2027.bib", names)
                self.assertIn("tri_artifact/paper/aaai2027.bst", names)
                self.assertIn("tri_artifact/paper/aaai2027.sty", names)
                self.assertIn("tri_artifact/paper/supplementary_material.tex", names)
                self.assertIn(
                    "tri_artifact/paper/source_anchored_external_transfer_table.tex",
                    names,
                )
                for figure in (
                    "fig1_shared_transition.pdf",
                    "fig2_diagnostic_workflow.pdf",
                    "fig2_policy_rulers.pdf",
                    "fig3_substitution_flow.pdf",
                    "fig4_sqlite_outcome_tree.pdf",
                    "fig5_paired_transfer_matrix.pdf",
                    "fig_s2_changed_calibration_round5.pdf",
                    "fig_s8_external_boundary_round5.pdf",
                    "fig4_wrong_write_mirror_round3.pdf",
                    "fig_source_model_transfer_fingerprints_compact.pdf",
                    "fig_enforcement_repairs_harms_compact.pdf",
                ):
                    self.assertIn(f"tri_artifact/paper/Figures/{figure}", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round4_figure1.py", names)
                self.assertIn(
                    "tri_artifact/paper/figure_source/plot_fig2_diagnostic_workflow.mjs",
                    names,
                )
                self.assertIn("tri_artifact/paper/figure_source/plot_round4_figures.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round5_figures.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round5_supplement.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round6_figures.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round7_figures.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round8_figures.py", names)
                self.assertIn("tri_artifact/paper/figure_source/plot_round10_figures.py", names)
                self.assertIn(
                    "tri_artifact/paper/figure_source/plot_submission_critical_effects.py", names
                )
                for required in (
                    "tri_artifact/reports/TRI_end_to_end_decision_decomposition_protocol.md",
                    "tri_artifact/reports/TRI_end_to_end_decision_decomposition_runbook.md",
                    "tri_artifact/scripts/run_end_to_end_decision_decomposition.py",
                    "tri_artifact/scripts/report_end_to_end_decision_decomposition.py",
                    "tri_artifact/tri/end_to_end_decision_decomposition.py",
                    "tri_artifact/tests/test_end_to_end_decision_decomposition.py",
                    "tri_artifact/reports/TRI_end_to_end_decision_decomposition_v2_protocol.md",
                    "tri_artifact/scripts/run_end_to_end_decision_decomposition_v2.py",
                    "tri_artifact/scripts/report_end_to_end_decision_decomposition_v2.py",
                    "tri_artifact/tri/end_to_end_decision_decomposition_v2.py",
                    "tri_artifact/tests/test_end_to_end_decision_decomposition_v2.py",
                    "tri_artifact/reports/TRI_independent_language_holdout_protocol.md",
                    "tri_artifact/scripts/freeze_independent_holdout_model_experiment.py",
                    "tri_artifact/scripts/report_independent_holdout_model_experiment.py",
                    "tri_artifact/scripts/run_independent_holdout_model_experiment.py",
                    "tri_artifact/tri/independent_holdout_model_experiment.py",
                    "tri_artifact/tests/test_independent_holdout_model_experiment.py",
                    "tri_artifact/reports/TRI_deployment_evaluation_decision_protocol.md",
                    "tri_artifact/reports/TRI_unified_environment_holdout_protocol.md",
                    "tri_artifact/scripts/freeze_unified_environment_holdout.py",
                    "tri_artifact/scripts/report_controller_selection.py",
                    "tri_artifact/scripts/build_unified_environment_forms.py",
                    "tri_artifact/tri/unified_environment_holdout.py",
                    "tri_artifact/tests/test_unified_environment_holdout.py",
                    "tri_artifact/reports/TRI_public_recall_calibrated_audit_protocol.md",
                    "tri_artifact/scripts/build_public_recall_calibrated_frame.py",
                    "tri_artifact/scripts/report_public_recall_calibrated_audit.py",
                    "tri_artifact/tri/public_recall_calibrated_audit.py",
                    "tri_artifact/tests/test_public_recall_calibrated_audit.py",
                    "tri_artifact/reports/TRI_submission_critical_replication_addendum_20260728.md",
                    "tri_artifact/reports/TRI_submission_critical_execution_runbook.md",
                    "tri_artifact/tri/convention_told_control.py",
                    "tri_artifact/scripts/run_convention_told_control.py",
                    "tri_artifact/scripts/report_convention_told_control.py",
                    "tri_artifact/tests/test_convention_told_control.py",
                    "tri_artifact/tri/revision_repeat_stability.py",
                    "tri_artifact/scripts/report_revision_repeat_stability.py",
                    "tri_artifact/tests/test_revision_repeat_stability.py",
                    "tri_artifact/scripts/run_submission_critical_matrix.py",
                    "tri_artifact/scripts/run_toolsandbox_null_repeat.py",
                    "tri_artifact/scripts/build_submission_critical_paper_assets.py",
                ):
                    self.assertIn(required, names)
                self.assertIn(
                    "tri_artifact/reports/decision_block_stratification_v1.json", names
                )
                self.assertIn(
                    "tri_artifact/reports/TRI_end_to_end_decision_decomposition_protocol.md",
                    names,
                )
                self.assertFalse(
                    any(
                        name.endswith("end_to_end_decision_decomposition_qwen_smoke_v1.jsonl")
                        or name.endswith("end_to_end_decision_decomposition_glm_smoke_v1.jsonl")
                        or name.endswith(
                            "end_to_end_decision_decomposition_glm_smoke_network_v1.jsonl"
                        )
                        for name in names
                    )
                )
                self.assertIn(
                    "tri_artifact/paper/figure_source/data/summary_csv/revision_decision_visible_gains.csv",
                    names,
                )
                self.assertIn(
                    "tri_artifact/paper/figure_source/data/summary_csv/sqlite_model_facing_outcomes.csv",
                    names,
                )
                self.assertIn(
                    "tri_artifact/human_validation/normalized_returns/annotator_1.csv",
                    names,
                )
                self.assertIn("tri_artifact/human_validation/analysis.json", names)
                self.assertFalse(any("annotation_key_private" in name for name in names))
                self.assertFalse(any("private_returns" in name for name in names))
                self.assertFalse(any(name.endswith(".xlsx") for name in names))
                self.assertFalse(any("TRI_AAAI" in name for name in names))
                self.assertFalse(
                    any(name.startswith("tri_artifact/reports/figures/") for name in names)
                )
                self.assertFalse(
                    any(name.startswith("tri_artifact/reports/submission_summary/") for name in names)
                )
                self.assertFalse(
                    any(
                        name.startswith("tri_artifact/reports/FIGURE_")
                        or name.startswith("tri_artifact/reports/FINAL_DELIVERY")
                        or name.startswith("tri_artifact/reports/NEW_FIGURES")
                        for name in names
                    )
                )
                self.assertIn(
                    "tri_artifact/reports/binding_drift_tri_glm_v7_full_v1.json",
                    names,
                )
                self.assertIn(
                    "tri_artifact/runs/binding_drift_tri_glm_self_reverify_v7_full_v1.jsonl",
                    names,
                )
                self.assertFalse(
                    any(
                        name.startswith("tri_artifact/external_pilots/appworld_runtime/")
                        for name in names
                    )
                )
                self.assertFalse(
                    any(name.startswith("tri_artifact/runs/") and archive.getinfo(name).file_size == 0 for name in names)
                )
                normalized = archive.read(
                    "tri_artifact/human_validation/normalized_returns/annotator_2.csv"
                ).decode()
                self.assertNotIn("comment", normalized.splitlines()[0])
                rewrites = archive.read(
                    "tri_artifact/human_validation/paraphrase_authoring.csv"
                ).decode()
                self.assertNotIn("author_notes", rewrites.splitlines()[0])
                for name in names:
                    if not name.endswith("/"):
                        data = archive.read(name)
                        self.assertIsNone(re.search(rb"sk-[A-Za-z0-9_-]{20,}", data))
                        self.assertIsNone(
                            re.search(rb"(?i)Bearer\s+[A-Za-z0-9._-]{20,}", data)
                        )
                        relative = Path(name).relative_to("tri_artifact")
                        if relative not in TASK_EMAIL_CONTENT_FILES:
                            self.assertIsNone(
                                re.search(
                                    rb"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
                                    data,
                                )
                            )
                        self.assertNotIn(b"/Users/", data)


if __name__ == "__main__":
    unittest.main()
