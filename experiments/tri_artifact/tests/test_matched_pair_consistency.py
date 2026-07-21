from __future__ import annotations

import copy
import json
from pathlib import Path

from tri.matched_pair_consistency import build_pairs, result_success, summarize_pairs


def task(task_id: str, style: str, binding: str, correct: str = "A") -> dict:
    return {
        "id": task_id,
        "domain": "mail",
        "style": style,
        "binding": binding,
        "update": "flip",
        "initial_state": [{"id": "A"}, {"id": "B"}],
        "refreshed_state": [{"id": "A"}, {"id": "B"}],
        "selector": "first",
        "action": "reply",
        "action_schema": {},
        "correct_target": correct,
    }


def test_build_pairs_holds_transition_fixed() -> None:
    tasks = [
        task("ea", "explicit_anchor", "anchored", "A"),
        task("id", "implicit_dynamic", "dynamic", "B"),
        task("ia", "implicit_anchor", "anchored", "A"),
        task("ed", "explicit_dynamic", "dynamic", "B"),
    ]
    pairs = build_pairs(tasks)
    assert len(pairs) == 2
    assert {pair["preserve_id"] for pair in pairs} == {"ea", "ia"}
    assert {pair["reevaluate_id"] for pair in pairs} == {"id", "ed"}


def test_incomplete_outputs_are_itt_incorrect() -> None:
    tasks = [
        task("ea", "explicit_anchor", "anchored"),
        task("id", "implicit_dynamic", "dynamic", "B"),
    ]
    pairs = build_pairs(tasks)
    summaries, missing = summarize_pairs(pairs, {"ea": True})
    assert missing == 1
    assert summaries["all"]["preserve_correct"] == 1
    assert summaries["all"]["reevaluate_correct"] == 0
    assert summaries["all"]["both_correct"] == 0


def test_api_and_parse_failures_are_incorrect() -> None:
    base = {"status": "ok", "task": {"correct_target": "A"}, "result": {"success": True}}
    assert result_success(base)
    api = copy.deepcopy(base)
    api["status"] = "api_error"
    assert not result_success(api)
    parse = copy.deepcopy(base)
    parse["result"]["errors"] = ["parse failure"]
    assert not result_success(parse)
