from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from tri.event_graph_controller import VersionedEntityStore, compile_oracle_selector
from tri.reference_lifecycle import INVALID
from tri.referential_ssa import (
    RssaAct,
    RssaBinding,
    RssaProgram,
    compile_oracle_rssa,
    compiler_payload,
    execute_rssa_enforced,
    execute_rssa_enforced_on_store,
    execute_rssa_free,
    ground_with_selector,
    issue_rssa_handles,
    parse_rssa_program,
    state_at_epoch,
    validate_rssa_program,
)


DATA = Path(__file__).resolve().parents[1] / "data"


def _load(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (DATA / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _smoke() -> list[dict]:
    return _load("temporal_referent_method_upgrade_smoke_v1.jsonl")


def _handles(task: dict):
    program = compile_oracle_rssa(task)
    grounded = ground_with_selector(task, program, compile_oracle_selector(task))
    return program, issue_rssa_handles(task, program, grounded)


def test_oracle_rssa_covers_frozen_20_without_private_compiler_inputs() -> None:
    rows = _smoke()
    assert len(rows) == 20
    assert [row["smoke_index"] for row in rows] == list(range(1, 21))
    for task in rows:
        program, handles = _handles(task)
        expected_epoch = "S0" if task["binding"] == "anchored" else (
            "S2" if "final_state" in task else "S1"
        )
        assert next(
            binding.epoch for binding in program.bindings if binding.role == "action_target"
        ) == expected_epoch
        assert execute_rssa_enforced(task, program, handles) == task["correct_target"]
        assert compiler_payload(task) == {
            "instruction": task["instruction"], "action": task["action"]
        }


def test_wrong_producer_edge_is_rejected() -> None:
    program = RssaProgram(
        2,
        (
            RssaBinding("r_action@0", "action_target", "S0"),
            RssaBinding("r_monitor@0", "monitoring_reference", "S1"),
        ),
        RssaAct("r_monitor@0"),
    )
    with pytest.raises(ValueError, match="action_target producer"):
        validate_rssa_program(program)


def test_monitoring_and_action_role_swap_is_rejected() -> None:
    obj = {
        "refresh_count": 1,
        "bindings": [{"name": "r_monitor@0", "role": "monitoring_reference", "epoch": "S0"}],
        "act": {"target_from": "r_monitor@0"},
    }
    with pytest.raises(ValueError, match="exactly one action_target"):
        parse_rssa_program(obj)


def test_duplicate_version_cannot_overwrite_a_handle() -> None:
    obj = {
        "refresh_count": 1,
        "bindings": [
            {"name": "r_action@0", "role": "action_target", "epoch": "S0"},
            {"name": "r_action@0", "role": "monitoring_reference", "epoch": "S1"},
        ],
        "act": {"target_from": "r_action@0"},
    }
    with pytest.raises(ValueError, match="single producer"):
        parse_rssa_program(obj)

    task = next(row for row in _smoke() if row["binding"] == "anchored")
    _, handles = _handles(task)
    with pytest.raises(FrozenInstanceError):
        handles["r_action@0"].target_id = task["post_refresh_target"]


def test_stale_referent_version_is_blocked() -> None:
    task = next(
        row for row in _smoke()
        if row["binding"] == "anchored" and row["correct_target"] != INVALID
    )
    program, handles = _handles(task)
    store = VersionedEntityStore(task["refreshed_state"])
    target = handles["r_action@0"].target_id
    handles = {
        **handles,
        "r_action@0": replace(handles["r_action@0"], expected_version=store.version(target)),
    }
    store.update(target, note="concurrent change")
    result = execute_rssa_enforced_on_store(program, handles, task["action"], store)
    assert result.status == "stale_version"
    assert store.writes == []


def test_action_scope_mismatch_is_blocked() -> None:
    task = next(row for row in _smoke() if row["binding"] == "anchored")
    program, handles = _handles(task)
    store = VersionedEntityStore(task["refreshed_state"])
    result = execute_rssa_enforced_on_store(program, handles, "delete", store)
    assert result.status == "scope_mismatch"
    assert store.writes == []


def test_missing_and_invalid_identity_are_not_rebound() -> None:
    present = next(
        row for row in _smoke()
        if row["binding"] == "anchored" and row["correct_target"] != INVALID
    )
    program, handles = _handles(present)
    target = handles["r_action@0"].target_id

    deleted = VersionedEntityStore(present["refreshed_state"])
    deleted.delete(target)
    assert execute_rssa_enforced_on_store(
        program, handles, present["action"], deleted
    ).status == "missing_target"

    invalid = VersionedEntityStore(present["refreshed_state"])
    field, required = handles["r_action@0"].action_preconditions[0]
    invalid.update(target, **{field: not required if isinstance(required, bool) else "invalid"})
    assert execute_rssa_enforced_on_store(
        program, handles, present["action"], invalid
    ).status == "invalid_target"
    assert deleted.writes == []
    assert invalid.writes == []


def test_legal_unrelated_world_update_does_not_false_block() -> None:
    task = next(
        row for row in _smoke()
        if row["binding"] == "anchored" and row["correct_target"] != INVALID
    )
    program, handles = _handles(task)
    store = VersionedEntityStore(task["refreshed_state"])
    target = handles["r_action@0"].target_id
    other = next(entity["id"] for entity in task["refreshed_state"] if entity["id"] != target)
    store.update(other, note="unrelated")
    result = execute_rssa_enforced_on_store(program, handles, task["action"], store)
    assert result.status == "written"
    assert result.written_id == target


def test_authorized_reselection_creates_a_new_final_epoch_binding() -> None:
    task = next(
        row for row in _smoke()
        if row["binding"] == "dynamic" and "final_state" not in row
    )
    program, handles = _handles(task)
    binding = next(item for item in program.bindings if item.role == "action_target")
    assert binding.name == "r_action@0"
    assert binding.epoch == "S1"
    assert handles[binding.name].target_id == task["post_refresh_target"]
    assert execute_rssa_enforced(task, program, handles) == task["correct_target"]


def test_multi_refresh_dynamic_binding_occurs_after_final_refresh() -> None:
    task = next(
        row for row in _smoke()
        if row["binding"] == "dynamic" and "final_state" in row
    )
    program, handles = _handles(task)
    assert program.refresh_count == 2
    assert state_at_epoch(task, "S1") == task["intermediate_state"]
    assert state_at_epoch(task, "S2") == task["final_state"]
    assert {
        (binding.role, binding.epoch) for binding in program.bindings
    } == {("monitoring_reference", "S1"), ("action_target", "S2")}
    assert execute_rssa_enforced(task, program, handles) == task["correct_target"]


def test_free_vs_enforced_isolates_unauthorized_substitution() -> None:
    task = next(
        row for row in _smoke()
        if row["binding"] == "anchored"
        and row["correct_target"] != INVALID
        and row["pre_refresh_target"] != row["post_refresh_target"]
    )
    program, handles = _handles(task)
    actor_proposal = task["post_refresh_target"]
    assert execute_rssa_free(task, actor_proposal) == actor_proposal
    assert execute_rssa_enforced(task, program, handles) == task["pre_refresh_target"]


def test_parser_rejects_extra_fields_and_out_of_trace_epoch() -> None:
    with pytest.raises(ValueError, match="exactly"):
        parse_rssa_program({
            "refresh_count": 1,
            "bindings": [{
                "name": "r_action@0", "role": "action_target", "epoch": "S0", "target_id": "X"
            }],
            "act": {"target_from": "r_action@0"},
        })
    with pytest.raises(ValueError, match="outside"):
        parse_rssa_program({
            "refresh_count": 1,
            "bindings": [{"name": "r_action@0", "role": "action_target", "epoch": "S2"}],
            "act": {"target_from": "r_action@0"},
        })
