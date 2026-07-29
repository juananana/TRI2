from __future__ import annotations

from scripts.build_submission_critical_paper_assets import MODEL_ORDER, build_main, build_supplement


def _metric(numerator: int, denominator: int) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": numerator / denominator,
        "ci95_state_cluster": [0.1, 0.8],
    }


def reports() -> tuple[dict, dict]:
    convention_models = []
    matched_models = []
    for index, model in enumerate(MODEL_ORDER):
        convention_models.append(
            {
                "model": model,
                "metrics": {
                    "plain_history": {"changed_pairacc": _metric(10 + index, 40)},
                    "convention_told": {"changed_pairacc": _metric(20 + index, 40)},
                },
                "paired_differences": [
                    {
                        "metric": "changed_pairacc",
                        "difference_right_minus_left": 0.25,
                        "ci95_state_cluster": [0.1, 0.4],
                    }
                ],
                "failures": {"incomplete_tasks": 0},
            }
        )
        matched_models.append(
            {
                "model": model,
                "metrics": {
                    "history_only": {"changed_pairacc": {"numerator": 5, "denominator": 32}},
                    "decision_visible": {"changed_pairacc": {"numerator": 15, "denominator": 32}},
                },
                "decision_visible_minus_history": {
                    "changed_pairacc": {"difference": 0.3125, "ci95_cluster": [0.1, 0.5]}
                },
                "failures": {"incomplete_tasks": 0},
            }
        )
    return {"models": convention_models}, {"models": matched_models}


def test_generated_fragments_keep_the_two_denominators_separate():
    convention, matched = reports()
    main = build_main(convention, matched)
    supplement = build_supplement(convention, matched)
    assert "40 changed pairs" in main
    assert "32 actionable changed" in main
    assert "separate frozen inventories" in main
    assert "inventories are not pooled" in main
    assert "changed-winner PairAcc" in main
    assert "fig_submission_critical_pairacc_effects.pdf" in main
    assert "Convention-told natural-history control" in supplement
    assert "Four-model full-diagnostic matched-call audit" in supplement
