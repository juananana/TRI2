from __future__ import annotations

import unittest
from pathlib import Path

from tri.policy_extreme_controls import analyze, load_jsonl


ROOT = Path(__file__).resolve().parents[1]


class PolicyExtremeControlsTest(unittest.TestCase):
    def test_frozen_v3_results(self) -> None:
        rows = load_jsonl(ROOT / "data" / "temporal_referent_v3_language_clusters.jsonl")
        report = analyze(rows)

        self.assertEqual(report["overall"]["n"], 160)
        self.assertEqual(
            report["overall"]["methods"]["always_lock_with_validity"]["correct"], 96
        )
        self.assertEqual(
            report["overall"]["methods"]["always_reevaluate"]["correct"], 96
        )
        self.assertEqual(
            report["by_binding"]["anchored"]["methods"]["always_lock_with_validity"]["correct"],
            80,
        )
        self.assertEqual(
            report["by_binding"]["anchored"]["methods"]["always_reevaluate"]["correct"],
            16,
        )
        self.assertEqual(
            report["by_binding"]["dynamic"]["methods"]["always_lock_with_validity"]["correct"],
            16,
        )
        self.assertEqual(
            report["by_binding"]["dynamic"]["methods"]["always_reevaluate"]["correct"],
            80,
        )


if __name__ == "__main__":
    unittest.main()
