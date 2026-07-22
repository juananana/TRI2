from pathlib import Path

from tri.v7_cluster_precision import build_primary_report, build_report


ROOT = Path(__file__).resolve().parents[1]


def test_cluster_precision_preserves_clusters_and_full_effect() -> None:
    report = build_report(ROOT / "runs", sizes=(5, 40), trials=100, seed=7)
    assert [row["model"] for row in report["models"]] == ["Qwen3.5", "GLM-5.1", "DeepSeek"]
    for row in report["models"]:
        assert row["matched_tasks"] == 240
        assert row["state_clusters"] == 40
        assert row["tasks_per_cluster"] == [6]
        assert row["full_delta"] > 0.15
        assert row["curve"][0]["tasks"] == 30
        assert row["curve"][1]["tasks"] == 240
        assert row["curve"][1]["positive_fraction"] == 1.0


def test_primary_precision_uses_complete_template_clusters() -> None:
    report = build_primary_report(ROOT / "runs", sizes=(5, 20), trials=100, seed=7)
    assert [row["model"] for row in report["models"]] == ["Qwen3.5", "GLM-5.1"]
    for row in report["models"]:
        assert row["matched_tasks"] == 160
        assert row["state_clusters"] == 20
        assert row["tasks_per_cluster"] == [8]
        assert row["full_delta"] > 0.25
        assert row["curve"][0]["tasks"] == 40
        assert row["curve"][1]["tasks"] == 160
