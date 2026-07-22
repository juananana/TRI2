from __future__ import annotations

from types import SimpleNamespace

from external_pilots.appworld_tri.evaluation import score_runtime
from external_pilots.appworld_tri.scenarios import build_scenarios


def test_appworld_mvp_is_balanced() -> None:
    scenarios = build_scenarios()
    assert len(scenarios) == 8
    cells = {
        (mode, transition): sum(
            scenario.reference_mode == mode and scenario.transition == transition
            for scenario in scenarios
        )
        for mode in ("preserve", "reevaluate")
        for transition in ("stable", "flip")
    }
    assert set(cells.values()) == {2}


def test_wrong_entity_write_is_scored_from_database_id() -> None:
    scenario = next(
        scenario
        for scenario in build_scenarios()
        if scenario.reference_mode == "preserve" and scenario.transition == "flip"
    )
    runtime = SimpleNamespace(
        scenario=scenario,
        initial_target_id="10",
        refreshed_target_id="12",
        correct_target_id="10",
        trace=[
            {
                "tool": "record_binding",
                "status": "ok",
                "synced_at_binding": False,
                "arguments": {"task_id": "10"},
            },
            {"tool": "postpone_task", "status": "ok", "arguments": {"task_id": "12"}},
        ],
        post_sync_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20T00:00:00"},
            {"task_id": 12, "due_date": "2023-05-19T00:00:00"},
        ],
        final_snapshot=[
            {"task_id": 10, "due_date": "2023-05-20T00:00:00"},
            {"task_id": 12, "due_date": "2023-05-20T00:00:00"},
        ],
        initial_snapshot=[],
    )
    result = score_runtime(runtime)
    assert result["initial_binding_correct"]
    assert result["wrong_entity_write"]
    assert result["unauthorized_rebinding"]
    assert not result["success"]
