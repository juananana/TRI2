import unittest

from tri.v3_alternative_baselines import (
    late_compiler_result,
    pre_refresh_untyped_plan_result,
    reminder_result,
)


class FakeClient:
    def __init__(self, response):
        self.response = response

    def chat(self, messages, temperature=0.0):
        return self.response


class SequenceClient:
    def __init__(self, responses):
        self.responses = iter(responses)

    def chat(self, messages, temperature=0.0):
        return next(self.responses)


def source(binding="anchored"):
    task = {
        "instruction": "choose before refresh" if binding == "anchored" else "refresh then choose",
        "binding": binding,
        "correct_target": "ID-A" if binding == "anchored" else "ID-B",
        "post_refresh_target": "ID-B",
        "initial_state": [
            {"id": "ID-A", "status": "open", "actionable": True},
            {"id": "ID-B", "status": "open", "actionable": True},
        ],
        "refreshed_state": [
            {"id": "ID-A", "status": "open", "actionable": True},
            {"id": "ID-B", "status": "open", "actionable": True},
        ],
        "action_schema": {"preconditions": {"status": "open", "actionable": True}},
    }
    return {
        "task": task,
        "result": {"compiled_ledger": {"selected_entity_id": "ID-A", "selector": "highest"}},
    }


class AlternativeBaselineTests(unittest.TestCase):
    def test_reminder_actor_uses_returned_target(self):
        result = reminder_result(FakeClient('{"target_id":"ID-A"}'), source(), 0.0)
        self.assertTrue(result["success"])

    def test_late_compiler_preserve_uses_generic_bound_id(self):
        result = late_compiler_result(
            FakeClient('{"reference_mode":"preserve","dynamic_target_id":null}'), source(), 0.0
        )
        self.assertEqual(result["predicted_target"], "ID-A")

    def test_late_compiler_reevaluate_uses_dynamic_target(self):
        result = late_compiler_result(
            FakeClient('{"reference_mode":"reevaluate","dynamic_target_id":"ID-B"}'),
            source("dynamic"),
            0.0,
        )
        self.assertTrue(result["success"])

    def test_pre_refresh_untyped_plan_uses_two_stage_outputs(self):
        client = SequenceClient([
            '{"plan":"After refresh, act on ID-A if it remains open."}',
            '{"action":"process","target_id":"ID-A"}',
        ])
        result = pre_refresh_untyped_plan_result(client, source(), 0.0)
        self.assertTrue(result["success"])
        self.assertEqual(result["compiled_plan"], "After refresh, act on ID-A if it remains open.")

    def test_pre_refresh_untyped_plan_rejects_structured_fields(self):
        result = pre_refresh_untyped_plan_result(
            FakeClient('{"plan":"act on ID-A","reference_mode":"preserve"}'), source(), 0.0
        )
        self.assertFalse(result["success"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
