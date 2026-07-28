from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
PAPER = REPOSITORY / "paper"
SUBMISSION = REPOSITORY / "submission"

ROOTS = (
    "data",
    "runs",
    "reports",
    "tri",
    "scripts",
    "tests",
    "external_pilots",
    "human_validation",
)
TOP_LEVEL = ("README.md", "PROTOCOL.md")
PAPER_FILES = (
    "AnonymousSubmission2027.tex",
    "aaai2027.bib",
    "aaai2027.bst",
    "aaai2027.sty",
    "ReproducibilityChecklist.tex",
    "supplementary_material.tex",
    "source_anchored_external_transfer_table.tex",
)
PAPER_FIGURES = (
    "fig1_shared_transition.pdf",
    "fig2_diagnostic_workflow.pdf",
    "fig2_policy_rulers.pdf",
    "fig3_substitution_flow.pdf",
    "fig4_sqlite_outcome_tree.pdf",
    "fig5_paired_transfer_matrix.pdf",
    "fig4_wrong_write_mirror_round3.pdf",
    "fig_enforcement_repairs_harms_compact.pdf",
    "fig_source_model_transfer_fingerprints_compact.pdf",
    "fig_s2_changed_calibration_round5.pdf",
    "tri_call_matched_ablation.pdf",
    "tri_component_audit_dotline.pdf",
    "tri_comprehensive_results.pdf",
    "fig_s8_external_boundary_round5.pdf",
)
FIGURE_SOURCE_ROOT = PAPER / "tri_final_figures"
FIGURE_SOURCE_FILES = (
    "README.md",
    "requirements.txt",
    "plot_fig2_diagnostic_workflow.mjs",
    "plot_round4_figure1.py",
    "plot_round4_figures.py",
    "plot_round5_figures.py",
    "plot_round5_supplement.py",
    "plot_round6_figures.py",
    "plot_round7_figures.py",
    "plot_round8_figures.py",
    "plot_round10_figures.py",
    "plot_submission_critical_effects.py",
    "outputs/fig1_shared_transition_symmetric_v3_editable.pptx",
    "data/summary_csv/matched_pairacc_and_marginals.csv",
    "data/summary_csv/revision_decision_visible_gains.csv",
    "data/summary_csv/revision_enforcement_and_failures.csv",
    "data/summary_csv/revision_source_grounded_by_source.csv",
    "data/summary_csv/v7_e2e_wrong_writes.csv",
    "data/summary_csv/v7_shared_eligible_pairacc_and_substitution.csv",
    "data/summary_csv/sqlite_model_facing_outcomes.csv",
    "data/summary_csv/main_figure_paired_scores.csv",
)

HUMAN_PUBLIC_FILES = {
    Path("human_validation/analysis.json"),
    Path("human_validation/analysis.md"),
    Path("human_validation/model_human_subset.json"),
    Path("human_validation/model_human_subset.md"),
    Path("human_validation/paraphrase_authoring.csv"),
    Path("human_validation/selected_sources.jsonl"),
    Path("human_validation/natural_elicitation_writer_form_zh.csv"),
    Path("human_validation/natural_elicitation_annotator_form_zh.csv"),
}

