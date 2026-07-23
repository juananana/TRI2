from __future__ import annotations

from tri.manuscript_consistency_audit import build_report, validate


def test_manuscript_consistency_audit_passes() -> None:
    report = build_report()
    validate(report)
    assert all(report["checks"].values())
    assert report["missing_bibliography_entries"] == []
    assert report["missing_labels"] == []
