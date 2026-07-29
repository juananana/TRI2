from __future__ import annotations

import json
from pathlib import Path

import pytest

from tri.public_recall_calibrated_audit import (
    ANNOTATORS,
    MODEL_PRELABELERS,
    blind_public_unit_id,
    build_blind_public_annotation_payload,
    build_sampling_frame,
    deduplicate_candidates,
    finite_population_zero_upper_bound,
    merge_public_annotation_returns,
    reconcile_candidate_inventories,
    report_audit,
    validate_human_annotation_provenance,
)


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
    assert item["weighted_denominator"] == 8
    assert item["bootstrap_ci95"] == [None, None]
    assert item["zero_positive_upper_bound_95"] > 0.03
    assert item["retrieval_sensitivity_identifiable"] is False
    assert item["zero_positive_bound_method"].startswith("exact hypergeometric")


def test_zero_positive_bound_uses_actual_sample_and_finite_population() -> None:
    sparse = finite_population_zero_upper_bound(100, 0, 10)
    census = finite_population_zero_upper_bound(100, 0, 100)
    assert sparse is not None and sparse > 0.2
    assert census == 0.0


def test_positive_candidate_makes_recall_estimable_and_controls_are_excluded() -> None:
    candidate = _row("A", 0)
    candidate.update({"audit_role": "retrieved_candidate", "inclusion_probability": 1.0, "adjudications": {name: True for name in ANNOTATORS}})
    random_row = _row("A", 1)
    random_row.update({"audit_role": "random_non_candidate", "inclusion_probability": 1.0, "adjudications": {name: False for name in ANNOTATORS}})
    control = {"dataset": "control", "unit_id": "c", "audit_role": "injected_control", "inclusion_probability": 1.0, "expected_strict_positive": True, "adjudications": {name: True for name in ANNOTATORS}}
    report = report_audit([candidate, random_row, control], {"A": 2}, bootstrap_samples=20)
    assert report["datasets"]["A"]["retrieval_sensitivity"] == 1.0
    assert report["recall_claim_allowed"] is False
    assert report["control_rows"] == 1
    assert set(report["datasets"]) == {"A"}


def test_candidate_reconciliation_distinguishes_inventory_roles() -> None:
    payload = [
        {"dataset": "A", "unit_id": "u1", "candidate_id": "A:c1"},
        {"dataset": "A", "unit_id": "u2", "candidate_id": "A:c2"},
    ]
    triage = [
        {
            "suite": "A",
            "case_id": "u1",
            "record_id": "external-a-u1",
            "source_kind": "external_structural_candidate",
        },
        {
            "suite": "B",
            "case_id": "closest",
            "record_id": "closest-b",
            "source_kind": "closest_case",
        },
        {
            "suite": "control",
            "case_id": "c",
            "record_id": "control-c",
            "source_kind": "injected_control",
        },
    ]
    ledger, report = reconcile_candidate_inventories(payload, triage)
    assert len(ledger) == 3
    assert report["overlap"] == 1
    assert report["payload_only"] == 1
    assert report["triage_only"] == 1
    assert report["union_audit_units"] == 3
    assert report["benchmark_population_complete"] is False
    assert report["sampling_allowed"] is False


def test_blind_public_packets_hide_sampling_role_gold_and_source_ids() -> None:
    natural = {
        "dataset": "A",
        "audit_unit_id": "candidate-looking-id",
        "cluster_id": "candidate-looking-id",
        "audit_role": "retrieved_candidate",
        "inclusion_probability": 1.0,
        "sample_seed": 4,
        "candidate_basis": ["retrieval"],
        "source_summary": {"instruction": "refresh then update the selected record"},
    }
    control = {
        "suite": "API-Bank",
        "control_id": "strict-positive-1",
        "audit_role": "injected_control",
        "inclusion_probability": 1.0,
        "expected_strict": True,
        "features": {"stable_entity_id": True},
    }
    for labeler in (*ANNOTATORS, *MODEL_PRELABELERS):
        payload = build_blind_public_annotation_payload(natural, labeler)
        serialized = str(payload)
        assert "retrieved_candidate" not in serialized
        assert "candidate-looking-id" not in serialized
        assert "inclusion_probability" not in payload
        assert payload["blind_unit_id"] == blind_public_unit_id(natural)
    control_payload = build_blind_public_annotation_payload(control, "M1")
    assert "expected_strict" not in control_payload
    assert "synthetic_feature_flags" not in str(control_payload)
    assert set(control_payload) == set(build_blind_public_annotation_payload(natural, "M1"))
    assert control_payload["labeler_id"] == "M1"


def _annotation(row: dict, labeler: str, strict: bool) -> dict:
    labels = {
        field: "yes" for field in build_blind_public_annotation_payload(row, labeler)["rubric_fields"]
    }
    if not strict:
        labels["stable_entity_id"] = "no"
    return {
        "labeler_id": labeler,
        "blind_unit_id": blind_public_unit_id(row),
        "feature_labels": labels,
        "strict_eligible": strict,
        "primary_exclusion_reason": "NONE" if strict else "stable_entity_id",
        "confidence": 4,
        "notes": "source-grounded test label",
    }


