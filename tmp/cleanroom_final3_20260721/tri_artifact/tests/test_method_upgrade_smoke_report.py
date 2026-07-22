from __future__ import annotations

from scripts.analyze_method_upgrade_smoke import decision, summarize


def test_complete_two_model_m2_smoke_passes_gate() -> None:
    rows = []
    for model in ("Qwen", "GLM"):
        for index in range(20):
            rows.append({
                "model": model, "method": "event_graph_selector", "task_id": str(index),
                "schema_valid": True, "mode_correct": True, "bound_id_correct": True,
                "selector_initial_correct": True, "selector_final_correct": True,
                "authorized_target_correct": True, "errors": [], "request_attempts": 1,
                "usage": [{"prompt_tokens": 10, "completion_tokens": 5}],
                "dataset_sha256": "frozen",
            })
    report = summarize(rows)
    result = decision(report)
    assert result["go_to_v7"]
    assert all(result["gates"].values())


def test_incomplete_preflight_cannot_unlock_v7() -> None:
    rows = [{
        "model": "Qwen", "method": "event_graph_selector", "task_id": "1",
        "schema_valid": True, "mode_correct": True, "bound_id_correct": True,
        "selector_initial_correct": True, "selector_final_correct": True,
        "authorized_target_correct": True, "errors": [], "request_attempts": 1, "usage": [],
    }]
    assert not decision(summarize(rows))["go_to_v7"]


def test_two_model_three_method_preflight_closes_loop_without_unlocking_v7() -> None:
    rows = []
    for model in ("Qwen", "GLM"):
        for method in ("exact_cta", "event_graph", "event_graph_selector"):
            rows.append({
                "model": model, "method": method, "task_id": "1",
                "schema_valid": True, "mode_correct": True, "bound_id_correct": True,
                "selector_initial_correct": True if method == "event_graph_selector" else None,
                "selector_final_correct": True if method == "event_graph_selector" else None,
                "authorized_target_correct": True if method == "event_graph_selector" else None,
                "errors": [], "request_attempts": 1, "usage": [],
            })
    result = decision(summarize(rows))
    assert result["preflight_closed_loop"]
    assert not result["go_to_v7"]
