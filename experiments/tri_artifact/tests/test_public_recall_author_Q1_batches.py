from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from scripts.ingest_public_recall_author_qa import (
    load_author_qa_csv,
    validate_reviewed_Q1_artifact,
)
from scripts.ingest_public_recall_annotations import validate_shared_role_registry
from scripts.prepare_public_recall_author_Q1_batches import (
    DEFAULT_QUEUE,
    DEFAULT_TEMPLATE,
    merge,
    prepare,
    read_csv,
    write_csv,
)
from tri.end_to_end_decision_decomposition import load_jsonl
from tri.public_recall_calibrated_audit import RUBRIC_FIELDS


def _token(role: str) -> str:
    return hashlib.sha256(f"private-test-token::{role}".encode()).hexdigest()


def _private_gate_files(tmp_path: Path, overlap: bool = False) -> tuple[Path, Path]:
    roles = {
        role: {"participant_token_sha256": _token("Q1" if overlap and role == "A1" else role)}
        for role in ("Q1", "A1", "A2", "A3")
    }
    registry = tmp_path / "private_role_registry.json"
    registry.write_text(
        json.dumps(
            {
                "version": "TRI-private-human-role-registry-v1",
                "status": "locked",
                "token_policy": "stable-per-person-random-128-bit-minimum-hashed-sha256",
                "one_token_per_natural_person": True,
                "coordinator_verified_no_role_overlap": True,
                "roles": roles,
            }
        ),
        encoding="utf-8",
    )
    provenance = tmp_path / "Q1_reviewer_provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "version": "TRI-public-recall-Q1-reviewer-provenance-v1",
                "status": "complete",
                "reviewer_role": "Q1",
                "participant_token_sha256": _token("Q1"),
                "human_review_completed": True,
                "reviewed_all_rows": True,
                "source_evidence_used": True,
                "model_suggestions_advisory_only": True,
            }
        ),
        encoding="utf-8",
    )
    return provenance, registry


def _complete_batches(output_dir: Path, manifest: dict) -> None:
    for batch in manifest["batches"]:
        path = output_dir / batch["path"]
        fields, rows = read_csv(path)
        for row in rows:
            row["qa_review_status"] = "human_Q1_reviewed"
            for field in RUBRIC_FIELDS:
                row[f"author_qa_feature_{field}"] = "no"
            row["author_qa_strict_eligible"] = "false"
            row["author_qa_primary_exclusion_reason"] = "stable_entity_id"
            row["author_qa_confidence"] = "4"
            row["author_qa_notes"] = "Human Q1 checked the supplied source evidence."
        write_csv(path, fields, rows)


def test_prepare_and_merge_Q1_batches(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["rows"] == 699
    assert [batch["rows"] for batch in manifest["batches"]] == [100] * 6 + [99]
    assert manifest["human_gate_unlocked"] is False
    assert manifest["prevalence_or_recall_claim_allowed"] is False
    first_fields, first_rows = read_csv(output_dir / manifest["batches"][0]["path"])
    assert "model_suggestion_stable_entity_id" in first_fields
    assert first_rows[0]["model_suggestion_stable_entity_id"] in {
        "yes", "no", "partial", "review_required"
    }
    provenance, registry = _private_gate_files(tmp_path)

    with pytest.raises(ValueError, match="not human-reviewed"):
        merge(
            DEFAULT_TEMPLATE,
            DEFAULT_QUEUE,
            manifest_path,
            output_dir,
            tmp_path / "merged.csv",
            provenance,
            registry,
        )

    _complete_batches(output_dir, manifest)

    merged = tmp_path / "merged.csv"
    reviewed_manifest = merge(
        DEFAULT_TEMPLATE,
        DEFAULT_QUEUE,
        manifest_path,
        output_dir,
        merged,
        provenance,
        registry,
    )
    validate_reviewed_Q1_artifact(
        DEFAULT_QUEUE,
        merged,
        reviewed_manifest,
        output_dir,
        registry,
        DEFAULT_TEMPLATE,
        manifest_path,
        provenance,
    )
    labels = load_author_qa_csv(merged)
    assert len(labels) == 699
    assert all(label["labeler_id"] == "Q1" for label in labels)


def test_merge_rejects_immutable_evidence_changes(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 699)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    path = output_dir / manifest["batches"][0]["path"]
    fields, rows = read_csv(path)
    rows[0]["source_evidence_json"] = "{}"
    write_csv(path, fields, rows)
    provenance, registry = _private_gate_files(tmp_path)
    with pytest.raises(ValueError, match="frozen projection changed"):
        merge(
            DEFAULT_TEMPLATE,
            DEFAULT_QUEUE,
            manifest_path,
            output_dir,
            tmp_path / "merged.csv",
            provenance,
            registry,
        )


def test_prepare_rejects_nonempty_output_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    with pytest.raises(ValueError, match="not empty"):
        prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)


def test_prepare_binds_template_evidence_to_queue(tmp_path: Path) -> None:
    fields, rows = read_csv(DEFAULT_TEMPLATE)
    rows[0]["source_evidence_json"], rows[1]["source_evidence_json"] = (
        rows[1]["source_evidence_json"],
        rows[0]["source_evidence_json"],
    )
    changed = tmp_path / "changed.csv"
    write_csv(changed, fields, rows)
    with pytest.raises(ValueError, match="source evidence mismatch"):
        prepare(changed, DEFAULT_QUEUE, tmp_path / "batches", 100)


def test_prepare_binds_queue_derived_review_columns(tmp_path: Path) -> None:
    fields, rows = read_csv(DEFAULT_TEMPLATE)
    rows[0]["review_priority"] = "3"
    changed = tmp_path / "changed.csv"
    write_csv(changed, fields, rows)
    with pytest.raises(ValueError, match="queue-derived columns mismatch"):
        prepare(changed, DEFAULT_QUEUE, tmp_path / "batches", 100)


