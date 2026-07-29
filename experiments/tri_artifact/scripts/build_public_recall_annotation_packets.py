#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from tri.public_recall_calibrated_audit import (
    ANNOTATORS,
    MODEL_PRELABELERS,
    SEED,
    blind_public_unit_id,
    build_blind_public_annotation_payload,
    unit_key,
)


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build blind public-recall annotation packets.")
    parser.add_argument(
        "--frame", type=Path, default=root / "data" / "public_recall_sampling_frame_v1.jsonl"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = read_jsonl(args.frame)
    if len(rows) != 699:
        raise ValueError("frozen public-recall frame must contain 699 rows")
    blind_ids = [blind_public_unit_id(row) for row in rows]
    if len(blind_ids) != len(set(blind_ids)):
        raise ValueError("blind public IDs are not unique")
    args.output.mkdir(parents=True, exist_ok=False)

    private_key = []
    for row in rows:
        private_key.append(
            {
                "blind_unit_id": blind_public_unit_id(row),
                "dataset": row.get("dataset") or row.get("suite"),
                "source_unit_key": (
                    f"control::{row['control_id']}"
                    if row.get("audit_role") == "injected_control"
                    else unit_key(row)
                ),
                "audit_role": row["audit_role"],
                "inclusion_probability": row["inclusion_probability"],
                "expected_strict": row.get("expected_strict"),
                "expected_strict_positive": row.get("expected_strict_positive"),
            }
        )
    key_path = args.output / "private_annotation_key.jsonl"
    write_jsonl(key_path, private_key)

    packet_hashes = {}
    order_manifests = {}
    for kind, labelers, directory in (
        ("human", ANNOTATORS, args.output / "human_forms"),
        ("model", MODEL_PRELABELERS, args.output / "model_prelabels"),
    ):
        directory.mkdir(parents=True, exist_ok=False)
        order_manifests[kind] = {}
        for labeler in labelers:
            ordered = list(rows)
            random.Random(SEED + 1000 * (1 if kind == "human" else 2) + int(labeler[1:])).shuffle(ordered)
            payloads = [build_blind_public_annotation_payload(row, labeler) for row in ordered]
            name = (
                f"annotator_{labeler}.jsonl"
                if kind == "human"
                else f"model_prelabel_{labeler}.jsonl"
            )
            path = directory / name
            write_jsonl(path, payloads)
            packet_hashes[str(path.relative_to(args.output))] = digest(path)
            order_manifests[kind][labeler] = [row["blind_unit_id"] for row in payloads]
    orders_path = args.output / "blind_orders.json"
    orders_path.write_text(json.dumps(order_manifests, indent=2) + "\n", encoding="utf-8")

    provenance_template = {
        "status": "pending-independent-human-annotation",
        "annotators": {
            annotator: {
                "source": "independent_human",
                "completed": False,
                "blind": True,
                "saw_model_prelabels_before_lock": False,
                "participant_token_sha256": None,
            }
            for annotator in ANNOTATORS
        },
        "private_annotation_key_sha256": digest(key_path),
        "annotation_returns_sha256": {annotator: None for annotator in ANNOTATORS},
    }
    (args.output / "human_annotation_provenance_template.json").write_text(
        json.dumps(provenance_template, indent=2) + "\n", encoding="utf-8"
    )
    role_registry_template = {
        "version": "TRI-private-human-role-registry-v1",
        "status": "pending",
        "token_policy": "stable-per-person-random-128-bit-minimum-hashed-sha256",
        "one_token_per_natural_person": True,
        "coordinator_verified_no_role_overlap": False,
        "roles": {
            role: {"participant_token_sha256": None}
            for role in ("Q1", "A1", "A2", "A3")
        },
    }
    (args.output / "private_role_registry_template.json").write_text(
        json.dumps(role_registry_template, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "audit_version": "TRI-public-recall-blind-packets-v4",
        "evidence_status": "packets only; no labels",
        "rows_per_labeler": len(rows),
        "human_annotators": list(ANNOTATORS),
        "model_prelabelers": list(MODEL_PRELABELERS),
        "packet_sha256": packet_hashes,
        "frame_sha256": digest(args.frame),
        "private_annotation_key_sha256": digest(key_path),
        "sampling_roles_hidden": True,
        "control_gold_hidden": True,
        "source_identity_hidden": True,
        "uniform_outer_evidence_schema": True,
        "suite_native_control_documents": True,
        "derived_classifications_removed": True,
        "model_prelabels_are_human_evidence": False,
        "next_gate": "lock three independent human returns before exposing model prelabels",
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
