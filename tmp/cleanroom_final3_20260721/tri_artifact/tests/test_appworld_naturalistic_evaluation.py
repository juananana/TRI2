from types import SimpleNamespace

from external_pilots.appworld_tri.naturalistic_evaluation import score_runtime
from external_pilots.appworld_tri.scenarios import build_scenarios


def test_preserve_flip_rebinding_is_conditional_tri() -> None:
    scenario = next(
        item
        for item in build_scenarios()
        if item.reference_mode == "preserve" and item.transition == "flip"
    )
    runtime = SimpleNamespace(
        scenario=scenario,
        initial_target_id="10",
        refreshed_target_id="12",
        correct_target_id="10",
        trace=[
            {
                "tool": "find_earliest_incomplete_task",
                "status": "ok",
                "synced": False,
                "returned_id": "10",
            },
            {"tool": "postpone_task", "status": "ok", "arguments": {"task_id": "12"}},
        ],
        post_sync_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20"},
            {"task_id": 12, "due_date": "2023-05-19"},
        ],
        final_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20"},
            {"task_id": 12, "due_date": "2023-05-20"},
        ],
        initial_snapshot=[],
    )
    result = score_runtime(runtime, "todoist")
    assert result["initial_binding_correct"]
    assert result["wrong_entity_write"]
    assert result["unauthorized_rebinding"]
    assert not result["success"]


def test_post_sync_find_is_not_preserve_binding() -> None:
    scenario = next(
        item
        for item in build_scenarios()
        if item.reference_mode == "preserve" and item.transition == "flip"
    )
    runtime = SimpleNamespace(
        scenario=scenario,
        initial_target_id="10",
        refreshed_target_id="12",
        correct_target_id="10",
        trace=[
            {
                "tool": "find_earliest_incomplete_task",
                "status": "ok",
                "synced": True,
                "returned_id": "12",
            },
            {"tool": "postpone_task", "status": "ok", "arguments": {"task_id": "12"}},
        ],
        post_sync_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20"},
            {"task_id": 12, "due_date": "2023-05-19"},
        ],
        final_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20"},
            {"task_id": 12, "due_date": "2023-05-20"},
        ],
        initial_snapshot=[],
    )
    result = score_runtime(runtime, "todoist")
    assert not result["initial_binding_correct"]
    assert result["wrong_entity_write"]
    assert not result["unauthorized_rebinding"]
