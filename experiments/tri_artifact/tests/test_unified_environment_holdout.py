from __future__ import annotations

from copy import deepcopy

import pytest

from tri.unified_environment_holdout import (
    ANNOTATORS,
    CANDIDATE_PAIRS_PER_ENV,
    CONTROLLERS,
    DEPLOYMENT_MODELS,
    ENVIRONMENT_COMMITS,
    derive_execution_rows,
    build_annotator_form,
    build_writer_forms,
    select_clear_clusters,
    selection_maximizers,
    summarize_executed_results,
    summarize_rule_star,
    validate_candidate_rows,
    validate_human_provenance,
)


def _candidate(environment: str, index: int, clear: bool = True) -> list[dict]:
    s0 = [{"id": "old", "actionable": True}, {"id": "new", "actionable": True}]
    changed = [{"id": "old", "actionable": True}, {"id": "new", "actionable": True}]
    stable = [{"id": "old", "actionable": True}, {"id": "other", "actionable": True}]
    rows = []
    for mode, instruction in (("preserve", "choose it before sync and act on it"), ("reevaluate", "sync then choose and act")):
        item_id = f"{environment}-{index}-{mode}"
        rows.append({
            "item_id": item_id,
            "cluster_id": f"{environment}-{index}",
            "environment": environment,
            "environment_commit": ENVIRONMENT_COMMITS[environment],
            "candidate_order": index,
            "writer_id": f"W{(index + (0 if mode == 'preserve' else 6)) % 12 + 1}",
            "reference_mode": mode,
            "instruction": instruction,
            "selector": "the new item",
            "action": "update",
            "action_schema": {"preconditions": {"actionable": True}},
            "preflight_state_diffs": {
                "changed_old": [{"target_id": "old", "field": "status"}],
                "changed_new": [{"target_id": "new", "field": "status"}],
                "stable_old": [{"target_id": "old", "field": "status"}],
            },
            "s0_state": s0,
            "s1_changed_state": changed,
            "s1_stable_state": stable,
            "pre_refresh_winner": "old",
            "post_refresh_winner": "new",
            "stable_winner": "old",
            "writer_intent": (
                "old" if mode == "preserve" else "new"
            ) if clear else "CLARIFY",
            "adjudications": {
                annotator: ("old" if mode == "preserve" else "new")
                for annotator in ANNOTATORS
            },
        })
    return rows


def _inventory(clear_counts: dict[str, int] | None = None) -> list[dict]:
    clear_counts = clear_counts or {
        environment: CANDIDATE_PAIRS_PER_ENV for environment in ENVIRONMENT_COMMITS
    }
    return [
        row
        for environment in ENVIRONMENT_COMMITS
        for index in range(CANDIDATE_PAIRS_PER_ENV)
        for row in _candidate(
            environment, index, clear=index < clear_counts[environment]
        )
    ]


def _frozen_rows() -> list[dict]:
    candidates = _inventory()
    validate_candidate_rows(candidates)
    return derive_execution_rows(select_clear_clusters(candidates))


def _executions(frozen: list[dict]) -> list[dict]:
    results = []
    for task in frozen:
        for model in DEPLOYMENT_MODELS:
            for controller in CONTROLLERS:
                results.append(
                    {
                        "environment": task["environment"],
                        "model": model,
                        "controller": controller,
                        "row_id": task["row_id"],
                        "execution_status": "success",
                        "initial_selection_id": task["pre_refresh_target"],
                        "refresh_completed": True,
                        "proposed_target_id": task["post_refresh_target"],
                        "mutated_target_id": task["post_refresh_target"],
                        "tool_trace": [
                            {"event": event}
                            for event in (
                                "initial_selection",
                                "refresh",
                                "target_proposal",
                                "mutation",
                                "tool_result",
                                "final_state_diff",
                            )
                        ],
                        "tool_result": {"status": "updated"},
                        "final_state_diff": [
                            {"target_id": task["post_refresh_target"], "operation": "update"}
                        ],
                        "collateral_change_count": 0,
                        "call_count": 1,
                        "input_tokens": 10,
                        "output_tokens": 2,
                        "latency_ms": 5.0,
                    }
                )
    return results


