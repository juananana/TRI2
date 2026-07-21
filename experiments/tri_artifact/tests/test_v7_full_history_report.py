from __future__ import annotations

import json
from pathlib import Path

from tri.v7_full_history_report import build_report


def row(task_id: str, binding: str, predicted: str, correct: str) -> dict:
    return {
        "model": "Qwen/test",
        "status": "ok",
        "api_request_attempts": 2,
        "api_retries": 0,
        "api_usage": [
            {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            {"prompt_tokens": 20, "completion_tokens": 3, "total_tokens": 23},
        ],
        "latency_s": 1.5,
        "task": {
            "id": task_id,
            "state_cluster_id": task_id,
            "binding": binding,
            "update": "flip",
            "pre_refresh_target": "A",
            "post_refresh_target": "B",
            "correct_target": correct,
        },
        "result": {
            "mode": "interactive",
            "predicted_target": predicted,
            "success": predicted == correct,
            "errors": [],
        },
    }


def test_full_history_report_separates_opposite_substitutions(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    rows = [row("anchored", "anchored", "B", "A"), row("dynamic", "dynamic", "A", "B")]
    path.write_text("".join(json.dumps(item) + "\n" for item in rows), encoding="utf-8")
    run = build_report([path], [], samples=100)["runs"][0]
    assert run["anchored_substitutions"] == 1
    assert run["dynamic_old_targets"] == 1
    assert run["api_request_attempts"] == 4
    assert run["prompt_tokens"] == 60
    assert run["completion_tokens"] == 10
    assert run["total_tokens"] == 70
    assert run["latency_seconds"] == 3.0


def test_full_history_pair_reports_direction_and_missing_rows(tmp_path: Path) -> None:
    left_path = tmp_path / "left.jsonl"
    right_path = tmp_path / "right.jsonl"
    left = [row("improves", "anchored", "B", "A"), row("missing-right", "anchored", "A", "A")]
    right = [row("improves", "anchored", "A", "A"), row("missing-left", "anchored", "A", "A")]
    left_path.write_text("".join(json.dumps(item) + "\n" for item in left), encoding="utf-8")
    right_path.write_text("".join(json.dumps(item) + "\n" for item in right), encoding="utf-8")
    pair = build_report([], [(left_path, right_path)], samples=100)["pairs"][0]
    assert pair["n"] == 1
    assert pair["a_wrong_b_right"] == 1
    assert pair["a_right_b_wrong"] == 0
    assert pair["only_a"] == ["missing-right"]
    assert pair["only_b"] == ["missing-left"]
