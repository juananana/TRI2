from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.independent_language_holdout import (
    WRITERS,
    load_assignments,
    load_jsonl,
    normalize_wjx_writer_export,
    read_table,
    sha256_path,
    validate_pairs,
    validate_writer_returns,
    write_annotation_wjx_forms,
)


def writer_export(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("writer export must use WRITER=PATH")
    writer_id, raw_path = value.split("=", 1)
    writer_id = writer_id.strip().upper()
    if writer_id not in WRITERS:
        raise argparse.ArgumentTypeError(f"unknown writer ID: {writer_id}")
    return writer_id, Path(raw_path)


def _ledger_bool(value: str, field: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"yes", "y", "true", "1", "是", "已完成", "完成"}:
        return True
    if normalized in {"no", "n", "false", "0", "否", "未完成", "没有"}:
        return False
    raise ValueError(f"invalid {field} in eligibility ledger")


def load_eligibility_ledger(path: Path) -> dict[str, dict[str, object]]:
    rows = read_table(path)
    required = {
        "writer_id",
        "response_id",
        "role",
        "adult",
        "english_task_ability",
        "consent",
        "no_assistance",
        "technical_issue",
        "completed",
        "prior_tri_exposure",
        "compensation_category",
        "completion_seconds",
        "ethics_determination",
    }
    if not rows or not required.issubset(rows[0]):
        missing = sorted(required - set(rows[0] if rows else {}))
        raise ValueError(f"eligibility ledger is missing columns: {missing}")
    output: dict[str, dict[str, object]] = {}
    for row in rows:
        writer_id = str(row["writer_id"]).strip().upper()
        if writer_id not in WRITERS or writer_id in output:
            raise ValueError(f"invalid or duplicate writer in eligibility ledger: {writer_id}")
        response_id = str(row["response_id"]).strip()
        if not response_id:
            raise ValueError(f"missing response_id for {writer_id}")
        role = str(row["role"]).strip().lower()
        if role != "writer":
            raise ValueError(f"invalid role for {writer_id}: {role}")
        compensation = str(row["compensation_category"]).strip()
        determination = str(row["ethics_determination"]).strip()
        if not compensation or not determination:
            raise ValueError(f"missing compensation or ethics determination for {writer_id}")
        try:
            completion_seconds = int(str(row["completion_seconds"]).strip())
        except ValueError as exc:
            raise ValueError(f"invalid completion_seconds for {writer_id}") from exc
        if completion_seconds <= 0:
            raise ValueError(f"invalid completion_seconds for {writer_id}")
        adult = _ledger_bool(row["adult"], "adult")
        english_task_ability = _ledger_bool(
            row["english_task_ability"], "english_task_ability"
        )
        consent = _ledger_bool(row["consent"], "consent")
        prior_tri_exposure = _ledger_bool(row["prior_tri_exposure"], "prior_tri_exposure")
        no_assistance = _ledger_bool(row["no_assistance"], "no_assistance")
        technical_issue = _ledger_bool(row["technical_issue"], "technical_issue")
        completed = _ledger_bool(row["completed"], "completed")
        if not all((adult, english_task_ability, consent, no_assistance, completed)):
            raise ValueError(f"writer eligibility gate failed for {writer_id}")
        if technical_issue or prior_tri_exposure:
            raise ValueError(f"writer independence gate failed for {writer_id}")
        output[writer_id] = {
            "response_id": response_id,
            "role": role,
            "adult": adult,
            "english_task_ability": english_task_ability,
            "consent": consent,
            "no_assistance": no_assistance,
            "technical_issue": technical_issue,
            "completed": completed,
            "prior_tri_exposure": prior_tri_exposure,
            "compensation_category": compensation,
            "completion_seconds": completion_seconds,
            "ethics_determination": determination,
        }
    if set(output) != set(WRITERS):
        raise ValueError("eligibility ledger must contain exactly W1-W12")
    if len({row["response_id"] for row in output.values()}) != len(WRITERS):
        raise ValueError("eligibility ledger response IDs must be unique")
    if len({row["ethics_determination"] for row in output.values()}) != 1:
        raise ValueError("eligibility ledger must use one recorded ethics determination")
    return output


def merge_eligibility(
    writer_id: str, raw: dict[str, str], ledger_row: dict[str, object]
) -> dict[str, str]:
    merged = dict(raw)
    response_id = next(
        (
            str(raw.get(name, "")).strip()
            for name in ("response_id", "participant_id", "participant_code", "答卷编号", "序号")
            if str(raw.get(name, "")).strip()
        ),
        "",
    )
    if not response_id or response_id != ledger_row["response_id"]:
        raise ValueError(f"eligibility response_id does not match WJX export for {writer_id}")
    for field in (
        "adult",
        "english_task_ability",
        "consent",
        "no_assistance",
        "technical_issue",
        "completed",
        "prior_tri_exposure",
    ):
        if str(raw.get(field, "")).strip():
            observed = _ledger_bool(raw[field], field)
            if observed != ledger_row[field]:
                raise ValueError(f"eligibility ledger conflicts with WJX export for {writer_id}/{field}")
        merged[field] = "yes" if ledger_row[field] else "no"
    for field in (
        "role",
        "compensation_category",
        "completion_seconds",
        "ethics_determination",
    ):
        merged[field] = str(ledger_row[field])
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate 12 WJX writer returns and generate blind annotation forms."
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
    parser.add_argument(
        "--eligibility-ledger",
        type=Path,
        help=(
            "Private 12-row sidecar for consent, independence, completion, compensation, and "
            "the applicable ethics/policy determination."
        ),
    )
    parser.add_argument("--output", type=Path)
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
        raise ValueError("private scenario key does not match the frozen 12-writer allocation")

    raw_rows = []
    source_hashes = {}
    eligibility = (
        load_eligibility_ledger(args.eligibility_ledger)
        if args.eligibility_ledger is not None
        else None
    )
    for writer_id in WRITERS:
        path = export_map[writer_id]
        exports = read_table(path)
        if len(exports) != 1:
            raise ValueError(f"{writer_id} export must contain exactly one submitted response")
        source_hashes[writer_id] = sha256_path(path)
        raw = exports[0]
        if eligibility is not None:
            raw = merge_eligibility(writer_id, raw, eligibility[writer_id])
        raw_rows.extend(
            normalize_wjx_writer_export(
                writer_id,
                raw,
                assignments,
                pair_map,
            )
        )
    authored = validate_writer_returns(raw_rows, assignments, pair_map)

    output = args.output or args.packet / "validated_annotation_packet"
    output.mkdir(parents=True, exist_ok=False)
    authored_path = output / "locked_authored_instructions.jsonl"
    authored_path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in authored),
        encoding="utf-8",
    )
    forms = output / "annotator_wjx_forms"
    write_annotation_wjx_forms(authored, pairs, assignments, forms)
    manifest = {
        "status": "post-primary human collection; awaiting blind annotation",
        "writer_rows": len(authored),
        "writers": len(WRITERS),
        "writer_export_sha256": source_hashes,
        "eligibility_ledger_sha256": (
            sha256_path(args.eligibility_ledger)
            if args.eligibility_ledger is not None
            else None
        ),
        "private_scenario_key_sha256": sha256_path(args.private_scenario_key),
        "allocation_sha256": sha256_path(args.packet / "writer_allocation.csv"),
        "locked_authored_instructions_sha256": sha256_path(authored_path),
        "annotator_forms": 36,
        "model_calls_allowed": False,
        "next_gate": "three independent annotators x 120 rows and >=40 clear complete pairs",
    }
    (output / "processing_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
