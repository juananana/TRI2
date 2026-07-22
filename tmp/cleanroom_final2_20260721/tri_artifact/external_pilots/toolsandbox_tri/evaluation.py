from __future__ import annotations

from typing import Any

from .environment import Runtime, reminder_rows


def _timestamps(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {str(row["reminder_id"]): float(row["reminder_timestamp"]) for row in rows}


def score_runtime(runtime: Runtime) -> dict[str, Any]:
    final_snapshot = reminder_rows()
    before = _timestamps(runtime.post_sync_snapshot)
    after = _timestamps(final_snapshot)
    writes = sorted(
        reminder_id
        for reminder_id in before.keys() & after.keys()
        if before[reminder_id] != after[reminder_id]
    )
    mutation_attempts = [event for event in runtime.trace if event["tool"] == "postpone_reminder"]
    successful_attempts = [event for event in mutation_attempts if event["status"] == "ok"]
    attempted_ids = [event["arguments"]["reminder_id"] for event in mutation_attempts]
    expected = runtime.scenario.correct_target_id
    final_state_success = writes == ([] if expected is None else [expected])
    wrong_write_ids = [target for target in writes if target != expected]
    invalid_attempts = sum(event["status"] == "rejected" for event in mutation_attempts)
    unnecessary_rejection = expected is not None and not successful_attempts
    tools = [event["tool"] for event in runtime.trace]
    binding_events = [
        event
        for event in runtime.trace
        if event["tool"] in {"record_binding", "observe_binding"}
        and event["status"] == "ok"
    ]
    binding_target_id = (
        str(binding_events[0]["arguments"]["reminder_id"])
        if len(binding_events) == 1
        else None
    )
    expected_binding_id = (
        runtime.scenario.initial_target_id
        if runtime.scenario.reference_mode == "preserve"
        else runtime.scenario.refreshed_target_id
    )
    binding_timing_correct = bool(
        len(binding_events) == 1
        and binding_events[0]["synced_at_binding"]
        == (runtime.scenario.reference_mode == "reevaluate")
    )
    initial_binding_correct = bool(
        binding_target_id == expected_binding_id and binding_timing_correct
    )
    binding_observed = len(binding_events) == 1
    if not runtime.scenario.require_binding_record:
        binding_observed = False
        binding_timing_correct = False
        initial_binding_correct = False
    try:
        search_index = tools.index("search_reminder")
        sync_index = tools.index("sync_reminders")
        search_order_success = (
            search_index < sync_index
            if runtime.scenario.reference_mode == "preserve"
            else sync_index < search_index
        )
    except ValueError:
        search_order_success = False
    order_success = (
        binding_timing_correct
        if runtime.scenario.require_binding_record
        else search_order_success
    )
    tri_opportunity = bool(
        runtime.scenario.require_binding_record
        and initial_binding_correct
        and runtime.synced
    )
    unauthorized_rebinding = bool(
        tri_opportunity
        and runtime.scenario.reference_mode == "preserve"
        and runtime.scenario.transition == "flip"
        and any(target != runtime.scenario.initial_target_id for target in writes)
    )
    premature_lock = bool(
        tri_opportunity
        and runtime.scenario.reference_mode == "reevaluate"
        and runtime.scenario.transition == "flip"
        and runtime.scenario.initial_target_id in writes
    )
    return {
        "scenario_id": runtime.scenario.scenario_id,
        "reference_mode": runtime.scenario.reference_mode,
        "transition": runtime.scenario.transition,
        "expected_target_id": expected,
        "attempted_target_ids": attempted_ids,
        "written_target_ids": writes,
        "wrong_write_ids": wrong_write_ids,
        "wrong_entity_write": bool(wrong_write_ids),
        "invalid_attempts": invalid_attempts,
        "unnecessary_rejection": unnecessary_rejection,
        "binding_required": runtime.scenario.require_binding_record,
        "binding_observed": binding_observed,
        "binding_target_id": binding_target_id,
        "binding_source": (
            binding_events[0].get("source", "agent_tool")
            if len(binding_events) == 1
            else None
        ),
        "expected_binding_id": expected_binding_id,
        "binding_timing_correct": binding_timing_correct,
        "initial_binding_correct": initial_binding_correct,
        "tri_opportunity": tri_opportunity,
        "unauthorized_rebinding": unauthorized_rebinding,
        "premature_lock": premature_lock,
        "search_order_success": search_order_success,
        "order_success": order_success,
        "final_state_success": final_state_success,
        "success": final_state_success and order_success and not unnecessary_rejection,
        "initial_snapshot": runtime.initial_snapshot,
        "post_sync_snapshot": runtime.post_sync_snapshot,
        "final_snapshot": final_snapshot,
        "tool_trace": runtime.trace,
        "cluster_id": runtime.scenario.cluster_id,
        "paraphrase_id": runtime.scenario.paraphrase_id,
    }
