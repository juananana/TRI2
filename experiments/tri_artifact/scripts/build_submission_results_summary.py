from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REPORTS = [
    "reports/current_claim_provenance.md",
    "reports/current_experiment_registry.md",
    "reports/claims_to_evidence.csv",
    "reports/main_paper_evidence_audit_v1.json",
    "reports/main_paper_evidence_audit_v1.md",
    "reports/call_matched_authorization_ablation_v2.json",
    "reports/call_matched_authorization_ablation_v2.md",
    "reports/revision_full_diagnostic_v2.json",
    "reports/revision_full_diagnostic_v2.md",
    "reports/revision_human_rewrite_v2.json",
    "reports/revision_human_rewrite_v2.md",
    "reports/revision_source_grounded_v2.json",
    "reports/revision_source_grounded_v2.md",
    "reports/revision_source_grounded_rule_star_frozen_v1.json",
    "reports/revision_source_grounded_rule_star_frozen_v1.md",
    "reports/public_audit_injected_sensitivity_v1.json",
    "reports/public_audit_injected_sensitivity_v1.md",
    "reports/TRI_revision_matched_audits_protocol.md",
    "reports/TRI_revision_matched_audits_execution_log.md",
    "reports/v7_core_replication.json",
    "reports/v7_deepseek_full_v1.json",
    "reports/v7_shared_eligible_pairacc_v1.json",
    "reports/deterministic_discourse_rule_v2.json",
    "reports/rule_hard_residual_v1.json",
    "reports/rule_hard_residual_v1.md",
    "reports/TRI_binding_drift_author_adaptation_v7_full_protocol.md",
    "reports/binding_drift_repro_audit.md",
    "reports/binding_drift_tri_glm_v7_full_v1.json",
    "reports/binding_drift_tri_glm_v7_full_v1.md",
    "reports/source_anchored_external_transfer_v1.json",
    "reports/source_anchored_external_transfer_v1.md",
    "reports/model_authored_linguistic_stress_transport_repaired_v2.json",
    "reports/model_authored_linguistic_stress_transport_repaired_v2.md",
    "reports/TRI_model_authored_linguistic_stress_transport_repair_addendum.md",
    "reports/external_public_opportunity_audit_v1.json",
    "reports/external_public_opportunity_audit_v1.md",
    "reports/benchmark_coverage_checklist.json",
    "reports/benchmark_coverage_checklist.md",
    "reports/v5_qwen_multirefresh_report.json",
    "reports/v6_matched_scalar_role_report.json",
    "human_validation/analysis.json",
    "human_validation/analysis.md",
]

FIGURES = [
    "reports/figures/tri_first_figure.pdf",
    "reports/figures/tri_comprehensive_results.pdf",
    "reports/figures/tri_schema_transfer_dense.pdf",
    "reports/figures/tri_call_matched_ablation.pdf",
    "reports/figures/tri_component_audit_dotline.pdf",
    "reports/figures/tri_claim_boundary_matrix.pdf",
    "reports/figures/tri_core_diagnostic.pdf",
    "reports/figures/tri_replication_attribution.pdf",
    "reports/figures/tri_revision_matched_confirmation.pdf",
    "reports/figures/tri_source_grounded_confirmation.pdf",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output: Path) -> dict[str, object]:
    report_dir = output / "reports"
    figure_dir = output / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, object]] = []
    for source_name in REPORTS:
        source = ROOT / source_name
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = report_dir / source.name
        shutil.copy2(source, destination)
        entries.append(
            {
                "kind": "report",
                "source": source_name,
                "file": str(destination.relative_to(output)),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    for source_name in FIGURES:
        source = ROOT / source_name
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = figure_dir / source.name
        shutil.copy2(source, destination)
        entries.append(
            {
                "kind": "figure",
                "source": source_name,
                "file": str(destination.relative_to(output)),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    manifest = {
        "status": "source-derived submission evidence summary",
        "boundaries": [
            "Primary, post-primary, and post-hoc status remains defined in current_claim_provenance.md.",
            "External nulls and mixed composition results are retained.",
            "This directory is an index of paper-facing evidence, not a replacement for raw outputs.",
        ],
        "entries": entries,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "README.md").write_text(
        """# Submission Results Summary

This directory collects the paper-facing evidence in one place. It is generated from frozen
reports; raw outputs, task inventories, protocols, and executable analyses remain in their original
artifact locations.

## Reading order

1. `reports/current_claim_provenance.md`: evidence chronology and claim status.
2. `reports/main_paper_evidence_audit_v1.md`: source-derived checks of manuscript numbers.
3. `reports/revision_full_diagnostic_v2.md`: full-diagnostic equal-call confirmation.
4. `reports/revision_human_rewrite_v2.md`: model-dependent equal-call transfer to volunteer rewrites.
5. `reports/revision_source_grounded_v2.md`: model-dependent matched-call results across three
   source-derived controlled substrates.
6. `reports/call_matched_authorization_ablation_v2.md`: earlier cross-schema matched-call ablation.
7. `reports/external_public_opportunity_audit_v1.md` and
   `reports/source_anchored_external_transfer_v1.md`: external null and limited bridge evidence.
8. `reports/model_authored_linguistic_stress_transport_repaired_v2.md`: model-authored language
   stress audit, including the failed dual-judge validity gate and transport repair.
9. `reports/binding_drift_tri_glm_v7_full_v1.md`: concurrent entity-lock and re-verification
   baseline adaptation on matched Preserve/Reevaluate tasks.
10. `reports/rule_hard_residual_v1.md`: post-hoc residual audit on the 20 rows missed by Rule*.
11. `reports/v5_qwen_multirefresh_report.json` and
   `reports/v6_matched_scalar_role_report.json`: mixed compositional boundary.
12. `figures/`: final paper-facing figures and supplementary result panels.

`manifest.json` records source paths, sizes, and SHA-256 hashes. Negative and post-hoc evidence is
included intentionally.
""",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "submission_summary",
    )
    args = parser.parse_args()
    manifest = build(args.output)
    print(f"{args.output} ({len(manifest['entries'])} files)")


if __name__ == "__main__":
    main()
