from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from tri.independent_holdout_model_experiment import (
    actor_base_payload,
    actor_payload,
    offline_rule,
    pairacc,
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
