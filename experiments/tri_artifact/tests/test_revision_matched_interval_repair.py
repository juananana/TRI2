from __future__ import annotations

from tri.revision_matched_interval_repair import corrected_changed_pair_difference


def test_changed_pair_bootstrap_retains_repeated_cluster_draws() -> None:
    rows = []
    for pair_index, visible_correct in enumerate((False, True)):
        for mode, gold in (("preserve", "A"), ("reevaluate", "B")):
            rows.append(
                {
                    "model": "synthetic",
                    "task": {
                        "pair_id": f"pair-{pair_index}",
                        "reference_mode_gold": mode,
                        "actionable_core": True,
                        "pre_refresh_target": "A",
                        "post_refresh_target": "B",
                        "correct_target": gold,
                    },
                    "outcomes": {
                        "history_only": "wrong",
                        "decision_visible": gold if visible_correct else "wrong",
                    },
                }
            )

    result = corrected_changed_pair_difference(rows, seed=7, samples=1000)
    assert result["difference"] == 0.5
    assert result["ci95_cluster"] == [0.0, 1.0]
