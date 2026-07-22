from __future__ import annotations

import unittest

from scripts.analyze_human_rewrite_model_results import action_valid, cluster_bootstrap, exact_mcnemar


class HumanRewriteModelResultsTest(unittest.TestCase):
    def test_exact_mcnemar(self) -> None:
        result = exact_mcnemar([False, False, True], [True, False, True])
        self.assertEqual(result["baseline_only"], 0)
        self.assertEqual(result["treatment_only"], 1)
        self.assertEqual(result["exact_mcnemar_p"], 1.0)

    def test_cluster_bootstrap(self) -> None:
        result = cluster_bootstrap(
            [False, False, True, True],
            [True, True, True, True],
            ["a", "a", "b", "b"],
            samples=1000,
            seed=3,
        )
        self.assertEqual(result["difference"], 0.5)
        self.assertEqual(result["cluster_95_interval"], [0.0, 1.0])

    def test_action_validity_uses_refreshed_schema(self) -> None:
        task = {
            "refreshed_state": [{"id": "A", "status": "open"}],
            "action_schema": {"preconditions": {"status": "open"}},
        }
        self.assertTrue(action_valid("A", task))
        self.assertFalse(action_valid("B", task))
        self.assertFalse(action_valid("REJECT", task))


if __name__ == "__main__":
    unittest.main()
