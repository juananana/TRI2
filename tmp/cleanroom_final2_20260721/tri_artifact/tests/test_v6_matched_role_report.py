from __future__ import annotations

import unittest
from pathlib import Path

from tri.v6_matched_role_report import load, paired_report


ROOT = Path(__file__).resolve().parents[1]


class V6MatchedRoleReportTest(unittest.TestCase):
    def test_qwen_matched_scalar_role_counts(self) -> None:
        report = paired_report(
            load(ROOT / "runs/v6_qwen_scalar_lifecycle_full.jsonl"),
            load(ROOT / "runs/v6_qwen_role_indexed_full.jsonl"),
            label="qwen",
        )
        scalar, role = report["controllers"]
        self.assertEqual((scalar["success"], scalar["n"]), (35, 40))
        self.assertEqual((role["success"], role["n"]), (39, 40))
        self.assertEqual(scalar["action_status"].get("wrong_entity_write"), 3)
        self.assertNotIn("wrong_entity_write", role["action_status"])
        self.assertEqual(report["paired"]["delta_percentage_points"], 10.0)
        self.assertEqual(report["paired"]["cluster_ci95"], [2.5, 20.0])

    def test_glm_transport_recovered_is_ceiling_tie(self) -> None:
        report = paired_report(
            load(ROOT / "runs/v6_glm_scalar_lifecycle_full.jsonl"),
            load(ROOT / "runs/v6_glm_role_indexed_transport_recovered.jsonl"),
            label="glm recovered",
        )
        scalar, role = report["controllers"]
        self.assertEqual((scalar["success"], scalar["n"]), (40, 40))
        self.assertEqual((role["success"], role["n"]), (40, 40))
        self.assertEqual(report["paired"]["delta_percentage_points"], 0.0)
        self.assertEqual(report["paired"]["cluster_ci95"], [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
