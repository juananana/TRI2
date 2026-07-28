from __future__ import annotations

from copy import deepcopy

import pytest

from tri.unified_environment_holdout import (
    ANNOTATORS,
    ENVIRONMENT_COMMITS,
    derive_execution_rows,
    build_annotator_form,
    build_writer_forms,
    select_clear_clusters,
    selection_maximizers,
    validate_candidate_rows,
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
            "writer_id": f"W{(index + (0 if mode == 'preserve' else 6)) % 12 + 1}",
            "reference_mode": mode,
            "instruction": instruction,
            "selector": "the new item",
            "action": "update",
            "action_schema": {"preconditions": {"actionable": True}},
            "s0_state": s0,
            "s1_changed_state": changed,
            "s1_stable_state": stable,
            "pre_refresh_winner": "old",
            "post_refresh_winner": "new",
            "writer_intent": mode if clear else "clarify",
            "adjudications": {annotator: mode for annotator in ANNOTATORS},
        })
    return rows


def test_candidate_validation_and_clear_gate_produce_120_rows() -> None:
    candidates = [row for environment in ENVIRONMENT_COMMITS for index in range(20) for row in _candidate(environment, index)]
    validate_candidate_rows(candidates)
    selected = select_clear_clusters(candidates)
    rows = derive_execution_rows(selected)
    assert len(selected) == 40
    assert len(rows) == 120
    assert {row["row_kind"] for row in rows} == {"changed_preserve", "changed_reevaluate", "stable_preserve"}


def test_clear_gate_rejects_insufficient_environment() -> None:
    candidates = [row for environment in ENVIRONMENT_COMMITS for index in range(20 if environment == "AgentDojo" else 19) for row in _candidate(environment, index)]
    validate_candidate_rows(candidates)
    with pytest.raises(RuntimeError, match="ToolSandbox"):
        select_clear_clusters(candidates)


def test_selection_keeps_ties_and_requires_two_strong_cells() -> None:
    rows = []
    for environment in ENVIRONMENT_COMMITS:
        for model in ("qwen", "glm"):
            rows.extend([
                {"environment": environment, "model": model, "controller": "e2e", "e2e": 1.0, "pairacc": 0.5, "wrong_writes": 2},
                {"environment": environment, "model": model, "controller": "pair", "e2e": 0.9, "pairacc": 1.0, "wrong_writes": 1},
            ])
    report = selection_maximizers(rows)
    assert len(report["cells"]) == 4
    assert report["promote_practical_selection"] is True


def test_changed_winner_is_required() -> None:
    rows = _candidate("AgentDojo", 0)
    broken = deepcopy(rows)
    broken[0]["post_refresh_winner"] = "old"
    with pytest.raises(ValueError, match="no winner change"):
        validate_candidate_rows(broken)


def test_forms_hide_alternate_states_and_gold(tmp_path) -> None:
    rows = _candidate("AgentDojo", 0)
    writer_dir = tmp_path / "writers"
    manifest = build_writer_forms(rows, writer_dir)
    text = (writer_dir / "writer_W1.md").read_text()
    assert manifest["forms"]
    assert "s1_changed_state" not in text
    assert "post_refresh_winner" not in text
    annotation = build_annotator_form(rows, "A1", tmp_path / "annotator.md")
    assert annotation["items"] == 2
