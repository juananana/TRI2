from __future__ import annotations

import pytest

pytest.importorskip("tool_sandbox")

from external_pilots.toolsandbox_tri.environment import (  # noqa: E402
    active_scenario,
    postpone_reminder,
    record_binding,
    search_all_reminders,
    sync_reminders,
)
from external_pilots.toolsandbox_tri.evaluation import score_runtime  # noqa: E402
from external_pilots.toolsandbox_tri.oracle import (  # noqa: E402
    run_frozen_oracle_suite,
    run_oracle,
    run_oracle_suite,
)
from external_pilots.toolsandbox_tri.agent_runner import run_agent  # noqa: E402
from external_pilots.toolsandbox_tri.matched_runner import run_matched_agent  # noqa: E402
from external_pilots.toolsandbox_tri.gate_replay import replay_lifecycle_gate  # noqa: E402
from external_pilots.toolsandbox_tri.scenarios import (  # noqa: E402
    build_matched_heldout_scenarios,
    build_pilot_scenarios,
    build_single_turn_2x2_scenarios,
)


def test_oracle_suite_is_perfect() -> None:
    rows = run_oracle_suite()
    assert len(rows) == 4
    assert all(row["success"] for row in rows)
    assert not any(row["wrong_entity_write"] for row in rows)
    assert sum(row["written_target_ids"] == [] for row in rows) == 2


def test_wrong_rebinding_is_scored_as_wrong_write() -> None:
    scenario = build_pilot_scenarios()[0]
    with active_scenario(scenario) as runtime:
        search_all_reminders()
        sync_reminders()
        postpone_reminder("REM-B")
        score = score_runtime(runtime)
    assert not score["success"]
    assert score["wrong_entity_write"]
    assert score["wrong_write_ids"] == ["REM-B"]


def test_locked_target_attempt_is_rejected_without_write() -> None:
    scenario = build_pilot_scenarios()[2]
    with active_scenario(scenario) as runtime:
        search_all_reminders()
        sync_reminders()
        result = postpone_reminder("REM-A")
        score = score_runtime(runtime)
    assert result["status"] == "rejected"
    assert score["written_target_ids"] == []
    assert score["invalid_attempts"] == 1


def test_remove_transition_preserves_snapshot_boundary() -> None:
    scenario = build_pilot_scenarios()[3]
    with active_scenario(scenario) as runtime:
        search_all_reminders()
        sync_reminders()
        score = score_runtime(runtime)
    assert {row["reminder_id"] for row in score["initial_snapshot"]} == {"REM-A", "REM-C"}
    assert {row["reminder_id"] for row in score["post_sync_snapshot"]} == {"REM-C"}
    assert score["success"]


class ScriptedClient:
    def __init__(self, outputs: list[dict]) -> None:
        self.outputs = iter(outputs)

    def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
        import json

        return json.dumps(next(self.outputs))


def test_autonomous_lifecycle_trace() -> None:
    state0 = {
        "reference_mode": "unknown",
        "selector": "earliest due reminder",
        "bound_target_id": None,
        "invalidity_policy": "reject",
    }
    state1 = {**state0, "reference_mode": "preserve", "bound_target_id": "REM-A"}
    client = ScriptedClient(
        [
            {"tool": "search_reminder", "arguments": {}, "state": state0},
            {"tool": "sync_reminders", "arguments": {}, "state": state1},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-A", "seconds": 86400},
                "state": state1,
            },
            {"tool": "finish", "arguments": {}, "state": state1},
        ]
    )
    result = run_agent(client, build_pilot_scenarios()[0], "lifecycle")
    assert result["success"]
    assert result["written_target_ids"] == ["REM-A"]
    assert result["finished"]


def test_frozen_oracle_suite_is_perfect_and_balanced() -> None:
    rows = run_frozen_oracle_suite()
    assert len(rows) == 24
    assert all(row["success"] for row in rows)
    assert not any(row["wrong_entity_write"] for row in rows)
    assert sum(row["reference_mode"] == "preserve" for row in rows) == 12
    assert sum(row["reference_mode"] == "reevaluate" for row in rows) == 12


def test_single_turn_2x2_oracle_is_perfect_and_auditable() -> None:
    scenarios = build_single_turn_2x2_scenarios()
    assert len(scenarios) == 96
    rows = [run_oracle(scenario) for scenario in scenarios]
    assert all(row["success"] for row in rows)
    assert all(row["binding_observed"] for row in rows)
    assert all(row["initial_binding_correct"] for row in rows)
    assert all(row["tri_opportunity"] for row in rows)
    assert not any(row["wrong_entity_write"] for row in rows)
    for mode in ("preserve", "reevaluate"):
        for transition in ("stable", "flip"):
            cell = [
                row
                for row in rows
                if row["reference_mode"] == mode and row["transition"] == transition
            ]
            assert len(cell) == 24


def test_binding_record_is_non_mutating_and_requires_latest_search() -> None:
    scenario = build_single_turn_2x2_scenarios()[0]
    with active_scenario(scenario) as runtime:
        before = runtime.initial_snapshot
        rejected = record_binding("REM-A")
        search_all_reminders()
        accepted = record_binding("REM-A")
        after = runtime.initial_snapshot
        trace_tools = [event["tool"] for event in runtime.trace]
    assert rejected["status"] == "rejected"
    assert accepted["status"] == "ok"
    assert before == after
    assert trace_tools == ["record_binding", "search_reminder", "record_binding"]


