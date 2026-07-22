from __future__ import annotations

import csv

from tri.main_paper_evidence_audit import ROOT, build_report, validate


def test_main_paper_evidence_audit_matches_frozen_sources() -> None:
    report = build_report()
    validate(report)
    assert report["all_checks_pass"] is True
    assert len(report["v7_table2"]) == 6
    assert report["v7_table2"][0]["latex_row"] == "Qwen / Gen. & 7/80 & 43/72 & 43/44 \\\\"


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
