from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from tri.call_matched_authorization_ablation import (
    ACTOR_CONDITIONS,
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    RUN_VERSION,
    TASK_FILE_SHA256,
    build_actor_payload,
    build_report,
    build_tasks,
    decision_enforced_target,
    parse_actor_output,
    parse_compiler_output,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"


def test_frozen_flip_inventory_is_automatic_and_balanced() -> None:
    tasks = build_tasks(SOURCE)
    assert len(tasks) == 80
    assert len({row["id"] for row in tasks}) == 80
    assert len({row["state_cluster_id"] for row in tasks}) == 40
    assert Counter(row["reference_mode_gold"] for row in tasks) == {
        "preserve": 40,
        "reevaluate": 40,
    }
    assert all(row["update"] == "flip" for row in tasks)
    assert all(row["pre_refresh_target"] != row["post_refresh_target"] for row in tasks)
    by_cluster: dict[str, list[dict]] = {}
    for row in tasks:
        by_cluster.setdefault(row["state_cluster_id"], []).append(row)
    assert all(
        [item["reference_mode_gold"] for item in pair] == ["preserve", "reevaluate"]
        for pair in by_cluster.values()
    )
    from tri.call_matched_authorization_ablation import jsonl_bytes, sha256_bytes, sha256_path

    assert sha256_bytes(jsonl_bytes(tasks)) == TASK_FILE_SHA256
    assert sha256_path(TASKS) == TASK_FILE_SHA256


def test_actor_payloads_differ_only_by_frozen_decision_block() -> None:
    task = build_tasks(SOURCE)[0]
    decision = {
        "reference_mode": "preserve",
        "bound_target_id": task["pre_refresh_target"],
        "selector": task["selector"],
    }
    history = build_actor_payload(task, None)
    visible = build_actor_payload(task, decision)
    assert ACTOR_CONDITIONS == ("history_only", "decision_visible")
    assert "compiler_decision" not in history
    assert visible.pop("compiler_decision") == decision
    assert visible == history


def test_provider_transport_disables_reasoning_explicitly() -> None:
    from scripts.run_call_matched_authorization_ablation import build_request_body

    body = build_request_body("Qwen/Qwen3.5-122B-A10B", [], 0.0, 500)
    assert body["enable_thinking"] is False
    assert body["max_tokens"] == 500


def test_output_parsers_are_strict_but_accept_fenced_json() -> None:
    compiler = parse_compiler_output(
        '```json\n{"reference_mode":"preserve","bound_target_id":"REM-1A",'
        '"selector":"earliest incomplete reminder"}\n```'
    )
    assert compiler["reference_mode"] == "preserve"
    assert compiler["bound_target_id"] == "REM-1A"
    assert parse_actor_output('{"action":"postpone","target_id":"REM-1A"}')["target_id"] == "REM-1A"
    with pytest.raises(ValueError):
        parse_compiler_output('{"reference_mode":"other","bound_target_id":null,"selector":"x"}')
    with pytest.raises(ValueError):
        parse_actor_output('{"target_id":"REM-1A"}')


def test_decision_enforcement_reuses_visible_target_and_can_help_or_harm() -> None:
    assert decision_enforced_target(
        {"reference_mode": "preserve", "bound_target_id": "A"}, "B"
    ) == "A"
    assert decision_enforced_target(
        {"reference_mode": "preserve", "bound_target_id": "A"}, "B"
    ) == "A"
    assert decision_enforced_target(
        {"reference_mode": "reevaluate", "bound_target_id": None}, "B"
    ) == "B"


def _run_row(task: dict, history: str, visible: str, compiler: dict | None = None) -> dict:
    compiler = compiler or {
        "reference_mode": task["reference_mode_gold"],
        "bound_target_id": task["pre_refresh_target"] if task["reference_mode_gold"] == "preserve" else None,
        "selector": task["selector"],
    }
    enforced = decision_enforced_target(compiler, visible)
    decision_id = f"decision-{task['id']}"
    return {
        "run_version": RUN_VERSION,
        "evidence_status": "post-primary",
        "model": "Qwen/Qwen3.5-122B-A10B",
        "task": task,
        "compiler_decision_id": decision_id,
        "compiler": {"parsed": compiler, "error": None, "attempts": [{"status": "success"}]},
        "actors": {
            "history_only": {
                "parsed": {"action": task["action"], "target_id": history},
                "error": None,
                "attempts": [{"status": "success"}],
                "compiler_decision_id": decision_id,
            },
            "decision_visible": {
                "parsed": {"action": task["action"], "target_id": visible},
                "error": None,
                "attempts": [{"status": "success"}],
                "compiler_decision_id": decision_id,
            },
        },
        "outcomes": {
            "history_only": history,
            "decision_visible": visible,
            "decision_enforced": enforced,
        },
        "logical_calls_planned": 3,
        "logical_calls_completed": 3,
        "complete": True,
    }


def test_validator_rejects_unshared_or_incomplete_calls() -> None:
    task = build_tasks(SOURCE)[0]
    row = _run_row(task, task["correct_target"], task["correct_target"])
    validate_run_row(row)
    bad = json.loads(json.dumps(row))
    bad["actors"]["decision_visible"]["compiler_decision_id"] = "different"
    with pytest.raises(ValueError):
        validate_run_row(bad)
    bad = json.loads(json.dumps(row))
    bad["logical_calls_completed"] = 2
    bad["complete"] = False
    with pytest.raises(ValueError):
        validate_run_row(bad, require_complete=True)


def test_four_task_health_gate_is_model_specific() -> None:
    from tri.call_matched_authorization_ablation import validate_health_smoke

    tasks = build_tasks(SOURCE)
    rows = [_run_row(task, task["correct_target"], task["correct_target"]) for task in tasks[:4]]
    validate_health_smoke(rows, "Qwen/Qwen3.5-122B-A10B", tasks)
    with pytest.raises(ValueError):
        validate_health_smoke(rows, "Pro/zai-org/GLM-5.1", tasks)


def test_report_pairacc_conditional_substitution_and_enforcement_accounting() -> None:
    tasks = build_tasks(SOURCE)[:4]
    rows = []
    for task in tasks:
        gold = task["correct_target"]
        history = task["post_refresh_target"] if task["reference_mode_gold"] == "preserve" else gold
        rows.append(_run_row(task, history, gold))
    report = build_report(rows, seed=BOOTSTRAP_SEED, samples=200)
    assert report["evidence_status"] == "post-primary"
    assert report["bootstrap"]["seed"] == 20260725
    assert BOOTSTRAP_SAMPLES == 10_000
    model = report["models"][0]
    assert model["state_clusters"] == 2
    assert model["metrics"]["history_only"]["changed_pairacc"]["count"] == 0
    assert model["metrics"]["decision_visible"]["changed_pairacc"]["count"] == 2
    assert model["metrics"]["decision_enforced"]["changed_pairacc"]["count"] == 2
    conditional = model["metrics"]["history_only"]["preserve_conditional_substitution"]
    assert conditional["numerator"] == 2
    assert conditional["denominator"] == 2
    assert model["enforcement"]["repairs"] == 0
    assert model["enforcement"]["harms"] == 0
    differences = {
        (row["left"], row["right"], row["metric"]): row
        for row in model["paired_differences"]
    }
    substitution_delta = differences[
        ("history_only", "decision_visible", "preserve_conditional_substitution")
    ]
    assert substitution_delta["difference_right_minus_left"] == -1.0


def test_api_or_parse_failure_stays_in_itt_denominator() -> None:
    tasks = build_tasks(SOURCE)[:2]
    good = _run_row(tasks[0], tasks[0]["correct_target"], tasks[0]["correct_target"])
    failed = _run_row(tasks[1], tasks[1]["correct_target"], tasks[1]["correct_target"])
    failed["actors"]["decision_visible"] = {
        "parsed": None,
        "error": "json_parse_error",
        "attempts": [{"status": "success", "raw_content": "not json"}],
        "compiler_decision_id": failed["compiler_decision_id"],
    }
    failed["outcomes"]["decision_visible"] = None
    failed["outcomes"]["decision_enforced"] = None
    failed["complete"] = False
    report = build_report([good, failed], seed=BOOTSTRAP_SEED, samples=50)
    model = report["models"][0]
    assert model["rows"] == 2
    assert model["metrics"]["decision_visible"]["e2e"]["denominator"] == 2
    assert model["failures"]["parse_or_schema"] == 1