def test_scripted_full_history_trace_exposes_preserve_rebinding() -> None:
    scenario = build_single_turn_2x2_scenarios()[2]
    client = ScriptedClient(
        [
            {"tool": "search_reminder", "arguments": {}},
            {"tool": "record_binding", "arguments": {"reminder_id": "REM-A"}},
            {"tool": "sync_reminders", "arguments": {}},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-B", "seconds": 86400},
            },
            {"tool": "finish", "arguments": {}},
        ]
    )
    result = run_agent(client, scenario, "full_history")
    assert result["tri_opportunity"]
    assert result["unauthorized_rebinding"]
    assert result["wrong_entity_write"]
    assert not result["success"]


def test_scripted_full_history_trace_accepts_reevaluate_flip() -> None:
    scenario = build_single_turn_2x2_scenarios()[3]
    client = ScriptedClient(
        [
            {"tool": "sync_reminders", "arguments": {}},
            {"tool": "search_reminder", "arguments": {}},
            {"tool": "record_binding", "arguments": {"reminder_id": "REM-B"}},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-B", "seconds": 86400},
            },
            {"tool": "finish", "arguments": {}},
        ]
    )
    result = run_agent(client, scenario, "full_history")
    assert result["tri_opportunity"]
    assert not result["premature_lock"]
    assert result["success"]


def test_generic_state_observation_does_not_add_an_agent_step() -> None:
    preserve = build_single_turn_2x2_scenarios()[2]
    preserve_client = ScriptedClient(
        [
            {
                "tool": "search_reminder",
                "arguments": {},
                "state": {"target_reminder_id": "REM-A"},
            },
            {
                "tool": "sync_reminders",
                "arguments": {},
                "state": {"target_reminder_id": "REM-A"},
            },
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-A", "seconds": 86400},
                "state": {"target_reminder_id": "REM-A"},
            },
            {"tool": "finish", "arguments": {}, "state": {"done": True}},
        ]
    )
    preserve_result = run_agent(preserve_client, preserve, "generic_state_observed")
    assert preserve_result["tri_opportunity"]
    assert preserve_result["binding_source"] == "controller_state"
    assert preserve_result["success"]

    reevaluate = build_single_turn_2x2_scenarios()[3]
    reevaluate_client = ScriptedClient(
        [
            {"tool": "sync_reminders", "arguments": {}, "state": {}},
            {"tool": "search_reminder", "arguments": {}, "state": {}},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-B", "seconds": 86400},
                "state": {"target_reminder_id": "REM-B"},
            },
            {"tool": "finish", "arguments": {}, "state": {"done": True}},
        ]
    )
    reevaluate_result = run_agent(
        reevaluate_client, reevaluate, "generic_state_observed"
    )
    assert reevaluate_result["tri_opportunity"]
    assert not reevaluate_result["premature_lock"]
    assert reevaluate_result["success"]


def test_matched_lifecycle_compiler_boundary() -> None:
    compiler_state = {
        "reference_mode": "preserve",
        "selector": "the editable reminder due earliest",
        "bound_target_id": "REM-A",
        "invalidity_policy": "reject",
    }
    client = ScriptedClient(
        [
            {"tool": "search_reminder", "arguments": {}},
            compiler_state,
            {"tool": "sync_reminders", "arguments": {}},
            {"tool": "search_reminder", "arguments": {}},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-A", "seconds": 86400},
            },
            {"tool": "finish", "arguments": {}},
        ]
    )
    result = run_matched_agent(client, build_pilot_scenarios()[0], "lifecycle")
    assert result["success"]
    assert result["compiler_calls"] == 1
    assert result["compiled_state"] == compiler_state
    assert result["written_target_ids"] == ["REM-A"]


def test_matched_generic_compiler_binding_is_observed_before_sync() -> None:
    compiler_state = {
        "task_goal": "postpone selected reminder after sync",
        "selected_entity_id": "REM-A",
        "selected_entity_snapshot": {"reminder_id": "REM-A"},
        "selector": "the editable reminder due earliest",
        "action": "postpone",
        "action_preconditions": {"editable": True},
    }
    client = ScriptedClient(
        [
            {"tool": "search_reminder", "arguments": {}},
            compiler_state,
            {"tool": "sync_reminders", "arguments": {}},
            {
                "tool": "postpone_reminder",
                "arguments": {"reminder_id": "REM-A", "seconds": 86400},
            },
            {"tool": "finish", "arguments": {}},
        ]
    )
    result = run_matched_agent(client, build_single_turn_2x2_scenarios()[2], "generic")
    assert result["controller"] == "matched_generic_state_observed"
    assert result["binding_source"] == "controller_state"
    assert result["tri_opportunity"]
    assert result["success"]


def test_matched_heldout_oracle_is_perfect() -> None:
    from external_pilots.toolsandbox_tri.oracle import run_oracle

    rows = [run_oracle(scenario) for scenario in build_matched_heldout_scenarios()]
    assert len(rows) == 24
    assert all(row["success"] for row in rows)
    assert not any(row["wrong_entity_write"] for row in rows)


def test_gate_replay_enforces_compiled_preserve_target() -> None:
    row = {
        "controller": "matched_lifecycle",
        "compiled_state": {
            "reference_mode": "preserve",
            "bound_target_id": "REM-A",
        },
        "order_success": True,
        "errors": [],
        "post_sync_snapshot": [{"reminder_id": "REM-A"}, {"reminder_id": "REM-B"}],
        "transition": "flip",
        "expected_target_id": "REM-A",
        "success": False,
    }
    replay = replay_lifecycle_gate(row)
    assert replay["success"]
    assert replay["written_target_ids"] == ["REM-A"]
    assert replay["gate_applied"]
