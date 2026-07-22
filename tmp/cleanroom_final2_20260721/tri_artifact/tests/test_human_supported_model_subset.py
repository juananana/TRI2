from __future__ import annotations

import unittest

from scripts.analyze_human_supported_model_subset import paired_cluster_bootstrap


class HumanSupportedModelSubsetTest(unittest.TestCase):
    def test_cluster_bootstrap_reports_clustered_effect(self) -> None:
        generic = [False, False, True, True]
        treatment = [True, True, True, True]
        clusters = ["a", "a", "b", "b"]
        result = paired_cluster_bootstrap(generic, treatment, clusters, samples=1000, seed=7)
        self.assertEqual(result["difference"], 0.5)
        self.assertEqual(result["n_clusters"], 2)
        self.assertEqual(result["cluster_95_interval"], [0.0, 1.0])


if __name__ == "__main__":
    unittest.main()
