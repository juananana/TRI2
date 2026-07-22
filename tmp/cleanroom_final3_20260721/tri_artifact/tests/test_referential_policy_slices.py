from __future__ import annotations

import unittest

from scripts.analyze_referential_policy_slices import (
    RUNS,
    DEFAULT_RUNS,
    load,
    paired_cluster_difference,
    summarize,
)


class ReferentialPolicySliceTest(unittest.TestCase):
    def test_frozen_inventory_partitions_without_loss(self) -> None:
        for filename in DEFAULT_RUNS.values():
            summary = summarize(load(RUNS / filename))
            core = summary["actionable_referential_core"]
            reject = summary["author_specified_reject_policy"]
            self.assertEqual(core["n"], 128)
            self.assertEqual(reject["n"], 32)
            self.assertEqual(core["n"] + reject["n"], 160)

    def test_reported_gated_counts(self) -> None:
        qwen = summarize(load(RUNS / DEFAULT_RUNS["Qwen Lifecycle-Gated"]))
        glm = summarize(load(RUNS / DEFAULT_RUNS["GLM Lifecycle-Gated"]))
        self.assertEqual(qwen["actionable_referential_core"]["correct"], 125)
        self.assertEqual(glm["actionable_referential_core"]["correct"], 128)
        self.assertEqual(qwen["author_specified_reject_policy"]["correct"], 32)
        self.assertEqual(glm["author_specified_reject_policy"]["correct"], 32)

    def test_paired_cluster_difference(self) -> None:
        baseline = load(RUNS / DEFAULT_RUNS["Qwen Generic"])
        gated = load(RUNS / DEFAULT_RUNS["Qwen Lifecycle-Gated"])
        result = paired_cluster_difference(baseline, gated, False, samples=1000, seed=9)
        self.assertEqual(result["n"], 128)
        self.assertEqual(result["n_clusters"], 20)
        self.assertGreater(result["difference"], 0)


if __name__ == "__main__":
    unittest.main()
