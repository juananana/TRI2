from __future__ import annotations

from typing import Any

from .simple_note_environment import Runtime


def _by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["note_id"]): row for row in rows}


def score_runtime(runtime: Runtime) -> dict[str, Any]:
    bindings = [
        item
        for item in runtime.trace
        if item["tool"] == "record_binding" and item.get("status") == "ok"
    ]
    writes = [
        item
        for item in runtime.trace
        if item["tool"] == "append_to_note" and item.get("status") == "ok"
    ]
    binding_id = bindings[0]["arguments"]["note_id"] if len(bindings) == 1 else None
    written_id = writes[-1]["arguments"]["note_id"] if writes else None
    expected_binding = (
        runtime.initial_target_id
        if runtime.scenario.reference_mode == "preserve"
        else runtime.refreshed_target_id
    )
    binding_timing_correct = bool(
        len(bindings) == 1
        and bindings[0]["synced_at_binding"]
        == (runtime.scenario.reference_mode == "reevaluate")
    )

    post_sync = _by_id(runtime.post_sync_snapshot)
    final = _by_id(runtime.final_snapshot)
    changed_content_ids = sorted(
        note_id
        for note_id in post_sync.keys() & final.keys()
        if post_sync[note_id]["content"] != final[note_id]["content"]
    )
    collateral_ids = [
        note_id for note_id in changed_content_ids if note_id != runtime.correct_target_id
    ]
    target_correct = written_id == runtime.correct_target_id
    initial_binding_correct = binding_id == expected_binding and binding_timing_correct
    wrong_entity_write = bool(written_id is not None and not target_correct)
    success = bool(
        initial_binding_correct
        and target_correct
        and changed_content_ids == [runtime.correct_target_id]
    )
    return {
        "scenario_id": runtime.scenario.scenario_id,
        "instruction": runtime.scenario.instruction,
        "reference_mode": runtime.scenario.reference_mode,
        "transition": runtime.scenario.transition,
        "paraphrase_id": runtime.scenario.paraphrase_id,
        "cluster_id": runtime.scenario.cluster_id,
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
            runtime.scenario.reference_mode == "preserve"
            and runtime.scenario.transition == "flip"
            and written_id == runtime.refreshed_target_id
        ),
        "premature_lock": bool(
            runtime.scenario.reference_mode == "reevaluate"
            and runtime.scenario.transition == "flip"
            and written_id == runtime.initial_target_id
        ),
        "changed_content_ids": changed_content_ids,
        "collateral_modification_ids": collateral_ids,
        "success": success,
        "trace": runtime.trace,
        "initial_snapshot": runtime.initial_snapshot,
        "post_sync_snapshot": runtime.post_sync_snapshot,
        "final_snapshot": runtime.final_snapshot,
    }
