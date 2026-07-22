from pathlib import Path

from tri.public_coverage_funnel import build_report


ROOT = Path(__file__).resolve().parents[1]


def test_public_coverage_funnel_matches_pinned_audits() -> None:
    report = build_report(ROOT)
    suites = {suite["benchmark"]: suite for suite in report["suites"]}
    toolsandbox = suites["ToolSandbox"]["funnel"]
    assert [row["count"] for row in toolsandbox] == [129, 43, 26, 18, 1, 0]
    appworld = suites["AppWorld"]["funnel"]
    assert [row["count"] for row in appworld] == [244, 1, 0, 42, 16, 0]
    tau3 = suites["tau3-bench"]["funnel"]
    assert [row["count"] for row in tau3] == [2449, 2250, 0, 0, 0]
    assert "not an independent recall audit" in report["status"]
