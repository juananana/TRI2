from __future__ import annotations

from pathlib import Path

from tri.model_assisted_public_recall_triage import (
    EVIDENCE_STATUS,
    SUITES,
    build_report,
    build_triage_rows,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parents[1]


def test_triage_queue_covers_all_public_suites_and_controls(tmp_path: Path) -> None:
    rows = build_triage_rows(ROOT)
    suites = {row["suite"] for row in rows}
    assert suites == set(SUITES)
    assert all(row["evidence_status"] == EVIDENCE_STATUS for row in rows)
    assert all(row["publication_status"] == "candidate_labels_only_not_independent_review" for row in rows)
    natural = [row for row in rows if row["source_kind"] != "injected_control"]
    controls = [row for row in rows if row["source_kind"] == "injected_control"]
    assert len(natural) >= 60
    assert len(controls) == 60

    triage_path = tmp_path / "triage.jsonl"
    write_jsonl(triage_path, rows)
    report = build_report(ROOT, rows, triage_path)
    assert report["decision"] == "MODEL-ASSISTED TRIAGE ONLY / NOT INDEPENDENT CALIBRATION"
    assert report["natural_candidate_strict"] == 0
    assert report["control_strict_positive_recall"] == {"numerator": 30, "denominator": 30}
    assert report["control_hard_negative_exclusion"] == {"numerator": 30, "denominator": 30}
    assert "cannot be reported as independent human recall calibration" in report["boundary"]


def test_human_review_queue_contains_closest_cases_and_near_matches(tmp_path: Path) -> None:
    rows = build_triage_rows(ROOT)
    triage_path = tmp_path / "triage.jsonl"
    write_jsonl(triage_path, rows)
    report = build_report(ROOT, rows, triage_path)
    queued_ids = {row["record_id"] for row in report["priority_queue"]}
    assert "closest-toolsandbox" in queued_ids
    assert "closest-appworld" in queued_ids
    assert "closest-tau3bench" in queued_ids
    assert any(row["suite"] == "BFCL" for row in report["priority_queue"])
    assert any(row["suite"] == "ToolTalk" for row in report["priority_queue"])
