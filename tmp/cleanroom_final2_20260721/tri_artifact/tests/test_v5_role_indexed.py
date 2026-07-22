from __future__ import annotations

import json
import unittest

from tri.run_v5_stress import action_reference, run_role_indexed
from tri.v3_sqlite_trajectory_eval import trajectory_rows
from tri.v5_stress_eval import stress_rows


class SequenceClient:
    def __init__(self, responses: list[dict]) -> None:
        self.responses = iter(json.dumps(response) for response in responses)

    def chat(self, messages, temperature=0.0):
        return next(self.responses)


class RoleIndexedStressTest(unittest.TestCase):
    def test_requires_exactly_one_action_target(self) -> None:
        with self.assertRaises(ValueError):
            action_reference({"references": []})
        with self.assertRaises(ValueError):
            action_reference({"references": [
                {"role": "action_target", "reference_mode": "preserve", "invalidity_policy": "reject"},
                {"role": "action_target", "reference_mode": "reevaluate", "invalidity_policy": "reject"},
            ]})

    def test_dynamic_monitor_does_not_replace_action_target(self) -> None:
        task = next(row for row in stress_rows(trajectory_rows()) if row["binding"] == "dynamic")
        client = SequenceClient([
            {"references": [
                {
                    "role": "action_target",
                    "reference_mode": "reevaluate",
                    "selector": task["selector"],
                    "bound_target_id": None,
                    "invalidity_policy": "reject",
                },
                {
                    "role": "monitoring_reference",
                    "reference_mode": "reevaluate",
                    "selector": task["selector"],
                    "bound_target_id": None,
                    "invalidity_policy": "reject",
                },
            ]},
            {"action": "process", "target_id": task["correct_target"]},
        ])
        result = run_role_indexed(client, task, 0.0)
        self.assertTrue(result["final_state_success"])
        self.assertEqual(result["acted_ids"], [task["correct_target"]])

    def test_preserved_action_target_is_gated_without_actor_call(self) -> None:
        task = next(
            row for row in stress_rows(trajectory_rows())
            if row["binding"] == "anchored" and row["update"] == "flip"
        )
        client = SequenceClient([{"references": [{
            "role": "action_target",
            "reference_mode": "preserve",
            "selector": task["selector"],
            "bound_target_id": task["pre_refresh_target"],
            "invalidity_policy": "reject",
        }]}])
        result = run_role_indexed(client, task, 0.0)
        self.assertTrue(result["final_state_success"])
        self.assertEqual(result["acted_ids"], [task["pre_refresh_target"]])
        self.assertEqual(len(result["raw_outputs"]), 1)


if __name__ == "__main__":
    unittest.main()
