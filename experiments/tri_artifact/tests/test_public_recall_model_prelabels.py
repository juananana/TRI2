from __future__ import annotations

import json
import csv
import copy
from pathlib import Path

import pytest

from tri.end_to_end_decision_decomposition import canonical_json, sha256_path, sha256_text
from tri.public_recall_model_prelabels import (
    EVIDENCE_STATUS,
    MODEL_IDS,
    RUN_SETTINGS,
    RUN_VERSION,
    SYSTEM_PROMPT,
    actor_payload,
    build_incomplete_review_report,
    build_postrun_quality_audit,
    build_review_report,
    build_author_qa_report,
    load_packet,
    parse_model_prelabel,
    prompt_hash,
    settings_hash,
    validate_run_inventory,
    validate_run_row,
)
from scripts.ingest_public_recall_author_qa import load_author_qa_csv


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "data" / "public_recall_model_prelabel_packets_v4"
PRIVATE_PACKET_ROOT = ROOT / "human_studies" / "public_recall_calibrated_audit_v4"
PROTOCOL = ROOT / "reports" / "TRI_public_recall_model_prelabels_protocol.md"


def _packets() -> dict[str, list[dict]]:
    manifest = PACKET_ROOT / "manifest.json"
    return {
        labeler: load_packet(
            PACKET_ROOT / "model_prelabels" / f"model_prelabel_{labeler}.jsonl",
            manifest,
            labeler,
        )
        for labeler in MODEL_IDS
    }


def _parsed(task: dict, strict: bool) -> dict:
    features = {field: "yes" for field in task["rubric_fields"]}
    if not strict:
        features["stable_entity_id"] = "no"
    return {
        "labeler_id": task["labeler_id"],
        "blind_unit_id": task["blind_unit_id"],
        "feature_labels": features,
        "strict_eligible": strict,
        "primary_exclusion_reason": "NONE" if strict else "stable_entity_id",
        "confidence": 4,
        "notes": "provisional model label",
    }


def _run_rows(
    tasks: list[dict], labeler: str, strict_ids: set[str], packet_sha256: str
) -> list[dict]:
    rows = []
    for index, task in enumerate(tasks):
        parsed = _parsed(task, task["blind_unit_id"] in strict_ids)
        raw = json.dumps({
            key: value
            for key, value in parsed.items()
            if key not in {"labeler_id", "blind_unit_id"}
        })
        rows.append({
            "run_version": RUN_VERSION,
            "evidence_status": EVIDENCE_STATUS,
            "labeler_id": labeler,
            "model": MODEL_IDS[labeler],
            "run_scope": "full",
            "task_index": index,
            "task": task,
            "task_sha256": sha256_text(canonical_json(task)),
            "packet_sha256": packet_sha256,
            "protocol_sha256": sha256_path(PROTOCOL),
            "health_smoke_sha256": "sha256:synthetic-health-smoke",
            "prompt_sha256": prompt_hash(),
            "settings_sha256": settings_hash(),
            "component": {
                "parsed": parsed,
                "attempts": [{
                    "attempt_index": 0,
                    "logical_call": "public_recall_model_prelabel",
                    "status": "success",
                    "raw_content": raw,
                    "request": {
                        "model": MODEL_IDS[labeler],
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {
                                "role": "user",
                                "content": json.dumps(
                                    actor_payload(task),
                                    sort_keys=True,
                                    ensure_ascii=False,
                                ),
                            },
                        ],
                        "temperature": RUN_SETTINGS["temperature"],
                        "max_tokens": RUN_SETTINGS["max_tokens"],
                        "enable_thinking": False,
                    },
                }],
                "usage": {},
                "error": None,
                "error_kind": None,
            },
            "complete": True,
        })
    return rows


def test_v4_packets_are_complete_and_model_only() -> None:
    packets = _packets()
    assert all(len(rows) == 699 for rows in packets.values())
    assert all(
        row["evidence_status"] == "model-assisted prelabel; never human evidence"
        for rows in packets.values()
        for row in rows
    )
    assert all(
        set(row["source_evidence"]) == {"document"}
        and "classification" not in json.dumps(row["source_evidence"])
        for rows in packets.values()
        for row in rows
    )


def test_parser_enforces_rubric_conjunction() -> None:
    task = _packets()["M1"][0]
    parsed = _parsed(task, False)
    raw = json.dumps({
        key: value
        for key, value in parsed.items()
        if key not in {"labeler_id", "blind_unit_id"}
    })
    assert parse_model_prelabel(raw, task)["strict_eligible"] is False
    invalid = json.loads(raw)
    invalid["strict_eligible"] = True
    with pytest.raises(ValueError, match="conjunction"):
        parse_model_prelabel(json.dumps(invalid), task)


