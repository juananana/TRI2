from __future__ import annotations

import json
from pathlib import Path

from tri.v7_core_report import build_report, markdown


def make_row(task_id: str, cluster: str, update: str, predicted: str) -> dict:
    return {
        "model": "Qwen/test",
        "status": "ok",
        "task": {
            "id": task_id,
            "state_cluster_id": cluster,
            "binding": "anchored",
            "update": update,
            "pre_refresh_target": "A",
            "post_refresh_target": "A" if update == "stable" else "B",
            "correct_target": "A",
            "bound_entity_present_after_refresh": True,
            "bound_entity_actionable_after_refresh": True,
        },
        "result": {
            "mode": "generic_structured_ledger_then_act",
            "compiled_ledger": {"selected_entity_id": "A"},
            "predicted_target": predicted,
            "success": predicted == "A",
            "errors": [],
        },
    }


def test_v7_report_conditions_drift_on_correct_initial_binding(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    rows = [
        make_row("flip", "c1", "flip", "B"),
        make_row("collision", "c1", "name_collision", "A"),
        make_row("stable", "c2", "stable", "A"),
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    report = build_report([path], [], samples=100)
    run = report["runs"][0]
    assert run["core_opportunities"] == 2
    assert run["core_drifts"] == 1
    assert run["stable_errors"] == 0
    assert "(2 in this report)" in markdown(report)
