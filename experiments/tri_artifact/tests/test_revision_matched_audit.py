from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from tri.call_matched_authorization_ablation import build_actor_payload
from tri.revision_matched_audit import (
    EVIDENCE_STATUS,
    RUN_VERSION,
    build_report,
    build_full_diagnostic,
    build_human_rewrite,
    build_source_grounded,
    enforced_target,
    load_jsonl,
    parse_actor_exact,
    parse_compiler_exact,
    validate_inventory,
)
from scripts.run_revision_matched_audit import MODEL_IDS, load_frozen, resolve_model, validate_resume_prefix
from scripts.run_revision_matrix import validate_existing
from scripts import run_submission_critical_matrix


ROOT = Path(__file__).resolve().parents[1]


def inventories():
    private_key = ROOT / "human_validation" / "annotation_key_private.csv"
    if private_key.is_file():
        human_rewrite = build_human_rewrite(
            ROOT / "data" / "temporal_referent_human_rewrites_v1.jsonl", ROOT
        )
    else:
        human_rewrite = load_jsonl(ROOT / "data" / "revision_human_rewrite_v1.jsonl")
    return {
        "full_diagnostic": build_full_diagnostic(
            ROOT / "data" / "temporal_referent_v3_language_clusters.jsonl"
        ),
        "human_rewrite": human_rewrite,
        "source_grounded": build_source_grounded(
            ROOT / "data" / "source_anchored_external_transfer_tasks_v1.jsonl",
            ROOT / "data" / "toolsandbox_tri_single_turn_2x2_v1.jsonl",
        ),
    }


def test_revision_inventories_have_frozen_denominators():
    results = {name: validate_inventory(rows, name) for name, rows in inventories().items()}
    assert results["full_diagnostic"]["rows"] == 160
    assert results["full_diagnostic"]["changed_pairs"] == 32
    assert results["human_rewrite"]["rows"] == 50
    assert results["human_rewrite"]["complete_pairs"] == 7
    assert results["source_grounded"]["complete_pairs"] == 30
    assert results["source_grounded"]["source_rows"] == {
        "AgentDojo": 20,
        "STATE-Bench": 20,
        "ToolSandbox": 20,
    }


def test_submission_critical_model_extension_uses_existing_siliconflow_ids():
    assert resolve_model("deepseek") == ("deepseek", "deepseek-ai/DeepSeek-V4-Pro")
    assert resolve_model("minimax") == ("minimax", "Pro/MiniMaxAI/MiniMax-M2.5")
    assert set(MODEL_IDS) == {"qwen", "glm", "deepseek", "minimax"}


def test_revision_runner_accepts_only_an_exact_complete_resume_prefix(tmp_path: Path):
    source = ROOT / "runs" / "revision_full_diagnostic_qwen_full_v1.jsonl"
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()[:3]]
    tasks, _, _ = load_frozen("full_diagnostic")
    validate_resume_prefix(
        rows,
        tasks,
        rows[0]["model"],
        "full",
        rows[0]["task_file_sha256"],
        rows[0]["protocol_sha256"],
    )
    partial = tmp_path / "partial.jsonl"
    partial.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert validate_existing(partial, "full_diagnostic", "qwen", "full") is False

    corrupted = deepcopy(rows)
    corrupted[1]["task_index"] = 99
    with pytest.raises(ValueError, match="task index"):
        validate_resume_prefix(
            corrupted,
            tasks,
            rows[0]["model"],
            "full",
            rows[0]["task_file_sha256"],
            rows[0]["protocol_sha256"],
        )


def test_submission_orchestrator_resumes_partial_revision_output(tmp_path: Path, monkeypatch):
    smoke = tmp_path / "smoke.jsonl"
    full = tmp_path / "full.jsonl"
    smoke.write_text("complete\n", encoding="utf-8")
    full.write_text("partial\n", encoding="utf-8")
    commands = []

    monkeypatch.setattr(
        run_submission_critical_matrix,
        "_revision_paths",
        lambda audit, alias: (smoke, full),
    )
    monkeypatch.setattr(
        run_submission_critical_matrix,
        "validate_revision_existing",
        lambda path, audit, alias, stage: path == smoke,
    )
    monkeypatch.setattr(run_submission_critical_matrix, "_run", commands.append)

    assert run_submission_critical_matrix.run_revision("full_diagnostic", "minimax") == full
    assert len(commands) == 1
    assert commands[0][-1] == "--resume"
    assert commands[0][commands[0].index("--output") + 1] == str(full)


