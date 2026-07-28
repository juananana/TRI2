from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from openpyxl import Workbook

from tri.wjx_human_audit import (
    _semantic_role,
    analyze,
    analyze_incomplete,
    load_allocation,
    load_key,
    normalize_export_row,
    read_table,
    select_frozen_sample,
)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def frozen_fixture(tmp_path: Path):
    forms = "ABCDEF"
    key_rows = []
    positions = {form: 0 for form in forms}
    for pair_index in range(18):
        first = forms[pair_index % 6]
        second = forms[(pair_index + 1) % 6]
        for form, mode, gold in ((first, "anchor", f"OLD-{pair_index}"), (second, "dynamic", f"NEW-{pair_index}")):
            positions[form] += 1
            key_rows.append(
                {
                    "public_item_id": f"Q-{form}{positions[form]:02d}",
                    "source_task_id": f"tri-demo-domain-explicit_{mode}-t{pair_index}-flip",
                    "variant": "original",
                    "category": "changed",
                    "subtype": "changed",
                    "binding": "anchored" if mode == "anchor" else "dynamic",
                    "update": "flip",
                    "style": f"explicit_{mode}",
                    "domain": "demo",
                    "discourse_referent_gold": gold,
                    "execution_gold": gold,
                    "pre_refresh_target": f"OLD-{pair_index}",
                    "post_refresh_target": f"NEW-{pair_index}",
                    "benchmark_correct_target": gold,
                    "candidate_order": "",
                    "display_order": "",
                    "reason_requested": "no",
                    "form": form,
                    "position": str(positions[form]),
                }
            )
    for form in forms:
        for offset, category in enumerate(("stable", "stable", "invalid", "invalid", "rewrite", "rewrite")):
            positions[form] += 1
            gold = "REJECT" if category == "invalid" else f"{form}X-{offset}"
            key_rows.append(
                {
                    "public_item_id": f"Q-{form}{positions[form]:02d}",
                    "source_task_id": f"tri-demo-{form}-{category}-{offset}",
                    "variant": "human_rewrite" if category == "rewrite" else "original",
                    "category": category,
                    "subtype": category,
                    "binding": "anchored",
                    "update": category,
                    "style": "explicit_anchor",
                    "domain": "demo",
                    "discourse_referent_gold": f"{form}X-{offset}",
                    "execution_gold": gold,
                    "pre_refresh_target": f"{form}X-{offset}",
                    "post_refresh_target": f"{form}Y-{offset}",
                    "benchmark_correct_target": gold,
                    "candidate_order": "",
                    "display_order": "",
                    "reason_requested": "no",
                    "form": form,
                    "position": str(positions[form]),
                }
            )
    key_path = tmp_path / "key.csv"
    write_csv(key_path, key_rows)

    allocation_rows = []
    for form in forms:
        for index in range(1, 7):
            allocation_rows.append(
                {
                    "participant_code": f"{form}-{index:02d}",
                    "form": form,
                    "valid_status": "primary" if index <= 5 else "reserve",
                    "completion_status": "",
                    "notes": "",
                }
            )
    allocation_path = tmp_path / "allocation.csv"
    write_csv(allocation_path, allocation_rows)
    return load_key(key_path), load_allocation(allocation_path)


def raw_submission(code: str, key_rows, *, wrong: bool = False):
    form = code[0]
    row = {
        "participant_code": code,
        "form": form,
        "submitted_at": f"2026-07-27T12:{int(code[-2:]):02d}:00",
        "age_18": "yes",
        "english_independent": "yes",
        "consent": "yes",
        "used_assistance": "no",
        "technical_issue": "no",
        "english_difficulty": "3",
    }
    for item in (item for item in key_rows if item["form"] == form):
        item_id = item["public_item_id"]
        row[f"{item_id}_referent"] = "WRONG-999" if wrong else item["discourse_referent_gold"]
        row[f"{item_id}_execution"] = "CLARIFY" if wrong else item["execution_gold"]
        row[f"{item_id}_confidence"] = "5"
    return row


def normalize(raw, key_rows, allocation):
    return normalize_export_row(raw, key_rows=key_rows, allocation=allocation)


