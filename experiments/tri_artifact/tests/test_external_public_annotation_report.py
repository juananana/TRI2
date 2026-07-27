from __future__ import annotations

from tri.external_public_annotation_report import (
    EXPECTED_MODELS,
    build_annotation_report,
    valid_annotation,
)


def _labels(strict: str = "no", source: str = "yes") -> dict[str, str]:
    return {
        "prior_selector_or_selection": "yes",
        "observable_stable_id_before_update": "yes",
        "binding_before_update": "unclear",
        "independent_update_after_binding": "no",
        "same_role_competing_entity": "unclear",
        "distinct_refreshed_winner": "no",
        "old_target_survives": "unclear",
        "old_target_action_valid": "unclear",
        "later_target_mutation": "yes",
        "timing_authorization": "absent",
        "target_level_outcome_observable": "yes",
        "source_anchored_eligible": source,
        "strict_native_tri_opportunity": strict,
    }


def _row(model: str, candidate_id: str, strict: str = "no") -> dict:
    return {
        "model": model,
        "candidate_id": candidate_id,
        "status": "ok",
        "annotation": {
            "candidate_id": candidate_id,
            "labels": _labels(strict=strict),
            "evidence": [],
            "primary_exclusion_reason": "no independent update",
            "notes": "",
        },
    }


def _transport_failed_row(model: str, candidate_id: str) -> dict:
    return {
        "model": model,
        "candidate_id": candidate_id,
        "status": "failed",
        "annotation": None,
        "transport_or_response_error": "URLError: temporary name resolution failure",
    }


def test_valid_annotation_requires_exact_schema() -> None:
    row = _row(EXPECTED_MODELS[0], "A")
    assert valid_annotation(row)
    del row["annotation"]["labels"]["old_target_survives"]
    assert not valid_annotation(row)


def test_report_treats_model_strict_yes_as_candidate_only() -> None:
    candidates = [{"candidate_id": "A"}]
    rows = [_row(EXPECTED_MODELS[0], "A", strict="yes"), _row(EXPECTED_MODELS[1], "A")]
    report = build_annotation_report(candidates, rows)
    assert report["complete_two_model_candidates"] == 1
    assert report["strict_yes_union"] == ["A"]
    assert report["strict_yes_intersection"] == []
    assert report["two_model_disagreement_candidates"] == 1


def test_report_uses_latest_transport_repair_attempt() -> None:
    candidates = [{"candidate_id": "A"}]
    rows = [
        _transport_failed_row(EXPECTED_MODELS[0], "A"),
        _row(EXPECTED_MODELS[0], "A"),
        _row(EXPECTED_MODELS[1], "A"),
    ]
    report = build_annotation_report(candidates, rows)
    assert report["observed_unique_rows"] == 2
    assert report["total_raw_rows_supplied"] == 3
    assert report["raw_failed_rows"] == 1
    assert report["complete_two_model_candidates"] == 1
    assert report["per_model"][EXPECTED_MODELS[0]]["valid"] == 1
    assert report["repeated_attempt_pairs"] == [f"{EXPECTED_MODELS[0]}::A"]


def test_report_marks_missing_pairs_incomplete() -> None:
    candidates = [{"candidate_id": "A"}]
    report = build_annotation_report(candidates, [_row(EXPECTED_MODELS[0], "A")])
    assert report["status"].startswith("incomplete ")
    assert report["observed_unique_rows"] == 1
    assert len(report["missing_pairs"]) == 1
