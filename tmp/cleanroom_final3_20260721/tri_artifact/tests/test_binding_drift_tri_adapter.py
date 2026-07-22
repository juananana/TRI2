import json
from pathlib import Path

from tri.binding_drift_tri_adapter import entity_lock_target, freeze_smoke, reverify_prompt, score_target, summarize


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_smoke_is_ten_symmetric_pairs() -> None:
    rows = freeze_smoke(ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")
    assert len(rows) == 20
    assert len({row["domain"] for row in rows}) == 10
    assert {row["binding"] for row in rows} == {"anchored", "dynamic"}
    assert all(row["update"] == "flip" for row in rows)
    assert all(row["bound_entity_actionable_after_refresh"] for row in rows)


def test_entity_lock_exposes_complementary_failure() -> None:
    rows = freeze_smoke(ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")
    correct = [entity_lock_target(row) == row["correct_target"] for row in rows]
    assert sum(correct) == 10
    assert all(correct[index] for index in range(0, 20, 2))
    assert not any(correct[index] for index in range(1, 20, 2))


def test_reverify_prompt_has_no_gold_or_mode_label() -> None:
    task = freeze_smoke(ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")[0]
    prompt = reverify_prompt(task)
    assert task["instruction"] in prompt
    assert task["correct_target"] not in prompt or task["correct_target"] in json.dumps(task["refreshed_state"])
    assert "reference_mode" not in prompt
    assert "correct_target" not in prompt


def test_summary_separates_modes() -> None:
    rows = []
    for binding, success in (("anchored", True), ("dynamic", False)):
        rows.append({"task": {"binding": binding}, "result": {"success": success, "drift_to_refreshed_winner": False, "premature_lock": not success, "other_visible_target": False, "ambiguous_or_clarify": False, "errors": []}})
    report = summarize(rows)
    assert report["correct"] == 1
    assert report["anchored"]["correct"] == 1
    assert report["dynamic"]["premature_lock"] == 1


def test_stable_dynamic_target_is_not_a_premature_lock() -> None:
    task = next(
        row
        for row in json.loads(
            "[" + ",".join(
                (ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")
                .read_text()
                .splitlines()
            ) + "]"
        )
        if row["binding"] == "dynamic" and row["update"] == "stable"
    )
    result = score_target(task, task["pre_refresh_target"])
    assert result["success"]
    assert not result["premature_lock"]
