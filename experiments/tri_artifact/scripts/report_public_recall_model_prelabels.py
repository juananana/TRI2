#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tri.end_to_end_decision_decomposition import canonical_json, load_jsonl, sha256_path
from tri.public_recall_model_prelabels import (
    MODEL_PRELABELERS,
    build_incomplete_review_report,
    build_postrun_quality_audit,
    build_review_report,
    load_packet,
    validate_run_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET_ROOT = ROOT / "data" / "public_recall_model_prelabel_packets_v4"
PROTOCOL = ROOT / "reports" / "TRI_public_recall_model_prelabels_protocol.md"


def labeled_paths(values: list[str]) -> dict[str, Path]:
    output = {}
    for value in values:
        if "=" not in value:
            raise SystemExit("run inputs must use LABELER=PATH")
        labeler, raw_path = value.split("=", 1)
        if labeler not in MODEL_PRELABELERS or labeler in output:
            raise SystemExit(f"unexpected or duplicate model prelabeler: {labeler}")
        output[labeler] = Path(raw_path)
    if set(output) != set(MODEL_PRELABELERS):
        raise SystemExit("review report requires M1, M2, and M3 runs")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a provisional model-prelabel review queue.")
    parser.add_argument("--run", action="append", default=[], required=True, metavar="M1=PATH")
    parser.add_argument("--smoke", action="append", default=[], required=True, metavar="M1=PATH")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="write an ineligible failure-aware author-QA queue without consensus claims",
    )
    parser.add_argument(
        "--private-key",
        type=Path,
        help="private role key used only for a separate post-run quality audit",
    )
    parser.add_argument(
        "--quality-output",
        type=Path,
        help="write aggregate role/control diagnostics separately from the public report",
    )
    args = parser.parse_args()
    if (args.private_key is None) != (args.quality_output is None):
        raise SystemExit("--private-key and --quality-output must be supplied together")
    run_paths = labeled_paths(args.run)
    smoke_paths = labeled_paths(args.smoke)
    manifest = PACKET_ROOT / "manifest.json"
    packets = {
        labeler: load_packet(
            PACKET_ROOT / "model_prelabels" / f"model_prelabel_{labeler}.jsonl",
            manifest,
            labeler,
        )
        for labeler in MODEL_PRELABELERS
    }
    runs = {labeler: load_jsonl(path) for labeler, path in run_paths.items()}
    packet_paths = {
        labeler: PACKET_ROOT / "model_prelabels" / f"model_prelabel_{labeler}.jsonl"
        for labeler in MODEL_PRELABELERS
    }
    packet_sha256 = {
        labeler: sha256_path(path) for labeler, path in packet_paths.items()
    }
    protocol_sha256 = sha256_path(PROTOCOL)
    smoke_runs = {labeler: load_jsonl(path) for labeler, path in smoke_paths.items()}
    health_smoke_sha256 = {
        labeler: sha256_path(path) for labeler, path in smoke_paths.items()
    }
    for labeler in MODEL_PRELABELERS:
        validate_run_inventory(
            smoke_runs[labeler],
            packets[labeler][:8],
            labeler,
            "smoke",
            packet_sha256[labeler],
            protocol_sha256,
        )
        if any(not row["complete"] for row in smoke_runs[labeler]):
            raise ValueError(f"{labeler} health smoke contains incomplete rows")
    builder = build_incomplete_review_report if args.allow_incomplete else build_review_report
    report, queue = builder(
        runs, packets, packet_sha256, protocol_sha256, health_smoke_sha256
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    return_paths = {}
    for labeler in MODEL_PRELABELERS:
        suffix = "_partial_returns.jsonl" if args.allow_incomplete else "_returns.jsonl"
        path = args.output.with_name(args.output.stem + f"_{labeler}{suffix}")
        path.write_text(
            "".join(
                canonical_json(row["component"]["parsed"]) + "\n"
                for row in runs[labeler]
                if row["component"].get("parsed") is not None
            ),
            encoding="utf-8",
        )
        return_paths[labeler] = path
    report["provenance"] = {
        "packet_manifest_sha256": sha256_path(manifest),
        "packet_sha256": packet_sha256,
        "protocol_sha256": protocol_sha256,
        "health_smoke_sha256": health_smoke_sha256,
        "run_sha256": {
            labeler: sha256_path(path) for labeler, path in run_paths.items()
        },
        "model_return_sha256": {
            labeler: sha256_path(path) for labeler, path in return_paths.items()
        },
        "formal_review_report_eligible": not args.allow_incomplete,
    }
    queue_path = args.output.with_name(args.output.stem + "_author_qa_queue.jsonl")
    queue_path.write_text(
        "".join(canonical_json(row) + "\n" for row in queue), encoding="utf-8"
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    quality_output = None
    if args.private_key is not None:
        manifest_value = json.loads(manifest.read_text(encoding="utf-8"))
        expected_key_sha256 = manifest_value.get("private_annotation_key_sha256")
        quality = build_postrun_quality_audit(
            queue,
            load_jsonl(args.private_key),
            private_key_sha256=sha256_path(args.private_key),
            expected_private_key_sha256=expected_key_sha256,
        )
        quality["provenance"]["public_report_sha256"] = sha256_path(args.output)
        args.quality_output.parent.mkdir(parents=True, exist_ok=True)
        args.quality_output.write_text(
            json.dumps(quality, indent=2) + "\n", encoding="utf-8"
        )
        quality_output = str(args.quality_output)
    csv_path = args.output.with_name(args.output.stem + "_author_qa_template.csv")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "review_priority",
            "blind_unit_id",
            "display_dataset",
            "complete_model_panel",
            "missing_model_labelers",
            "rubric_disagreement_fields",
            "strict_positive_votes",
            "strict_unanimous",
            "provisional_majority_strict",
            "mean_model_confidence",
            "source_evidence_json",
            "model_labels_json",
            *[f"author_qa_feature_{field}" for field in packets["M1"][0]["rubric_fields"]],
            "author_qa_strict_eligible",
            "author_qa_primary_exclusion_reason",
            "author_qa_confidence",
            "author_qa_notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in queue:
            values = {field: row.get(field) for field in fields}
            values["missing_model_labelers"] = ";".join(
                row.get("missing_model_labelers") or []
            )
            values["rubric_disagreement_fields"] = ";".join(
                row.get("rubric_disagreement_fields") or []
            )
            values["source_evidence_json"] = canonical_json(row["source_evidence"])
            values["model_labels_json"] = canonical_json(row["model_labels"])
            writer.writerow(values)
    print(json.dumps({
        **report,
        "queue": str(queue_path),
        "author_qa_template": str(csv_path),
        "model_returns": {
            labeler: str(path) for labeler, path in return_paths.items()
        },
        "quality_output": quality_output,
    }, indent=2))


if __name__ == "__main__":
    main()
