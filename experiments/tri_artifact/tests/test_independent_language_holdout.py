from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from scripts.prepare_independent_holdout_annotation import (
    load_eligibility_ledger,
    merge_eligibility,
)

from tri.independent_language_holdout import (
    ANNOTATORS,
    WRITERS,
    build_annotation_order,
    build_assignments,
    build_model_tasks,
    build_scenario_pairs,
    clear_complete_pairs,
    normalize_wjx_writer_export,
    validate_annotation_returns,
    validate_writer_returns,
    writer_combined_wjx,
    writer_item_order,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"


def inventory():
    pairs = build_scenario_pairs(SOURCE)
    assignments = build_assignments(pairs)
    return pairs, assignments, {row["pair_id"]: row for row in pairs}


def raw_writer_export(writer_id, assignments, pair_map, *, response_id=None):
    stage_a = writer_item_order(assignments, writer_id)
    stage_b = sorted(stage_a, key=lambda row: row["item_id"])
    raw = {
        "response_id": response_id or f"response-{writer_id}",
        "no_assistance": "是",
        "technical_issue": "否",
        "completed": "是",
        "1. 年满18周岁": "是",
        "2. 可独立阅读和写作": "是",
        "3. 自愿同意": "是，我自愿同意",
    }
    for offset, assignment in enumerate(stage_a):
        raw[f"{4 + offset}. Stage A"] = f"Independent request for {assignment['item_id']}."
    for offset, assignment in enumerate(stage_b):
        pair = pair_map[assignment["pair_id"]]
        target = (
            pair["pre_refresh_target"]
            if assignment["mode"] == "preserve"
            else pair["post_refresh_target"]
        )
        raw[f"{14 + 2 * offset}. Stage B intent"] = target
        raw[f"{15 + 2 * offset}. confidence"] = "5 - very certain"
    return raw


def complete_writer_rows(assignments, pair_map):
    rows = []
    for writer_id in WRITERS:
        rows.extend(
            normalize_wjx_writer_export(
                writer_id,
                raw_writer_export(writer_id, assignments, pair_map),
                assignments,
                pair_map,
            )
        )
    return rows


def complete_authored_and_annotations():
    pairs, assignments, pair_map = inventory()
    authored = validate_writer_returns(
        complete_writer_rows(assignments, pair_map), assignments, pair_map
    )
    annotations = [
        {
            "annotator_id": annotator,
            "item_id": item["item_id"],
            "target": item["writer_intent"],
            "confidence": "5",
        }
        for annotator in ANNOTATORS
        for item in authored
    ]
    return pairs, assignments, pair_map, authored, annotations


def test_holdout_has_sixty_pairs_and_balanced_disjoint_twelve_writers():
    pairs, assignments, _ = inventory()
    assert len(pairs) == 60
    assert len(assignments) == 120
    for writer in WRITERS:
        rows = [row for row in assignments if row["writer_id"] == writer]
        assert len(rows) == 10
        assert sum(row["mode"] == "preserve" for row in rows) == 5
    by_pair = {}
    for row in assignments:
        by_pair.setdefault(row["pair_id"], []).append(row)
    assert all(len({row["writer_id"] for row in rows}) == 2 for rows in by_pair.values())


def test_final_writer_forms_have_two_pages_and_ten_dynamic_echoes():
    _, assignments, pair_map = inventory()
    for writer in WRITERS:
        form = writer_combined_wjx(
            writer, assignments, pair_map, page_size=10, title_suffix="12人版最终"
        )
        assert form.count("[填空题]") == 10
        assert form.count("根据这条原句，你原本打算操作哪个对象") == 10
        assert form.count("你对这个意图判断有多确定") == 10
        assert form.count("[分页栏]") == 1
        assert all(form.count(f"[q{question}]") == 1 for question in range(4, 14))
        assert form.index("【B 阶段｜第 1/1 页】") > form.rindex("[填空题]")


def test_annotation_orders_are_complete_randomized_and_nonadjacent():
    _, assignments, _ = inventory()
    pair_by_item = {row["item_id"]: row["pair_id"] for row in assignments}
    orders = [build_annotation_order(assignments, annotator) for annotator in ANNOTATORS]
    assert len({tuple(order) for order in orders}) == 3
    for order in orders:
        assert len(order) == 120 and len(set(order)) == 120
        assert all(pair_by_item[a] != pair_by_item[b] for a, b in zip(order, order[1:]))


def test_wjx_export_normalization_and_full_clarity_gate():
    pairs, assignments, pair_map = inventory()
    authored = validate_writer_returns(
        complete_writer_rows(assignments, pair_map), assignments, pair_map
    )
    annotation_rows = [
        {
            "annotator_id": annotator,
            "item_id": item["item_id"],
            "target": item["writer_intent"],
            "confidence": "5",
        }
        for annotator in ANNOTATORS
        for item in authored
    ]
    annotations = validate_annotation_returns(annotation_rows, authored)
    clarity = clear_complete_pairs(authored, annotations)
    assert clarity["clear_complete_pairs"] == 60
    assert clarity["main_paper_threshold_met"] is True
    tasks = build_model_tasks(authored, pairs, clarity)
    assert len(tasks) == 120
    assert all(row["clear_complete_pair"] for row in tasks)


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda raw: raw.pop("4. Stage A"), "missing core questions"),
        (lambda raw: raw.pop("no_assistance"), "no-assistance"),
        (lambda raw: raw.__setitem__("technical_issue", "maybe"), "technical_issue"),
        (lambda raw: raw.__setitem__("15. confidence", "6"), "confidence"),
    ],
)
def test_malformed_writer_exports_are_rejected(mutation, message):
    _, assignments, pair_map = inventory()
    raw = raw_writer_export("W1", assignments, pair_map)
    mutation(raw)
    with pytest.raises(ValueError, match=message):
        normalize_wjx_writer_export("W1", raw, assignments, pair_map)