SECRET_PATTERN = re.compile(rb"sk-[A-Za-z0-9_-]{20,}")
BEARER_PATTERN = re.compile(rb"(?i)Bearer\s+[A-Za-z0-9._-]{20,}")
EMAIL_PATTERN = re.compile(rb"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
LOCAL_HOME_PATTERN = re.compile(rb"/Users/[^/\s\"']+")
TASK_EMAIL_CONTENT_FILES = {
    Path("data/external_public_annotation_candidates_v1.jsonl"),
    Path("data/revision_source_grounded_v1.jsonl"),
    Path("data/source_anchored_external_transfer_tasks_v1.jsonl"),
    Path("runs/revision_source_grounded_deepseek_full_v1.jsonl"),
    Path("runs/revision_source_grounded_deepseek_full_v2.jsonl"),
    Path("runs/revision_source_grounded_glm_full_v1.jsonl"),
    Path("runs/revision_source_grounded_glm_full_v2.jsonl"),
    Path("runs/revision_source_grounded_minimax_full_v2.jsonl"),
    Path("runs/revision_source_grounded_qwen_full_v1.jsonl"),
    Path("runs/revision_source_grounded_qwen_full_v2.jsonl"),
    Path("runs/revision_source_grounded_rule_star_frozen_v1.jsonl"),
    Path("scripts/run_source_anchored_external_transfer.py"),
    Path("tri/source_anchored_external_transfer.py"),
}
INTERNAL_REPORT_PREFIXES = (
    "AAAI",
    "TRI_AAAI",
    "TRI_paper_introduction_for_review",
    "paper_iteration_blueprint",
)
PACKAGING_ONLY = {
    Path("scripts/build_current_supplement.py"),
    Path("tests/test_build_current_supplement.py"),
}
TEMPORARY_REPORTS = {
    Path("reports/FIGURE_DESIGN_README.md"),
    Path("reports/FIGURE_USAGE_GUIDE.md"),
    Path("reports/FINAL_DELIVERY.md"),
    Path("reports/NEW_FIGURES_SUMMARY.md"),
    Path("reports/使用指南.md"),
    Path("reports/最终图表指南.md"),
}
FAILED_LOCAL_RUNS = {
    Path("runs/end_to_end_decision_decomposition_qwen_smoke_v1.jsonl"),
    Path("runs/end_to_end_decision_decomposition_glm_smoke_v1.jsonl"),
    Path("runs/end_to_end_decision_decomposition_glm_smoke_network_v1.jsonl"),
}


def excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    parts = set(relative.parts)
    if relative.parts[:2] == ("external_pilots", "appworld_runtime"):
        return True
    if relative.parts[:2] in {
        ("reports", "figures"),
        ("reports", "submission_summary"),
    }:
        return True
    if parts & {"__pycache__", ".pytest_cache", ".git"}:
        return True
    if path.name.startswith(".") or path.suffix in {".pyc", ".xlsx"}:
        return True
    if relative in PACKAGING_ONLY:
        return True
    if relative in TEMPORARY_REPORTS:
        return True
    if relative in FAILED_LOCAL_RUNS:
        return True
    if relative.parts[0] == "runs" and path.stat().st_size == 0:
        return True
    if relative.parts[0] == "reports" and path.name.startswith(INTERNAL_REPORT_PREFIXES):
        return True
    if relative.parts[0] == "human_validation":
        return not (
            relative in HUMAN_PUBLIC_FILES
            or relative.parts[:2] == ("human_validation", "normalized_returns")
        )
    return False


def submission_clean_data(source: Path) -> bytes:
    data = source.read_bytes()
    relative = source.relative_to(ROOT) if source.is_relative_to(ROOT) else None
    drop_columns: set[str] = set()
    if relative and relative.parts[:2] == ("human_validation", "normalized_returns"):
        drop_columns = {"comment"}
    elif relative == Path("human_validation/paraphrase_authoring.csv"):
        drop_columns = {"author_notes"}
    if drop_columns:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
        fieldnames = [name for name in (reader.fieldnames or []) if name not in drop_columns]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
        data = output.getvalue().encode()
    if b"\x00" not in data:
        data = LOCAL_HOME_PATTERN.sub(b"$HOME", data)
    if SECRET_PATTERN.search(data):
        raise ValueError(f"possible API key in {source}")
    if BEARER_PATTERN.search(data):
        raise ValueError(f"possible bearer credential in {source}")
    # These exact frozen task-bearing files legitimately contain email entities.
    # Keep their source evidence byte-for-byte; continue rejecting email-shaped
    # strings everywhere an author identity or contact metadata could appear.
    if EMAIL_PATTERN.search(data) and relative not in TASK_EMAIL_CONTENT_FILES:
        raise ValueError(f"possible identity-bearing email in {source}")
    if b"/Users/" in data:
        raise ValueError(f"non-anonymous local path in {source}")
    return data


def source_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for name in TOP_LEVEL:
        source = ROOT / name
        files.append((source, Path("tri_artifact") / name))
    for root_name in ROOTS:
        source_root = ROOT / root_name
        for source in sorted(source_root.rglob("*")):
            if source.is_file() and not excluded(source):
                files.append((source, Path("tri_artifact") / source.relative_to(ROOT)))
    for name in PAPER_FILES:
        source = PAPER / name
        files.append((source, Path("tri_artifact") / "paper" / name))
    for name in PAPER_FIGURES:
        source = PAPER / "Figures" / name
        files.append((source, Path("tri_artifact") / "paper" / "Figures" / name))
    for name in FIGURE_SOURCE_FILES:
        source = FIGURE_SOURCE_ROOT / name
        files.append((source, Path("tri_artifact") / "paper" / "figure_source" / name))
    return files


def verify_archive_manifest(archive: zipfile.ZipFile) -> None:
    manifest_name = "tri_artifact/SOURCE_MANIFEST.tsv"
    rows = archive.read(manifest_name).decode("utf-8").splitlines()
    if not rows or rows[0] != "sha256\tbytes\tpath":
        raise ValueError("invalid manifest header")
    observed: dict[str, tuple[str, int]] = {}
    for line_number, line in enumerate(rows[1:], start=2):
        parts = line.split("\t")
        if len(parts) != 3:
            raise ValueError(f"invalid manifest row {line_number}")
        sha256, size_text, name = parts
        if name in observed:
            raise ValueError(f"duplicate manifest member: {name}")
        observed[name] = (sha256, int(size_text))
    expected = set(archive.namelist()) - {manifest_name}
    if set(observed) != expected:
        missing = sorted(expected - set(observed))
        extra = sorted(set(observed) - expected)
        raise ValueError(f"manifest membership mismatch: missing={missing}, extra={extra}")
    for name, (expected_sha256, expected_size) in observed.items():
        data = archive.read(name)
        if len(data) != expected_size or digest(data) != expected_sha256:
            raise ValueError(f"manifest size/hash mismatch: {name}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(output: Path) -> None:
    files = source_files()
    seen: set[Path] = set()
    manifest_rows = ["sha256\tbytes\tpath"]
    payloads: list[tuple[Path, bytes]] = []
    for source, archive_path in files:
        if archive_path in seen:
            raise ValueError(f"duplicate archive path: {archive_path}")
        seen.add(archive_path)
        data = submission_clean_data(source)
        payloads.append((archive_path, data))
        manifest_rows.append(f"{digest(data)}\t{len(data)}\t{archive_path.as_posix()}")

    readme = """# TRI Current Reproducibility Artifact

This archive corresponds to the current TRI AAAI manuscript. It contains frozen datasets,
raw model outputs, protocols, report generators, tests, external-pilot code, paper source,
and final figure PDFs with their plotting source. It also contains de-identified normalized human responses and aggregate
analysis, while API credentials, private answer mappings, workbooks, coordination forms, and
participant-identifying materials are excluded.

The validated test environment is Python 3.12 with pytest 9.1.1. From `tri_artifact/`, run
`PYTHONPATH=. python3 -m pytest -q tests`. Most analysis code uses only the Python standard
library, but the shipped test suite itself requires pytest. The archive-packaging test is
intentionally excluded because it requires the parent submission tree. ToolSandbox tests require the pinned environment documented in
`external_pilots/toolsandbox_tri/README.md`. The downloaded AppWorld package, databases, and
released public trajectories are excluded; setup is documented in
`external_pilots/appworld_tri/README.md`. See `reports/` for frozen protocols and
machine-readable result reports. `SOURCE_MANIFEST.tsv` records the SHA-256 and byte size of
every archived source file.
""".encode()
    readme_path = Path("tri_artifact") / "ARTIFACT_README.md"
    payloads.append((readme_path, readme))
    manifest_rows.append(f"{digest(readme)}\t{len(readme)}\t{readme_path.as_posix()}")
    manifest = ("\n".join(manifest_rows) + "\n").encode()

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for archive_path, data in payloads:
                archive.writestr(archive_path.as_posix(), data)
            archive.writestr("tri_artifact/SOURCE_MANIFEST.tsv", manifest)
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"corrupt archive member: {bad}")
            verify_archive_manifest(archive)
            names = set(archive.namelist())
            required = {
                "tri_artifact/data/external_public_annotation_candidates_v1.jsonl",
                "tri_artifact/data/temporal_referent_v3_language_clusters.jsonl",
                "tri_artifact/reports/TRI_external_public_siliconflow_annotation_addendum.md",
                "tri_artifact/reports/external_public_annotation_v1.json",
                "tri_artifact/runs/external_public_annotation_siliconflow_v1.jsonl",
                "tri_artifact/data/source_anchored_external_transfer_tasks_v1.jsonl",
                "tri_artifact/reports/TRI_source_anchored_external_transfer_model_addendum.md",
                "tri_artifact/reports/source_anchored_external_transfer_v1.json",
                "tri_artifact/runs/source_anchored_external_transfer_siliconflow_repaired_v1.jsonl",
                "tri_artifact/scripts/report_source_anchored_external_transfer.py",
                "tri_artifact/data/model_authored_linguistic_semantics_v1.jsonl",
                "tri_artifact/data/model_authored_linguistic_stress_v1.jsonl",
                "tri_artifact/reports/TRI_model_authored_linguistic_stress_protocol.md",
                "tri_artifact/reports/TRI_model_authored_linguistic_stress_transport_repair_addendum.md",
                "tri_artifact/reports/model_authored_linguistic_stress_transport_repaired_v2.json",
                "tri_artifact/runs/model_authored_linguistic_author_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_judge_qwen_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_judge_glm_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_evaluate_qwen_generic_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_evaluate_qwen_cta_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_evaluate_glm_generic_full_v1.jsonl",
                "tri_artifact/runs/model_authored_linguistic_evaluate_glm_cta_full_v1.jsonl",
                "tri_artifact/reports/TRI_binding_drift_author_adaptation_v7_full_protocol.md",
                "tri_artifact/reports/binding_drift_tri_glm_v7_full_v1.json",
                "tri_artifact/runs/binding_drift_tri_glm_self_reverify_v7_full_v1.jsonl",
                "tri_artifact/tri/binding_drift_tri_adapter.py",
                "tri_artifact/tri/run_models.py",
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
                "tri_artifact/paper/AnonymousSubmission2027.tex",
                "tri_artifact/paper/source_anchored_external_transfer_table.tex",
                "tri_artifact/paper/Figures/fig1_shared_transition.pdf",
                "tri_artifact/paper/Figures/fig2_diagnostic_workflow.pdf",
                "tri_artifact/paper/Figures/fig2_policy_rulers.pdf",
                "tri_artifact/paper/Figures/fig3_substitution_flow.pdf",
                "tri_artifact/paper/Figures/fig4_sqlite_outcome_tree.pdf",
                "tri_artifact/paper/Figures/fig5_paired_transfer_matrix.pdf",
                "tri_artifact/paper/Figures/fig_s2_changed_calibration_round5.pdf",
                "tri_artifact/paper/Figures/fig_s8_external_boundary_round5.pdf",
                "tri_artifact/paper/Figures/fig4_wrong_write_mirror_round3.pdf",
                "tri_artifact/paper/Figures/fig_source_model_transfer_fingerprints_compact.pdf",
                "tri_artifact/paper/Figures/fig_enforcement_repairs_harms_compact.pdf",
                "tri_artifact/paper/figure_source/plot_round4_figure1.py",
                "tri_artifact/paper/figure_source/plot_fig2_diagnostic_workflow.mjs",
                "tri_artifact/paper/figure_source/plot_round4_figures.py",
                "tri_artifact/paper/figure_source/plot_round5_figures.py",
                "tri_artifact/paper/figure_source/plot_round5_supplement.py",
                "tri_artifact/paper/figure_source/plot_round6_figures.py",
                "tri_artifact/paper/figure_source/plot_round7_figures.py",
                "tri_artifact/paper/figure_source/plot_round8_figures.py",
                "tri_artifact/paper/figure_source/plot_round10_figures.py",
                "tri_artifact/paper/figure_source/plot_submission_critical_effects.py",
                "tri_artifact/paper/figure_source/data/summary_csv/revision_decision_visible_gains.csv",
                "tri_artifact/paper/figure_source/data/summary_csv/sqlite_model_facing_outcomes.csv",
                "tri_artifact/SOURCE_MANIFEST.tsv",
            }
            missing = required - names
            if missing:
                raise ValueError(f"missing required artifact files: {sorted(missing)}")
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(f"{output} ({output.stat().st_size} bytes; {len(payloads)} payload files)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(SUBMISSION / "tri_anonymous_artifact_current.zip"),
    )
    args = parser.parse_args()
    build(Path(args.output))


if __name__ == "__main__":
    main()
