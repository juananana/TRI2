#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from scripts.prepare_public_recall_author_Q1_batches import (
    DEFAULT_QUEUE,
    DEFAULT_TEMPLATE,
    model_suggestions,
    read_csv,
    validate_inventory,
)
from tri.end_to_end_decision_decomposition import load_jsonl, sha256_path
from tri.public_recall_calibrated_audit import RUBRIC_FIELDS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "human_studies" / "public_recall_Q0_model_drafts_v1.csv"
VERSION = "TRI-public-recall-Q0-model-panel-drafts-v1"
STATUS = "model_only_draft_pending_human_review"
Q0_FIELDS = (
    "q0_status",
    *(f"q0_feature_{field}" for field in RUBRIC_FIELDS),
    "q0_strict_eligible",
    "q0_primary_exclusion_reason",
    "q0_panel_agreement",
    "q0_missing_model_labelers",
    "q0_tie_fields",
    "q0_notes",
)


def build_draft(row: dict[str, str]) -> dict[str, str]:
    labels = json.loads(row["model_labels_json"])
    suggestions = model_suggestions(row)
    feature_values = {
        field: suggestions[f"model_suggestion_{field}"] for field in RUBRIC_FIELDS
    }
    ties = [field for field, value in feature_values.items() if value == "review_required"]
    available = [label for label in labels.values() if label is not None]
    missing = sorted({"M1", "M2", "M3"} - set(labels))
    if ties:
        strict = "review_required"
        exclusion = "review_required"
    elif all(value == "yes" for value in feature_values.values()):
        strict = "true"
        exclusion = "NONE"
    else:
        strict = "false"
        proposed_reasons = Counter(
            label["primary_exclusion_reason"]
            for label in available
            if label["primary_exclusion_reason"] in RUBRIC_FIELDS
            and feature_values[label["primary_exclusion_reason"]] != "yes"
        )
        if proposed_reasons:
            top = max(proposed_reasons.values())
            exclusion = sorted(
                reason for reason, count in proposed_reasons.items() if count == top
            )[0]
        else:
            exclusion = next(
                field for field in RUBRIC_FIELDS if feature_values[field] != "yes"
            )
    agreement_numerator = 0
    agreement_denominator = 0
    for field in RUBRIC_FIELDS:
        counts = Counter(label["feature_labels"][field] for label in available)
        if counts:
            agreement_numerator += max(counts.values())
            agreement_denominator += sum(counts.values())
    agreement = agreement_numerator / agreement_denominator if agreement_denominator else 0.0
    strict_votes = sum(bool(label["strict_eligible"]) for label in available)
    return {
        "q0_status": STATUS,
        **{f"q0_feature_{field}": value for field, value in feature_values.items()},
        "q0_strict_eligible": strict,
        "q0_primary_exclusion_reason": exclusion,
        "q0_panel_agreement": f"{agreement:.6f}",
        "q0_missing_model_labelers": ";".join(missing),
        "q0_tie_fields": ";".join(ties),
        "q0_notes": (
            "Model-panel draft only; human Q1 must inspect source evidence. "
            f"Available labels={len(available)}/3; strict votes={strict_votes}/{len(available)}."
        ),
    }


def build(template: Path, queue_path: Path, output: Path) -> Path:
    fields, rows = read_csv(template)
    queue = load_jsonl(queue_path)
    validate_inventory(fields, rows, queue)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_fields = [
        "review_priority",
        "blind_unit_id",
        "display_dataset",
        "source_evidence_json",
        "model_labels_json",
        *Q0_FIELDS,
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **{field: row[field] for field in output_fields[:5]},
                    **build_draft(row),
                }
            )
    manifest = {
        "version": VERSION,
        "evidence_status": "model-assisted review draft; not human evidence",
        "rows": len(rows),
        "template_sha256": sha256_path(template),
        "queue_sha256": sha256_path(queue_path),
        "draft_csv_sha256": sha256_path(output),
        "q0_status": STATUS,
        "writes_human_Q1_fields": False,
        "human_gate_unlocked": False,
        "independent_human_evidence": False,
        "prevalence_or_recall_claim_allowed": False,
    }
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build non-human Q0 drafts for later public-recall Q1 review."
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(build(args.template, args.queue, args.output))


if __name__ == "__main__":
    main()
