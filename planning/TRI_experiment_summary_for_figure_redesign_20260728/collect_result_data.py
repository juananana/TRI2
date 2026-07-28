from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "data"
BUNDLE_SOURCE = REPO / "experiments/tri_artifact/reports/submission_summary"
BUNDLE_DEST = DATA / "paper_facing_result_bundle"
ADD_DEST = DATA / "additional_result_reports"
MANIFEST = DATA / "result_files_manifest.csv"
SOURCE_DEST = HERE / "sources"


ADDITIONAL_REPORTS = [
    # Primary, component, and identifiability results.
    "experiments/tri_artifact/reports/v3_factorial_qwen_primary_cluster.json",
    "experiments/tri_artifact/reports/v3_factorial_qwen_primary_cluster.md",
    "experiments/tri_artifact/reports/v3_factorial_glm_primary_cluster.json",
    "experiments/tri_artifact/reports/v3_factorial_glm_primary_cluster.md",
    "experiments/tri_artifact/reports/field_ablation.json",
    "experiments/tri_artifact/reports/field_ablation.md",
    "experiments/tri_artifact/reports/v3_referential_policy_slices.json",
    "experiments/tri_artifact/reports/v3_referential_policy_slices.md",
    "experiments/tri_artifact/reports/matched_pair_consistency.json",
    "experiments/tri_artifact/reports/matched_pair_consistency.md",
    "experiments/tri_artifact/reports/policy_extreme_controls.json",
    "experiments/tri_artifact/reports/policy_extreme_controls.md",
    "experiments/tri_artifact/reports/evaluation_selection_regret_v1.json",
    "experiments/tri_artifact/reports/evaluation_selection_regret_v1.md",
    "experiments/tri_artifact/reports/crossed_cluster_sensitivity_v1.json",
    "experiments/tri_artifact/reports/crossed_cluster_sensitivity_v1.md",
    # Current decision-visibility addenda.
    "experiments/tri_artifact/reports/decision_block_stratification_v1.json",
    "experiments/tri_artifact/reports/decision_block_stratification_v1.md",
    # V7, history, write consequences, and stability.
    "experiments/tri_artifact/reports/v7_core_replication.json",
    "experiments/tri_artifact/reports/v7_core_replication.md",
    "experiments/tri_artifact/reports/v7_core_sqlite_replay.json",
    "experiments/tri_artifact/reports/v7_core_sqlite_replay.md",
    "experiments/tri_artifact/reports/v7_matched_full_history_three_model_final_v1.json",
    "experiments/tri_artifact/reports/v7_matched_full_history_three_model_final_v1.md",
    "experiments/tri_artifact/reports/v7_matched_full_history_sqlite_replay_v1.json",
    "experiments/tri_artifact/reports/v7_matched_full_history_sqlite_replay_v1.md",
    "experiments/tri_artifact/reports/v7_leave_group_out_sensitivity_v1.json",
    "experiments/tri_artifact/reports/v7_leave_group_out_sensitivity_v1.md",
    "experiments/tri_artifact/reports/v7_repeat_stability_v1.json",
    "experiments/tri_artifact/reports/v7_repeat_stability_v1.md",
    "experiments/tri_artifact/reports/v3_cluster_sample_sufficiency_v1.json",
    "experiments/tri_artifact/reports/v3_cluster_sample_sufficiency_v1.md",
    "experiments/tri_artifact/reports/v7_cluster_sample_sufficiency_v1.json",
    "experiments/tri_artifact/reports/v7_cluster_sample_sufficiency_v1.md",
    # Schema transfer and method-upgrade boundary.
    "experiments/tri_artifact/reports/v3_qwen_unseen_report.json",
    "experiments/tri_artifact/reports/v3_qwen_unseen_report.md",
    "experiments/tri_artifact/reports/v3_oracle_qwen_unseen.json",
    "experiments/tri_artifact/reports/v3_oracle_qwen_unseen.md",
    "experiments/tri_artifact/reports/method_upgrade_closed_loop_v1.json",
    "experiments/tri_artifact/reports/method_upgrade_closed_loop_v1.md",
    "experiments/tri_artifact/reports/method_upgrade_closed_loop_new_methods_v1.json",
    "experiments/tri_artifact/reports/method_upgrade_closed_loop_new_methods_v1.md",
    # Human aggregate results only; no raw platform exports or annotator files.
    "experiments/tri_artifact/reports/wjx_six_form_human_construct_audit_incomplete_cutoff_v1.json",
    "experiments/tri_artifact/reports/wjx_six_form_human_construct_audit_incomplete_cutoff_v1.md",
    "experiments/tri_artifact/reports/wjx_six_form_human_construct_audit_item_counts_v1.json",
    # External coverage and limited bridge results.
    "experiments/tri_artifact/reports/public_suite_coverage_funnel_v1.json",
    "experiments/tri_artifact/reports/public_suite_coverage_funnel_v1.md",
    "experiments/tri_artifact/reports/external_public_annotation_v1.json",
    "experiments/tri_artifact/reports/external_public_annotation_v1.md",
    "experiments/tri_artifact/reports/model_assisted_public_recall_triage_v1.json",
    "experiments/tri_artifact/reports/model_assisted_public_recall_triage_v1.md",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_qwen_full_history_full_v1.json",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_qwen_full_history_full_v1.md",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_glm_full_history_full_v1.json",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_glm_full_history_full_v1.md",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_matched_generic_qwen_full_v1.json",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_matched_generic_qwen_full_v1.md",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_matched_generic_glm_full_v1.json",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_matched_generic_glm_full_v1.md",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_qwen_generic_state_observed_full_v1.json",
    "experiments/tri_artifact/reports/toolsandbox_single_turn_qwen_generic_state_observed_full_v1.md",
    "experiments/tri_artifact/reports/appworld_naturalistic_v1.json",
    "experiments/tri_artifact/reports/appworld_naturalistic_v1.md",
    # Negative composition.
    "experiments/tri_artifact/reports/v5_qwen_multirefresh_report.json",
    "experiments/tri_artifact/reports/v5_qwen_multirefresh_report.md",
    "experiments/tri_artifact/reports/v6_matched_scalar_role_report.json",
    "experiments/tri_artifact/reports/v6_matched_scalar_role_report.md",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    SOURCE_DEST.mkdir(parents=True, exist_ok=True)
    copy_file(
        REPO / "experiments/tri_artifact/reports/current_claim_provenance.md",
        SOURCE_DEST / "current_claim_provenance.md",
    )
    copy_file(
        REPO / "experiments/tri_artifact/reports/current_experiment_registry.md",
        SOURCE_DEST / "current_experiment_registry.md",
    )
    BUNDLE_DEST.mkdir(parents=True, exist_ok=True)
    copy_file(BUNDLE_SOURCE / "README.md", BUNDLE_DEST / "README.md")
    copy_file(BUNDLE_SOURCE / "manifest.json", BUNDLE_DEST / "manifest.json")
    shutil.copytree(
        BUNDLE_SOURCE / "reports",
        BUNDLE_DEST / "reports",
        dirs_exist_ok=True,
    )

    for relative in ADDITIONAL_REPORTS:
        source = REPO / relative
        copy_file(source, ADD_DEST / source.name)

    manifest_rows: list[dict[str, str | int]] = []
    for path in sorted((BUNDLE_DEST).rglob("*")):
        if path.is_file():
            manifest_rows.append(
                {
                    "collection": "paper_facing_result_bundle",
                    "file": str(path.relative_to(HERE)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "source": str(path.relative_to(BUNDLE_DEST)),
                }
            )
    for relative in ADDITIONAL_REPORTS:
        path = ADD_DEST / Path(relative).name
        manifest_rows.append(
            {
                "collection": "additional_result_reports",
                "file": str(path.relative_to(HERE)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "source": relative,
            }
        )

    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["collection", "file", "bytes", "sha256", "source"],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"collected {len(manifest_rows)} result files; manifest={MANIFEST}")


if __name__ == "__main__":
    main()
