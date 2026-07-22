from pathlib import Path

from scripts.freeze_v7_repeat_stability import freeze, load, validate


ROOT = Path(__file__).resolve().parents[1]


def test_repeat_stability_subset_is_balanced_and_deterministic() -> None:
    source = load(ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")
    first = freeze(source)
    second = freeze(source)
    summary = validate(first)
    assert [row["id"] for row in first] == [row["id"] for row in second]
    assert summary["tasks"] == 40
    assert summary["state_clusters"] == 40
    assert sorted(summary["update"].values()) == [13, 13, 14]
