from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from scripts.run_independent_holdout_model_experiment import api_key_from_environment
from tri.independent_holdout_model_experiment import (
    BOOTSTRAP_SEED,
    MODEL_IDS,
    build_claim_gate,
    build_report,
    actor_base_payload,
    actor_payload,
    offline_rule,
    pairacc,
    render_markdown,
    sqlite_consistency,
)
from tri.independent_language_holdout import (
    ANNOTATORS,
    build_assignments,
    build_model_tasks,
    build_scenario_pairs,
    clear_complete_pairs,
    sha256_bytes,
    validate_annotation_returns,
    validate_writer_returns,
)


ROOT = Path(__file__).resolve().parents[1]


def model_tasks():
    pairs = build_scenario_pairs(ROOT / "data" / "temporal_referent_v7_core_replication.jsonl")
    assignments = build_assignments(pairs)
    pair_map = {row["pair_id"]: row for row in pairs}
    raw = []
    for assignment in assignments:
        pair = pair_map[assignment["pair_id"]]
        instruction = (
            f"Select the {pair['selector']} before synchronization and remember it; synchronize, then "
            f"{pair['action']} it."
            if assignment["mode"] == "preserve"
            else f"Synchronize first; then select {pair['selector']} and {pair['action']} it."
        )
        intent = (
            pair["pre_refresh_target"]
            if assignment["mode"] == "preserve"
            else pair["post_refresh_target"]
        )
        raw.append(
            {
                "item_id": assignment["item_id"],
                "writer_id": assignment["writer_id"],
                "instruction": instruction,
                "instruction_sha256": sha256_bytes(instruction.encode()),
                "writer_intent": intent,
                "writer_confidence": "5",
                "writer_submission_id": f"response-{assignment['writer_id']}",
                "age_18": True,
                "english_independent": True,
                "consent": True,
                "no_assistance": True,
                "technical_issue": False,
                "completed": True,
            }
        )
    authored = validate_writer_returns(raw, assignments, pair_map)
    annotations = validate_annotation_returns(
        [
            {
                "annotator_id": annotator,
                "item_id": row["item_id"],
                "target": row["writer_intent"],
                "confidence": "5",
            }
            for annotator in ANNOTATORS
            for row in authored
        ],
        authored,
    )
    return build_model_tasks(authored, pairs, clear_complete_pairs(authored, annotations))


def test_primary_actor_payloads_differ_only_by_compiler_decision():
    task = model_tasks()[0]
    decision = {
        "reference_mode": task["reference_mode_design"],
        "bound_target_id": task["pre_refresh_target"]
        if task["reference_mode_design"] == "preserve"
        else None,
        "selector": task["selector"],
    }
    history = actor_payload(task, "history_only", decision)
    visible = actor_payload(task, "decision_visible", decision)
    assert visible.pop("compiler_decision") == decision
    assert history == visible == actor_base_payload(task)


def test_rule_and_sqlite_checks_are_offline_and_target_faithful():
    task = next(row for row in model_tasks() if row["reference_mode_design"] == "preserve")
    rule = offline_rule(task)
    assert set(rule) == {"reference_mode", "target_id", "error"}
    correct = sqlite_consistency(task, task["correct_target"])
    wrong = sqlite_consistency(task, task["post_refresh_target"])
    assert correct["status"] == "successful_write"
    assert wrong["status"] == "wrong_entity_write"
    assert wrong["acted_ids"] == [task["post_refresh_target"]]


def test_pairacc_uses_only_complete_clear_pairs():
    tasks = model_tasks()[:2]
    rows = [
        {"task": task, "outcomes": {"history_only": task["correct_target"]}}
        for task in tasks
    ]
    assert pairacc(rows, "history_only") == (1, 1)
    broken = deepcopy(rows)
    broken[0]["outcomes"]["history_only"] = broken[0]["task"]["post_refresh_target"]
    assert pairacc(broken, "history_only") == (0, 1)


