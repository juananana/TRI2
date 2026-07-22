from __future__ import annotations

import json
from pathlib import Path

from tri.v7_write_audit import build_report


def test_write_audit_separates_core_and_dynamic_old_writes(tmp_path: Path) -> None:
    run_path = tmp_path / "run.jsonl"
    replay_path = tmp_path / "replay.jsonl"
    base = {
        "model": "Qwen/test",
        "status": "ok",
        "result": {
            "mode": "generic_structured_ledger_then_act",
            "compiled_ledger": {"selected_entity_id": "A"},
            "errors": [],
        },
    }
    anchored = json.loads(json.dumps(base))
    anchored["task"] = {
        "id": "a", "state_cluster_id": "c1", "binding": "anchored", "update": "flip",
        "pre_refresh_target": "A", "post_refresh_target": "B", "correct_target": "A",
        "bound_entity_present_after_refresh": True, "bound_entity_actionable_after_refresh": True,
    }
    anchored["result"].update({"predicted_target": "B", "success": False})
    dynamic = json.loads(json.dumps(base))
    dynamic["task"] = {
        "id": "d", "state_cluster_id": "c2", "binding": "dynamic", "update": "flip",
        "pre_refresh_target": "A", "post_refresh_target": "B", "correct_target": "B",
        "bound_entity_present_after_refresh": True, "bound_entity_actionable_after_refresh": True,
    }
    dynamic["result"].update({"predicted_target": "A", "success": False})
    run_path.write_text(json.dumps(anchored) + "\n" + json.dumps(dynamic) + "\n", encoding="utf-8")
    replay_rows = [
        {"model": "Qwen/test", "mode": "generic_structured_ledger_then_act", "task_id": task_id,
         "action_status": "wrong_entity_write"}
        for task_id in ("a", "d")
    ]
    replay_path.write_text("".join(json.dumps(row) + "\n" for row in replay_rows), encoding="utf-8")
    report = build_report([run_path], replay_path)
    row = report["summary"][0]
    assert row["core_tri_writes"] == 1
    assert row["dynamic_old_target_writes"] == 1
    assert row["other_wrong_writes"] == 0
