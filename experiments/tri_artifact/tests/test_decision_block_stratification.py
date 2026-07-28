from __future__ import annotations

import json
from pathlib import Path

from tri.decision_block_stratification import (
    authored_stratification,
    interface_redundancy,
    v7_boundary,
    validate_complete_matched_rows,
)
from scripts.analyze_decision_block_stratification import MATCHED_INPUTS


ROOT = Path(__file__).resolve().parents[1]


def _component(payload: dict, parsed: dict) -> dict:
    return {
        "parsed": parsed,
        "attempts": [{"request": {"messages": [{"content": "system"}, {"content": json.dumps(payload)}]}}],
    }


def _matched_row(mode: str, compiler_mode: str, history: str, visible: str, bound: str = "A") -> dict:
    task = {
        "id": f"{mode}-{history}-{visible}",
        "reference_mode_gold": mode,
        "initial_selected_id": "A",
        "pre_refresh_target": "A",
        "post_refresh_target": "B",
        "correct_target": "A" if mode == "preserve" else "B",
        "selector": "highest priority",
        "action": "archive",
    }
    decision = {"reference_mode": compiler_mode, "bound_target_id": bound, "selector": task["selector"]}
    base = {"initial_selected_id": "A", "selector": task["selector"]}
    return {
        "complete": True,
        "logical_calls_completed": 3,
        "task": task,
        "compiler": _component(base, decision),
        "actors": {
            "history_only": _component(base, {"action": "archive", "target_id": history}),
            "decision_visible": _component({**base, "compiler_decision": decision}, {"action": "archive", "target_id": visible}),
        },
        "outcomes": {"history_only": history, "decision_visible": visible},
    }


def test_authored_strata_and_discordances() -> None:
    rows = [
        _matched_row("preserve", "preserve", "B", "A"),
        _matched_row("preserve", "reevaluate", "A", "B", bound="B"),
        _matched_row("reevaluate", "reevaluate", "B", "B", bound=None),
    ]
    result = authored_stratification(rows)
    correct = result["by_compiler_mode_correctness"]["correct"]
    wrong = result["by_compiler_mode_correctness"]["wrong"]
    assert correct["rows"] == 2
    assert correct["exact_target"]["paired_discordance"]["visible_repairs"] == 1
    assert wrong["rows"] == 1
    assert wrong["exact_target"]["paired_discordance"]["visible_harms"] == 1
    assert result["preserve_by_compiler_bound_id_correctness"]["wrong"]["rows"] == 1


def test_interface_redundancy_is_exact() -> None:
    rows = [_matched_row("preserve", "preserve", "A", "A")]
    checks = interface_redundancy(rows)
    assert all(metric["numerator"] == 1 for metric in checks.values())
    rows[0]["compiler"]["parsed"]["selector"] = "Highest priority"
    checks = interface_redundancy(rows)
    assert checks["compiler_selector_equals_base_selector"]["numerator"] == 0


def test_complete_validation_rejects_incomplete() -> None:
    row = _matched_row("preserve", "preserve", "A", "A")
    validate_complete_matched_rows([row], 1)
    row["complete"] = False
    try:
        validate_complete_matched_rows([row], 1)
    except ValueError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError("incomplete row was accepted")


def _v7_row(pair: str, binding: str, prediction: str, ledger: dict) -> dict:
    return {
        "task": {
            "id": f"{pair}-{binding}",
            "state_cluster_id": pair,
            "update": "flip",
            "binding": binding,
            "pre_refresh_target": "A",
            "post_refresh_target": "B",
            "correct_target": "A" if binding == "anchored" else "B",
        },
        "result": {"predicted_target": prediction, "compiled_ledger": ledger},
    }


def test_v7_boundary_uses_controller_specific_binding_field() -> None:
    rows = []
    for index in range(40):
        pair = f"p{index}"
        rows.append(_v7_row(pair, "anchored", "A", {"selected_entity_id": "A"}))
        rows.append(_v7_row(pair, "dynamic", "B", {"selected_entity_id": "A"}))
    result = v7_boundary(rows, "Generic")
    assert result["preserve_initial_binding"]["numerator"] == 40
    assert result["changed_pairacc"]["numerator"] == 40


def test_frozen_integration_counts() -> None:
    qwen = [json.loads(line) for line in (ROOT / "runs/revision_full_diagnostic_qwen_full_v1.jsonl").read_text().splitlines() if line]
    glm = [json.loads(line) for line in (ROOT / "runs/revision_full_diagnostic_glm_full_v1.jsonl").read_text().splitlines() if line]
    validate_complete_matched_rows(qwen, 160)
    validate_complete_matched_rows(glm, 160)
    qwen_result = authored_stratification(qwen)["by_compiler_mode_correctness"]
    glm_result = authored_stratification(glm)["by_compiler_mode_correctness"]
    assert qwen_result["correct"]["rows"] == 137
    assert qwen_result["wrong"]["rows"] == 23
    assert qwen_result["correct"]["exact_target"]["history_only"]["numerator"] == 105
    assert qwen_result["correct"]["exact_target"]["decision_visible"]["numerator"] == 119
    assert glm_result["correct"]["rows"] == 141
    assert glm_result["wrong"]["rows"] == 19
    assert glm_result["correct"]["exact_target"]["history_only"]["numerator"] == 110
    assert glm_result["correct"]["exact_target"]["decision_visible"]["numerator"] == 136


def test_frozen_interface_census_has_760_exact_repetitions() -> None:
    rows = []
    for relative, expected in MATCHED_INPUTS.values():
        source = ROOT / relative
        source_rows = [json.loads(line) for line in source.read_text().splitlines() if line]
        validate_complete_matched_rows(source_rows, expected)
        rows.extend(source_rows)
    assert len(rows) == 760
    checks = interface_redundancy(rows)
    assert all(metric["numerator"] == 760 for metric in checks.values())
