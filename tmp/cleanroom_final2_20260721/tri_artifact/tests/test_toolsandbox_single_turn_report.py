from __future__ import annotations

from tri.toolsandbox_single_turn_report import build_report


def _row(mode: str, transition: str, cluster: str, error: bool = False) -> dict:
    unauthorized = error and mode == "preserve" and transition == "flip"
    premature = error and mode == "reevaluate" and transition == "flip"
    return {
        "model": "test-model",
        "controller": "full_history",
        "scenario_id": f"{mode}-{transition}-{cluster}-{error}",
        "reference_mode": mode,
        "transition": transition,
        "cluster_id": cluster,
        "errors": [],
        "binding_observed": True,
        "initial_binding_correct": True,
        "tri_opportunity": True,
        "final_state_success": not error,
        "wrong_entity_write": error,
        "unauthorized_rebinding": unauthorized,
        "premature_lock": premature,
    }


def test_report_uses_opportunity_denominator_and_directional_errors() -> None:
    rows = [
        _row("preserve", "flip", "a", error=True),
        _row("preserve", "flip", "b", error=False),
        _row("reevaluate", "flip", "a", error=True),
        _row("reevaluate", "flip", "b", error=False),
    ]
    report = build_report(rows)
    assert report["inventory"]["duplicate_model_controller_task_keys"] == 0
    cells = {
        (row["reference_mode"], row["transition"]): row for row in report["cells"]
    }
    assert cells[("preserve", "flip")]["unauthorized_rebindings"] == 1
    assert cells[("preserve", "flip")]["premature_locks"] == 0
    assert cells[("reevaluate", "flip")]["unauthorized_rebindings"] == 0
    assert cells[("reevaluate", "flip")]["premature_locks"] == 1
    assert cells[("preserve", "flip")]["conditional_mechanism_error_rate"] == 0.5