def test_review_report_is_descriptive_and_prioritizes_disagreement() -> None:
    packets = _packets()
    blind_ids = sorted(task["blind_unit_id"] for task in packets["M1"])
    packet_sha256 = {
        labeler: sha256_path(
            PACKET_ROOT / "model_prelabels" / f"model_prelabel_{labeler}.jsonl"
        )
        for labeler in MODEL_IDS
    }
    runs = {
        "M1": _run_rows(packets["M1"], "M1", {blind_ids[0]}, packet_sha256["M1"]),
        "M2": _run_rows(
            packets["M2"], "M2", {blind_ids[0], blind_ids[1]}, packet_sha256["M2"]
        ),
        "M3": _run_rows(packets["M3"], "M3", {blind_ids[1]}, packet_sha256["M3"]),
    }
    field_disagreement_id = blind_ids[2]
    for labeler, field in (("M2", "competing_same_role_entity"), ("M3", "old_entity_remains_actionable")):
        row = next(
            item for item in runs[labeler]
            if item["task"]["blind_unit_id"] == field_disagreement_id
        )
        parsed = row["component"]["parsed"]
        parsed["feature_labels"]["stable_entity_id"] = "yes"
        parsed["feature_labels"][field] = "no"
        parsed["primary_exclusion_reason"] = field
        row["component"]["attempts"][-1]["raw_content"] = json.dumps({
            key: value
            for key, value in parsed.items()
            if key not in {"labeler_id", "blind_unit_id"}
        })
    for labeler in MODEL_IDS:
        validate_run_inventory(
            runs[labeler],
            packets[labeler],
            labeler,
            "full",
            packet_sha256[labeler],
            sha256_path(PROTOCOL),
        )
    report, queue = build_review_report(
        runs,
        packets,
        packet_sha256,
        sha256_path(PROTOCOL),
        {labeler: "sha256:synthetic-health-smoke" for labeler in MODEL_IDS},
    )
    assert report["rows"] == 699
    assert report["disagreement_rows"] == 2
    assert report["rubric_disagreement_rows"] == 3
    assert report["independent_human_evidence"] is False
    assert report["prevalence_or_recall_claim_allowed"] is False
    assert queue[0]["review_priority"] == 0
    assert queue[0]["author_qa_strict_eligible"] is None
    field_row = next(row for row in queue if row["blind_unit_id"] == field_disagreement_id)
    assert field_row["strict_unanimous"] is True
    assert field_row["rubric_unanimous"] is False
    assert field_row["review_priority"] == 0

    qa_labels = []
    for queue_row in queue:
        features = {}
        for field in queue_row["model_labels"]["M1"]["feature_labels"]:
            votes = [
                item["feature_labels"][field]
                for item in queue_row["model_labels"].values()
            ]
            features[field] = max(set(votes), key=votes.count)
        strict = all(value == "yes" for value in features.values())
        qa_labels.append({
            "labeler_id": "Q1",
            "blind_unit_id": queue_row["blind_unit_id"],
            "feature_labels": features,
            "strict_eligible": strict,
            "primary_exclusion_reason": (
                "NONE" if strict else next(field for field, value in features.items() if value != "yes")
            ),
            "confidence": 4,
            "notes": "author QA test",
        })
    qa_report = build_author_qa_report(queue, qa_labels)
    assert qa_report["rows"] == 699
    assert qa_report["independent_human_evidence"] is False
    assert qa_report["human_gate_unlocked"] is False


