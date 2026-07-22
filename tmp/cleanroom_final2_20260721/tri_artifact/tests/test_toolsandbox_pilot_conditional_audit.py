from __future__ import annotations

from pathlib import Path

from tri.toolsandbox_pilot_conditional_audit import (
    build_report,
    strict_opportunity,
    unauthorized_rebinding,
)


def row(controller: str = "matched_generic", written: str = "REM-B") -> dict:
    state = (
        {"selected_entity_id": "REM-A"}
        if "generic" in controller
        else {"bound_target_id": "REM-A"}
    )
    return {
        "model": "test/model",
        "controller": controller,
        "scenario_id": "s1",
        "reference_mode": "preserve",
        "transition": "flip",
        "compiled_state": state,
        "expected_target_id": "REM-A",
        "post_sync_snapshot": [{"reminder_id": "REM-A"}, {"reminder_id": "REM-B"}],
        "written_target_ids": [written],
        "wrong_entity_write": written != "REM-A",
        "errors": [],
    }


def task() -> dict:
    return {
        "scenario_id": "s1",
        "initial_target_id": "REM-A",
        "refreshed_target_id": "REM-B",
    }


def test_strict_opportunity_requires_correct_auditable_binding() -> None:
    assert strict_opportunity(row(), task())
    assert unauthorized_rebinding(row(), task())
    bad = row()
    bad["compiled_state"]["selected_entity_id"] = "REM-C"
    assert not strict_opportunity(bad, task())


def test_untyped_plan_is_excluded() -> None:
    assert not strict_opportunity(row("matched_untyped"), task())


def test_report_lists_violation_ids(tmp_path: Path) -> None:
    import json

    manifest = tmp_path / "manifest.jsonl"
    run = tmp_path / "run.jsonl"
    manifest.write_text(json.dumps(task()) + "\n", encoding="utf-8")
    run.write_text(json.dumps(row()) + "\n", encoding="utf-8")
    report = build_report([run], manifest)
    summary = report["summary"][0]
    assert summary["strict_opportunities"] == 1
    assert summary["conditional_tri_violations"] == 1
    assert summary["violation_task_ids"] == ["s1"]
