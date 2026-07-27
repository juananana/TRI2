from __future__ import annotations

import unittest

from tri.model_authored_linguistic_stress import (
    build_author_payload,
    build_semantic_specs,
    build_tasks,
    cluster_bootstrap_difference,
    judge_accepts,
    parse_author_output,
    parse_judge_output,
    prediction_rows_from_run,
    run_rule,
)
import json
import tempfile
from pathlib import Path


class ModelAuthoredLinguisticStressTest(unittest.TestCase):
    def test_semantic_specs_are_changed_surviving_opposite_gold_pairs(self) -> None:
        specs = build_semantic_specs()
        self.assertEqual(len(specs), 24)
        self.assertEqual(len({row["domain"] for row in specs}), 24)
        self.assertEqual(set(build_author_payload(specs[0])), {
            "workflow_domain", "entity_type", "selector_meaning", "requested_action",
            "state_update_meaning", "linguistic_style", "preserve_event_order",
            "reevaluate_event_order",
        })

    def test_author_parse_and_task_build_keep_failed_generation_in_itt(self) -> None:
        specs = build_semantic_specs()
        parsed = parse_author_output(
            '{"preserve_instruction":"Choose the highest item now. After the workspace updates, act on the item you chose.",'
            '"reevaluate_instruction":"After the workspace updates, choose the highest item and act on that item."}'
        )
        author_rows = [
            {"spec": spec, "spec_index": index, "parsed": parsed if index != 3 else None}
            for index, spec in enumerate(specs, 1)
        ]
        tasks = build_tasks(specs, author_rows)
        self.assertEqual(len(tasks), 48)
        self.assertEqual(sum(row["generation_valid"] for row in tasks), 46)
        self.assertEqual(sum(row["reference_mode_gold"] == "preserve" for row in tasks), 24)

    def test_judge_schema_and_acceptance(self) -> None:
        task = {"reference_mode_gold": "preserve"}
        parsed = parse_judge_output(
            '{"classified_mode":"preserve","selector_preserved":true,'
            '"action_preserved":true,"unambiguous":true,"notes":"faithful"}'
        )
        self.assertTrue(judge_accepts(task, {"status": "ok", "parsed": parsed}))
        self.assertFalse(judge_accepts(task, {"status": "api_error", "parsed": parsed}))

    def test_frozen_rule_runs_without_gold_fields(self) -> None:
        specs = build_semantic_specs()
        parsed = {
            "preserve_instruction": "Choose the highest item, refresh the workspace, and act on the item chosen earlier.",
            "reevaluate_instruction": "Refresh the workspace, choose the highest item, and act on that item.",
        }
        tasks = build_tasks(specs, [
            {"spec": spec, "spec_index": index, "parsed": parsed}
            for index, spec in enumerate(specs, 1)
        ])
        predictions = run_rule(tasks)
        self.assertEqual(len(predictions), 48)

    def test_cluster_bootstrap_difference(self) -> None:
        result = cluster_bootstrap_difference({"a": (False, True), "b": (True, True)}, samples=1000, seed=3)
        self.assertEqual(result["difference"], 0.5)
        self.assertEqual(result["n_pairs"], 2)

    def test_exact_transport_repair_recovers_two_hyphen_id(self) -> None:
        task = {
            "id": "t1",
            "initial_state": [{"id": "MAS-01-A"}],
            "refreshed_state": [{"id": "MAS-01-A"}, {"id": "MAS-01-B"}],
        }
        row = {
            "task": task,
            "status": "ok",
            "result": {
                "predicted_target": "MAS-01",
                "compiled_ledger": {"selected_entity_id": "MAS-01-A"},
                "raw_outputs": ["{}", '{"target_id":"MAS-01-B"}'],
                "errors": [],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.jsonl"
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            repaired = prediction_rows_from_run(path, "generic", transport_repair=True)["t1"]
        self.assertEqual(repaired["predicted_target"], "MAS-01-B")
        self.assertEqual(repaired["initial_binding"], "MAS-01-A")


if __name__ == "__main__":
    unittest.main()
