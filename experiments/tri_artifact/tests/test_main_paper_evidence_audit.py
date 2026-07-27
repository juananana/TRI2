from __future__ import annotations

import csv

from tri.main_paper_evidence_audit import (
    PAPER,
    ROOT,
    build_report,
    default_paper_path,
    validate,
)


def test_main_paper_evidence_audit_matches_frozen_sources() -> None:
    assert PAPER.is_file()
    report = build_report()
    validate(report)
    assert report["all_checks_pass"] is True
    assert len(report["v7_diagnostic_table"]) == 6
    assert report["v7_diagnostic_table"][0]["latex_row"] == "Qwen / Generic & 7/80 & 43/72 & 43/44 \\\\"
    assert report["selection_regret"]["proxy_evaluations"] == 20
    assert report["selection_regret"]["zero_pairacc_maximizer_rows"] == 15
    assert report["selection_regret"]["maximum_worst_case_selection_regret"] == 1.0
    assert [row["opportunities"] for row in report["external_extension"]] == [70, 73, 64, 87]
    assert [row["wrong_writes"] for row in report["external_extension"]] == [6, 13, 5, 4]
    assert all(row["mechanism_errors"] == 0 for row in report["external_extension"])
    assert report["source_anchored_external_transfer"]["preserve_changed_substitutions"] == [2, 64]
    assert report["source_anchored_external_transfer"]["state_bench_substitutions"] == [0, 34]


def test_default_paper_path_prefers_archive_layout(tmp_path) -> None:
    artifact_root = tmp_path / "tri_artifact"
    paper = artifact_root / "paper" / "AnonymousSubmission2027.tex"
    paper.parent.mkdir(parents=True)
    paper.write_text("archive paper", encoding="utf-8")
    assert default_paper_path(artifact_root) == paper


def test_claims_to_evidence_has_valid_status_and_sources() -> None:
    path = ROOT / "reports/claims_to_evidence.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 10
    assert len({row["claim_id"] for row in rows}) == len(rows)
    allowed = {
        "primary/frozen",
        "post-primary replication/audit",
        "post-hoc",
        "planned/unverified",
    }
    for row in rows:
        assert row["evidence_status"] in allowed
        assert row["boundary"]
        for source in row["source_report"].split(";"):
            assert (ROOT / source).is_file(), source
        if row["evidence_status"] == "planned/unverified":
            assert row["role"] == "none"
