from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.prepare_independent_holdout_annotation import (
    load_eligibility_ledger,
    merge_eligibility,
)
from scripts.freeze_independent_holdout_model_tasks import (
    validate_annotation_provenance,
)

from tri.independent_language_holdout import (
    ANNOTATORS,
    MODEL_PRELABELERS,
    WRITERS,
    build_annotation_order,
    build_blind_prelabel_tasks,
    build_assignments,
    build_model_tasks,
    build_scenario_pairs,
    clear_complete_pairs,
    design_fidelity_summary,
    blind_item_id,
    normalize_wjx_writer_content,
    normalize_wjx_writer_export,
    resolve_blind_annotation_returns,
    validate_provisional_writer_returns,
    validate_annotation_returns,
    validate_writer_returns,
    writer_combined_wjx,
    writer_item_order,
    write_annotation_wjx_forms,
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


def test_distributable_annotation_forms_keep_private_key_outside(tmp_path):
    pairs, assignments, pair_map = inventory()
    authored = validate_writer_returns(
        complete_writer_rows(assignments, pair_map), assignments, pair_map
    )
    forms = tmp_path / "forms"
    write_annotation_wjx_forms(authored, pairs, assignments, forms)
    assert (tmp_path / "private_annotation_key.jsonl").is_file()
    assert not (forms / "private_annotation_key.jsonl").exists()
    text = next(forms.glob("annotator_A1_part_*_wjx.txt")).read_text()
    assert "【情境 01｜BI-" in text
    assert "【情境 01｜IH-" not in text


def test_blind_prelabel_tasks_exclude_writer_design_and_pair_labels():
    pairs, assignments, pair_map = inventory()
    authored = validate_writer_returns(
        complete_writer_rows(assignments, pair_map), assignments, pair_map
    )
    forbidden = {
        "writer_id",
        "item_id",
        "writer_intent",
        "writer_confidence",
        "mode",
        "reference_mode_design",
        "pair_id",
        "design_target",
        "correct_target",
        "gold",
    }
    for prelabeler in MODEL_PRELABELERS:
        tasks = build_blind_prelabel_tasks(authored, pairs, assignments, prelabeler)
        assert len(tasks) == 120
        assert all(not forbidden.intersection(row) for row in tasks)
        assert all("CLARIFY" in row["allowed_targets"] for row in tasks)
        assert all(row["blind_item_id"].startswith("BI-") for row in tasks)
        assert all(not row["blind_item_id"].endswith(("-P", "-R")) for row in tasks)
        assert all(row["model_prelabeler_id"].startswith("M") for row in tasks)


def test_blind_annotation_key_resolves_without_exposing_condition_ids():
    _, assignments, _ = inventory()
    key_rows = [
        {"blind_item_id": blind_item_id(row["item_id"]), "item_id": row["item_id"]}
        for row in assignments
    ]
    returns = [
        {
            "annotator_id": "A1",
            "blind_item_id": blind_item_id(assignments[0]["item_id"]),
            "target": "CLARIFY",
            "confidence": "3",
        }
    ]
    resolved = resolve_blind_annotation_returns(returns, key_rows)
    assert resolved[0]["item_id"] == assignments[0]["item_id"]
    assert assignments[0]["item_id"] not in returns[0]["blind_item_id"]


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


def test_design_fidelity_precheck_bounds_the_future_clarity_gate():
    _, assignments, pair_map = inventory()
    authored = validate_writer_returns(
        complete_writer_rows(assignments, pair_map), assignments, pair_map
    )
    authored[0]["design_intent_aligned"] = False
    summary = design_fidelity_summary(authored)
    assert summary["design_aligned_items"] == 119
    assert summary["design_aligned_complete_pairs"] == 59
    assert summary["maximum_possible_clear_complete_pairs"] == 59
    assert summary["annotation_gate_feasible"] is True


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


def test_provisional_content_staging_does_not_relax_formal_eligibility_gate():
    _, assignments, pair_map = inventory()
    rows = []
    for writer_id in WRITERS:
        raw = raw_writer_export(writer_id, assignments, pair_map)
        for field in ("no_assistance", "technical_issue", "completed"):
            raw.pop(field)
        rows.extend(
            normalize_wjx_writer_content(writer_id, raw, assignments, pair_map)
        )
        with pytest.raises(ValueError, match="no-assistance"):
            normalize_wjx_writer_export(writer_id, raw, assignments, pair_map)
    staged = validate_provisional_writer_returns(rows, assignments, pair_map)
    assert len(staged) == 120
    assert all("writer_submission_id" not in row for row in staged)


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


def test_clarity_gate_rejects_writer_intent_that_conflicts_with_assigned_order():
    _, _, _, authored, rows = complete_authored_and_annotations()
    item = authored[0]
    replacement = next(
        target
        for target in item["allowed_target_ids"]
        if target not in {"CLARIFY", item["writer_intent"]}
    )
    item["writer_intent"] = replacement
    item["writer_intent_determinate"] = True
    item["design_intent_aligned"] = False
    for row in rows:
        if row["item_id"] == item["item_id"]:
            row["target"] = replacement
    annotations = validate_annotation_returns(rows, authored)
    clarity = clear_complete_pairs(authored, annotations)
    assert clarity["item_clear"][item["item_id"]] is False
    assert clarity["design_aligned_items"] == 119
    assert clarity["design_aligned_complete_pairs"] == 59


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


def test_private_eligibility_accepts_namespaced_ids_for_separate_wjx_surveys(tmp_path):
    path = tmp_path / "eligibility.csv"
    path.write_text(
        "writer_id,response_id,role,adult,english_task_ability,consent,no_assistance,"
        "technical_issue,completed,prior_tri_exposure,compensation_category,"
        "completion_seconds,ethics_determination\n"
        + "".join(
            f"W{i},W{i}:1,writer,yes,yes,yes,yes,no,yes,no,"
            "noncontingent,600,policy-review-20260728\n"
            for i in range(1, 13)
        ),
        encoding="utf-8",
    )
    ledger = load_eligibility_ledger(path)
    merged = merge_eligibility("W1", {"序号": "1"}, ledger["W1"])
    assert merged["response_id"] == "W1:1"


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


def test_annotation_provenance_requires_locked_independent_humans(tmp_path):
    returns = tmp_path / "returns.csv"
    key = tmp_path / "key.jsonl"
    returns.write_text("blind_item_id,target\nBI-X,CLARIFY\n", encoding="utf-8")
    key.write_text('{"blind_item_id":"BI-X","item_id":"IH-X"}\n', encoding="utf-8")
    import hashlib

    manifest = {
        "status": "independent-human-annotation-complete",
        "annotation_returns_sha256": hashlib.sha256(returns.read_bytes()).hexdigest(),
        "private_annotation_key_sha256": hashlib.sha256(key.read_bytes()).hexdigest(),
        "annotators": {
            annotator: {
                "source": "independent_human",
                "completed": True,
                "blind": True,
                "saw_model_prelabels_before_lock": False,
            }
            for annotator in ANNOTATORS
        },
    }
    path = tmp_path / "provenance.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert validate_annotation_provenance(path, returns, key)["status"].startswith(
        "independent-human"
    )
    manifest["annotators"]["A1"]["saw_model_prelabels_before_lock"] = True
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="A1"):
        validate_annotation_provenance(path, returns, key)
