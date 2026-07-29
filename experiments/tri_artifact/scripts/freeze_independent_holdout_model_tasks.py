from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tri.independent_language_holdout import (
    build_model_tasks,
    clear_complete_pairs,
    jsonl_bytes,
    load_jsonl,
    resolve_blind_annotation_returns,
    sha256_path,
    validate_annotation_returns,
)


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def validate_annotation_provenance(
    path: Path, annotation_returns: Path, annotation_key: Path
) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("status") != "independent-human-annotation-complete":
        raise ValueError("annotation provenance is not complete independent-human evidence")
    annotators = manifest.get("annotators", {})
    if set(annotators) != {"A1", "A2", "A3"}:
        raise ValueError("annotation provenance requires exactly human A1-A3")
    for annotator_id, record in annotators.items():
        if (
            record.get("source") != "independent_human"
            or record.get("completed") is not True
            or record.get("blind") is not True
            or record.get("saw_model_prelabels_before_lock") is not False
        ):
            raise ValueError(f"invalid independent-human provenance for {annotator_id}")
    if manifest.get("annotation_returns_sha256") != sha256_path(annotation_returns):
        raise ValueError("annotation provenance does not match returned labels")
    if manifest.get("private_annotation_key_sha256") != sha256_path(annotation_key):
        raise ValueError("annotation provenance does not match the blind-ID key")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--annotation-returns", type=Path, required=True)
    parser.add_argument("--annotation-key", type=Path, required=True)
    parser.add_argument("--processing-manifest", type=Path, required=True)
    parser.add_argument("--eligibility-ledger", type=Path, required=True)
    parser.add_argument("--annotation-provenance", type=Path, required=True)
    parser.add_argument(
        "--tasks",
        type=Path,
        default=ROOT / "data" / "independent_language_holdout_v1.jsonl",
    )
    args = parser.parse_args()
    pairs = load_jsonl(args.packet / "private_scenario_key.jsonl")
    authored_path = args.packet / "locked_authored_instructions.jsonl"
    authored = load_jsonl(authored_path)
    processing = json.loads(args.processing_manifest.read_text(encoding="utf-8"))
    if not processing.get("eligibility_ledger_sha256"):
        raise ValueError("formal model freeze requires a validated eligibility ledger")
    if processing["eligibility_ledger_sha256"] != sha256_path(args.eligibility_ledger):
        raise ValueError("processing manifest does not match the eligibility ledger")
    if processing.get("locked_authored_instructions_sha256") != sha256_path(authored_path):
        raise ValueError("processing manifest does not match locked authored instructions")
    if processing.get("private_scenario_key_sha256") != sha256_path(
        args.packet / "private_scenario_key.jsonl"
    ):
        raise ValueError("processing manifest does not match private scenario key")
    if processing.get("private_annotation_key_sha256") != sha256_path(args.annotation_key):
        raise ValueError("processing manifest does not match the blind-ID key")
    validate_annotation_provenance(
        args.annotation_provenance, args.annotation_returns, args.annotation_key
    )
    blind_rows = resolve_blind_annotation_returns(
        read_csv(args.annotation_returns), load_jsonl(args.annotation_key)
    )
    annotations = validate_annotation_returns(blind_rows, authored)
    clarity = clear_complete_pairs(authored, annotations)
    tasks = build_model_tasks(authored, pairs, clarity)
    if args.tasks.exists():
        raise SystemExit(f"Refusing to overwrite {args.tasks}")
    args.tasks.write_bytes(jsonl_bytes(tasks))
    report = {
        "evidence_status": "post-primary human audit; model experiment not yet run",
        **{key: value for key, value in clarity.items() if key != "item_clear"},
        "all_rows": len(tasks),
        "task_sha256": sha256_path(args.tasks),
        "authored_sha256": sha256_path(authored_path),
        "annotation_returns_sha256": sha256_path(args.annotation_returns),
        "processing_manifest_sha256": sha256_path(args.processing_manifest),
        "annotation_provenance_sha256": sha256_path(args.annotation_provenance),
    }
    report_path = ROOT / "reports" / "independent_language_holdout_clarity_v1.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
