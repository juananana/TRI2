from __future__ import annotations

from scripts.analyze_method_upgrade_closed_loop import (
    collect,
    combined_upgrade,
    conclusions,
    summarize,
)


def test_closed_loop_matrix_and_decision_are_reproducible() -> None:
    rows = collect()
    assert len(rows) == 240
    summary = summarize(rows)
    combined = combined_upgrade(summary)
    result = conclusions(summary, combined)
    assert not result["promote_m2_to_main_method"]
    assert result["recommended_main_method"] == "Exact CTA"
    assert result["recommended_compositional_extension"] == "Role-Indexed Lifecycle"
    values = {(row["model"], row["method"]): (row["correct"], row["n"]) for row in combined}
    assert values[("Qwen", "M1 Event Graph")] == (9, 20)
    assert values[("Qwen", "M2 Executable Selector")] == (15, 20)
    assert values[("GLM", "M1 Event Graph")] == (20, 20)
    assert values[("GLM", "M2 Executable Selector")] == (18, 20)
