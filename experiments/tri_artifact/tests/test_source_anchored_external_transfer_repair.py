from __future__ import annotations

from scripts.repair_source_anchored_external_transfer_execution import repair_row


def test_repair_preserves_model_fields_and_replaces_execution_failure(monkeypatch) -> None:
    row = {
        "task_id": "task-1",
        "model": "model",
        "controller": "condition",
        "predicted_target_id": "A",
        "expected_target_id": "A",
        "first_transport_error": None,
        "second_transport_error": None,
        "first_parse_error": None,
        "second_parse_error": None,
        "first_raw_content": '{"selected_target_id":"A"}',
        "second_raw_content": '{"tool":"write","arguments":{"id":"A"}}',
        "write_executed": False,
        "source_execution_error": "FileNotFoundError",
        "exact_target_success": False,
        "wrong_entity_write": False,
        "status": "failed",
    }
    monkeypatch.setattr(
        "scripts.repair_source_anchored_external_transfer_execution._execute_source_write",
        lambda task, predicted, state_root, agentdojo_root: (True, None),
    )
    repaired = repair_row(
        row,
        {
            "expected_target_id": "A",
            "initial_winner_id": "A",
            "refreshed_winner_id": "A",
            "old_target_present_after_refresh": True,
            "old_target_action_valid_after_refresh": True,
        },
        None,
        None,
    )
    assert repaired["first_raw_content"] == row["first_raw_content"]
    assert repaired["second_raw_content"] == row["second_raw_content"]
    assert repaired["model_requests_added_by_repair"] == 0
    assert repaired["write_executed"]
    assert repaired["exact_target_success"]
    assert repaired["status"] == "ok"