def synthetic_run_row(task, model, history_target, visible_target):
    decision = {
        "reference_mode": task["reference_mode_design"],
        "bound_target_id": (
            task["pre_refresh_target"]
            if task["reference_mode_design"] == "preserve"
            else None
        ),
        "selector": task["selector"],
    }
    targets = {
        "history_only": history_target,
        "decision_visible": visible_target,
        "timing_reminder": task["correct_target"],
        "cta": task["correct_target"],
    }
    actors = {}
    for condition, target in targets.items():
        actors[condition] = {
            "logical_call": condition,
            "parsed": (
                {"action": task["action"], "target_id": target}
                if target is not None
                else None
            ),
            "error": None if target is not None else "synthetic_parse_failure",
            "error_kind": None if target is not None else "parse_or_schema",
            "attempts": [],
            "usage": {},
        }
    row = {
        "run_version": "TRI-independent-language-holdout-model-v1",
        "evidence_status": "post-primary; protocol and implementations frozen before own calls",
        "run_scope": "synthetic",
        "model": model,
        "task": deepcopy(task),
        "compiler": {
            "logical_call": "compiler",
            "parsed": decision,
            "error": None,
            "error_kind": None,
            "attempts": [],
            "usage": {},
        },
        "actors": actors,
        "outcomes": targets,
        "sqlite_consistency": {
            condition: sqlite_consistency(task, target)
            for condition, target in targets.items()
        },
        "rule_star": offline_rule(task),
        "logical_calls_planned": 5,
        "logical_calls_attempted": 0,
        "logical_calls_completed": sum(target is not None for target in targets.values()) + 1,
        "complete": all(target is not None for target in targets.values()),
    }
    return row


def synthetic_three_model_rows(adverse_visible_write=False):
    tasks = model_tasks()[:8]
    rows = []
    for model in MODEL_IDS.values():
        for index, task in enumerate(tasks):
            visible = task["correct_target"]
            if adverse_visible_write and index == 0:
                visible = (
                    task["post_refresh_target"]
                    if task["correct_target"] == task["pre_refresh_target"]
                    else task["pre_refresh_target"]
                )
            rows.append(synthetic_run_row(task, model, None, visible))
    return rows


def test_report_is_itt_pair_clustered_and_promotes_only_when_exact_gate_passes():
    report = build_report(synthetic_three_model_rows(), samples=200, seed=BOOTSTRAP_SEED)
    assert report["bootstrap"] == {
        "unit": "pair_id",
        "samples": 200,
        "seed": 20260728,
    }
    assert report["claim_promotion"]["promote_claim"] is True
    assert report["claim_promotion"]["models_with_positive_pairacc_ci_excluding_zero"] == 3
    for model in report["models"]:
        assert model["metrics"]["history_only"]["clear_pair_pairacc"]["rate"] == 0
        assert model["metrics"]["decision_visible"]["clear_pair_pairacc"]["rate"] == 1
        assert model["metrics"]["history_only"]["all_row_e2e"] == {
            "numerator": 0,
            "denominator": 8,
            "rate": 0.0,
            "ci95_pair_cluster": [0.0, 0.0],
        }
        assert model["compiler_and_initial_binding"]["compiler_mode_error"]["numerator"] == 0
    assert "Promote abstract-level claim: **YES**" in render_markdown(report)


def test_wrong_write_harm_above_five_points_blocks_claim_promotion():
    report = build_report(
        synthetic_three_model_rows(adverse_visible_write=True), samples=500, seed=BOOTSTRAP_SEED
    )
    gate = report["claim_promotion"]
    assert gate["all_three_pairacc_point_estimates_positive"] is True
    assert gate["wrong_write_margin_met_for_every_model"] is False
    assert gate["promote_claim"] is False
    assert all(
        item["wrong_write_rate_difference"] == 0.125 for item in gate["models"]
    )


def test_runner_accepts_only_llm_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("SILICONFLOW_API_KEY", "must-not-be-used")
    assert api_key_from_environment() == ""
    monkeypatch.setenv("LLM_API_KEY", " expected-key ")
    assert api_key_from_environment() == "expected-key"


def test_claim_gate_includes_the_frozen_plus_five_point_boundary():
    models = [
        {
            "model": model,
            "primary_pairacc_contrast": {
                "difference_right_minus_left": 0.1,
                "ci95_pair_cluster": [0.01, 0.2],
            },
            "wrong_write_rate_contrast": {"difference_right_minus_left": 0.05},
        }
        for model in MODEL_IDS.values()
    ]
    assert build_claim_gate(models)["promote_claim"] is True
    models[0]["wrong_write_rate_contrast"]["difference_right_minus_left"] = 0.0500001
    assert build_claim_gate(models)["promote_claim"] is False
