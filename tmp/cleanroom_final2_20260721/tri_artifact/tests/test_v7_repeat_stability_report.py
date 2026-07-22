from pathlib import Path

from tri.v7_repeat_stability_report import build_report


ROOT = Path(__file__).resolve().parents[1]


def test_repeat_report_has_three_complete_matched_runs() -> None:
    report = build_report(
        ROOT / "runs", ROOT / "data" / "temporal_referent_v7_repeat_stability_v1.jsonl"
    )
    assert report["expected_tasks"] == 40
    assert report["decision"] in {"stable", "mixed", "unstable"}
    for model in report["models"]:
        assert len(model["paired"]) == 3
        for controller in model["controllers"].values():
            assert len(controller["runs"]) == 3
            assert all(run["n"] == 40 for run in controller["runs"])
            assert all(run["api_errors"] == 0 for run in controller["runs"])
