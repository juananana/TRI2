from __future__ import annotations

import unittest

from scripts.analyze_human_validation import agreement, majority, normalize_response


class HumanValidationAnalysisTest(unittest.TestCase):
    def test_three_way_tie_has_no_majority(self) -> None:
        self.assertIsNone(majority(["A", "B", "CLARIFY"]))

    def test_two_votes_define_majority(self) -> None:
        self.assertEqual(majority(["A", "B", "A"]), "A")

    def test_reject_normalization(self) -> None:
        self.assertEqual(normalize_response("INVALID_BOUND_ENTITY"), "REJECT")
        self.assertEqual(normalize_response(" reject "), "REJECT")

    def test_perfect_agreement(self) -> None:
        result = agreement({"i1": ["A", "A", "A"], "i2": ["B", "B", "B"]})
        self.assertEqual(result["semantic_pairwise_agreement"], 1.0)
        self.assertEqual(result["semantic_unanimous_rate"], 1.0)
        self.assertEqual(result["fleiss_kappa"], 1.0)
        self.assertEqual(result["krippendorff_alpha_nominal"], 1.0)


if __name__ == "__main__":
    unittest.main()