def test_incomplete_review_report_keeps_missing_votes_out_of_consensus() -> None:
    packets = _packets()
    packet_sha256 = {
        labeler: sha256_path(
            PACKET_ROOT / "model_prelabels" / f"model_prelabel_{labeler}.jsonl"
        )
        for labeler in MODEL_IDS
    }
    runs = {
        labeler: _run_rows(packets[labeler], labeler, set(), packet_sha256[labeler])
        for labeler in MODEL_IDS
    }
    failed = runs["M3"][7]
    failed["component"].update(
        parsed=None,
        error="json_parse_error: synthetic failure",
        error_kind="parse_or_schema",
    )
    failed["component"]["attempts"][-1]["raw_content"] = "not-json"
    failed["complete"] = False
    with pytest.raises(ValueError, match="contains incomplete rows"):
        build_review_report(
            runs,
            packets,
            packet_sha256,
            sha256_path(PROTOCOL),
            {labeler: "sha256:synthetic-health-smoke" for labeler in MODEL_IDS},
        )
    report, queue = build_incomplete_review_report(
        runs,
        packets,
        packet_sha256,
        sha256_path(PROTOCOL),
        {labeler: "sha256:synthetic-health-smoke" for labeler in MODEL_IDS},
    )
    failed_id = failed["task"]["blind_unit_id"]
    failed_queue_row = next(row for row in queue if row["blind_unit_id"] == failed_id)
    assert report["formal_review_report_gate_passed"] is False
    assert report["complete_model_panel_rows"] == 698
    assert report["model_coverage"]["M3"]["incomplete"] == 1
    assert failed_queue_row["missing_model_labelers"] == ["M3"]
    assert failed_queue_row["provisional_majority_strict"] is None
    assert failed_queue_row["review_priority"] == 0
    assert failed_queue_row["evidence_allowed"] is False
    private_key_path = PRIVATE_PACKET_ROOT / "private_annotation_key.jsonl"
    if private_key_path.is_file():
        private_key = [
            json.loads(line)
            for line in private_key_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        private_key_sha256 = sha256_path(private_key_path)
        quality = build_postrun_quality_audit(
            queue,
            private_key,
            private_key_sha256=private_key_sha256,
            expected_private_key_sha256=private_key_sha256,
        )
        assert quality["model_quality"]["M3"]["incomplete"] == 1
        assert quality["role_summary"]["retrieved_candidate"]["rows"] == 116
        assert quality["natural_zero_claim_allowed"] is False
        assert quality["prevalence_or_recall_claim_allowed"] is False
        assert quality["provenance"]["private_annotation_key_sha256"] == private_key_sha256
        with pytest.raises(ValueError, match="frozen manifest hash"):
            build_postrun_quality_audit(
                queue,
                private_key,
                private_key_sha256="0" * 64,
                expected_private_key_sha256=private_key_sha256,
            )
    else:
        assert not (ROOT / "human_studies").exists()
    qa_labels = [
        {**row["model_labels"]["M1"], "labeler_id": "Q1"} for row in queue
    ]
    qa_report = build_author_qa_report(queue, qa_labels)
    assert qa_report["strict_agreement_with_model_majority"]["total"] == 698
    assert qa_report["missing_model_panel_rows"] == 1


def test_fabricated_parsed_label_without_attempt_is_rejected() -> None:
    task = _packets()["M1"][0]
    packet_sha256 = sha256_path(
        PACKET_ROOT / "model_prelabels" / "model_prelabel_M1.jsonl"
    )
    row = _run_rows([task], "M1", set(), packet_sha256)[0]
    row["component"]["attempts"] = []
    with pytest.raises(ValueError, match="retained bounded request attempts"):
        validate_run_row(
            row,
            task,
            0,
            "full",
            packet_sha256,
            sha256_path(PROTOCOL),
            "sha256:synthetic-health-smoke",
        )

    valid = _run_rows([task], "M1", set(), packet_sha256)[0]
    tampered_model = copy.deepcopy(valid)
    tampered_model["component"]["attempts"][0]["request"]["model"] = MODEL_IDS["M2"]
    with pytest.raises(ValueError, match="recorded payload mismatch"):
        validate_run_row(
            tampered_model, task, 0, "full", packet_sha256,
            sha256_path(PROTOCOL), "sha256:synthetic-health-smoke",
        )
    tampered_raw = copy.deepcopy(valid)
    tampered_raw["component"]["attempts"][0]["raw_content"] = "{}"
    with pytest.raises(ValueError):
        validate_run_row(
            tampered_raw, task, 0, "full", packet_sha256,
            sha256_path(PROTOCOL), "sha256:synthetic-health-smoke",
        )
    with pytest.raises(ValueError, match="run scope mismatch"):
        validate_run_row(
            valid, task, 0, "smoke", packet_sha256,
            sha256_path(PROTOCOL), None,
        )


def test_author_qa_csv_requires_all_rubric_fields(tmp_path: Path) -> None:
    task = _packets()["M1"][0]
    path = tmp_path / "qa.csv"
    fields = [
        "blind_unit_id",
        *[f"author_qa_feature_{field}" for field in task["rubric_fields"]],
        "author_qa_strict_eligible",
        "author_qa_primary_exclusion_reason",
        "author_qa_confidence",
        "author_qa_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "blind_unit_id": task["blind_unit_id"],
            **{
                f"author_qa_feature_{field}": "yes"
                for field in task["rubric_fields"]
            },
            "author_qa_strict_eligible": "true",
            "author_qa_primary_exclusion_reason": "NONE",
            "author_qa_confidence": "5",
            "author_qa_notes": "checked against source evidence",
        })
    labels = load_author_qa_csv(path)
    assert labels[0]["strict_eligible"] is True
    assert set(labels[0]["feature_labels"]) == set(task["rubric_fields"])
