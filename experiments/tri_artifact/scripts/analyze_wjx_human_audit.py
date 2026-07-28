from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median

from tri.wjx_human_audit import (
    analyze,
    analyze_incomplete,
    dump_report,
    load_allocation,
    load_key,
    normalize_export_row,
    read_table,
    render_markdown,
    select_frozen_sample,
)


def _response_id(row: dict[str, str]) -> str:
    return str(row.get("response_id") or row.get("答卷编号") or row.get("序号") or "").strip()


def _submitted_at(row: dict[str, str]) -> str:
    return str(
        row.get("submitted_at")
        or row.get("提交答卷时间")
        or row.get("提交时间")
        or row.get("开始时间")
        or ""
    ).strip()


def _duration_seconds(value: str) -> int | None:
    value = str(value).strip()
    if not value:
        return None
    hours = re.search(r"(\d+)\s*小时", value)
    minutes = re.search(r"(\d+)\s*分", value)
    seconds = re.search(r"(\d+)\s*秒", value)
    if not any((hours, minutes, seconds)):
        return int(value) if value.isdigit() else None
    return (
        (int(hours.group(1)) * 3600 if hours else 0)
        + (int(minutes.group(1)) * 60 if minutes else 0)
        + (int(seconds.group(1)) if seconds else 0)
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _form_spec(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("form response must use FORM=PATH")
    form, path = value.split("=", 1)
    form = form.strip().upper()
    if form not in "ABCDEF":
        raise argparse.ArgumentTypeError(f"unknown form: {form}")
    return form, Path(path)


def _item_count_table(
    groups: dict[str, list[dict]], key_rows: list[dict[str, str]]
) -> list[dict]:
    rows = []
    for item in key_rows:
        item_id = item["public_item_id"]
        output = {
            "public_item_id": item_id,
            "source_task_id": item["source_task_id"],
            "form": item["form"],
            "position": item["position"],
            "category": item["category"],
            "binding": item.get("binding", ""),
            "update": item.get("update", ""),
            "candidate_order": item.get("candidate_order", ""),
            "referent_gold": item["discourse_referent_gold"],
            "execution_gold": item["execution_gold"],
        }
        for group_name, participants in groups.items():
            answers = [
                participant["responses"][item_id]
                for participant in participants
                if participant["form"] == item["form"]
            ]
            output[group_name] = {
                "labels": len(answers),
                "referent_counts": dict(
                    sorted(Counter(answer["referent"] for answer in answers).items())
                ),
                "execution_counts": dict(
                    sorted(Counter(answer["execution"] for answer in answers).items())
                ),
                "confidence_counts": {
                    str(score): count
                    for score, count in sorted(
                        Counter(answer["confidence"] for answer in answers).items()
                    )
                },
            }
        rows.append(output)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze the frozen six-form WJX construct audit.")
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--responses", type=Path, nargs="+")
    inputs.add_argument("--form-response", action="append", type=_form_spec)
    parser.add_argument("--participant-map", type=Path)
    parser.add_argument("--participant-map-output", type=Path)
    parser.add_argument("--selection-ledger-output", type=Path)
    parser.add_argument("--item-count-output", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    key_rows = load_key(args.answer_key)
    allocation = load_allocation(args.allocation)
    participant_map = json.loads(args.participant_map.read_text(encoding="utf-8")) if args.participant_map else {}
    normalized = []
    source_hashes = {}
    raw_by_form = Counter()
    beyond_cap_by_form = Counter()
    durations = []

    if args.form_response:
        seen_forms = Counter(form for form, _ in args.form_response)
        if seen_forms != Counter({form: 1 for form in "ABCDEF"}):
            raise ValueError("form responses must contain exactly one file for each of A-F")
        private_map: dict[str, dict[str, str]] = {}
        for form, path in args.form_response:
            rows = sorted(read_table(path), key=lambda row: (_submitted_at(row), _response_id(row)))
            raw_by_form[form] = len(rows)
            beyond_cap_by_form[form] = max(0, len(rows) - 6)
            source_hashes[form] = _sha256(path)
            mapped_rows = rows[:6]
            form_map = {
                _response_id(row): f"{form}-{index:02d}"
                for index, row in enumerate(mapped_rows, 1)
            }
            private_map[form] = form_map
            for row in mapped_rows:
                duration = _duration_seconds(row.get("所用时间", ""))
                if duration is not None:
                    durations.append(duration)
                normalized.append(
                    normalize_export_row(
                        row,
                        key_rows=key_rows,
                        allocation=allocation,
                        participant_map=form_map,
                    )
                )
        if args.participant_map_output:
            args.participant_map_output.parent.mkdir(parents=True, exist_ok=True)
            args.participant_map_output.write_text(
                json.dumps(private_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    else:
        normalized = [
            normalize_export_row(
                row,
                key_rows=key_rows,
                allocation=allocation,
                participant_map=participant_map,
            )
            for path in args.responses
            for row in read_table(path)
        ]

    selected, ledger = select_frozen_sample(normalized, require_complete=False)
    complete = len(selected) == 30 and Counter(row["form"] for row in selected) == Counter({form: 5 for form in "ABCDEF"})
    if not complete and not args.allow_incomplete:
        counts = Counter(row["form"] for row in selected)
        raise ValueError(f"incomplete frozen sample: {dict(sorted(counts.items()))}")
    report = analyze(selected, key_rows) if complete else analyze_incomplete(selected, key_rows, all_rows=normalized)
    report["selection_ledger"] = ledger
    exclusion_reasons = Counter(
        reason for entry in ledger for reason in entry["exclusion_reasons"]
    )
    exclusion_patterns = Counter(
        "+".join(entry["exclusion_reasons"])
        for entry in ledger
        if entry["exclusion_reasons"]
    )
    report["collection"] = {
        "raw_by_form": {form: raw_by_form[form] for form in "ABCDEF"},
        "mapped_total": len(normalized),
        "primary_total": sum(row["allocation_role"] == "primary" for row in normalized),
        "reserve_total": sum(row["allocation_role"] == "reserve" for row in normalized),
        "valid_total": sum(entry["valid"] for entry in ledger),
        "invalid_total": sum(not entry["valid"] for entry in ledger),
        "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        "exclusion_pattern_counts": dict(sorted(exclusion_patterns.items())),
        "beyond_frozen_cap_by_form": {form: beyond_cap_by_form[form] for form in "ABCDEF"},
        "duration_seconds": {
            "minimum": min(durations) if durations else None,
            "median": median(durations) if durations else None,
            "maximum": max(durations) if durations else None,
            "below_five_minutes": sum(value < 300 for value in durations),
            "below_ten_minutes": sum(value < 600 for value in durations),
        },
    }
    report["private_source_sha256"] = source_hashes
    primary_rows = [row for row in normalized if row["allocation_role"] == "primary"]
    relaxed_rows: list[dict] = []
    if not complete:
        relaxed_by_form = {}
        for form in "ABCDEF":
            form_rows = [
                row
                for row in normalized
                if row["form"] == form
                and row["age_18"]
                and row["english_independent"]
                and row["consent"]
                and row["end_check_complete"]
                and not row["technical_issue"]
                and all(
                    answer["referent"] is not None
                    and answer["execution"] is not None
                    and answer["confidence"] is not None
                    for answer in row["responses"].values()
                )
            ]
            primaries = [row for row in form_rows if row["allocation_role"] == "primary"][:5]
            reserves = [row for row in form_rows if row["allocation_role"] == "reserve"]
            relaxed_by_form[form] = primaries + reserves[: 5 - len(primaries)]
        relaxed_rows = [row for form in "ABCDEF" for row in relaxed_by_form[form]]
        relaxed = analyze_incomplete(relaxed_rows, key_rows)
        report["post_hoc_assistance_relaxed_sensitivity"] = {
            "warning": "Ignores the frozen assistance exclusion but still excludes technical issues; post-hoc and not evidence.",
            "participants": len(relaxed_rows),
            "selected_by_form": {
                form: len(relaxed_by_form[form]) for form in "ABCDEF"
            },
            "referent": relaxed["eligible_exploratory"]["referent"],
            "execution": relaxed["eligible_exploratory"]["execution"],
        }
    if not complete and len(primary_rows) == 30:
        sensitivity = analyze(primary_rows, key_rows)
        report["non_evidentiary_all_primary_sensitivity"] = {
            "warning": "Includes submissions excluded by the frozen eligibility rules; not evidence.",
            "participants": 30,
            "referent": {
                key: sensitivity["referent"][key]
                for key in (
                    "majority_gold",
                    "unanimous",
                    "pair_majority_correct",
                    "pair_denominator",
                )
            },
            "execution": {
                key: sensitivity["execution"][key]
                for key in (
                    "majority_gold",
                    "unanimous",
                    "majority_distribution",
                    "clarify_majorities",
                    "identity_correct_execution_disagrees",
                )
            },
        }
    if args.selection_ledger_output:
        args.selection_ledger_output.parent.mkdir(parents=True, exist_ok=True)
        args.selection_ledger_output.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.item_count_output:
        args.item_count_output.parent.mkdir(parents=True, exist_ok=True)
        args.item_count_output.write_text(
            json.dumps(
                _item_count_table(
                    {
                        "strict_eligible": selected,
                        "post_hoc_assistance_relaxed": relaxed_rows,
                        "all_primary": primary_rows,
                    },
                    key_rows,
                ),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    dump_report(report, args.output)
    markdown_output = args.markdown_output or args.output.with_suffix(".md")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"evidence_status": report["evidence_status"], "complete": complete, "selected": len(selected), "valid_by_form": dict(sorted(Counter(row["form"] for row in selected).items()))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
