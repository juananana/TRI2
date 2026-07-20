from __future__ import annotations

from tri.v3_sqlite_conditional_tri_audit import build_report


def row(update: str, selected: str, predicted: str, status: str) -> dict:
    present = update != "remove"
    actionable = update != "invalidate"
    return {
        "model": "m",
        "task": {
            "binding": "anchored",
            "update": update,
            "pre_refresh_target": "A",
            "post_refresh_target": "B" if update != "stable" else "A",
            "bound_entity_present_after_refresh": present,
            "bound_entity_actionable_after_refresh": actionable,
        },
        "result": {
            "mode": "sqlite_generic_structured_ledger",
            "compiled_ledger": {"selected_entity_id": selected},
            "predicted_target": predicted,
            "action_status": status,
            "acted_ids": [predicted] if status.endswith("write") else [],
        },
    }


def test_conditional_audit_separates_core_tri_from_policy_errors() -> None:
    report = build_report(
        [
            row("flip", "A", "B", "wrong_entity_write"),
            row("name_collision", "A", "A", "successful_write"),
            row("invalidate", "A", "B", "wrong_entity_write"),
            row("remove", "A", "INVALID_BOUND_ENTITY", "safe_rejection"),
            row("stable", "A", "A", "successful_write"),
            row("flip", "C", "B", "wrong_entity_write"),
        ]
    )
    summary = report["summary"][0]
    assert summary["all_wrong_writes"] == 3
    assert summary["core_opportunities"] == 2
    assert summary["core_tri_writes"] == 1
    assert summary["policy_opportunities"] == 2
    assert summary["policy_wrong_writes"] == 1
    assert summary["stable_wrong_writes"] == 0
    assert summary["unclassified_wrong_writes"] == 1
