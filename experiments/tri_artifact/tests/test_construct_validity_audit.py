from __future__ import annotations

import numpy as np

from tri.construct_validity_audit import featurize, fit_logistic, overlap_counts, predict_probabilities


def test_order_features_distinguish_event_order() -> None:
    preserve = featurize("Select the earliest item. Refresh, then edit that exact item.", True)
    reevaluate = featurize("Refresh first. Then select the earliest item and edit it.", True)
    assert preserve[-2:] == [1.0, 0.0]
    assert reevaluate[-2:] == [0.0, 1.0]


def test_regularized_logistic_learns_separable_fixture() -> None:
    x = np.array([[0.0], [0.0], [1.0], [1.0]])
    y = np.array([0, 0, 1, 1])
    beta = fit_logistic(x, y)
    probabilities = predict_probabilities(beta, x)
    assert all(probabilities[:2] < 0.5)
    assert all(probabilities[2:] >= 0.5)


def test_overlap_partition() -> None:
    result = overlap_counts([True, True, False, False], [True, False, True, False])
    assert result["both_correct"] == 1
    assert result["rule_only"] == 1
    assert result["model_only"] == 1
    assert result["both_wrong"] == 1
    assert result["model_error_rule_solvable_rate"] == 0.5
