#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path

from tri.end_to_end_decision_decomposition import canonical_json, load_jsonl, sha256_path
from tri.private_role_registry import validate_private_role_registry
from tri.public_recall_calibrated_audit import RUBRIC_FIELDS, validate_annotation_return
from tri.public_recall_model_prelabels import build_author_qa_report

from scripts.prepare_public_recall_author_Q1_batches import (
    REVIEWED_VERSION,
    REVIEWER_PROVENANCE_VERSION,
    VERSION as BATCH_VERSION,
    merge as rebuild_reviewed_Q1,
)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def load_author_qa_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    output = []
    for row in rows:
        item = {
            "labeler_id": "Q1",
            "blind_unit_id": row["blind_unit_id"],
            "feature_labels": {
                field: row[f"author_qa_feature_{field}"].strip().lower()
                for field in RUBRIC_FIELDS
            },
            "strict_eligible": parse_bool(row["author_qa_strict_eligible"]),
            "primary_exclusion_reason": row[
                "author_qa_primary_exclusion_reason"
            ].strip(),
            "confidence": int(row["author_qa_confidence"]),
            "notes": row["author_qa_notes"].strip(),
        }
        output.append(validate_annotation_return(item, "Q1"))
    return output


def validate_reviewed_Q1_artifact(
    queue_path: Path,
    qa_csv: Path,
    review_manifest_path: Path,
    reviewed_batches_dir: Path,
    role_registry_path: Path,
    template_path: Path,
    batch_manifest_path: Path,
    reviewer_provenance_path: Path,
) -> dict:
    manifest = json.loads(review_manifest_path.read_text(encoding="utf-8"))
    registry = json.loads(role_registry_path.read_text(encoding="utf-8"))
    role_hashes = validate_private_role_registry(registry, ("Q1", "A1", "A2", "A3"))
    batch_manifest = json.loads(batch_manifest_path.read_text(encoding="utf-8"))
    reviewer_provenance = json.loads(
        reviewer_provenance_path.read_text(encoding="utf-8")
    )
    expected_batch_ids = [f"Q1-{number:02d}" for number in range(1, 8)]
    batch_records = batch_manifest.get("batches")
    if not (
        batch_manifest.get("version") == BATCH_VERSION
        and batch_manifest.get("rows") == 699
        and batch_manifest.get("batch_size") == 100
        and batch_manifest.get("template_sha256") == sha256_path(template_path)
        and batch_manifest.get("queue_sha256") == sha256_path(queue_path)
        and isinstance(batch_records, list)
        and [item.get("batch_id") for item in batch_records] == expected_batch_ids
        and [item.get("rows") for item in batch_records] == [100] * 6 + [99]
    ):
        raise ValueError("frozen Q1 batch manifest is invalid")
    if not (
        reviewer_provenance.get("version") == REVIEWER_PROVENANCE_VERSION
        and reviewer_provenance.get("status") == "complete"
        and reviewer_provenance.get("reviewer_role") == "Q1"
        and reviewer_provenance.get("participant_token_sha256") == role_hashes["Q1"]
        and reviewer_provenance.get("human_review_completed") is True
        and reviewer_provenance.get("reviewed_all_rows") is True
        and reviewer_provenance.get("source_evidence_used") is True
        and reviewer_provenance.get("model_suggestions_advisory_only") is True
    ):
        raise ValueError("Q1 reviewer provenance is incomplete or inconsistent")
    if not (
        manifest.get("version") == REVIEWED_VERSION
        and manifest.get("rows") == 699
        and manifest.get("reviewer_role") == "Q1"
        and manifest.get("participant_token_sha256") == role_hashes["Q1"]
        and manifest.get("human_review_completed") is True
        and manifest.get("model_suggestions_advisory_only") is True
        and manifest.get("human_gate_unlocked") is False
        and manifest.get("prevalence_or_recall_claim_allowed") is False
        and manifest.get("queue_sha256") == sha256_path(queue_path)
        and manifest.get("template_sha256") == sha256_path(template_path)
        and manifest.get("batch_manifest_sha256") == sha256_path(batch_manifest_path)
        and manifest.get("reviewer_provenance_sha256")
        == sha256_path(reviewer_provenance_path)
        and manifest.get("reviewed_csv_sha256") == sha256_path(qa_csv)
        and manifest.get("private_role_registry_sha256") == sha256_path(role_registry_path)
    ):
        raise ValueError("reviewed Q1 manifest does not match the locked QA artifact")
    batches = manifest.get("reviewed_batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("reviewed Q1 manifest has no reviewed-batch hashes")
    if [item.get("batch_id") for item in batches] != expected_batch_ids or [
        item.get("path") for item in batches
    ] != [item.get("path") for item in batch_records]:
        raise ValueError("reviewed Q1 manifest does not cover the frozen seven batches")
    seen = set()
    for batch in batches:
        if not isinstance(batch, dict) or set(batch) != {"batch_id", "path", "sha256"}:
            raise ValueError("reviewed Q1 manifest has an invalid batch record")
        path = reviewed_batches_dir / batch["path"]
        if batch["batch_id"] in seen or not path.is_file() or sha256_path(path) != batch["sha256"]:
            raise ValueError(f"reviewed Q1 batch hash mismatch: {batch.get('batch_id')}")
        seen.add(batch["batch_id"])
    with tempfile.TemporaryDirectory() as directory:
        rebuilt_csv = Path(directory) / "rebuilt.csv"
        rebuild_reviewed_Q1(
            template_path,
            queue_path,
            batch_manifest_path,
            reviewed_batches_dir,
            rebuilt_csv,
            reviewer_provenance_path,
            role_registry_path,
        )
        if rebuilt_csv.read_bytes() != qa_csv.read_bytes():
            raise ValueError("reviewed Q1 CSV does not match reconstruction from locked batches")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate non-independent author QA of public-recall model prelabels."
    )
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--qa-csv", type=Path, required=True)
    parser.add_argument("--review-manifest", type=Path, required=True)
    parser.add_argument("--reviewed-batches-dir", type=Path, required=True)
    parser.add_argument("--private-role-registry", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--batch-manifest", type=Path, required=True)
    parser.add_argument("--reviewer-provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reviewed_manifest = validate_reviewed_Q1_artifact(
        args.queue,
        args.qa_csv,
        args.review_manifest,
        args.reviewed_batches_dir,
        args.private_role_registry,
        args.template,
        args.batch_manifest,
        args.reviewer_provenance,
    )
    queue = load_jsonl(args.queue)
    labels = load_author_qa_csv(args.qa_csv)
    report = build_author_qa_report(queue, labels)
    report["provenance"] = {
        "queue_sha256": sha256_path(args.queue),
        "qa_csv_sha256": sha256_path(args.qa_csv),
        "review_manifest_sha256": sha256_path(args.review_manifest),
        "private_role_registry_sha256": sha256_path(args.private_role_registry),
        "template_sha256": sha256_path(args.template),
        "batch_manifest_sha256": sha256_path(args.batch_manifest),
        "reviewer_provenance_sha256": sha256_path(args.reviewer_provenance),
        "reviewed_batch_sha256": {
            item["batch_id"]: item["sha256"] for item in reviewed_manifest["reviewed_batches"]
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    labels_path = args.output.with_name(args.output.stem + "_validated_labels.jsonl")
    labels_path.write_text(
        "".join(canonical_json(row) + "\n" for row in labels), encoding="utf-8"
    )
    print(json.dumps({**report, "validated_labels": str(labels_path)}, indent=2))


if __name__ == "__main__":
    main()
