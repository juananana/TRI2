#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.end_to_end_decision_decomposition import canonical_json
from tri.private_role_registry import validate_private_role_registry
from tri.public_recall_calibrated_audit import (
    ANNOTATORS,
    MODEL_PRELABELERS,
    merge_public_annotation_returns,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "human_studies" / "public_recall_calibrated_audit_v4"
Q1_REVIEWED_VERSION = "TRI-public-recall-author-Q1-reviewed-v1"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_labeled_paths(values: list[str], allowed: tuple[str, ...]) -> dict[str, Path]:
    output: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit("annotation paths must use LABELER=PATH")
        labeler, raw_path = value.split("=", 1)
        if labeler not in allowed or labeler in output:
            raise SystemExit(f"unexpected or duplicate annotation labeler: {labeler}")
        output[labeler] = Path(raw_path)
    return output


def validate_shared_role_registry(
    q1_review_manifest: dict, role_registry_path: Path
) -> None:
    if not (
        q1_review_manifest.get("version") == Q1_REVIEWED_VERSION
        and q1_review_manifest.get("reviewer_role") == "Q1"
        and q1_review_manifest.get("human_review_completed") is True
        and q1_review_manifest.get("human_gate_unlocked") is False
        and q1_review_manifest.get("prevalence_or_recall_claim_allowed") is False
        and q1_review_manifest.get("private_role_registry_sha256")
        == sha256_path(role_registry_path)
    ):
        raise ValueError(
            "independent annotation ingestion must share Q1's locked private role registry"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and merge blind public-recall annotation returns."
    )
    parser.add_argument(
        "--frame",
        type=Path,
        default=ROOT / "data" / "public_recall_sampling_frame_v1.jsonl",
    )
    parser.add_argument(
        "--frame-manifest",
        type=Path,
        default=ROOT / "data" / "public_recall_sampling_frame_v1.manifest.json",
    )
    parser.add_argument(
        "--private-key", type=Path, default=PACKET / "private_annotation_key.jsonl"
    )
    parser.add_argument(
        "--packet-manifest", type=Path, default=PACKET / "manifest.json"
    )
    parser.add_argument("--human-provenance", type=Path, required=True)
    parser.add_argument("--private-role-registry", type=Path, required=True)
    parser.add_argument("--q1-review-manifest", type=Path, required=True)
    parser.add_argument(
        "--human-return", action="append", default=[], metavar="A1=PATH", required=True
    )
    parser.add_argument(
        "--model-return", action="append", default=[], metavar="M1=PATH"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    human_paths = parse_labeled_paths(args.human_return, ANNOTATORS)
    if set(human_paths) != set(ANNOTATORS):
        raise SystemExit("exactly A1, A2, and A3 human returns are required")
    model_paths = parse_labeled_paths(args.model_return, MODEL_PRELABELERS)
    frame_manifest = json.loads(args.frame_manifest.read_text(encoding="utf-8"))
    packet_manifest = json.loads(args.packet_manifest.read_text(encoding="utf-8"))
    frame_sha256 = sha256_path(args.frame)
    key_sha256 = sha256_path(args.private_key)
    if (
        frame_manifest.get("audit_version") != "TRI-public-recall-sampling-frame-v1"
        or frame_manifest.get("rows") != 699
        or frame_manifest.get("frame_sha256") != frame_sha256
    ):
        raise SystemExit("frozen sampling-frame manifest validation failed")
    if (
        packet_manifest.get("audit_version") != "TRI-public-recall-blind-packets-v4"
        or packet_manifest.get("rows_per_labeler") != 699
        or packet_manifest.get("frame_sha256") != frame_sha256
        or packet_manifest.get("private_annotation_key_sha256") != key_sha256
        or packet_manifest.get("model_prelabels_are_human_evidence") is not False
        or packet_manifest.get("uniform_outer_evidence_schema") is not True
        or packet_manifest.get("suite_native_control_documents") is not True
        or packet_manifest.get("derived_classifications_removed") is not True
    ):
        raise SystemExit("blind-packet manifest validation failed")
    human_hashes = {labeler: sha256_path(path) for labeler, path in human_paths.items()}
    provenance = json.loads(args.human_provenance.read_text(encoding="utf-8"))
    role_registry = json.loads(args.private_role_registry.read_text(encoding="utf-8"))
    q1_review_manifest = json.loads(
        args.q1_review_manifest.read_text(encoding="utf-8")
    )
    validate_shared_role_registry(q1_review_manifest, args.private_role_registry)
    role_hashes = validate_private_role_registry(
        role_registry, ("Q1", "A1", "A2", "A3")
    )
    merged = merge_public_annotation_returns(
        frame=read_jsonl(args.frame),
        private_key=read_jsonl(args.private_key),
        human_returns={labeler: read_jsonl(path) for labeler, path in human_paths.items()},
        human_provenance=provenance,
        private_key_sha256=key_sha256,
        human_return_sha256=human_hashes,
        model_returns={labeler: read_jsonl(path) for labeler, path in model_paths.items()},
        role_token_sha256=role_hashes,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(canonical_json(row) + "\n" for row in merged), encoding="utf-8"
    )
    manifest = {
        "audit_version": "TRI-public-recall-annotation-ingestion-v1",
        "evidence_status": "independent-human gate passed; labels merged",
        "rows": len(merged),
        "frame_sha256": frame_sha256,
        "frame_manifest_sha256": sha256_path(args.frame_manifest),
        "packet_manifest_sha256": sha256_path(args.packet_manifest),
        "private_annotation_key_sha256": key_sha256,
        "human_provenance_sha256": sha256_path(args.human_provenance),
        "private_role_registry_sha256": sha256_path(args.private_role_registry),
        "q1_review_manifest_sha256": sha256_path(args.q1_review_manifest),
        "human_return_sha256": human_hashes,
        "model_return_sha256": {
            labeler: sha256_path(path) for labeler, path in model_paths.items()
        },
        "human_majority_labelers": list(ANNOTATORS),
        "model_prelabels_descriptive_only": True,
        "output_sha256": sha256_path(args.output),
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
