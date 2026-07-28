from __future__ import annotations

from tri.public_recall_calibrated_audit import ANNOTATORS, build_sampling_frame, deduplicate_candidates, report_audit


def _row(dataset: str, index: int) -> dict:
    return {"dataset": dataset, "unit_id": f"u-{index}", "payload": index}


def test_deduplication_and_stratified_sampling() -> None:
    population = [_row("A", i) for i in range(5)] + [_row("B", i) for i in range(150)]
    candidates = [_row("A", 0), _row("A", 0), _row("B", 3)]
    frame = build_sampling_frame(population, candidates, [{"dataset": "control", "unit_id": "p", "expected_strict_positive": True}], per_dataset=2, seed=4)
    natural = [row for row in frame if row["audit_role"] != "injected_control"]
    assert len(deduplicate_candidates(candidates)) == 2
    assert sum(row["audit_role"] == "retrieved_candidate" for row in natural) == 2
    assert sum(row["audit_role"] == "random_non_candidate" for row in natural) == 4
    assert len([row for row in frame if row["audit_role"] == "injected_control"]) == 1


def test_zero_positive_report_has_upper_bound_and_no_recall() -> None:
    rows = []
    for index in range(4):
        row = _row("A", index)
        row.update({"audit_role": "random_non_candidate", "inclusion_probability": 0.5, "adjudications": {name: False for name in ANNOTATORS}})
        rows.append(row)
    report = report_audit(rows, {"A": 100}, bootstrap_samples=20)
    item = report["datasets"]["A"]
    assert item["weighted_positive"] == 0
    assert item["zero_positive_upper_bound_95"] == 0.03
    assert item["retrieval_sensitivity_identifiable"] is False


def test_positive_candidate_makes_recall_estimable_and_controls_are_excluded() -> None:
    candidate = _row("A", 0)
    candidate.update({"audit_role": "retrieved_candidate", "inclusion_probability": 1.0, "adjudications": {name: True for name in ANNOTATORS}})
    random_row = _row("A", 1)
    random_row.update({"audit_role": "random_non_candidate", "inclusion_probability": 1.0, "adjudications": {name: False for name in ANNOTATORS}})
    control = {"dataset": "control", "unit_id": "c", "audit_role": "injected_control", "inclusion_probability": 1.0, "expected_strict_positive": True, "adjudications": {name: True for name in ANNOTATORS}}
    report = report_audit([candidate, random_row, control], {"A": 2}, bootstrap_samples=20)
    assert report["datasets"]["A"]["retrieval_sensitivity"] == 1.0
    assert report["control_rows"] == 1
    assert set(report["datasets"]) == {"A"}
