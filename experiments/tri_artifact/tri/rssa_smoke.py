from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .event_graph_controller import VersionedEntityStore, compile_oracle_selector
from .reference_lifecycle import INVALID
from .referential_ssa import (
    RssaBinding,
    RssaProgram,
    compile_oracle_rssa,
    compiler_payload,
    execute_rssa_enforced_on_store,
    execute_rssa_free_on_store,
    ground_with_selector,
    issue_rssa_handles,
    parse_rssa_program,
    rssa_program_to_dict,
    state_at_epoch,
)
from .run_models import format_exception, normalize_target


COMPILER_SYSTEM = """Compile the instruction into a minimal epoch-scoped referential SSA program. Return JSON only,
with exactly this schema:
{"refresh_count":integer,"bindings":[{"name":"r_action@0 or r_monitor@N","role":"action_target or monitoring_reference","epoch":"S0, S1, ..."}],"act":{"target_from":"one binding name"}}

S0 is the world before any refresh; Si is the world after exactly i completed refreshes. Count
every requested refresh. Create one action_target binding at the epoch where the instruction
authorizes selection of the mutation target. Create a separate monitoring_reference binding for
each explicitly requested monitoring-only observation. Every binding name is single-assignment
and unique. ACT.target_from must name the action_target binding, never a monitoring binding. Do
not output an entity ID, selector, state contents, validity decision, explanation, or extra field."""


GROUNDER_SYSTEM = """Resolve only the requested referential binding against the single supplied world epoch. Return
JSON only as {"target_id":"one exact entity ID"}. Follow the instruction's selector and the
requested role. Do not reason over an unavailable earlier or later state, do not change the
binding epoch, and do not return prose or an alternative entity for an invalid bound target."""


ACTOR_SYSTEM = """Propose the final mutation target using the instruction, compiled referential program, resolved
bindings, final state, and action preconditions. Return JSON only as {"target_id":"one exact ID
or INVALID_BOUND_ENTITY"}. Monitoring references are not action targets. If the authorized action
target is missing or violates an action precondition, return INVALID_BOUND_ENTITY."""


FORBIDDEN_REQUEST_FIELDS = {
    "binding", "correct_target", "pre_refresh_target", "post_refresh_target",
    "new_leader", "selector", "phenomenon", "style", "template_id", "update",
    "bound_entity_present_after_refresh", "bound_entity_actionable_after_refresh",
    "distractor_referent", "smoke_source", "source_task_id",
}


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def strict_json_object(text: str) -> dict[str, Any]:
    try:
        obj = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"strict JSON parse failed: {exc.msg}") from exc
    if not isinstance(obj, dict):
        raise ValueError("response must be one JSON object")
    return obj


def _binding_dict(binding: RssaBinding) -> dict[str, str]:
    return {"name": binding.name, "role": binding.role, "epoch": binding.epoch}


def grounder_payload(task: Mapping[str, Any], binding: RssaBinding) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "action": task["action"],
        "binding_request": _binding_dict(binding),
        "world_epoch_state": state_at_epoch(task, binding.epoch),
    }


def actor_payload(
    task: Mapping[str, Any], program: RssaProgram, grounded: Mapping[str, str]
) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "action": task["action"],
        "action_schema": task.get("action_schema", {}),
        "final_state": task.get("final_state", task["refreshed_state"]),
        "compiled_program": rssa_program_to_dict(program),
        "resolved_bindings": [
            {**_binding_dict(binding), "target_id": grounded[binding.name]}
            for binding in program.bindings
        ],
    }


def request_field_leaks(obj: Any) -> list[str]:
    leaks: set[str] = set()
    if isinstance(obj, Mapping):
        leaks.update(str(key) for key in obj if key in FORBIDDEN_REQUEST_FIELDS)
        for value in obj.values():
            leaks.update(request_field_leaks(value))
    elif isinstance(obj, list):
        for value in obj:
            leaks.update(request_field_leaks(value))
    return sorted(leaks)


