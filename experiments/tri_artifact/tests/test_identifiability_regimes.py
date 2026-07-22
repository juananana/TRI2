from pathlib import Path

from tri.identifiability_regimes import load_jsonl, summarize


ROOT = Path(__file__).resolve().parents[1]


def test_v3_identifiability_regime_audit_exposes_one_sided_controls() -> None:
    tasks = load_jsonl(ROOT / "data/temporal_referent_v3_language_clusters.jsonl")
    rows = [
        {
            "status": "ok",
            "task": task,
            "result": {
                "predicted_target": task["correct_target"],
                "compiled_ledger": {"selected_entity_id": task["pre_refresh_target"]},
            },
        }
        for task in tasks
    ]
    report = summarize(rows)
    assert report["regimes"]["aggregate_e2e"]["accuracy"] == 1.0
    assert report["regimes"]["preserve_only"]["n"] == 80
    assert report["regimes"]["reevaluate_only"]["n"] == 80
    assert report["conditional_changed_winner"]["eligible"] == 32
    assert report["changed_pairacc"]["pair_accuracy"] == 1.0


def test_missing_or_failed_rows_are_incorrect_under_regime_audit() -> None:
    tasks = load_jsonl(ROOT / "data/temporal_referent_v3_language_clusters.jsonl")
    row = {
        "status": "error",
        "task": tasks[0],
        "result": {
            "predicted_target": tasks[0]["correct_target"],
            "compiled_ledger": {"selected_entity_id": tasks[0]["pre_refresh_target"]},
        },
    }
    report = summarize([row])
    assert report["regimes"]["aggregate_e2e"]["correct"] == 0