def test_force_rebuild_cleans_only_generated_Q1_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 699)
    prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100, force=True)
    assert not (output_dir / "public_recall_author_Q1_batch_08.csv").exists()
    assert len(list(output_dir.glob("public_recall_author_Q1_batch_*.csv"))) == 7
    (output_dir / "reviewer_notes.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="unrelated files"):
        prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100, force=True)


def test_force_validation_failure_preserves_existing_batches(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    before = {
        path.name: path.read_bytes() for path in output_dir.iterdir() if path.is_file()
    }
    fields, rows = read_csv(DEFAULT_TEMPLATE)
    rows[0]["review_priority"] = "3"
    invalid_template = tmp_path / "invalid.csv"
    write_csv(invalid_template, fields, rows)
    with pytest.raises(ValueError, match="queue-derived columns mismatch"):
        prepare(invalid_template, DEFAULT_QUEUE, output_dir, 100, force=True)
    after = {
        path.name: path.read_bytes() for path in output_dir.iterdir() if path.is_file()
    }
    assert manifest_path.is_file()
    assert after == before


def test_merge_rejects_manifest_or_batch_assignment_changes(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["batches"][0]["first_blind_unit_id"] = "PU-TAMPERED"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    provenance, registry = _private_gate_files(tmp_path)
    with pytest.raises(ValueError, match="manifest metadata mismatch"):
        merge(
            DEFAULT_TEMPLATE,
            DEFAULT_QUEUE,
            manifest_path,
            output_dir,
            tmp_path / "merged.csv",
            provenance,
            registry,
        )


def test_Q1_and_annotator_role_overlap_is_rejected(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 699)
    provenance, registry = _private_gate_files(tmp_path, overlap=True)
    with pytest.raises(ValueError, match="cross-role participant overlap"):
        merge(
            DEFAULT_TEMPLATE,
            DEFAULT_QUEUE,
            manifest_path,
            output_dir,
            tmp_path / "merged.csv",
            provenance,
            registry,
        )


def test_reviewed_manifest_rejects_changed_batch(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _complete_batches(output_dir, manifest)
    provenance, registry = _private_gate_files(tmp_path)
    merged = tmp_path / "merged.csv"
    reviewed_manifest = merge(
        DEFAULT_TEMPLATE,
        DEFAULT_QUEUE,
        manifest_path,
        output_dir,
        merged,
        provenance,
        registry,
    )
    batch_path = output_dir / manifest["batches"][0]["path"]
    batch_path.write_bytes(batch_path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="batch hash mismatch"):
        validate_reviewed_Q1_artifact(
            DEFAULT_QUEUE,
            merged,
            reviewed_manifest,
            output_dir,
            registry,
            DEFAULT_TEMPLATE,
            manifest_path,
            provenance,
        )


def test_formal_ingestion_rejects_nonstandard_batch_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 699)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _complete_batches(output_dir, manifest)
    provenance, registry = _private_gate_files(tmp_path)
    merged = tmp_path / "merged.csv"
    reviewed_manifest = merge(
        DEFAULT_TEMPLATE,
        DEFAULT_QUEUE,
        manifest_path,
        output_dir,
        merged,
        provenance,
        registry,
    )
    with pytest.raises(ValueError, match="batch manifest is invalid"):
        validate_reviewed_Q1_artifact(
            DEFAULT_QUEUE,
            merged,
            reviewed_manifest,
            output_dir,
            registry,
            DEFAULT_TEMPLATE,
            manifest_path,
            provenance,
        )


def test_formal_ingestion_reconstructs_merged_csv(tmp_path: Path) -> None:
    output_dir = tmp_path / "batches"
    manifest_path = prepare(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output_dir, 100)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _complete_batches(output_dir, manifest)
    provenance, registry = _private_gate_files(tmp_path)
    merged = tmp_path / "merged.csv"
    reviewed_manifest = merge(
        DEFAULT_TEMPLATE,
        DEFAULT_QUEUE,
        manifest_path,
        output_dir,
        merged,
        provenance,
        registry,
    )
    fields, rows = read_csv(merged)
    rows[0]["author_qa_notes"] = "Different but still syntactically valid human note."
    write_csv(merged, fields, rows)
    reviewed = json.loads(reviewed_manifest.read_text(encoding="utf-8"))
    from tri.end_to_end_decision_decomposition import sha256_path

    reviewed["reviewed_csv_sha256"] = sha256_path(merged)
    reviewed_manifest.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match="reconstruction from locked batches"):
        validate_reviewed_Q1_artifact(
            DEFAULT_QUEUE,
            merged,
            reviewed_manifest,
            output_dir,
            registry,
            DEFAULT_TEMPLATE,
            manifest_path,
            provenance,
        )


def test_independent_ingestion_requires_same_role_registry_as_Q1(tmp_path: Path) -> None:
    _, registry = _private_gate_files(tmp_path)
    from tri.end_to_end_decision_decomposition import sha256_path

    q1_manifest = {
        "version": "TRI-public-recall-author-Q1-reviewed-v1",
        "reviewer_role": "Q1",
        "human_review_completed": True,
        "human_gate_unlocked": False,
        "prevalence_or_recall_claim_allowed": False,
        "private_role_registry_sha256": sha256_path(registry),
    }
    validate_shared_role_registry(q1_manifest, registry)
    replacement = tmp_path / "replacement_registry.json"
    replacement.write_text(registry.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="share Q1's locked private role registry"):
        validate_shared_role_registry(q1_manifest, replacement)