def test_matched_actor_payloads_differ_only_by_decision():
    task = inventories()["source_grounded"][0]
    decision = {
        "reference_mode": task["reference_mode_gold"],
        "bound_target_id": task["pre_refresh_target"]
        if task["reference_mode_gold"] == "preserve"
        else None,
        "selector": task["selector"],
    }
    history = build_actor_payload(task, None)
    visible = build_actor_payload(task, decision)
    assert visible.pop("compiler_decision") == decision
    assert visible == history


def test_exact_id_parser_does_not_truncate_suffixes():
    task = {
        "initial_state": [{"id": "MAS-01-A"}, {"id": "MAS-01-B"}],
        "refreshed_state": [{"id": "MAS-01-A"}, {"id": "MAS-01-B"}],
    }
    compiler = parse_compiler_exact(
        '{"reference_mode":"preserve","bound_target_id":"MAS-01-A","selector":"fewest"}',
        task,
    )
    actor = parse_actor_exact('{"action":"write","target_id":"MAS-01-B"}', task)
    assert compiler["bound_target_id"] == "MAS-01-A"
    assert actor["target_id"] == "MAS-01-B"
    with pytest.raises(ValueError):
        parse_actor_exact('{"action":"write","target_id":"MAS-01"}', task)


def test_source_pairs_are_opposite_gold_and_state_matched():
    tasks = inventories()["source_grounded"]
    by_pair = {}
    for task in tasks:
        by_pair.setdefault(task["pair_id"], []).append(task)
    assert len(by_pair) == 30
    for pair in by_pair.values():
        assert len(pair) == 2
        assert {task["reference_mode_gold"] for task in pair} == {"preserve", "reevaluate"}
        assert pair[0]["initial_state"] == pair[1]["initial_state"]
        assert pair[0]["refreshed_state"] == pair[1]["refreshed_state"]
        assert pair[0]["correct_target"] != pair[1]["correct_target"]


def test_enforcement_applies_action_validity_without_reselection():
    task = inventories()["full_diagnostic"]
    reject = next(
        row
        for row in task
        if row["reference_mode_gold"] == "preserve" and not row["actionable_core"]
    )
    decision = {
        "reference_mode": "preserve",
        "bound_target_id": reject["pre_refresh_target"],
        "selector": reject["selector"],
    }
    assert enforced_target(decision, reject["post_refresh_target"], reject) == "INVALID_BOUND_ENTITY"


def test_report_preserves_pair_and_wrong_write_denominators():
    rows = []
    for task in inventories()["source_grounded"]:
        decision = {
            "reference_mode": task["reference_mode_gold"],
            "bound_target_id": task["pre_refresh_target"]
            if task["reference_mode_gold"] == "preserve"
            else None,
            "selector": task["selector"],
        }
        history = task["post_refresh_target"]
        visible = task["correct_target"]
        enforced = enforced_target(decision, visible, task)
        component = {"parsed": {"action": task["action"], "target_id": visible}, "attempts": []}
        rows.append(
            {
                "run_version": RUN_VERSION,
                "evidence_status": EVIDENCE_STATUS,
                "model": "synthetic-test-model",
                "task": task,
                "logical_calls_planned": 3,
                "logical_calls_completed": 3,
                "complete": True,
                "compiler": {"parsed": decision, "attempts": []},
                "actors": {"history_only": component, "decision_visible": component},
                "outcomes": {
                    "history_only": history,
                    "decision_visible": visible,
                    "decision_enforced": enforced,
                },
            }
        )
    report = build_report(rows, samples=200)
    model = report["models"][0]
    assert model["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 0
    assert model["metrics"]["decision_visible"]["changed_pairacc"]["numerator"] == 30
    assert model["metrics"]["history_only"]["fixed_executor_wrong_writes"]["numerator"] == 30
    assert model["decision_visible_minus_history"]["changed_pairacc"]["difference"] == 1.0
