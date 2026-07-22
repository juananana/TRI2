from __future__ import annotations

import json

from tri.method_upgrade_smoke import compile_task, score_compilation
from tri.v7_core_replication import task_rows


def _task(binding: str) -> dict:
    return next(row for row in task_rows() if row["binding"] == binding and row["update"] == "flip")


def test_exact_cta_scoring() -> None:
    task = _task("anchored")
    result = score_compilation("exact_cta", task, {
        "reference_mode": "preserve",
        "selector": task["selector"],
        "bound_target_id": task["pre_refresh_target"],
        "invalidity_policy": "reject",
    })
    assert result["schema_valid"]
    assert result["mode_correct"]
    assert result["bound_id_correct"]


def test_event_graph_selector_scores_authorized_target() -> None:
    task = _task("dynamic")
    result = score_compilation("event_graph_selector", task, {
        "events": [
            {"id": "E1", "type": "REFRESH", "state": "final", "role": None, "referent": None, "target_id": None},
            {"id": "E2", "type": "SELECT", "state": "final", "role": "action_target", "referent": None, "target_id": None},
            {"id": "E3", "type": "ACT", "state": None, "role": "action", "referent": "E2", "target_id": None},
        ],
        "edges": [["E1", "E2"], ["E2", "E3"]],
        "selector_ast": {
            "filters": [
                {"field": key, "op": "eq", "value": value}
                for key, value in task["action_schema"]["preconditions"].items()
            ],
            "order_by": {"field": "due_minutes", "direction": "asc"},
            "limit": 1,
        },
    })
    assert result["schema_valid"]
    assert result["selector_initial_correct"]
    assert result["selector_final_correct"]
    assert result["authorized_target_correct"]


def test_compile_task_records_usage_and_errors() -> None:
    task = _task("anchored")

    class FakeClient:
        request_attempts = 0
        usage_records: list[dict] = []

        def chat(self, messages, temperature=0.0):
            self.request_attempts += 1
            self.usage_records.append({"prompt_tokens": 10, "completion_tokens": 5})
            return json.dumps({
                "reference_mode": "preserve", "selector": task["selector"],
                "bound_target_id": task["pre_refresh_target"], "invalidity_policy": "reject",
            })

    result = compile_task(FakeClient(), "exact_cta", task)
    assert result["schema_valid"]
    assert result["request_attempts"] == 1
    assert result["usage"] == [{"prompt_tokens": 10, "completion_tokens": 5}]


def test_m2_derives_anchored_id_from_selector_not_redundant_model_id() -> None:
    task = _task("anchored")

    class FakeClient:
        request_attempts = 0
        usage_records: list[dict] = []

        def chat(self, messages, temperature=0.0):
            self.request_attempts += 1
            self.usage_records.append({})
            return json.dumps({
                "events": [
                    {"id": "E1", "type": "SELECT", "state": "initial", "role": "action_target", "referent": None, "target_id": None},
                    {"id": "E2", "type": "REFRESH", "state": "final", "role": None, "referent": None, "target_id": None},
                    {"id": "E3", "type": "ACT", "state": None, "role": "action", "referent": "E1", "target_id": None},
                ],
                "edges": [["E1", "E2"], ["E2", "E3"]],
                "selector_ast": {
                    "filters": [
                        {"field": key, "op": "eq", "value": value}
                        for key, value in task["action_schema"]["preconditions"].items()
                    ],
                    "order_by": {"field": "due_minutes", "direction": "asc"},
                    "limit": 1,
                },
            })

    result = compile_task(FakeClient(), "event_graph_selector", task)
    assert result["predicted_target"] == task["pre_refresh_target"]
    assert result["success"]
    assert result["request_attempts"] == 1


def test_m1_dynamic_uses_actor_after_event_compilation() -> None:
    task = _task("dynamic")

    class FakeClient:
        def __init__(self) -> None:
            self.request_attempts = 0
            self.usage_records: list[dict] = []
            self.responses = iter([
                {
                    "events": [
                        {"id": "E1", "type": "REFRESH", "state": "final", "role": None, "referent": None, "target_id": None},
                        {"id": "E2", "type": "SELECT", "state": "final", "role": "action_target", "referent": None, "target_id": None},
                        {"id": "E3", "type": "ACT", "state": None, "role": "action", "referent": "E2", "target_id": None},
                    ],
                    "edges": [["E1", "E2"], ["E2", "E3"]],
                },
                {"target_id": task["post_refresh_target"]},
            ])

        def chat(self, messages, temperature=0.0):
            self.request_attempts += 1
            self.usage_records.append({})
            return json.dumps(next(self.responses))

    result = compile_task(FakeClient(), "event_graph", task)
    assert result["success"]
    assert result["actor_output"] == {"target_id": task["post_refresh_target"]}
    assert result["request_attempts"] == 2
