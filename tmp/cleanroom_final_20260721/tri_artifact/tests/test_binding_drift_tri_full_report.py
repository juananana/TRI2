import json
from pathlib import Path

from tri.binding_drift_tri_full_report import build_report, classify_gate, scored_rows, slice_summary


ROOT = Path(__file__).resolve().parents[1]


def load_tasks() -> list[dict]:
    path = ROOT / "data/temporal_referent_v7_core_replication.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def test_full_inventory_forms_complete_authorization_pairs() -> None:
    tasks = load_tasks()
    targets = {task["id"]: task["correct_target"] for task in tasks}
    summary = slice_summary(scored_rows(tasks, targets, "oracle_test"))
    assert summary["correct"] == 240
    assert summary["anchored"]["correct"] == 120
    assert summary["dynamic"]["correct"] == 120
    assert summary["paired_authorization"] == {"n": 120, "both_correct": 120}
    assert {name: row["n"] for name, row in summary["by_update"].items()} == {
        "flip": 80,
        "stable": 80,
        "name_collision": 80,
    }


def test_gate_detects_unconditional_reresolution() -> None:
    tasks = load_tasks()
    oracle = slice_summary(scored_rows(tasks, {task["id"]: task["correct_target"] for task in tasks}, "oracle"))
    reresolve = slice_summary(scored_rows(tasks, {task["id"]: task["post_refresh_target"] for task in tasks}, "reresolve"))
    assert classify_gate(oracle, reresolve) == "complementary_policy_result"


def test_full_report_accepts_complete_adapted_run(tmp_path: Path) -> None:
    tasks = load_tasks()
    adapted = tmp_path / "adapted.jsonl"
    rows = [
        {
            "task": task,
            "result": {"predicted_target": task["post_refresh_target"]},
            "api_request_attempts": 1,
            "api_retries": 0,
            "usage": [{"total_tokens": 10}],
            "latency_s": 0.1,
        }
        for task in tasks
    ]
    adapted.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    report = build_report(
        ROOT / "data/temporal_referent_v7_core_replication.jsonl",
        adapted,
        ROOT / "runs/v7_glm_compile_then_act_full.jsonl",
        ROOT / "runs/deterministic_discourse_rule_v2_v7.jsonl",
    )
    assert report["n_tasks"] == 240
    assert report["interpretation_gate"] == "complementary_policy_result"
    assert report["run_audit"]["request_attempts"] == 240
    assert report["paired_comparison"]["clusters"] == 40
    assert report["post_run_information_audit"]["status"] == "not_information_matched_to_cta"
    assert report["post_run_information_audit"]["preserve_changed_winner_tasks"] == 80
    assert not report["post_run_information_audit"]["performance_comparison_is_confirmatory"]
