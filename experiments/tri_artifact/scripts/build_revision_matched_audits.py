#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.revision_matched_audit import (
    build_full_diagnostic,
    build_human_rewrite,
    build_source_grounded,
    jsonl_bytes,
    sha256_bytes,
    sha256_path,
    validate_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
PROTOCOL = ROOT / "reports" / "TRI_revision_matched_audits_protocol.md"
MANIFEST = ROOT / "reports" / "revision_matched_audits_manifest_v1.json"
PREFLIGHT_MANIFEST = ROOT / "reports" / "revision_matched_audits_manifest_preflight_v0.json"
OUTPUTS = {
    "full_diagnostic": ROOT / "data" / "revision_full_diagnostic_v1.jsonl",
    "human_rewrite": ROOT / "data" / "revision_human_rewrite_v1.jsonl",
    "source_grounded": ROOT / "data" / "revision_source_grounded_v1.jsonl",
}
SOURCES = {
    "primary": ROOT / "data" / "temporal_referent_v3_language_clusters.jsonl",
    "human": ROOT / "data" / "temporal_referent_human_rewrites_v1.jsonl",
    "source_anchored": ROOT / "data" / "source_anchored_external_transfer_tasks_v1.jsonl",
    "toolsandbox": ROOT / "data" / "toolsandbox_tri_single_turn_2x2_v1.jsonl",
    "human_key": ROOT / "human_validation" / "annotation_key_private.csv",
    "human_annotator_1": ROOT / "human_validation" / "normalized_returns" / "annotator_1.csv",
    "human_annotator_2": ROOT / "human_validation" / "normalized_returns" / "annotator_2.csv",
    "human_annotator_3": ROOT / "human_validation" / "normalized_returns" / "annotator_3.csv",
}


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise SystemExit(f"Refusing to overwrite a different frozen file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and freeze the three revision matched audits.")
    parser.add_argument("--check", action="store_true", help="Validate without writing files.")
    parser.add_argument(
        "--amend-before-calls",
        action="store_true",
        help="Retain the preflight manifest and update hashes only before any revision raw run exists.",
    )
    args = parser.parse_args()

    inventories = {
        "full_diagnostic": build_full_diagnostic(SOURCES["primary"]),
        "human_rewrite": build_human_rewrite(SOURCES["human"], ROOT),
        "source_grounded": build_source_grounded(SOURCES["source_anchored"], SOURCES["toolsandbox"]),
    }
    validations = {name: validate_inventory(rows, name) for name, rows in inventories.items()}
    task_hashes = {name: sha256_bytes(jsonl_bytes(rows)) for name, rows in inventories.items()}
    manifest = {
        "manifest_version": "TRI-revision-matched-audits-manifest-v1",
        "frozen_date": "2026-07-26",
        "evidence_status": "post-primary; protocol frozen before own calls",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha256_path(PROTOCOL),
        "inventories": {
            name: {
                "path": str(OUTPUTS[name].relative_to(ROOT)),
                "sha256": task_hashes[name],
                **validations[name],
            }
            for name in inventories
        },
        "sources": {
            name: {"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path)}
            for name, path in SOURCES.items()
        },
        "parser_sha256": sha256_path(ROOT / "tri" / "revision_matched_audit.py"),
        "frozen_rule_star_sha256": sha256_path(ROOT / "tri" / "deterministic_discourse_rule_v2.py"),
        "boundaries": [
            "not primary evidence",
            "human rewrites retain authored task semantics",
            "source-grounded rows are controlled interventions, not native benchmark tasks",
            "no independent public-suite recall calibration",
        ],
    }
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if not MANIFEST.exists() or MANIFEST.read_bytes() != payload:
            raise SystemExit("Frozen manifest or inventory bytes do not match the current builders.")
        for name, rows in inventories.items():
            if not OUTPUTS[name].exists() or OUTPUTS[name].read_bytes() != jsonl_bytes(rows):
                raise SystemExit(f"Frozen inventory mismatch: {name}")
    else:
        for name, rows in inventories.items():
            write_frozen(OUTPUTS[name], jsonl_bytes(rows))
        if args.amend_before_calls and MANIFEST.exists() and MANIFEST.read_bytes() != payload:
            raw_runs = list((ROOT / "runs").glob("revision_*_qwen_*_v1.jsonl"))
            raw_runs += list((ROOT / "runs").glob("revision_*_glm_*_v1.jsonl"))
            raw_runs += list((ROOT / "runs").glob("revision_*_deepseek_*_v1.jsonl"))
            if raw_runs:
                raise SystemExit("Refusing a pre-call amendment after revision model outputs exist.")
            write_frozen(PREFLIGHT_MANIFEST, MANIFEST.read_bytes())
            MANIFEST.write_bytes(payload)
        else:
            write_frozen(MANIFEST, payload)
    print(json.dumps({"manifest": str(MANIFEST), "inventories": validations}, indent=2))


if __name__ == "__main__":
    main()