def _human_provenance(candidate_sha256: str = "a" * 64) -> dict:
    return {
        "status": "complete-locked-before-model-calls",
        "candidate_sha256": candidate_sha256,
        "environment_commits": ENVIRONMENT_COMMITS,
        "locked_before_model_calls": True,
        "ethics": {
            "confirmed_before_recruitment": True,
            "determination": "exempt",
        },
        "writers": {
            f"W{index}": {
                "adult": True,
                "consented": True,
                "independent": True,
                "completed": True,
                "prior_tri_exposure": False,
                "saw_tri_templates_or_rule_star": False,
                "saw_model_outputs_or_results": False,
            }
            for index in range(1, 13)
        },
        "annotators": {
            f"A{index}": {
                "independent": True,
                "blind": True,
                "completed": True,
                "saw_model_outputs_before_lock": False,
            }
            for index in range(1, 4)
        },
    }


def test_candidate_validation_and_clear_gate_produce_120_rows() -> None:
    candidates = _inventory()
    validate_candidate_rows(candidates)
    selected = select_clear_clusters(candidates)
    rows = derive_execution_rows(selected)
    assert len(selected) == 40
    assert len(rows) == 120
    assert {row["row_kind"] for row in rows} == {"changed_preserve", "changed_reevaluate", "stable_preserve"}
    assert [
        cluster["candidate_order"] for cluster in selected[:20]
    ] == list(range(20))


def test_clear_gate_rejects_insufficient_environment() -> None:
    candidates = _inventory({"AgentDojo": 20, "ToolSandbox": 19})
    validate_candidate_rows(candidates)
    with pytest.raises(RuntimeError, match="ToolSandbox"):
        select_clear_clusters(candidates)


def test_clear_gate_rejects_writer_intent_that_conflicts_with_assigned_order() -> None:
    candidates = _inventory({"AgentDojo": 20, "ToolSandbox": 20})
    candidates[0]["writer_intent"] = "new"
    candidates[0]["adjudications"] = {
        annotator: "new" for annotator in ANNOTATORS
    }
    validate_candidate_rows(candidates)
    with pytest.raises(RuntimeError, match="AgentDojo"):
        select_clear_clusters(candidates)


def test_selection_keeps_ties_and_requires_two_strong_cells() -> None:
    rows = []
    for environment in ENVIRONMENT_COMMITS:
        for model in DEPLOYMENT_MODELS:
            for index, controller in enumerate(CONTROLLERS):
                rows.append({
                    "environment": environment,
                    "model": model,
                    "controller": controller,
                    "e2e": 1.0 if index == 0 else 0.9 - 0.01 * index,
                    "pairacc": 1.0 if index == 1 else 0.5 - 0.01 * index,
                    "wrong_write_rate": 0.2 if index == 0 else 0.1,
                })
    report = selection_maximizers(rows)
    assert len(report["cells"]) == 6
    assert report["promote_practical_selection"] is True
    assert all(cell["e2e_regret_of_pairacc_maximizers"] == pytest.approx([0.11, 0.11]) for cell in report["cells"])


def test_selection_rejects_incomplete_frozen_controller_set() -> None:
    rows = [
        {
            "environment": "AgentDojo",
            "model": "qwen",
            "controller": CONTROLLERS[0],
            "e2e": 1.0,
            "pairacc": 1.0,
            "wrong_write_rate": 0.0,
        }
    ]
    with pytest.raises(ValueError, match="complete 2-environment x 3-model matrix"):
        selection_maximizers(rows)


def test_candidate_pair_shared_fields_and_action_validity_are_enforced() -> None:
    rows = _inventory()
    mismatched = deepcopy(rows)
    mismatched[1]["selector"] = "different"
    with pytest.raises(ValueError, match="shared field selector"):
        validate_candidate_rows(mismatched)
    invalid = deepcopy(rows)
    invalid[0]["s1_changed_state"][0]["actionable"] = False
    invalid[1]["s1_changed_state"][0]["actionable"] = False
    with pytest.raises(ValueError, match="not action-valid"):
        validate_candidate_rows(invalid)


def test_changed_winner_is_required() -> None:
    rows = _inventory()
    broken = deepcopy(rows)
    broken[0]["post_refresh_winner"] = "old"
    with pytest.raises(ValueError, match="no winner change"):
        validate_candidate_rows(broken)


def test_preflight_state_diff_must_touch_only_the_intended_target() -> None:
    rows = _inventory()
    rows[0]["preflight_state_diffs"]["changed_old"].append(
        {"target_id": "new", "field": "status"}
    )
    rows[1]["preflight_state_diffs"]["changed_old"].append(
        {"target_id": "new", "field": "status"}
    )
    with pytest.raises(ValueError, match="preflight state diff target mismatch"):
        validate_candidate_rows(rows)


