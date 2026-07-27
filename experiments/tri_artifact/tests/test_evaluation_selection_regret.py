from __future__ import annotations

from tri.evaluation_selection_regret import build_report, validate


def by_key(report: dict) -> dict[tuple[str, str, str], dict]:
    return {
        (row["dataset"], row["model_family"], row["proxy_regime"]): row
        for row in report["rows"]
    }


def test_selection_regret_report_is_complete_and_valid() -> None:
    report = build_report()
    validate(report)
    assert report["summary"]["candidate_sets"] == 5
    assert report["summary"]["proxy_evaluations"] == 20
    assert report["summary"]["one_sided_or_stable_evaluations"] == 15
    assert report["summary"]["one_sided_or_stable_zero_pairacc_rows"] == 15
    assert report["summary"]["aggregate_suboptimal_rows"] == 0
    assert report["summary"]["aggregate_pairacc_optimal_rows"] == 5


def test_preserve_only_selects_always_lock_with_large_regret() -> None:
    rows = by_key(build_report())
    qwen = rows[("v3", "Qwen", "preserve_only")]
    assert qwen["proxy_maximizers"] == [
        "Always-Lock+validity",
        "Qwen-Lifecycle-Gated",
    ]
    assert qwen["zero_pairacc_maximizer_exists"] is True
    assert qwen["best_pairacc_in_candidate_set"] == 1.0
    assert qwen["worst_case_selection_regret"] == 1.0


def test_reevaluate_only_can_leave_good_and_bad_policies_tied() -> None:
    rows = by_key(build_report())
    glm = rows[("v3", "GLM", "reevaluate_only")]
    assert glm["proxy_maximizers"] == [
        "Always-Reevaluate",
        "GLM-CTA",
        "GLM-Lifecycle-Gated",
        "GLM-Lifecycle-free",
    ]
    assert glm["pairacc_among_maximizers"] == {"minimum": 0.0, "maximum": 1.0}
    assert glm["worst_case_selection_regret"] == 1.0
    assert glm["optimistic_selection_regret"] == 0.0


def test_aggregate_selects_pairacc_optimal_gated_configuration() -> None:
    rows = by_key(build_report())
    glm = rows[("v3", "GLM", "aggregate_e2e")]
    assert glm["proxy_maximizers"] == ["GLM-Lifecycle-Gated"]
    assert glm["best_pairacc_in_candidate_set"] == 1.0
    assert glm["worst_case_selection_regret"] == 0.0
