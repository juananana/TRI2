from pathlib import Path

from tri.v7_shared_eligible_pairacc import build_report, shared_eligible


ROOT = Path(__file__).resolve().parents[1]


def _row(task_id: str, initial: str, predicted: str, *, status: str = "ok") -> dict:
    task = {
        "id": task_id,
        "binding": "anchored",
        "update": "flip",
        "pre_refresh_target": "A",
        "post_refresh_target": "B",
        "bound_entity_present_after_refresh": True,
        "bound_entity_actionable_after_refresh": True,
    }
    return {
        "status": status,
        "task": task,
        "result": {
            "predicted_target": predicted,
            "compiled_ledger": {"selected_entity_id": initial},
            "errors": [],
        },
    }


def test_shared_eligible_requires_both_correct_initial_bindings() -> None:
    generic = [_row("kept", "A", "B"), _row("cta-missed", "A", "B")]
    cta = [_row("kept", "A", "A"), _row("cta-missed", "B", "A")]
    result = shared_eligible(generic, cta)
    assert result["eligible"] == 1
    assert result["generic_substitutions"] == 1
    assert result["cta_substitutions"] == 0
    assert result["task_ids"] == ["kept"]


def test_frozen_v7_audit_reproduces_pairacc_counts() -> None:
    report = build_report(ROOT / "runs", samples=100, seed=7)
    by_model = {row["model"]: row for row in report["models"]}
    assert by_model["Qwen3.5"]["generic_pairacc"]["both_correct"] == 7
    assert by_model["Qwen3.5"]["cta_pairacc"]["both_correct"] == 31
    assert by_model["GLM-5.1"]["generic_pairacc"]["both_correct"] == 15
    assert by_model["GLM-5.1"]["cta_pairacc"]["both_correct"] == 66
    assert by_model["DeepSeek"]["generic_pairacc"]["both_correct"] == 17
    assert by_model["DeepSeek"]["cta_pairacc"]["both_correct"] == 64
