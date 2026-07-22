from __future__ import annotations

from tri.v3_generic_tri_audit import build_report


def row(update: str, selected: str, predicted: str, pre: str = "A", post: str = "B") -> dict:
    return {
        "model": "m",
        "task": {
            "binding": "anchored",
            "update": update,
            "pre_refresh_target": pre,
            "post_refresh_target": post,
            "correct_target": pre,
            "bound_entity_present_after_refresh": True,
            "bound_entity_actionable_after_refresh": True,
            "template_id": "t1",
        },
        "result": {
            "compiled_ledger": {"selected_entity_id": selected},
            "predicted_target": predicted,
        },
    }


def test_generic_audit_conditions_on_selected_entity_id() -> None:
    report = build_report(
        [
            row("flip", "A", "B"),
            row("flip", "A", "A"),
            row("stable", "A", "A", post="A"),
            row("flip", "C", "B"),
        ]
    )
    flip = next(x for x in report["summary"] if x["update"] == "flip")
    assert flip["initial_binding_correct"] == 2
    assert flip["opportunities"] == 2
    assert flip["drift_to_new_leader"] == 1
    assert flip["final_wrong_target"] == 1
