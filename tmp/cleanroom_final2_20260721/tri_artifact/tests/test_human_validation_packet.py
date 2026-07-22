from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.make_human_validation_packet import write_packets


class HumanValidationPacketTest(unittest.TestCase):
    def task(self, index: int) -> dict:
        return {
            "id": f"tri-secret-explicit_anchor-{index}",
            "style": "explicit_anchor",
            "binding": "anchored",
            "update": "flip",
            "domain": "mail",
            "instruction": f"Original instruction {index}",
            "initial_state": [{"id": f"A-{index}"}, {"id": f"B-{index}"}],
            "refreshed_state": [{"id": f"A-{index}"}, {"id": f"B-{index}"}],
            "action_schema": {"preconditions": {}},
            "pre_refresh_target": f"A-{index}",
            "post_refresh_target": f"B-{index}",
            "correct_target": f"A-{index}",
        }

    def test_participant_forms_hide_condition_and_variant_metadata(self) -> None:
        sources = [self.task(index) for index in range(2)]
        rewrites = {row["id"]: f"Natural rewrite {index}" for index, row in enumerate(sources)}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_packets(output, sources, rewrites)
            with (output / "annotator_1.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 4)
            self.assertEqual(
                set(rows[0]),
                {
                    "item_id", "instruction", "initial_state_json", "refreshed_state_json",
                    "action_schema_json", "candidate_ids", "response", "confidence_1_to_5",
                    "comment",
                },
            )
            self.assertTrue(all(row["item_id"].startswith("HV-") for row in rows))
            serialized = json.dumps(rows)
            self.assertNotIn("explicit_anchor", serialized)
            self.assertNotIn("tri-secret", serialized)
            self.assertNotIn("human_rewrite", serialized)

            with (output / "annotation_key_private.csv").open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                key_rows = list(csv.DictReader(handle))
            self.assertEqual({row["variant"] for row in key_rows}, {"original", "human_rewrite"})
            self.assertTrue(all(row["source_task_id"].startswith("tri-secret") for row in key_rows))

if __name__ == "__main__":
    unittest.main()
