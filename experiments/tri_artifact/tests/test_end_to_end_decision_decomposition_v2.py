from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from tri.end_to_end_decision_decomposition import canonical_json, sha256_path, sha256_text
from tri.end_to_end_decision_decomposition_v2 import (
    ACTOR_CONDITIONS,
    ACTOR_SYSTEM_PROMPT,
    BOOTSTRAP_SAMPLES,
    COMPILER_SYSTEM_PROMPT,
    MODEL_IDS,
    TASK_FILE_SHA256,
    actor_order,
    build_actor_base_payload,
    build_actor_payload,
    build_compiler_payload,
    build_report,
    load_frozen_tasks,
    parse_compiler_output,
    placebo_fragment,
    prompt_hashes,
    settings_hash,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"


def _attempt(model: str, system: str, payload: dict, raw: str) -> list[dict]:
    return [{
        "status": "success",
        "request": {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, sort_keys=True, ensure_ascii=False)},
            ],
            "temperature": 0.0,
            "max_tokens": 500,
            "enable_thinking": False,
        },
        "raw_content": raw,
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
    }]


def _synthetic_row(task: dict, index: int) -> dict:
    model = MODEL_IDS["qwen"]
    compiler = {
        "reference_mode": task["reference_mode_gold"],
        "pre_refresh_candidate_id": task["pre_refresh_target"],
        "bound_target_id": task["pre_refresh_target"] if task["reference_mode_gold"] == "preserve" else None,
        "selector": task["selector"],
    }
    compiler_payload = build_compiler_payload(task)
    compiler_component = {
        "parsed": compiler,
        "attempts": _attempt(model, COMPILER_SYSTEM_PROMPT, compiler_payload, json.dumps(compiler)),
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
    }
    actors = {}
    for condition in ACTOR_CONDITIONS:
        target = task["correct_target"]
        payload = build_actor_payload(task, compiler, condition)
        parsed = {"action": task["action"], "target_id": target}
        actors[condition] = {
            "parsed": parsed,
            "attempts": _attempt(model, ACTOR_SYSTEM_PROMPT, payload, json.dumps(parsed)),
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }
    row = {
        "run_version": "TRI-end-to-end-decision-decomposition-v2",
        "task": task,
        "task_sha256": sha256_text(canonical_json(task)),
        "task_file_sha256": TASK_FILE_SHA256,
        "prompt_sha256": prompt_hashes(),
        "settings_sha256": settings_hash(),
        "task_index": index,
        "actor_order": list(actor_order(index)),
        "model": model,
        "logical_calls_planned": 9,
        "compiler": compiler_component,
        "actors": actors,
        "outcomes": {condition: task["correct_target"] for condition in ACTOR_CONDITIONS},
    }
    return row


def test_inventory_and_rotation_are_balanced() -> None:
    tasks = load_frozen_tasks(TASKS)
    assert sha256_path(TASKS) == TASK_FILE_SHA256
    assert len(tasks) == 80
    assert all(Counter(order[position] for order in [actor_order(i) for i in range(80)]) == {
        condition: 10 for condition in ACTOR_CONDITIONS
    } for position in range(8))


def test_actor_base_has_no_injected_initial_or_gold_target() -> None:
    task = load_frozen_tasks(TASKS)[0]
    base = build_actor_base_payload(task)
    assert "initial_selected_id" not in base
    assert "correct_target" not in base
    assert "pre_refresh_target" not in base
    assert set(build_compiler_payload(task)) == {
        "instruction", "s0_state", "selector", "action", "action_schema"
    }


def test_cells_are_distinct_and_placebo_contains_no_timing_field() -> None:
    task = load_frozen_tasks(TASKS)[0]
    compiler = {
        "reference_mode": "preserve",
        "pre_refresh_candidate_id": task["pre_refresh_target"],
        "bound_target_id": task["pre_refresh_target"],
        "selector": task["selector"],
    }
    assert set(build_actor_payload(task, compiler, "placebo")["context_summary"]) == {
        "requested_action", "tool_schema", "state_record_counts"
    }
    assert "reference_mode" not in build_actor_payload(task, compiler, "id_control")
    assert "pre_refresh_candidate_id" in build_actor_payload(task, compiler, "id_control")["compiler_fragment"]
    assert "follow_instruction" in build_actor_payload(task, compiler, "full_follow")


def test_compiler_requires_model_produced_candidate_and_consistent_bound_id() -> None:
    raw = json.dumps({
        "reference_mode": "preserve",
        "pre_refresh_candidate_id": "ALT-1A",
        "bound_target_id": "ALT-1A",
        "selector": "highest severity alert",
    })
    assert parse_compiler_output(raw)["pre_refresh_candidate_id"] == "ALT-1A"
    with pytest.raises(ValueError):
        parse_compiler_output(raw.replace("ALT-1A", "ALT-1B", 1))


def test_synthetic_full_report_has_all_cells_and_promotion_gate() -> None:
    tasks = load_frozen_tasks(TASKS)
    rows = [_synthetic_row(task, index) for index, task in enumerate(tasks)]
    for row in rows:
        validate_run_row(row)
    report = build_report(rows, seed=1, samples=10)
    assert len(report["models"]) == 1
    assert set(report["models"][0]["cells"]) == set(ACTOR_CONDITIONS)
    assert report["claim_promotion"]["decisions"]