def test_annotation_ingestion_requires_locked_humans_and_excludes_models() -> None:
    frame = [_row("A", 0), _row("A", 1)]
    for row in frame:
        row.update({"audit_role": "random_non_candidate", "inclusion_probability": 1.0})
    private_key = [
        {
            "blind_unit_id": blind_public_unit_id(row),
            "audit_role": row["audit_role"],
            "inclusion_probability": row["inclusion_probability"],
        }
        for row in frame
    ]
    human_returns = {
        annotator: [_annotation(row, annotator, row["unit_id"] == "u-0") for row in frame]
        for annotator in ANNOTATORS
    }
    model_returns = {
        "M1": [_annotation(row, "M1", False) for row in frame]
    }
    hashes = {annotator: f"hash-{annotator}" for annotator in ANNOTATORS}
    role_hashes = {
        "Q1": "0" * 64,
        "A1": "1" * 64,
        "A2": "2" * 64,
        "A3": "3" * 64,
    }
    provenance = {
        "status": "complete-locked-before-model-prelabels",
        "private_annotation_key_sha256": "key-hash",
        "annotation_returns_sha256": hashes,
        "annotators": {
            annotator: {
                "source": "independent_human",
                "completed": True,
                "blind": True,
                "saw_model_prelabels_before_lock": False,
                "participant_token_sha256": role_hashes[annotator],
            }
            for annotator in ANNOTATORS
        },
    }
    merged = merge_public_annotation_returns(
        frame,
        private_key,
        human_returns,
        provenance,
        "key-hash",
        hashes,
        model_returns,
        role_token_sha256=role_hashes,
    )
    report = report_audit(
        merged, {"A": 2}, bootstrap_samples=20, verified_ingestion=True
    )
    assert report["independent_human_gate_passed"] is True
    assert report["datasets"]["A"]["weighted_positive"] == 1
    assert report["model_prelabels_used_for_majority"] is False
    assert report["model_prelabels"]["M1"]["strict_positive"] == 0
    assert report["human_agreement"]["strict_eligible"]["unanimous_rate"] == 1.0


def test_annotation_ingestion_rejects_model_or_incomplete_human_provenance() -> None:
    row = _row("A", 0)
    row.update({"audit_role": "retrieved_candidate", "inclusion_probability": 1.0})
    human_returns = {
        annotator: [_annotation(row, annotator, True)] for annotator in ANNOTATORS
    }
    provenance = {
        "status": "complete-locked-before-model-prelabels",
        "private_annotation_key_sha256": "key",
        "annotation_returns_sha256": {annotator: annotator for annotator in ANNOTATORS},
        "annotators": {
            annotator: {
                "source": "model" if annotator == "A2" else "independent_human",
                "completed": True,
                "blind": True,
                "saw_model_prelabels_before_lock": False,
                "participant_token_sha256": annotator * 32,
            }
            for annotator in ANNOTATORS
        },
    }
    with pytest.raises(ValueError, match="independent-human provenance"):
        merge_public_annotation_returns(
            [row],
            [{
                "blind_unit_id": blind_public_unit_id(row),
                "audit_role": row["audit_role"],
                "inclusion_probability": 1.0,
            }],
            human_returns,
            provenance,
            "key",
            {annotator: annotator for annotator in ANNOTATORS},
            role_token_sha256={annotator: annotator * 32 for annotator in ANNOTATORS},
        )


def test_generic_complete_status_cannot_unlock_human_evidence() -> None:
    provenance = {
        "status": "complete",
        "private_annotation_key_sha256": "key",
        "annotation_returns_sha256": {annotator: annotator for annotator in ANNOTATORS},
        "annotators": {},
    }
    with pytest.raises(ValueError, match="not complete and locked"):
        validate_human_annotation_provenance(
            provenance,
            "key",
            {annotator: annotator for annotator in ANNOTATORS},
            {annotator: annotator * 32 for annotator in ANNOTATORS},
        )


def test_v4_payload_removes_derived_labels_and_normalizes_control_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    frame = [
        json.loads(line)
        for line in (root / "data" / "public_recall_sampling_frame_v1.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    natural_keys: dict[str, set[tuple[str, ...]]] = {}
    for row in frame:
        payload = build_blind_public_annotation_payload(row, "M1")
        assert set(payload["source_evidence"]) == {"document"}
        document = payload["source_evidence"]["document"]
        assert '"classification"' not in document
        assert "excluded_" not in document
        assert "tri_like_" not in document
        assert "synthetic_feature_flags" not in document
        parsed = json.loads(document)
        dataset = str(row.get("dataset") or row.get("suite"))
        if row["audit_role"] != "injected_control":
            natural_keys.setdefault(dataset, set()).add(tuple(sorted(parsed)))
    for row in frame:
        if row["audit_role"] != "injected_control":
            continue
        payload = build_blind_public_annotation_payload(row, "M1")
        parsed = json.loads(payload["source_evidence"]["document"])
        dataset = str(row.get("suite"))
        assert tuple(sorted(parsed)) in natural_keys[dataset]