def _target_valid(task: Mapping[str, Any], target: str | None) -> bool:
    if target in {None, INVALID}:
        return False
    final_state = task.get("final_state", task["refreshed_state"])
    row = next((item for item in final_state if item.get("id") == target), None)
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    return row is not None and all(row.get(key) == value for key, value in preconditions.items())


def _outcome(task: Mapping[str, Any], target: str | None) -> dict[str, Any]:
    correct = task["correct_target"]
    return {
        "target": target,
        "success": target == correct,
        "wrong_write": bool(target not in {None, INVALID, correct} and _target_valid(task, target)),
        "false_block": bool(target == INVALID and correct != INVALID),
        "invalid_attempt": bool(target not in {None, INVALID} and not _target_valid(task, target)),
    }


def score_program_structure(task: Mapping[str, Any], program: RssaProgram) -> dict[str, bool]:
    oracle = compile_oracle_rssa(task)
    inventory = sorted((item.role, item.epoch) for item in program.bindings)
    oracle_inventory = sorted((item.role, item.epoch) for item in oracle.bindings)
    roles = sorted(item.role for item in program.bindings)
    oracle_roles = sorted(item.role for item in oracle.bindings)
    action_binding = next(item for item in program.bindings if item.role == "action_target")
    oracle_action = next(item for item in oracle.bindings if item.role == "action_target")
    return {
        "refresh_count_correct": program.refresh_count == oracle.refresh_count,
        "action_binding_epoch_correct": action_binding.epoch == oracle_action.epoch,
        "binding_inventory_correct": inventory == oracle_inventory,
        "producer_edge_correct": program.act.target_from == action_binding.name,
        "role_correct": roles == oracle_roles,
    }


def _call(client: Any, system: str, payload: dict[str, Any]) -> str:
    leaks = request_field_leaks(payload)
    if leaks:
        raise ValueError(f"forbidden request fields: {leaks}")
    return client.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ], 0.0)


