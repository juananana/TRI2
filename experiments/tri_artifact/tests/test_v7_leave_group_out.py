from pathlib import Path

from tri.v7_leave_group_out import build_report


ROOT = Path(__file__).resolve().parents[1]


def test_leave_group_out_is_matched_and_positive() -> None:
    report = build_report(ROOT / "runs")
    assert [row["model"] for row in report["models"]] == ["Qwen3.5", "GLM-5.1", "DeepSeek"]
    for row in report["models"]:
        assert row["n"] == 240
        assert len(row["leave_one_domain_out"]) == 10
        assert len(row["leave_one_template_out"]) >= 4
        assert row["domain_delta_range"][0] > 0
        assert row["template_delta_range"][0] > 0