def test_forms_hide_alternate_states_and_gold(tmp_path) -> None:
    rows = _inventory()
    writer_dir = tmp_path / "writers"
    manifest = build_writer_forms(rows, writer_dir)
    text = (writer_dir / "writer_W1.md").read_text()
    assert manifest["forms"]
    assert "s1_changed_state" not in text
    assert "post_refresh_winner" not in text
    annotation = build_annotator_form(rows[:2], "A1", tmp_path / "annotator.md")
    assert annotation["items"] == 2


def test_candidate_inventory_enforces_30_per_environment_and_frozen_order() -> None:
    incomplete = _inventory()[:-2]
    with pytest.raises(ValueError, match="exactly 30 candidate pairs"):
        validate_candidate_rows(incomplete)
    duplicated_order = _inventory()
    for row in duplicated_order:
        if row["environment"] == "AgentDojo" and row["candidate_order"] == 29:
            row["candidate_order"] = 28
    with pytest.raises(ValueError, match="candidate_order"):
        validate_candidate_rows(duplicated_order)


def test_anonymous_inventory_rejects_private_sidecar_fields() -> None:
    rows = _inventory()
    rows[0]["email_address"] = "redacted-participant-contact"
    with pytest.raises(ValueError, match="private field leaked"):
        validate_candidate_rows(rows)


def test_human_provenance_gate_cannot_be_bypassed() -> None:
    provenance = _human_provenance()
    validate_human_provenance(provenance, "a" * 64)
    provenance["annotators"]["A1"]["saw_model_outputs_before_lock"] = True
    with pytest.raises(ValueError, match="annotator independence gate"):
        validate_human_provenance(provenance, "a" * 64)
    provenance = _human_provenance()
    provenance["status"] = "complete"
    with pytest.raises(ValueError, match="not complete and locked"):
        validate_human_provenance(provenance, "a" * 64)


def test_execution_summary_is_itt_and_derives_controller_metrics() -> None:
    frozen = _frozen_rows()
    results = _executions(frozen)
    failed = next(
        row
        for row in results
        if row["environment"] == "AgentDojo"
        and row["model"] == "qwen"
        and row["controller"] == "ordinary_full_history"
        and row["row_id"].endswith("changed_preserve")
    )
    failed.update(
        execution_status="parse_failure",
        proposed_target_id=None,
        mutated_target_id=None,
        tool_result=None,
        final_state_diff=[],
    )
    summaries = summarize_executed_results(frozen, results)
    summary = next(
        row
        for row in summaries
        if row["environment"] == "AgentDojo"
        and row["model"] == "qwen"
        and row["controller"] == "ordinary_full_history"
    )
    assert len(summaries) == 36
    assert summary["rows"] == 60
    assert summary["e2e_numerator"] == 59
    assert summary["pairacc_numerator"] == 19
    assert summary["api_or_parse_failures"] == 1
    assert summary["calls"] == 60


def test_execution_summary_rejects_incomplete_matrix() -> None:
    frozen = _frozen_rows()
    results = _executions(frozen)
    with pytest.raises(ValueError, match="cover frozen matrix"):
        summarize_executed_results(frozen, results[:-1])


def test_execution_summary_rejects_trace_and_state_diff_inconsistency() -> None:
    frozen = _frozen_rows()
    results = _executions(frozen)
    results[0]["tool_trace"] = list(reversed(results[0]["tool_trace"]))
    with pytest.raises(ValueError, match="out of order"):
        summarize_executed_results(frozen, results)
    results = _executions(frozen)
    results[0]["final_state_diff"].append(
        {"target_id": "collateral", "operation": "update"}
    )
    with pytest.raises(ValueError, match="collateral_change_count"):
        summarize_executed_results(frozen, results)


def test_rule_star_is_scored_separately_on_exact_frozen_rows() -> None:
    frozen = _frozen_rows()
    results = [
        {
            "row_id": task["row_id"],
            "rule_source_sha256": "b" * 64,
            "execution_status": "success",
            "predicted_target_id": task["post_refresh_target"],
            "mutated_target_id": task["post_refresh_target"],
            "final_state_diff": [
                {"target_id": task["post_refresh_target"], "operation": "update"}
            ],
            "collateral_change_count": 0,
        }
        for task in frozen
    ]
    report = summarize_rule_star(frozen, results)
    assert "excluded from frozen controller selection" in report["evidence_role"]
    assert all(item["pairacc"] == 1.0 for item in report["datasets"].values())
    with pytest.raises(ValueError, match="exactly cover"):
        summarize_rule_star(frozen, results[:-1])
