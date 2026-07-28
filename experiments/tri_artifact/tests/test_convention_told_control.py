from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from scripts.run_convention_told_control import ADDENDUM, PROTOCOL, TASKS
from tri.convention_told_control import (
    CONDITIONS,
    CONVENTION_SYSTEM_PROMPT,
    CONVENTION_TEXT,
    EVIDENCE_STATUS,
    PAYLOAD_KEYS,
    PLAIN_SYSTEM_PROMPT,
    RUN_VERSION,
    build_payload,
    build_report,
    load_frozen_inventory,
    parse_output,
    payload_sha256,
    sha256_path,
    validate_payload,
    validate_resume_prefix,
    validate_smoke,
)


ROOT = Path(__file__).resolve().parents[1]


def _component(target: str | None, error_kind: str | None = None) -> dict:
    return {
        "logical_call": "test",
        "parsed": None if target is None else {"action": "process", "target_id": target},
        "error": None if target is not None else "synthetic failure",
        "error_kind": error_kind,
        "attempts": [],
        "usage": {},
    }


def _row(task: dict, index: int, model: str = "synthetic-model") -> dict:
    conditions = {
        "plain_history": _component(task["post_refresh_target"]),
        "convention_told": _component(task["correct_target"]),
    }
    return {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": "full",
        "timestamp_utc": "2026-07-28T00:00:00+00:00",
        "model": model,
        "endpoint": "https://api.siliconflow.cn/v1",
        "api_settings": {},
        "task_file_sha256": sha256_path(TASKS),
        "protocol_sha256": sha256_path(PROTOCOL),
        "addendum_sha256": sha256_path(ADDENDUM),
        "task": task,
        "task_index": index,
        "condition_order": list(CONDITIONS),
        "user_payload_sha256": payload_sha256(task),
        "conditions": conditions,
        "outcomes": {
            condition: conditions[condition]["parsed"]["target_id"] for condition in CONDITIONS
        },
        "logical_calls_planned": 2,
        "logical_calls_attempted": 2,
        "logical_calls_completed": 2,
        "complete": True,
    }


def test_frozen_inventory_and_payload_have_exact_denominators_and_no_design_fields():
    tasks = load_frozen_inventory(TASKS)
    assert len(tasks) == 80
    assert len({task["pair_id"] for task in tasks}) == 40
    payload = build_payload(tasks[0])
    assert set(payload) == PAYLOAD_KEYS
    assert "selector" not in payload
    assert "initial_selected_id" not in payload
    assert "correct_target" not in payload
    validate_payload(payload)


def test_condition_prompt_diff_is_only_the_frozen_convention():
    assert CONVENTION_TEXT in CONVENTION_SYSTEM_PROMPT
    assert CONVENTION_SYSTEM_PROMPT.replace(" " + CONVENTION_TEXT, "") == PLAIN_SYSTEM_PROMPT


def test_output_parser_requires_exact_process_or_invalid_schema():
    assert parse_output('{"action":"process","target_id":"ALT-1A"}')["target_id"] == "ALT-1A"
    assert parse_output(
        '{"action":"invalid","target_id":"INVALID_BOUND_ENTITY"}'
    )["target_id"] == "INVALID_BOUND_ENTITY"
    with pytest.raises(ValueError):
        parse_output('{"action":"acknowledge","target_id":"ALT-1A"}')
    with pytest.raises(ValueError):
        parse_output('{"action":"process","target_id":"ALT-1A","gold":"ALT-1A"}')


def test_report_uses_all_40_pairs_and_recovers_synthetic_convention_gain():
    tasks = load_frozen_inventory(TASKS)
    rows = [_row(task, index) for index, task in enumerate(tasks)]
    report = build_report(rows, samples=200)
    model = report["models"][0]
    assert model["metrics"]["plain_history"]["changed_pairacc"]["denominator"] == 40
    assert model["metrics"]["convention_told"]["changed_pairacc"]["numerator"] == 40
    assert model["paired_differences"][0]["difference_right_minus_left"] == 1.0


def test_smoke_gate_allows_one_failure_per_condition_but_not_two():
    tasks = load_frozen_inventory(TASKS)
    rows = [_row(task, index) for index, task in enumerate(tasks[:16])]
    validate_smoke(rows, tasks, "synthetic-model")
    rows[0]["conditions"]["plain_history"] = _component(None, "api")
    rows[0]["outcomes"]["plain_history"] = None
    rows[0]["complete"] = False
    validate_smoke(rows, tasks, "synthetic-model")
    rows[1]["conditions"]["plain_history"] = _component(None, "parse_or_schema")
    rows[1]["outcomes"]["plain_history"] = None
    rows[1]["complete"] = False
    with pytest.raises(ValueError, match="failure gate"):
        validate_smoke(rows, tasks, "synthetic-model")


def test_resume_requires_exact_versioned_prefix():
    tasks = load_frozen_inventory(TASKS)
    rows = [_row(task, index) for index, task in enumerate(tasks[:3])]
    validate_resume_prefix(
        rows,
        tasks,
        "synthetic-model",
        "full",
        sha256_path(TASKS),
        sha256_path(PROTOCOL),
        sha256_path(ADDENDUM),
    )
    broken = deepcopy(rows)
    broken[1]["task_index"] = 99
    with pytest.raises(ValueError, match="task index"):
        validate_resume_prefix(
            broken,
            tasks,
            "synthetic-model",
            "full",
            sha256_path(TASKS),
            sha256_path(PROTOCOL),
            sha256_path(ADDENDUM),
        )

