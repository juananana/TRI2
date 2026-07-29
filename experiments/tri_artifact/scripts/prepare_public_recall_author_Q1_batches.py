#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import tempfile
import uuid
from collections import Counter
from pathlib import Path

from tri.end_to_end_decision_decomposition import canonical_json, load_jsonl, sha256_path
from tri.private_role_registry import validate_private_role_registry
from tri.public_recall_calibrated_audit import RUBRIC_FIELDS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = (
    ROOT / "reports" / "public_recall_model_prelabels_partial_v1_author_qa_template.csv"
)
DEFAULT_QUEUE = (
    ROOT / "reports" / "public_recall_model_prelabels_partial_v1_author_qa_queue.jsonl"
)
DEFAULT_OUTPUT_DIR = (
    ROOT / "human_studies" / "public_recall_author_Q1_batches_v1"
)
VERSION = "TRI-public-recall-author-Q1-batches-v1"
REVIEWED_VERSION = "TRI-public-recall-author-Q1-reviewed-v1"
REVIEWER_PROVENANCE_VERSION = "TRI-public-recall-Q1-reviewer-provenance-v1"
STATUS_FIELD = "qa_review_status"
SUGGESTION_FIELDS = tuple(f"model_suggestion_{field}" for field in RUBRIC_FIELDS)
BATCH_FIELDS = (
    "qa_batch_id",
    "qa_batch_row",
    STATUS_FIELD,
    *SUGGESTION_FIELDS,
    "model_suggestion_tie_fields",
)
EDITABLE_FIELDS = {
    *(f"author_qa_feature_{field}" for field in RUBRIC_FIELDS),
    "author_qa_strict_eligible",
    "author_qa_primary_exclusion_reason",
    "author_qa_confidence",
    "author_qa_notes",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        return list(reader.fieldnames), list(reader)


def csv_bytes(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(csv_bytes(fields, rows))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_inventory(
    fields: list[str], rows: list[dict[str, str]], queue: list[dict]
) -> None:
    required = {
        "blind_unit_id",
        "review_priority",
        "source_evidence_json",
        "model_labels_json",
        *EDITABLE_FIELDS,
    }
    if not required <= set(fields):
        raise ValueError(f"Q1 template missing columns: {sorted(required - set(fields))}")
    row_ids = [row["blind_unit_id"] for row in rows]
    queue_ids = [row["blind_unit_id"] for row in queue]
    if len(rows) != 699 or len(set(row_ids)) != 699 or row_ids != queue_ids:
        raise ValueError("Q1 template must match the ordered 699-row review queue")
    for row, queued in zip(rows, queue, strict=True):
        try:
            source = json.loads(row["source_evidence_json"])
            labels = json.loads(row["model_labels_json"])
        except json.JSONDecodeError as exc:
            raise ValueError(f"Q1 template has invalid JSON: {row['blind_unit_id']}") from exc
        if canonical_json(source) != canonical_json(queued.get("source_evidence")):
            raise ValueError(f"Q1 template source evidence mismatch: {row['blind_unit_id']}")
        if canonical_json(labels) != canonical_json(queued.get("model_labels")):
            raise ValueError(f"Q1 template model labels mismatch: {row['blind_unit_id']}")
        expected_columns = {
            "review_priority": str(queued["review_priority"]),
            "blind_unit_id": str(queued["blind_unit_id"]),
            "display_dataset": str(queued["display_dataset"]),
            "complete_model_panel": str(queued["complete_model_panel"]),
            "missing_model_labelers": ";".join(queued.get("missing_model_labelers") or []),
            "rubric_disagreement_fields": ";".join(
                queued.get("rubric_disagreement_fields") or []
            ),
            "strict_positive_votes": str(queued["strict_positive_votes"]),
            "strict_unanimous": (
                "" if queued.get("strict_unanimous") is None else str(queued["strict_unanimous"])
            ),
            "provisional_majority_strict": (
                ""
                if queued.get("provisional_majority_strict") is None
                else str(queued["provisional_majority_strict"])
            ),
            "mean_model_confidence": (
                ""
                if queued.get("mean_model_confidence") is None
                else str(queued["mean_model_confidence"])
            ),
        }
        if any(row[field] != value for field, value in expected_columns.items()):
            raise ValueError(f"Q1 template queue-derived columns mismatch: {row['blind_unit_id']}")


def model_suggestions(row: dict[str, str]) -> dict[str, str]:
    labels = json.loads(row["model_labels_json"])
    suggestions: dict[str, str] = {}
    ties = []
    for field in RUBRIC_FIELDS:
        counts = Counter(
            label["feature_labels"][field]
            for label in labels.values()
            if label is not None
        )
        if not counts:
            value = "review_required"
            ties.append(field)
        else:
            top = max(counts.values())
            winners = sorted(value for value, count in counts.items() if count == top)
            if len(winners) != 1:
                value = "review_required"
                ties.append(field)
            else:
                value = winners[0]
        suggestions[f"model_suggestion_{field}"] = value
    suggestions["model_suggestion_tie_fields"] = ";".join(ties)
    return suggestions


def frozen_projection(
    rows: list[dict[str, str]], original_fields: list[str]
) -> str:
    immutable_fields = [field for field in original_fields if field not in EDITABLE_FIELDS]
    projection_fields = [
        "qa_batch_id",
        "qa_batch_row",
        *SUGGESTION_FIELDS,
        "model_suggestion_tie_fields",
        *immutable_fields,
    ]
    return sha256_bytes(
        ("".join(canonical_json({field: row[field] for field in projection_fields}) + "\n" for row in rows)).encode("utf-8")
    )


def expected_batches(
    rows: list[dict[str, str]], original_fields: list[str], batch_size: int
) -> list[tuple[str, str, list[dict[str, str]]]]:
    output = []
    for start in range(0, len(rows), batch_size):
        batch_number = len(output) + 1
        batch_id = f"Q1-{batch_number:02d}"
        batch_rows = []
        for offset, row in enumerate(rows[start : start + batch_size], start=1):
            batch_rows.append(
                {
                    "qa_batch_id": batch_id,
                    "qa_batch_row": str(offset),
                    STATUS_FIELD: "pending_human_Q1_review",
                    **model_suggestions(row),
                    **row,
                }
            )
        name = f"public_recall_author_Q1_batch_{batch_number:02d}.csv"
        output.append((batch_id, name, batch_rows))
    return output


def prepare(
    template: Path,
    queue_path: Path,
    output_dir: Path,
    batch_size: int,
    force: bool = False,
) -> Path:
    if batch_size <= 0:
        raise ValueError("batch size must be positive")
    fields, rows = read_csv(template)
    queue = load_jsonl(queue_path)
    validate_inventory(fields, rows, queue)
    batch_fields = [*BATCH_FIELDS, *fields]
    planned_batches = expected_batches(rows, fields, batch_size)

    existing = list(output_dir.iterdir()) if output_dir.exists() else []
    if existing and not force:
        raise ValueError("Q1 output directory is not empty; use --force only to rebuild intentionally")
    if existing:
        allowed = re.compile(r"public_recall_author_Q1_batch_\d{2}\.csv")
        unexpected = [path.name for path in existing if path.name != "manifest.json" and not allowed.fullmatch(path.name)]
        if unexpected:
            raise ValueError(f"Q1 output directory contains unrelated files: {sorted(unexpected)}")
        for path in existing:
            if not path.is_file():
                raise ValueError(f"Q1 output directory contains a non-file entry: {path.name}")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staged_dir = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.staged-", dir=output_dir.parent)
    )
    backup_dir: Path | None = None
    try:
        batches = []
        for batch_id, name, batch_rows in planned_batches:
            path = staged_dir / name
            write_csv(path, batch_fields, batch_rows)
            batches.append(
                {
                    "batch_id": batch_id,
                    "path": name,
                    "rows": len(batch_rows),
                    "sha256_before_review": sha256_path(path),
                    "frozen_projection_sha256": frozen_projection(batch_rows, fields),
                    "priority_counts": dict(
                        sorted(Counter(row["review_priority"] for row in batch_rows).items())
                    ),
                    "first_blind_unit_id": batch_rows[0]["blind_unit_id"],
                    "last_blind_unit_id": batch_rows[-1]["blind_unit_id"],
                }
            )
        manifest = {
            "version": VERSION,
            "evidence_status": (
                "author QA work packets over model-assisted labels; never independent-human evidence"
            ),
            "rows": len(rows),
            "batch_size": batch_size,
            "batches": batches,
            "template_sha256": sha256_path(template),
            "queue_sha256": sha256_path(queue_path),
            "required_review_status": "human_Q1_reviewed",
            "human_gate_unlocked": False,
            "prevalence_or_recall_claim_allowed": False,
        }
        (staged_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        for batch in batches:
            if sha256_path(staged_dir / batch["path"]) != batch["sha256_before_review"]:
                raise ValueError(f"staged Q1 batch hash mismatch: {batch['batch_id']}")

        if output_dir.exists():
            backup_dir = output_dir.with_name(
                f".{output_dir.name}.backup-{uuid.uuid4().hex}"
            )
            output_dir.rename(backup_dir)
        try:
            staged_dir.rename(output_dir)
        except Exception:
            if backup_dir is not None and backup_dir.exists() and not output_dir.exists():
                backup_dir.rename(output_dir)
            raise
        if backup_dir is not None:
            shutil.rmtree(backup_dir)
        return output_dir / "manifest.json"
    finally:
        if staged_dir.exists():
            shutil.rmtree(staged_dir)


def merge(
    template: Path,
    queue_path: Path,
    manifest_path: Path,
    input_dir: Path,
    output: Path,
    reviewer_provenance_path: Path,
    role_registry_path: Path,
) -> Path:
    original_fields, original_rows = read_csv(template)
    queue = load_jsonl(queue_path)
    validate_inventory(original_fields, original_rows, queue)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("version") != VERSION
        or manifest.get("rows") != 699
        or manifest.get("template_sha256") != sha256_path(template)
        or manifest.get("queue_sha256") != sha256_path(queue_path)
    ):
        raise ValueError("Q1 batch manifest does not match the frozen template and queue")
    reviewer_provenance = json.loads(reviewer_provenance_path.read_text(encoding="utf-8"))
    role_registry = json.loads(role_registry_path.read_text(encoding="utf-8"))
    role_hashes = validate_private_role_registry(role_registry, ("Q1", "A1", "A2", "A3"))
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
    original_by_id = {row["blind_unit_id"]: row for row in original_rows}
    reviewed: list[dict[str, str]] = []
    observed_ids: set[str] = set()
    immutable_fields = set(original_fields) - EDITABLE_FIELDS
    expected = expected_batches(original_rows, original_fields, manifest["batch_size"])
    if len(manifest.get("batches", [])) != len(expected):
        raise ValueError("Q1 batch manifest has an unexpected batch count")
    reviewed_batch_hashes = []
    for batch, (expected_batch_id, expected_path, expected_rows) in zip(
        manifest["batches"], expected, strict=True
    ):
        expected_meta = {
            "batch_id": expected_batch_id,
            "path": expected_path,
            "rows": len(expected_rows),
            "sha256_before_review": sha256_bytes(
                csv_bytes([*BATCH_FIELDS, *original_fields], expected_rows)
            ),
            "frozen_projection_sha256": frozen_projection(expected_rows, original_fields),
            "priority_counts": dict(
                sorted(Counter(row["review_priority"] for row in expected_rows).items())
            ),
            "first_blind_unit_id": expected_rows[0]["blind_unit_id"],
            "last_blind_unit_id": expected_rows[-1]["blind_unit_id"],
        }
        if batch != expected_meta:
            raise ValueError(f"Q1 batch manifest metadata mismatch: {expected_path}")
        fields, rows = read_csv(input_dir / batch["path"])
        if fields != [*BATCH_FIELDS, *original_fields]:
            raise ValueError(f"Q1 batch header mismatch: {batch['path']}")
        if len(rows) != batch["rows"]:
            raise ValueError(f"Q1 batch row-count mismatch: {batch['path']}")
        if frozen_projection(rows, original_fields) != batch["frozen_projection_sha256"]:
            raise ValueError(f"Q1 batch assignment or frozen projection changed: {batch['path']}")
        for expected_row, row in zip(expected_rows, rows, strict=True):
            blind_id = row["blind_unit_id"]
            if blind_id in observed_ids or blind_id not in original_by_id:
                raise ValueError(f"duplicate or unexpected Q1 blind ID: {blind_id}")
            observed_ids.add(blind_id)
            if (
                row["qa_batch_id"] != expected_row["qa_batch_id"]
                or row["qa_batch_row"] != expected_row["qa_batch_row"]
            ):
                raise ValueError(f"Q1 batch assignment changed: {blind_id}")
            if any(row[field] != original_by_id[blind_id][field] for field in immutable_fields):
                raise ValueError(f"immutable Q1 evidence fields changed: {blind_id}")
            expected_suggestions = model_suggestions(original_by_id[blind_id])
            if any(row[field] != value for field, value in expected_suggestions.items()):
                raise ValueError(f"model-suggestion fields changed: {blind_id}")
            if row[STATUS_FIELD] != "human_Q1_reviewed":
                raise ValueError(f"Q1 row is not human-reviewed: {blind_id}")
            if any(not row[field].strip() for field in EDITABLE_FIELDS):
                raise ValueError(f"Q1 row has incomplete human fields: {blind_id}")
            reviewed.append({field: row[field] for field in original_fields})
        reviewed_batch_hashes.append(
            {"batch_id": batch["batch_id"], "path": batch["path"], "sha256": sha256_path(input_dir / batch["path"])}
        )
    expected_ids = [row["blind_unit_id"] for row in original_rows]
    reviewed_by_id = {row["blind_unit_id"]: row for row in reviewed}
    if set(reviewed_by_id) != set(expected_ids):
        raise ValueError("reviewed Q1 batches do not cover the frozen 699-row inventory")
    write_csv(output, original_fields, [reviewed_by_id[blind_id] for blind_id in expected_ids])
    reviewed_manifest = {
        "version": REVIEWED_VERSION,
        "evidence_status": "author QA of model-assisted labels; not independent-human evidence",
        "rows": len(expected_ids),
        "reviewer_role": "Q1",
        "participant_token_sha256": role_hashes["Q1"],
        "human_review_completed": True,
        "model_suggestions_advisory_only": True,
        "human_gate_unlocked": False,
        "prevalence_or_recall_claim_allowed": False,
        "template_sha256": sha256_path(template),
        "queue_sha256": sha256_path(queue_path),
        "batch_manifest_sha256": sha256_path(manifest_path),
        "reviewer_provenance_sha256": sha256_path(reviewer_provenance_path),
        "private_role_registry_sha256": sha256_path(role_registry_path),
        "reviewed_batches": reviewed_batch_hashes,
        "reviewed_csv_sha256": sha256_path(output),
    }
    reviewed_manifest_path = output.with_suffix(".manifest.json")
    reviewed_manifest_path.write_text(
        json.dumps(reviewed_manifest, indent=2) + "\n", encoding="utf-8"
    )
    return reviewed_manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare or merge public-recall author-Q1 batches.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    prepare_parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    prepare_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    prepare_parser.add_argument("--batch-size", type=int, default=100)
    prepare_parser.add_argument("--force", action="store_true")
    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    merge_parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    merge_parser.add_argument("--manifest", type=Path, required=True)
    merge_parser.add_argument("--input-dir", type=Path, required=True)
    merge_parser.add_argument("--output", type=Path, required=True)
    merge_parser.add_argument("--reviewer-provenance", type=Path, required=True)
    merge_parser.add_argument("--private-role-registry", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        manifest = prepare(args.template, args.queue, args.output_dir, args.batch_size, args.force)
        print(manifest)
    else:
        reviewed_manifest = merge(
            args.template,
            args.queue,
            args.manifest,
            args.input_dir,
            args.output,
            args.reviewer_provenance,
            args.private_role_registry,
        )
        print(reviewed_manifest)


if __name__ == "__main__":
    main()
