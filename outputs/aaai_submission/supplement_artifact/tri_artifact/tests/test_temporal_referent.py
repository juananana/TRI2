from __future__ import annotations

import unittest

from tri.run_models import normalize_target, parse_json
from tri.lifecycle_ablation import predict as lifecycle_predict
from tri.lifecycle_tasks import task_rows as lifecycle_task_rows
from tri.tasks import task_rows
from tri.tool_env import ToolEnvironment


class TemporalReferentTests(unittest.TestCase):
    def test_task_grid_is_balanced(self) -> None:
        rows = task_rows()
        self.assertEqual(len(rows), 10 * 5 * 2 * 3)
        ids = {r["id"] for r in rows}
        self.assertEqual(len(ids), len(rows))

    def test_flip_conditions_have_different_pre_and_post_targets(self) -> None:
        for row in task_rows():
            if row["update"] == "flip":
                self.assertNotEqual(row["pre_refresh_target"], row["post_refresh_target"])

    def test_anchored_and_dynamic_oracles_differ_only_on_flip(self) -> None:
        rows = task_rows()
        by_key = {(r["domain"], r["paraphrase"], r["binding"], r["update"]): r for r in rows}
        for r in rows:
            other_binding = "dynamic" if r["binding"] == "anchored" else "anchored"
            other = by_key[(r["domain"], r["paraphrase"], other_binding, r["update"])]
            if r["update"] == "flip":
                self.assertNotEqual(r["correct_target"], other["correct_target"])
            elif r["update"] == "stable":
                self.assertEqual(r["correct_target"], other["correct_target"])
            else:
                self.assertNotEqual(r["correct_target"], other["correct_target"])

    def test_removed_anchored_requires_invalid(self) -> None:
        for row in task_rows():
            if row["binding"] == "anchored" and row["update"] == "removed":
                self.assertEqual(row["correct_target"], "INVALID_BOUND_ENTITY")
                self.assertFalse(row["bound_entity_present_after_refresh"])

    def test_parser_helpers(self) -> None:
        self.assertEqual(parse_json('```json\n{"target_id":"INC-104"}\n```')["target_id"], "INC-104")
        self.assertEqual(parse_json('{"tool":"process"}\n{"target_id":"INC-104"}')["tool"], "process")
        self.assertEqual(normalize_target("Please use INC-104."), "INC-104")

    def test_tool_environment_refresh_and_process(self) -> None:
        task = next(
            row for row in task_rows()
            if row["domain"] == "incident" and row["paraphrase"] == "p0"
            and row["binding"] == "anchored" and row["update"] == "flip"
        )
        env = ToolEnvironment(task)
        self.assertEqual(env.observe()["entities"], task["initial_state"])
        self.assertEqual(env.refresh()["entities"], task["refreshed_state"])
        self.assertTrue(env.process(task["post_refresh_target"])["ok"])
        self.assertEqual(env.trace[-1]["arguments"]["target_id"], task["post_refresh_target"])

    def test_lifecycle_task_grid_and_oracles(self) -> None:
        rows = lifecycle_task_rows()
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({r["id"] for r in rows}), 30)
        by_key = {(r["domain"], r["paraphrase"], r["binding"]): r for r in rows}
        for row in rows:
            other_binding = "dynamic" if row["binding"] == "anchored" else "anchored"
            other = by_key[(row["domain"], row["paraphrase"], other_binding)]
            self.assertNotEqual(row["correct_target"], other["correct_target"])
            if row["lifecycle_scenario"] == "action_invalid" and row["binding"] == "anchored":
                self.assertEqual(row["correct_target"], "INVALID_BOUND_ENTITY")
                self.assertFalse(row["bound_entity_actionable_after_refresh"])
            if row["lifecycle_scenario"] in {"rename_and_flip", "name_collision"} and row["binding"] == "anchored":
                self.assertEqual(row["correct_target"], row["pre_refresh_target"])

    def test_lifecycle_full_ledger_ablation_is_oracle(self) -> None:
        for row in lifecycle_task_rows():
            self.assertEqual(lifecycle_predict(row, "full_lifecycle_ledger"), row["correct_target"])


if __name__ == "__main__":
    unittest.main()