def test_frozen_sample_uses_reserve_only_for_invalid_primary(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    rows = [normalize(raw_submission(code, key_rows), key_rows, allocation) for code in allocation]
    invalid = next(row for row in rows if row["participant_code"] == "A-01")
    invalid["used_assistance"] = True
    selected, ledger = select_frozen_sample(rows)
    selected_codes = {row["participant_code"] for row in selected}
    assert len(selected) == 30
    assert "A-01" not in selected_codes
    assert "A-06" in selected_codes
    assert next(row for row in ledger if row["participant_code"] == "A-01")["exclusion_reasons"] == ["used_assistance"]


def test_answers_never_trigger_reserve_replacement(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    rows = [
        normalize(raw_submission(code, key_rows, wrong=code == "A-06"), key_rows, allocation)
        for code in allocation
    ]
    selected, _ = select_frozen_sample(rows)
    assert "A-06" not in {row["participant_code"] for row in selected}


def test_analysis_requires_five_labels_and_eighteen_pairs(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    rows = [
        normalize(raw_submission(code, key_rows), key_rows, allocation)
        for code, assigned in allocation.items()
        if assigned["valid_status"] == "primary"
    ]
    selected, _ = select_frozen_sample(rows)
    report = analyze(selected, key_rows)
    assert report["participants"] == 30
    assert report["items"] == 72
    assert report["complete_changed_pairs"] == 18
    assert report["referent"]["majority_gold"] == 72
    assert report["referent"]["pair_majority_correct"] == 18
    assert report["execution"]["majority_gold"] == 72

    selected[0]["responses"].pop(next(iter(selected[0]["responses"])))
    with pytest.raises(ValueError, match="item set"):
        analyze(selected, key_rows)


def test_numbered_wjx_headers_are_normalized(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    form_items = sorted((row for row in key_rows if row["form"] == "A"), key=lambda row: int(row["position"]))
    raw = {
        "participant_code": "A-01",
        "1. 你是否已年满18周岁？": "是",
        "2. 英文阅读？": "是",
        "3. 是否同意？": "我已阅读知情同意书，并自愿同意参加",
        "40. 是否使用协助？": "没有",
        "41. 是否技术问题？": "没有",
        "42. 总体感受？": "一般",
    }
    for offset, item in enumerate(form_items):
        base = 4 + 3 * offset
        raw[f"{base}. 一、指代"] = f"对象 {item['discourse_referent_gold']}"
        raw[f"{base + 1}. 二、执行"] = (
            "拒绝执行" if item["execution_gold"] == "REJECT" else f"执行 {item['execution_gold']}"
        )
        raw[f"{base + 2}. 三、信心"] = "非常确定（5）"
    normalized = normalize(raw, key_rows, allocation)
    assert normalized["age_18"] and normalized["consent"]
    assert all(answer["confidence"] == 5 for answer in normalized["responses"].values())


def test_wjx_choice_prefixes_and_non_numeric_ids_are_normalized(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    item = next(row for row in key_rows if row["form"] == "A")
    item["candidate_order"] = "BR-main | BR-rel | BR-dev"
    item["discourse_referent_gold"] = "BR-main"
    item["execution_gold"] = "BR-main"
    raw = raw_submission("A-01", key_rows)
    raw.update(
        {
            "age_18": "A. 是",
            "english_independent": "A. 是",
            "consent": "A. 我已阅读知情同意书，并自愿同意参加",
            "used_assistance": "A. 没有",
            "technical_issue": "A. 没有",
            f"{item['public_item_id']}_referent": "B. 对象 BR-main",
            f"{item['public_item_id']}_execution": "C. 执行 BR-main",
            f"{item['public_item_id']}_confidence": "E. 非常确定（5）",
        }
    )
    normalized = normalize(raw, key_rows, allocation)
    answer = normalized["responses"][item["public_item_id"]]
    assert normalized["age_18"] and not normalized["used_assistance"]
    assert answer == {"referent": "BR-main", "execution": "BR-main", "confidence": 5}


def test_xlsx_tables_are_read_without_platform_type_leakage(tmp_path: Path):
    path = tmp_path / "responses.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["序号", "提交答卷时间", "1. 资格"])
    sheet.append([1, "2026/07/27 20:00:00", "A. 是"])
    workbook.save(path)
    assert read_table(path) == [
        {"序号": "1", "提交答卷时间": "2026/07/27 20:00:00", "1. 资格": "A. 是"}
    ]


def test_item_specific_ids_share_semantic_agreement_categories():
    first = {"pre_refresh_target": "DOC-7", "post_refresh_target": "DOC-8"}
    second = {"pre_refresh_target": "BR-main", "post_refresh_target": "BR-rel"}
    assert [_semantic_role(label, first) for label in ("DOC-7", "DOC-8", "DOC-9")] == [
        "PRE_REFRESH_TARGET",
        "POST_REFRESH_TARGET",
        "OTHER_CANDIDATE",
    ]
    assert [_semantic_role(label, second) for label in ("BR-main", "BR-rel", "BR-dev")] == [
        "PRE_REFRESH_TARGET",
        "POST_REFRESH_TARGET",
        "OTHER_CANDIDATE",
    ]


def test_incomplete_cutoff_never_promotes_fixed_rater_statistics(tmp_path: Path):
    key_rows, allocation = frozen_fixture(tmp_path)
    rows = [
        normalize(raw_submission(code, key_rows), key_rows, allocation)
        for code, assigned in allocation.items()
        if assigned["valid_status"] == "primary"
    ]
    for row in rows:
        if not row["participant_code"].endswith("-01"):
            row["used_assistance"] = True
    selected, ledger = select_frozen_sample(rows, require_complete=False)
    report = analyze_incomplete(selected, key_rows, all_rows=rows)
    assert len(selected) == 6
    assert report["evidence_status"] == "post-primary audit (failed frozen eligibility gate; descriptive boundary evidence)"
    assert report["quality_gate"]["selected_valid_by_form"] == {
        form: 1 for form in "ABCDEF"
    }
    assert report["coverage"]["labels_per_item_distribution"] == {"1": 72}
    assert report["coverage"]["complete_changed_pairs_at_five_labels"] == 0
    assert "fleiss_kappa" not in report["eligible_exploratory"]["referent"]
    assert sum(entry["selected"] for entry in ledger) == 6
    serialized = json.dumps(report)
    assert not any(
        private_field in serialized
        for private_field in ("response_id", "答卷编号", "来自IP", "submitted_at")
    )
