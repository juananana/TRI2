#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.public_recall_calibrated_audit import render_markdown, report_audit


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Report the public recall-calibrated audit.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--population-size", action="append", default=[], metavar="DATASET=N")
    parser.add_argument(
        "--population-report",
        type=Path,
        default=ROOT / "reports" / "public_recall_population_v1.json",
    )
    parser.add_argument(
        "--frame-manifest",
        type=Path,
        default=ROOT / "data" / "public_recall_sampling_frame_v1.manifest.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10_000)
    parser.add_argument("--ingestion-manifest", type=Path)
    parser.add_argument("--allow-unverified", action="store_true")
    args = parser.parse_args()
    population_report = json.loads(args.population_report.read_text(encoding="utf-8"))
    frame_manifest = json.loads(args.frame_manifest.read_text(encoding="utf-8"))
    sizes = {
        str(dataset): int(size)
        for dataset, size in population_report.get("population_by_dataset", {}).items()
    }
    if args.population_size and not args.allow_unverified:
        raise SystemExit("verified reporting forbids --population-size overrides")
    for value in args.population_size:
        if "=" not in value:
            raise SystemExit("--population-size must be DATASET=N")
        dataset, raw = value.split("=", 1)
        sizes[dataset] = int(raw)
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    observed_datasets = {
        str(row["dataset"])
        for row in rows
        if row.get("audit_role") != "injected_control"
    }
    if set(sizes) != observed_datasets:
        raise SystemExit(
            f"population/report dataset mismatch: sizes={sorted(sizes)}, rows={sorted(observed_datasets)}"
        )
    verified = not args.allow_unverified
    ingestion_manifest = None
    if not args.allow_unverified:
        if args.ingestion_manifest is None:
            raise SystemExit("verified reporting requires --ingestion-manifest")
        ingestion_manifest = json.loads(args.ingestion_manifest.read_text(encoding="utf-8"))
        observed = hashlib.sha256(args.input.read_bytes()).hexdigest()
        if (
            population_report.get("audit_version") != "TRI-public-recall-population-v1"
            or frame_manifest.get("audit_version") != "TRI-public-recall-sampling-frame-v1"
            or population_report.get("population_sha256")
            != frame_manifest.get("population_sha256")
            or population_report.get("candidate_sha256")
            != frame_manifest.get("candidate_census_sha256")
            or frame_manifest.get("population_report_sha256")
            != hashlib.sha256(args.population_report.read_bytes()).hexdigest()
            or ingestion_manifest.get("audit_version")
            != "TRI-public-recall-annotation-ingestion-v1"
            or ingestion_manifest.get("output_sha256") != observed
            or ingestion_manifest.get("frame_sha256") != frame_manifest.get("frame_sha256")
            or ingestion_manifest.get("frame_manifest_sha256")
            != hashlib.sha256(args.frame_manifest.read_bytes()).hexdigest()
            or ingestion_manifest.get("model_prelabels_descriptive_only") is not True
        ):
            raise SystemExit("frozen population/frame/ingestion hash chain failed")
    report = report_audit(
        rows,
        sizes,
        bootstrap_samples=args.bootstrap_samples,
        verified_ingestion=verified,
    )
    if verified and report["independent_human_gate_passed"] is not True:
        raise SystemExit("independent-human evidence gate failed")
    report["provenance"] = {
        "labeled_ledger_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "ingestion_manifest_sha256": (
            hashlib.sha256(args.ingestion_manifest.read_bytes()).hexdigest()
            if args.ingestion_manifest
            else None
        ),
        "population_report_sha256": hashlib.sha256(
            args.population_report.read_bytes()
        ).hexdigest(),
        "frame_manifest_sha256": hashlib.sha256(
            args.frame_manifest.read_bytes()
        ).hexdigest(),
        "verified_ingestion": verified,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))


if __name__ == "__main__":
    main()
