from __future__ import annotations

import copy
import unittest

from tri.deterministic_discourse_rule import infer_reference_mode, predict_task, resolve_selector
from tri.deterministic_discourse_rule_v2 import infer_reference_mode_v2, predict_task_v2


class DeterministicDiscourseRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = {
            "instruction": "Select the highest-priority unread email now. Refresh, then reply to it.",
            "initial_state": [
                {"id": "A", "priority": 9, "status": "unread", "actionable": True},
                {"id": "B", "priority": 7, "status": "unread", "actionable": True},
            ],
            "refreshed_state": [
                {"id": "A", "priority": 9, "status": "unread", "actionable": True},
                {"id": "B", "priority": 11, "status": "unread", "actionable": True},
            ],
            "action_schema": {"preconditions": {"status": "unread", "actionable": True}},
            "binding": "anchored",
            "correct_target": "A",
            "pre_refresh_target": "A",
            "post_refresh_target": "B",
            "new_leader": "B",
        }

    def test_event_order_modes(self) -> None:
        self.assertEqual(infer_reference_mode(self.task["instruction"])[0], "preserve")
        dynamic = "Refresh the mailbox, then choose the highest-priority unread email."
        self.assertEqual(infer_reference_mode(dynamic)[0], "reevaluate")

    def test_numeric_selector(self) -> None:
        target, error = resolve_selector(
            self.task["instruction"], self.task["initial_state"], self.task["action_schema"]
        )
        self.assertIsNone(error)
        self.assertEqual(target, "A")

    def test_forbidden_fields_cannot_change_prediction(self) -> None:
        expected = predict_task(self.task)
        changed = copy.deepcopy(self.task)
        for key in (
            "binding",
            "correct_target",
            "pre_refresh_target",
            "post_refresh_target",
            "new_leader",
        ):
            changed[key] = "POISONED"
        self.assertEqual(predict_task(changed), expected)

    def test_preserved_invalid_target_is_rejected(self) -> None:
        task = copy.deepcopy(self.task)
        task["refreshed_state"][0]["status"] = "read"
        self.assertEqual(predict_task(task)["predicted_target"], "INVALID_BOUND_ENTITY")

    def test_v2_expanded_event_vocabulary(self) -> None:
        anchored = "Record the identity of the highest-priority unread email before synchronization."
        dynamic = "Refresh the mailbox, then refind the highest-priority unread email."
        self.assertEqual(infer_reference_mode_v2(anchored)[0], "preserve")
        self.assertEqual(infer_reference_mode_v2(dynamic)[0], "reevaluate")

    def test_v2_forbidden_fields_cannot_change_prediction(self) -> None:
        expected = predict_task_v2(self.task)
        changed = copy.deepcopy(self.task)
        changed.update({"binding": "POISONED", "correct_target": "POISONED", "selector": "POISONED"})
        self.assertEqual(predict_task_v2(changed), expected)


if __name__ == "__main__":
    unittest.main()
