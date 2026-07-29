#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.public_recall_calibrated_audit import reconcile_candidate_inventories, unit_key


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Reconcile frozen public candidate inventories.")
    parser.add_argument(
        "--annotation-candidates",
        type=Path,
        default=root / "data" / "external_public_annotation_candidates_v1.jsonl",
    )
    parser.add_argument(
        "--triage",
        type=Path,
        default=root / "data" / "model_assisted_public_recall_triage_v1.jsonl",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=root / "data" / "public_candidate_reconciliation_v1.jsonl",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=root / "reports" / "public_candidate_reconciliation_v1.json",
    )
    parser.add_argument(
        "--population",
        type=Path,
        default=root / "data" / "public_recall_population_v1.jsonl",
    )
    parser.add_argument(
        "--candidate-census",
        type=Path,
        default=root / "data" / "public_recall_candidate_census_v1.jsonl",
    )
    args = parser.parse_args()

    ledger, report = reconcile_candidate_inventories(
        read_jsonl(args.annotation_candidates), read_jsonl(args.triage)
    )
    if args.population.is_file() and args.candidate_census.is_file():
        population = read_jsonl(args.population)
        census = read_jsonl(args.candidate_census)
        population_keys = {unit_key(row) for row in population}
        census_keys = {unit_key(row) for row in census}
        expected_datasets = {
            "ToolSandbox",
            "AppWorld",
            "tau3-bench",
            "API-Bank",
            "BFCL",
            "ToolTalk",
        }
        if (
            len(population) != 3600
            or len(population_keys) != len(population)
            or {row["dataset"] for row in population} != expected_datasets
            or len(census) != 116
            or len(census_keys) != len(census)
            or not census_keys.issubset(population_keys)
        ):
            raise ValueError("public population/candidate census failed the frozen completeness gate")
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        report.update(
            {
                "benchmark_population_complete": True,
                "population_rows": len(population),
                "routed_candidate_census_rows": len(census),
                "population_sha256": digest(args.population),
                "routed_candidate_census_sha256": digest(args.candidate_census),
                "sampling_allowed": True,
                "sampling_blocker": None,
            }
        )
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in ledger),
        encoding="utf-8",
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