def run_rssa_task(
    compiler_client: Any,
    grounder_client: Any,
    actor_client: Any,
    task: dict[str, Any],
) -> dict[str, Any]:
    clients = (compiler_client, grounder_client, actor_client)
    before_attempts = [getattr(client, "request_attempts", 0) for client in clients]
    before_usage = [len(getattr(client, "usage_records", [])) for client in clients]
    errors: list[str] = []
    raw_compiler = ""
    raw_grounding: dict[str, str] = {}
    raw_actor = ""
    compiled_obj: dict[str, Any] | None = None
    actor_obj: dict[str, Any] | None = None
    program: RssaProgram | None = None
    grounded: dict[str, str] = {}
    schema_valid = False
    scores = {
        "refresh_count_correct": False,
        "action_binding_epoch_correct": False,
        "binding_inventory_correct": False,
        "producer_edge_correct": False,
        "role_correct": False,
    }
    grounding_complete = False
    grounding_correct_for_program = False
    action_grounding_authorized_correct = False
    actor_target: str | None = None
    free_target: str | None = None
    enforced_target: str | None = None
    free_gate_status: str | None = None
    enforced_gate_status: str | None = None
    pipeline_complete = False

    try:
        payload = compiler_payload(task)
        raw_compiler = _call(compiler_client, COMPILER_SYSTEM, payload)
        compiled_obj = strict_json_object(raw_compiler)
        program = parse_rssa_program(compiled_obj)
        schema_valid = True
        scores = score_program_structure(task, program)
    except Exception as exc:
        errors.append(f"compiler: {format_exception(exc)}")

    if program is not None:
        for binding in program.bindings:
            try:
                payload = grounder_payload(task, binding)
                raw = _call(grounder_client, GROUNDER_SYSTEM, payload)
                raw_grounding[binding.name] = raw
                obj = strict_json_object(raw)
                if set(obj) != {"target_id"}:
                    raise ValueError("grounder output must contain exactly target_id")
                target = normalize_target(obj["target_id"])
                if target is None:
                    raise ValueError("grounder target_id cannot be null")
                grounded[binding.name] = target
            except Exception as exc:
                errors.append(f"grounder[{binding.name}]: {format_exception(exc)}")
        grounding_complete = len(grounded) == len(program.bindings)

    handles = None
    if program is not None and grounding_complete:
        selector = compile_oracle_selector(task)
        oracle_for_program = ground_with_selector(task, program, selector)
        grounding_correct_for_program = grounded == oracle_for_program
        action_name = program.act.target_from
        expected_authorized = (
            task["pre_refresh_target"]
            if task["binding"] == "anchored" else task["post_refresh_target"]
        )
        action_grounding_authorized_correct = grounded[action_name] == expected_authorized
        handles = issue_rssa_handles(task, program, grounded)
        try:
            payload = actor_payload(task, program, grounded)
            raw_actor = _call(actor_client, ACTOR_SYSTEM, payload)
            actor_obj = strict_json_object(raw_actor)
            if set(actor_obj) != {"target_id"}:
                raise ValueError("actor output must contain exactly target_id")
            actor_target = normalize_target(actor_obj["target_id"])
            if actor_target is None:
                raise ValueError("actor target_id cannot be null")
            pipeline_complete = True
        except Exception as exc:
            errors.append(f"actor: {format_exception(exc)}")

        final_state = task.get("final_state", task["refreshed_state"])
        enforced_result = execute_rssa_enforced_on_store(
            program, handles, task["action"], VersionedEntityStore(final_state)
        )
        enforced_gate_status = enforced_result.status
        enforced_target = (
            enforced_result.written_id if enforced_result.status == "written" else INVALID
        )
        if actor_target is not None:
            free_result = execute_rssa_free_on_store(
                task, actor_target, VersionedEntityStore(final_state)
            )
            free_gate_status = free_result.status
            free_target = free_result.written_id if free_result.status == "written" else INVALID

    attempts = [
        getattr(client, "request_attempts", 0) - before
        for client, before in zip(clients, before_attempts)
    ]
    usage = [
        getattr(client, "usage_records", [])[before:]
        for client, before in zip(clients, before_usage)
    ]
    free_outcome = _outcome(task, free_target)
    enforced_outcome = _outcome(task, enforced_target)
    return {
        "task_id": task["id"],
        "smoke_index": task["smoke_index"],
        "smoke_source": task["smoke_source"],
        "binding": task["binding"],
        "update": task["update"],
        "schema_valid": schema_valid,
        **scores,
        "grounding_complete": grounding_complete,
        "grounding_correct_for_program": grounding_correct_for_program,
        "action_grounding_authorized_correct": action_grounding_authorized_correct,
        "pipeline_complete": pipeline_complete,
        "compiled_ir": compiled_obj,
        "grounded_targets": grounded,
        "actor_output": actor_obj,
        "raw_compiler_output": raw_compiler,
        "raw_grounder_outputs": raw_grounding,
        "raw_actor_output": raw_actor,
        "free_gate_status": free_gate_status,
        "enforced_gate_status": enforced_gate_status,
        "free": free_outcome,
        "enforced": enforced_outcome,
        "actor_handle_disagreement": bool(
            actor_target is not None
            and handles is not None
            and actor_target != handles[program.act.target_from].target_id
        ),
        "errors": errors,
        "request_attempts": {
            "compiler": attempts[0], "grounder": attempts[1], "actor": attempts[2]
        },
        "usage": {"compiler": usage[0], "grounder": usage[1], "actor": usage[2]},
        "system_prompt_sha256": {
            "compiler": hashlib.sha256(COMPILER_SYSTEM.encode()).hexdigest(),
            "grounder": hashlib.sha256(GROUNDER_SYSTEM.encode()).hexdigest(),
            "actor": hashlib.sha256(ACTOR_SYSTEM.encode()).hexdigest(),
        },
    }
