from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from .event_graph_controller import (
    GateResult,
    ReferentialCapability,
    SelectorAST,
    VersionedEntityStore,
    execute_selector,
)
from .reference_lifecycle import INVALID


_BINDING_NAME = re.compile(r"^r_[a-z][a-z0-9_]*@[0-9]+$")
_EPOCH_NAME = re.compile(r"^S([0-9]+)$")
_ROLES = {"action_target", "monitoring_reference"}


@dataclass(frozen=True)
class RssaBinding:
    name: str
    role: str
    epoch: str


@dataclass(frozen=True)
class RssaAct:
    target_from: str


@dataclass(frozen=True)
class RssaProgram:
    refresh_count: int
    bindings: tuple[RssaBinding, ...]
    act: RssaAct


@dataclass(frozen=True)
class RssaHandle:
    name: str
    target_id: str
    role: str
    producer_binding: str
    binding_epoch: str
    action_scope: tuple[str, ...]
    action_preconditions: tuple[tuple[str, Any], ...]
    expected_version: int | None = None


def _exact_keys(obj: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(obj) != expected:
        raise ValueError(f"{label} must contain exactly {sorted(expected)}")


def parse_rssa_program(obj: Mapping[str, Any]) -> RssaProgram:
    if not isinstance(obj, Mapping):
        raise ValueError("R-SSA output must be a JSON object")
    _exact_keys(obj, {"refresh_count", "bindings", "act"}, "program")
    raw_bindings = obj["bindings"]
    raw_act = obj["act"]
    if not isinstance(raw_bindings, list):
        raise ValueError("bindings must be an array")
    if not isinstance(raw_act, Mapping):
        raise ValueError("act must be an object")
    bindings: list[RssaBinding] = []
    for raw in raw_bindings:
        if not isinstance(raw, Mapping):
            raise ValueError("each binding must be an object")
        _exact_keys(raw, {"name", "role", "epoch"}, "binding")
        bindings.append(RssaBinding(
            name=str(raw["name"]),
            role=str(raw["role"]),
            epoch=str(raw["epoch"]),
        ))
    _exact_keys(raw_act, {"target_from"}, "act")
    program = RssaProgram(
        refresh_count=obj["refresh_count"],
        bindings=tuple(bindings),
        act=RssaAct(target_from=str(raw_act["target_from"])),
    )
    validate_rssa_program(program)
    return program


def rssa_program_to_dict(program: RssaProgram) -> dict[str, Any]:
    return {
        "refresh_count": program.refresh_count,
        "bindings": [
            {"name": binding.name, "role": binding.role, "epoch": binding.epoch}
            for binding in program.bindings
        ],
        "act": {"target_from": program.act.target_from},
    }


def validate_rssa_program(program: RssaProgram) -> None:
    if (
        isinstance(program.refresh_count, bool)
        or not isinstance(program.refresh_count, int)
        or program.refresh_count < 1
    ):
        raise ValueError("refresh_count must be an integer of at least one")
    if not program.bindings:
        raise ValueError("program requires at least one binding")
    names = [binding.name for binding in program.bindings]
    if len(names) != len(set(names)):
        raise ValueError("binding versions must have a single producer")
    for binding in program.bindings:
        if not _BINDING_NAME.fullmatch(binding.name):
            raise ValueError(f"invalid versioned binding name: {binding.name}")
        if binding.role not in _ROLES:
            raise ValueError(f"invalid referential role: {binding.role}")
        match = _EPOCH_NAME.fullmatch(binding.epoch)
        if match is None or int(match.group(1)) > program.refresh_count:
            raise ValueError(f"binding epoch is outside the world trace: {binding.epoch}")
    action_bindings = [binding for binding in program.bindings if binding.role == "action_target"]
    if len(action_bindings) != 1:
        raise ValueError("program must have exactly one action_target binding")
    if program.act.target_from != action_bindings[0].name:
        raise ValueError("ACT.target_from must reference the action_target producer")


def compile_oracle_rssa(task: Mapping[str, Any]) -> RssaProgram:
    refresh_count = 2 if "final_state" in task else 1
    action_epoch = "S0" if task["binding"] == "anchored" else f"S{refresh_count}"
    bindings = [RssaBinding("r_action@0", "action_target", action_epoch)]
    if refresh_count == 2:
        bindings.append(RssaBinding("r_monitor@0", "monitoring_reference", "S1"))
        bindings.sort(key=lambda item: (int(item.epoch[1:]), item.role, item.name))
    program = RssaProgram(refresh_count, tuple(bindings), RssaAct("r_action@0"))
    validate_rssa_program(program)
    return program


def state_at_epoch(task: Mapping[str, Any], epoch: str) -> list[dict[str, Any]]:
    match = _EPOCH_NAME.fullmatch(epoch)
    if match is None:
        raise ValueError(f"invalid epoch: {epoch}")
    index = int(match.group(1))
    refresh_count = 2 if "final_state" in task else 1
    if index < 0 or index > refresh_count:
        raise ValueError(f"epoch {epoch} is outside task trace")
    if index == 0:
        return task["initial_state"]
    if refresh_count == 1:
        return task["refreshed_state"]
    if index == 1:
        return task["intermediate_state"]
    return task["final_state"]


def ground_with_selector(
    task: Mapping[str, Any], program: RssaProgram, selector: SelectorAST
) -> dict[str, str]:
    validate_rssa_program(program)
    return {
        binding.name: execute_selector(selector, state_at_epoch(task, binding.epoch))
        for binding in program.bindings
    }


def issue_rssa_handles(
    task: Mapping[str, Any],
    program: RssaProgram,
    grounded_targets: Mapping[str, str],
    expected_versions: Mapping[str, int | None] | None = None,
) -> dict[str, RssaHandle]:
    validate_rssa_program(program)
    if set(grounded_targets) != {binding.name for binding in program.bindings}:
        raise ValueError("grounded targets must match the program binding inventory")
    versions = expected_versions or {}
    preconditions = tuple(sorted(task.get("action_schema", {}).get("preconditions", {}).items()))
    handles: dict[str, RssaHandle] = {}
    for binding in program.bindings:
        handles[binding.name] = RssaHandle(
            name=binding.name,
            target_id=grounded_targets[binding.name],
            role=binding.role,
            producer_binding=binding.name,
            binding_epoch=binding.epoch,
            action_scope=(task["action"],) if binding.role == "action_target" else (),
            action_preconditions=preconditions if binding.role == "action_target" else (),
            expected_version=versions.get(binding.name),
        )
    return handles


def _action_binding(program: RssaProgram) -> RssaBinding:
    validate_rssa_program(program)
    return next(binding for binding in program.bindings if binding.name == program.act.target_from)


def execute_rssa_enforced_on_store(
    program: RssaProgram,
    handles: Mapping[str, RssaHandle],
    action: str,
    store: VersionedEntityStore,
) -> GateResult:
    binding = _action_binding(program)
    handle = handles.get(binding.name)
    if handle is None:
        return GateResult("missing_handle")
    if handle.role != "action_target" or handle.role != binding.role:
        return GateResult("role_mismatch")
    if handle.producer_binding != binding.name or handle.name != binding.name:
        return GateResult("source_mismatch")
    if handle.binding_epoch != binding.epoch:
        return GateResult("epoch_mismatch")
    if action not in handle.action_scope:
        return GateResult("scope_mismatch")
    capability = ReferentialCapability(
        target_id=handle.target_id,
        action=action,
        source_event=handle.producer_binding,
        binding_epoch=handle.binding_epoch,
        action_preconditions=handle.action_preconditions,
        expected_version=handle.expected_version,
    )
    return store.atomic_write(capability, action)


def execute_rssa_free_on_store(
    task: Mapping[str, Any], proposed_target: str, store: VersionedEntityStore
) -> GateResult:
    if proposed_target == INVALID:
        return GateResult("actor_rejected")
    capability = ReferentialCapability(
        target_id=proposed_target,
        action=task["action"],
        source_event="free_actor",
        binding_epoch=f"S{2 if 'final_state' in task else 1}",
        action_preconditions=tuple(
            sorted(task.get("action_schema", {}).get("preconditions", {}).items())
        ),
    )
    return store.atomic_write(capability, task["action"])


def execute_rssa_enforced(
    task: Mapping[str, Any], program: RssaProgram, handles: Mapping[str, RssaHandle]
) -> str:
    final_state = task.get("final_state", task["refreshed_state"])
    result = execute_rssa_enforced_on_store(
        program, handles, task["action"], VersionedEntityStore(final_state)
    )
    return result.written_id if result.status == "written" else INVALID


def execute_rssa_free(task: Mapping[str, Any], proposed_target: str) -> str:
    final_state = task.get("final_state", task["refreshed_state"])
    result = execute_rssa_free_on_store(task, proposed_target, VersionedEntityStore(final_state))
    return result.written_id if result.status == "written" else INVALID


def compiler_payload(task: Mapping[str, Any]) -> dict[str, str]:
    return {"instruction": task["instruction"], "action": task["action"]}
