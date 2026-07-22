from __future__ import annotations

from types import SimpleNamespace

from external_pilots.appworld_tri.simple_note_evaluation import score_runtime
from external_pilots.appworld_tri.simple_note_scenarios import build_scenarios


def test_simple_note_mvp_is_balanced() -> None:
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


def test_simple_note_wrong_write_uses_database_content_diff() -> None:
    scenario = next(
        scenario
        for scenario in build_scenarios()
        if scenario.reference_mode == "preserve" and scenario.transition == "flip"
    )
    runtime = SimpleNamespace(
        scenario=scenario,
        initial_target_id="20",
        refreshed_target_id="22",
        correct_target_id="20",
        trace=[
            {
                "tool": "record_binding",
                "status": "ok",
                "synced_at_binding": False,
                "arguments": {"note_id": "20"},
            },
            {"tool": "append_to_note", "status": "ok", "arguments": {"note_id": "22"}},
        ],
        post_sync_snapshot=[
            {"note_id": 20, "content": "A"},
            {"note_id": 22, "content": "B"},
        ],
        final_snapshot=[
            {"note_id": 20, "content": "A"},
            {"note_id": 22, "content": "B\nreviewed"},
        ],
        initial_snapshot=[],
    )
    result = score_runtime(runtime)
    assert result["initial_binding_correct"]
    assert result["wrong_entity_write"]
    assert result["unauthorized_rebinding"]
    assert result["changed_content_ids"] == ["22"]
    assert not result["success"]
