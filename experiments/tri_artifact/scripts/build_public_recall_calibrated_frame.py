#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from tri.public_recall_calibrated_audit import build_sampling_frame


ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a frozen public-audit sampling frame.")
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--controls", type=Path)
    parser.add_argument(
        "--population-report",
        type=Path,
        default=ROOT / "reports" / "public_recall_population_v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-dataset", type=int, default=100)
    args = parser.parse_args()
    frame = build_sampling_frame(read(args.population), read(args.candidates), read(args.controls) if args.controls else [], args.per_dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in frame), encoding="utf-8")
    by_dataset: dict[str, Counter[str]] = defaultdict(Counter)
    for row in frame:
        if row["audit_role"] != "injected_control":
            by_dataset[str(row["dataset"])][str(row["audit_role"])] += 1
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    population_report = json.loads(args.population_report.read_text(encoding="utf-8"))
    if (
        population_report.get("population_sha256") != digest(args.population)
        or population_report.get("candidate_sha256") != digest(args.candidates)
    ):
        raise ValueError("population report does not match the supplied population and census")
    manifest = {
        "audit_version": "TRI-public-recall-sampling-frame-v1",
        "evidence_status": "frozen blind-annotation frame; no labels",
        "rows": len(frame),
        "natural_rows": sum(row["audit_role"] != "injected_control" for row in frame),
        "control_rows": sum(row["audit_role"] == "injected_control" for row in frame),
        "by_dataset": {
            dataset: dict(sorted(counts.items()))
            for dataset, counts in sorted(by_dataset.items())
        },
        "per_dataset_noncandidate_cap": args.per_dataset,
        "seed": 20260729,
        "population_sha256": digest(args.population),
        "candidate_census_sha256": digest(args.candidates),
        "population_report_sha256": digest(args.population_report),
        "controls_sha256": digest(args.controls) if args.controls else None,
        "frame_sha256": digest(args.output),
        "human_labels_complete": False,
        "model_calls_allowed": False,
        "next_gate": "three independent blind labels per row; controls excluded from estimates",
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**manifest, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
