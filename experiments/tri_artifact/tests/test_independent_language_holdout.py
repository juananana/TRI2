from __future__ import annotations

from pathlib import Path

from tri.independent_language_holdout import (
    ANNOTATORS,
    WRITERS,
    build_annotation_order,
    build_assignments,
    build_model_tasks,
    build_scenario_pairs,
    clear_complete_pairs,
    sha256_bytes,
    validate_annotation_returns,
    validate_writer_returns,
    writer_combined_wjx,
    writer_stage_a_wjx,
    writer_stage_b_wjx,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"


def inventory():
    pairs = build_scenario_pairs(SOURCE)
    assignments = build_assignments(pairs)
    return pairs, assignments, {row["pair_id"]: row for row in pairs}


def test_holdout_has_sixty_pairs_and_balanced_disjoint_writers():
    pairs, assignments, _ = inventory()
    assert len(pairs) == 60
    assert len({row["domain"] for row in pairs}) == 10
    assert len(assignments) == 120
    for writer in WRITERS:
        rows = [row for row in assignments if row["writer_id"] == writer]
        assert len(rows) == 20
        assert sum(row["mode"] == "preserve" for row in rows) == 10
    by_pair = {}
    for row in assignments:
        by_pair.setdefault(row["pair_id"], []).append(row)
    assert all(len({row["writer_id"] for row in rows}) == 2 for rows in by_pair.values())


def test_writer_wjx_forms_are_short_and_readable():
    _, assignments, pair_map = inventory()
    for writer in WRITERS:
        stage_a = writer_stage_a_wjx(writer, 1, assignments, pair_map)
        stage_b = writer_stage_b_wjx(writer, 1, assignments, pair_map)
        assert stage_a.count("[填空题]") == 10
        assert stage_a.count("当前可见记录：") == 10
        assert stage_a.count("\u2028") >= 50
        assert "同步后的记录：" not in stage_a
        assert stage_b.count("你在已提交的英文请求中打算操作哪个对象") == 10
        assert stage_b.count("你对这个意图判断有多确定") == 10
        assert "同步后的记录：" in stage_b


def test_combined_writer_wjx_keeps_all_a_items_before_b_items():
    _, assignments, pair_map = inventory()
    for writer in WRITERS:
        form = writer_combined_wjx(writer, assignments, pair_map)
        assert form.count("[填空题]") == 20
        assert form.count("根据这条原句，你原本打算操作哪个对象") == 20
        assert form.count("你对这个意图判断有多确定") == 20
        assert form.count("[分页栏]") == 7
        assert form.index("【A 阶段｜第 4/4 页】") < form.index("【B 阶段｜第 1/4 页】")
        assert form.index("【B 阶段｜第 1/4 页】") < form.index("【同步后列表】")
        assert "负责人" not in form and "可执行" not in form
        assert "Check today's weather, then send me a reminder." in form
        assert form.count("你在 A 阶段写下：“[q") == 20
        assert all(form.count(f"[q{question}]") == 1 for question in range(4, 24))
        b_stage = form[form.index("【B 阶段｜第 1/4 页】") :]
        assert "【必须表达的顺序】" not in b_stage


def test_twelve_writer_two_page_prototype_halves_writer_burden():
    pairs, _, pair_map = inventory()
    writers = tuple(f"W{index}" for index in range(1, 13))
    assignments = build_assignments(pairs, writers)
    for writer in writers:
        rows = [row for row in assignments if row["writer_id"] == writer]
        assert len(rows) == 10
        assert sum(row["mode"] == "preserve" for row in rows) == 5
    form = writer_combined_wjx(
        "W1",
        assignments,
        pair_map,
        page_size=10,
        title_suffix="12人版两页预览",
    )
    assert form.count("[填空题]") == 10
    assert form.count("根据这条原句，你原本打算操作哪个对象") == 10
    assert form.count("[分页栏]") == 1
    assert "【A 阶段｜第 1/1 页】" in form
    assert "【B 阶段｜第 1/1 页】" in form
    assert all(form.count(f"[q{question}]") == 1 for question in range(4, 14))


def test_twelve_writer_final_form_has_pilot_usability_fixes():
    pairs, _, pair_map = inventory()
    writers = tuple(f"W{index}" for index in range(1, 13))
    assignments = build_assignments(pairs, writers)
    form = writer_combined_wjx(
        "W1",
        assignments,
        pair_map,
        page_size=10,
        title_suffix="12人版最终",
    )
    assert "不要因为现在看到新列表而改变原句含义" in form
    assert "【意图确认 01/10｜" in form
    assert "【意图确认 10/10｜" in form
    assert "已解决 否" not in form
    assert "已完成 否" not in form
    assert "未解决" in form
    assert "未完成" in form


def test_annotation_orders_keep_pair_members_nonadjacent():
    _, assignments, _ = inventory()
    pair_by_item = {row["item_id"]: row["pair_id"] for row in assignments}
    for annotator in ANNOTATORS:
        order = build_annotation_order(assignments, annotator)
        assert len(order) == 120 and len(set(order)) == 120
        assert all(pair_by_item[a] != pair_by_item[b] for a, b in zip(order, order[1:]))


def test_return_validation_and_clear_pair_gate():
    pairs, assignments, pair_map = inventory()
    writer_rows = []
    for assignment in assignments:
        instruction = f"Independent request for {assignment['item_id']}."
        pair = pair_map[assignment["pair_id"]]
        intent = (
            pair["pre_refresh_target"]
            if assignment["mode"] == "preserve"
            else pair["post_refresh_target"]
        )
        writer_rows.append(
            {
                "item_id": assignment["item_id"],
                "writer_id": assignment["writer_id"],
                "instruction": instruction,
                "instruction_sha256": sha256_bytes(instruction.encode()),
                "writer_intent": intent,
                "writer_confidence": "5",
            }
        )
    authored = validate_writer_returns(writer_rows, assignments, pair_map)
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
    assert all(row["correct_target"] == row["design_target"] for row in tasks)