def test_duplicate_writer_response_ids_and_missing_rows_are_rejected():
    _, assignments, pair_map = inventory()
    rows = complete_writer_rows(assignments, pair_map)
    for row in rows:
        if row["writer_id"] == "W2":
            row["writer_submission_id"] = "response-W1"
    with pytest.raises(ValueError, match="identifiers must be unique"):
        validate_writer_returns(rows, assignments, pair_map)
    with pytest.raises(ValueError, match="all 120"):
        validate_writer_returns(rows[:-1], assignments, pair_map)


def test_annotation_validator_rejects_invalid_ids_confidence_duplicates_and_missing_rows():
    _, _, _, authored, rows = complete_authored_and_annotations()
    invalid_target = deepcopy(rows)
    invalid_target[0]["target"] = "NOT-A-TARGET"
    with pytest.raises(ValueError, match="invalid annotation target"):
        validate_annotation_returns(invalid_target, authored)
    invalid_confidence = deepcopy(rows)
    invalid_confidence[0]["confidence"] = "6"
    with pytest.raises(ValueError, match="invalid annotation confidence"):
        validate_annotation_returns(invalid_confidence, authored)
    duplicate = deepcopy(rows)
    duplicate[-1] = deepcopy(duplicate[0])
    with pytest.raises(ValueError, match="3 labels"):
        validate_annotation_returns(duplicate, authored)
    duplicate_annotator = deepcopy(rows)
    for row in duplicate_annotator:
        if row["annotator_id"] == "A3":
            row["annotator_id"] = "A2"
    with pytest.raises(ValueError, match="3 labels"):
        validate_annotation_returns(duplicate_annotator, authored)
    with pytest.raises(ValueError, match="3 labels"):
        validate_annotation_returns(rows[:-1], authored)


def test_clarity_gate_requires_at_least_forty_complete_pairs():
    _, _, _, authored, rows = complete_authored_and_annotations()
    pair_ids = sorted({item["pair_id"] for item in authored})
    item_by_pair = {pair_id: next(item for item in authored if item["pair_id"] == pair_id) for pair_id in pair_ids}
    for pair_id in pair_ids[:21]:
        item_id = item_by_pair[pair_id]["item_id"]
        changed = 0
        for row in rows:
            if row["item_id"] == item_id and changed < 2:
                row["target"] = "CLARIFY"
                changed += 1
    annotations = validate_annotation_returns(rows, authored)
    clarity = clear_complete_pairs(authored, annotations)
    assert clarity["clear_complete_pairs"] == 39
    assert clarity["main_paper_threshold_met"] is False
    pairs, _, _ = inventory()
    with pytest.raises(ValueError, match="at least 40"):
        build_model_tasks(authored, pairs, clarity)


def test_private_eligibility_sidecar_is_complete_and_response_matched(tmp_path):
    path = tmp_path / "eligibility.csv"
    path.write_text(
        "writer_id,response_id,role,adult,english_task_ability,consent,no_assistance,"
        "technical_issue,completed,prior_tri_exposure,compensation_category,"
        "completion_seconds,ethics_determination\n"
        + "".join(
            f"W{i},response-W{i},writer,yes,yes,yes,yes,no,yes,no,"
            "noncontingent,600,policy-review-20260728\n"
            for i in range(1, 13)
        ),
        encoding="utf-8",
    )
    ledger = load_eligibility_ledger(path)
    merged = merge_eligibility("W1", {"response_id": "response-W1"}, ledger["W1"])
    assert merged["no_assistance"] == "yes"
    assert merged["technical_issue"] == "no"
    assert merged["completed"] == "yes"
    assert merged["prior_tri_exposure"] == "no"
    assert merged["ethics_determination"] == "policy-review-20260728"
    with pytest.raises(ValueError, match="does not match"):
        merge_eligibility("W1", {"response_id": "different"}, ledger["W1"])


def test_private_eligibility_sidecar_rejects_missing_writer(tmp_path):
    path = tmp_path / "eligibility.csv"
    path.write_text(
        "writer_id,response_id,role,adult,english_task_ability,consent,no_assistance,"
        "technical_issue,completed,prior_tri_exposure,compensation_category,"
        "completion_seconds,ethics_determination\n"
        + "".join(
            f"W{i},response-W{i},writer,yes,yes,yes,yes,no,yes,no,"
            "noncontingent,600,policy-review-20260728\n"
            for i in range(1, 12)
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="exactly W1-W12"):
        load_eligibility_ledger(path)
