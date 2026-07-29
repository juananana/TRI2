from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.independent_language_holdout import (
    WRITERS,
    design_fidelity_summary,
    load_assignments,
    load_jsonl,
    normalize_wjx_writer_content,
    read_table,
    sha256_path,
    validate_pairs,
    validate_provisional_writer_returns,
    write_annotation_wjx_forms,
)


MISSING_ELIGIBILITY_FIELDS = (
    "no_assistance",
    "technical_issue",
    "completed",
    "prior_tri_exposure",
    "compensation_category",
    "ethics_determination",
)


def writer_export(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("writer export must use WRITER=PATH")
    writer_id, raw_path = value.split("=", 1)
    writer_id = writer_id.strip().upper()
    if writer_id not in WRITERS:
        raise argparse.ArgumentTypeError(f"unknown writer ID: {writer_id}")
    return writer_id, Path(raw_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Stage de-identified writer content without passing or weakening the formal "
            "eligibility gate."
        )
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--private-scenario-key", type=Path, required=True)
    parser.add_argument(
        "--writer-export",
        action="append",
        type=writer_export,
        required=True,
        help="Repeat exactly once for each writer, for example W1=/private/W1.xlsx.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    export_map: dict[str, Path] = {}
    for writer_id, path in args.writer_export:
        if writer_id in export_map:
            raise ValueError(f"duplicate export for {writer_id}")
        export_map[writer_id] = path
    if set(export_map) != set(WRITERS):
        missing = sorted(set(WRITERS) - set(export_map))
        extra = sorted(set(export_map) - set(WRITERS))
        raise ValueError(f"need exactly W1-W12 exports; missing={missing}, extra={extra}")

    assignments = load_assignments(args.packet / "writer_allocation.csv")
    pairs = load_jsonl(args.private_scenario_key)
    validate_pairs(pairs)
    pair_map = {row["pair_id"]: row for row in pairs}
    if {row["pair_id"] for row in assignments} != set(pair_map):
        raise ValueError("private scenario key does not match the frozen allocation")

    raw_rows = []
    source_hashes = {}
    for writer_id in WRITERS:
        path = export_map[writer_id]
        exports = read_table(path)
        if len(exports) != 1:
            raise ValueError(f"{writer_id} export must contain exactly one submitted response")
        source_hashes[writer_id] = sha256_path(path)
        raw = dict(exports[0])
        local_response_id = str(raw.get("序号", "")).strip()
        if not local_response_id:
            raise ValueError(f"{writer_id} export is missing its survey-local response ID")
        raw["response_id"] = f"{writer_id}:{local_response_id}"
        raw_rows.extend(
            normalize_wjx_writer_content(writer_id, raw, assignments, pair_map)
        )
    authored = validate_provisional_writer_returns(raw_rows, assignments, pair_map)
    design = design_fidelity_summary(authored)

    args.output.mkdir(parents=True, exist_ok=False)
    authored_path = args.output / "provisional_authored_instructions.jsonl"
    authored_path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in authored),
        encoding="utf-8",
    )
    forms = args.output / "provisional_annotator_wjx_forms"
    write_annotation_wjx_forms(authored, pairs, assignments, forms)
    annotation_key = args.output / "private_annotation_key.jsonl"
    manifest = {
        "status": "staging-only; formal eligibility gate failed",
        "evidence_allowed": False,
        "model_calls_allowed": False,
        "writer_rows": len(authored),
        "writers": len(WRITERS),
        **design,
        "observed_core_checks": ["adult", "english_task_ability", "consent"],
        "missing_eligibility_fields": list(MISSING_ELIGIBILITY_FIELDS),
        "writer_export_sha256": source_hashes,
        "private_scenario_key_sha256": sha256_path(args.private_scenario_key),
        "allocation_sha256": sha256_path(args.packet / "writer_allocation.csv"),
        "provisional_authored_instructions_sha256": sha256_path(authored_path),
        "annotator_forms": 36,
        "private_annotation_key_sha256": sha256_path(annotation_key),
        "privacy": (
            "Source exports remain private because they contain platform metadata; the staged "
            "JSONL omits response identifiers and platform metadata."
        ),
        "next_gate": (
            "Recollect or redesign the writer task because the 40-pair clarity gate is not "
            "reachable even under unanimous future annotation. Complete the private eligibility "
            "ledger before using the current responses for any human-evidence claim."
            if not design["annotation_gate_feasible"]
            else "Complete and validate the private eligibility ledger before human-evidence "
            "claims, clarity-gate promotion, or holdout model calls."
        ),
    }
    (args.output / "staging_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
