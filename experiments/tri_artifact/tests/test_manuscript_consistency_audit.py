from __future__ import annotations

from tri.manuscript_consistency_audit import _without_comments, build_report, validate


def test_comment_stripping_preserves_escaped_percentages() -> None:
    source = "Accuracy is 98.1\\%. Scope remains controlled. % author note"
    assert _without_comments(source) == "Accuracy is 98.1\\%. Scope remains controlled. "


def test_manuscript_consistency_audit_passes() -> None:
    report = build_report()
    validate(report)
    assert all(report["checks"].values())
    assert report["missing_bibliography_entries"] == []
    assert report["missing_labels"] == []
