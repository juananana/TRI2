from __future__ import annotations

from typing import Any, Literal


App = Literal["todoist", "simple_note"]


def score_runtime(runtime: Any, app: App) -> dict[str, Any]:
    if app == "todoist":
        find_tool = "find_earliest_incomplete_task"
        write_tool = "postpone_task"
        id_key = "task_id"
        changed_field = "due_date"
    else:
        find_tool = "find_alphabetically_first_note"
        write_tool = "append_to_note"
        id_key = "note_id"
        changed_field = "content"

    finds = [event for event in runtime.trace if event["tool"] == find_tool]
    expected_synced = runtime.scenario.reference_mode == "reevaluate"
    timed_finds = [event for event in finds if event["synced"] == expected_synced]
    binding_event = timed_finds[0] if timed_finds else None
    binding_id = binding_event["returned_id"] if binding_event else None
    expected_binding = (
        runtime.initial_target_id
        if runtime.scenario.reference_mode == "preserve"
        else runtime.refreshed_target_id
    )
    binding_timing_correct = binding_event is not None
    initial_binding_correct = binding_id == expected_binding and binding_timing_correct

    writes = [
        event
        for event in runtime.trace
        if event["tool"] == write_tool and event.get("status") == "ok"
    ]
    written_id = writes[-1]["arguments"][id_key] if writes else None
    target_correct = written_id == runtime.correct_target_id
    wrong_entity_write = bool(written_id is not None and not target_correct)

    post_sync = {str(row[id_key]): row for row in runtime.post_sync_snapshot}
    final = {str(row[id_key]): row for row in runtime.final_snapshot}
    changed_ids = sorted(
        entity_id
        for entity_id in post_sync.keys() & final.keys()
        if post_sync[entity_id][changed_field] != final[entity_id][changed_field]
    )
    collateral_ids = [
        entity_id for entity_id in changed_ids if entity_id != runtime.correct_target_id
    ]
    success = bool(
        initial_binding_correct
        and target_correct
        and changed_ids == [runtime.correct_target_id]
    )
    return {
        "scenario_id": runtime.scenario.scenario_id,
        "instruction": runtime.scenario.instruction,
        "reference_mode": runtime.scenario.reference_mode,
        "transition": runtime.scenario.transition,
        "paraphrase_id": runtime.scenario.paraphrase_id,
        "cluster_id": runtime.scenario.cluster_id,
        "app": app,
        "initial_target_id": runtime.initial_target_id,
        "refreshed_target_id": runtime.refreshed_target_id,
        "correct_target_id": runtime.correct_target_id,
        "bound_target_id": binding_id,
        "written_target_id": written_id,
        "initial_binding_correct": initial_binding_correct,
        "binding_timing_correct": binding_timing_correct,
        "target_correct": target_correct,
        "wrong_entity_write": wrong_entity_write,
        "stable_error": runtime.scenario.transition == "stable" and not target_correct,
        "unauthorized_rebinding": bool(
            initial_binding_correct
            and runtime.scenario.reference_mode == "preserve"
            and runtime.scenario.transition == "flip"
            and written_id == runtime.refreshed_target_id
        ),
        "premature_lock": bool(
            initial_binding_correct
            and runtime.scenario.reference_mode == "reevaluate"
            and runtime.scenario.transition == "flip"
            and written_id == runtime.initial_target_id
        ),
        "changed_entity_ids": changed_ids,
        "collateral_modification_ids": collateral_ids,
        "success": success,
        "trace": runtime.trace,
        "initial_snapshot": runtime.initial_snapshot,
        "post_sync_snapshot": runtime.post_sync_snapshot,
        "final_snapshot": runtime.final_snapshot,
    }
