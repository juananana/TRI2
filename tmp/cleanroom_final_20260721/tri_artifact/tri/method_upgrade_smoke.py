from __future__ import annotations

import hashlib
import json
from typing import Any

from .event_graph_controller import (
    Event,
    EventGraph,
    SelectorAST,
    derive_reference_mode,
    execute_selector,
    validate_event_graph,
)
from .reference_lifecycle import INVALID
from .run_models import format_exception, normalize_target, parse_json


METHODS = ("exact_cta", "event_graph", "event_graph_selector")


EXACT_CTA_SYSTEM = """Compile the user's instruction before any refresh occurs. Separate reference identity from action validity. Return JSON only with exactly these fields:
{"reference_mode":"preserve or reevaluate","selector":"natural-language selector","bound_target_id":"initial-state ID or null","invalidity_policy":"reject"}
Use preserve when the instruction selects or identifies the action target before refresh, including implicit wording such as find/check/pick before refresh. Use reevaluate only when target selection is deferred until after the final refresh. For preserve, resolve and store the exact initial-state ID. For reevaluate, bound_target_id must be null. A monitoring reference never replaces the action target."""


EVENT_GRAPH_SYSTEM = """Compile the user's instruction into an ordered event graph before any refresh occurs. Return JSON only:
{"events":[{"id":"E1","type":"SELECT|REFRESH|OBSERVE|ACT","state":"initial|intermediate|final|null","role":"action_target|monitoring_reference|action|null","referent":"event ID or null","target_id":"initial-state ID or null"}],"edges":[["E1","E2"]]}
ACT must reference exactly one SELECT whose role is action_target. If the action target is selected before refresh, that SELECT uses state=initial and its concrete target_id. If selection is deferred until after the last refresh, the action-target SELECT uses state=final and target_id=null. Represent monitoring observations separately; they must not replace the action target. Use forward DAG edges and no extra fields."""


EVENT_GRAPH_SELECTOR_SYSTEM = """Compile the user's instruction into an ordered event graph plus an executable selector before any refresh occurs. Return JSON only:
{"events":[{"id":"E1","type":"SELECT|REFRESH|OBSERVE|ACT","state":"initial|intermediate|final|null","role":"action_target|monitoring_reference|action|null","referent":"event ID or null","target_id":"initial-state ID or null"}],"edges":[["E1","E2"]],"selector_ast":{"filters":[{"field":"field_name","op":"eq","value":"literal"}],"order_by":{"field":"field_name","direction":"asc|desc"},"limit":1}}
ACT must reference exactly one action_target SELECT. A pre-refresh action target uses state=initial; a target deferred until after the last refresh uses state=final. For this method target_id must always be null because the controller executes selector_ast at the SELECT event and derives the bound ID itself. Monitoring observations are separate. The selector AST may omit order_by only for a selector uniquely defined by equality filters. Translate lowest/earliest/soonest to asc and highest/largest/latest/oldest to desc. Filters must include action-relevant eligibility conditions visible in the selector. Use only fields present in initial_state."""


EVENT_GRAPH_ACTOR_SYSTEM = """Execute the final action using the compiled event graph and the final refreshed state. ACT references the action_target SELECT. The SELECT occurs in the final state, so execute the original natural-language selector on final_state and return JSON only: {"target_id":"one exact ID"}. Respect every action precondition and never use a monitoring_reference as the action target."""


def compiler_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "action": task["action"],
        "action_schema": task.get("action_schema", {}),
        "future_state_epochs": (
            ["intermediate", "final"] if "final_state" in task else ["final"]
        ),
        "constraint": "Future state contents are unavailable during compilation.",
    }


def _parse_graph(obj: dict[str, Any]) -> EventGraph:
    raw_events = obj.get("events")
    raw_edges = obj.get("edges")
    if not isinstance(raw_events, list) or not isinstance(raw_edges, list):
        raise ValueError("event graph requires events and edges arrays")
    events = tuple(Event(
        event_id=str(raw["id"]),
        event_type=str(raw["type"]),
        state=raw.get("state"),
        role=raw.get("role"),
        referent=raw.get("referent"),
        target_id=normalize_target(raw.get("target_id")),
    ) for raw in raw_events)
    edges = tuple((str(edge[0]), str(edge[1])) for edge in raw_edges)
    graph = EventGraph(events, edges)
    validate_event_graph(graph)
    return graph


def _parse_selector(obj: dict[str, Any]) -> SelectorAST:
    raw = obj.get("selector_ast")
    if not isinstance(raw, dict) or raw.get("limit") != 1:
        raise ValueError("selector_ast must be an object with limit=1")
    filters: list[tuple[str, Any]] = []
    for item in raw.get("filters", []):
        if set(item) != {"field", "op", "value"} or item["op"] != "eq":
            raise ValueError("selector filters only support field/op=eq/value")
        filters.append((str(item["field"]), item["value"]))
    order = raw.get("order_by")
    if order is None:
        order_field = direction = None
    else:
        if set(order) != {"field", "direction"} or order["direction"] not in {"asc", "desc"}:
            raise ValueError("order_by requires field and asc/desc direction")
        order_field = str(order["field"])
        direction = str(order["direction"])
    return SelectorAST(tuple(filters), order_field, direction)


def _source_event(graph: EventGraph) -> Event:
    action = next(event for event in graph.events if event.event_type == "ACT")
    return next(event for event in graph.events if event.event_id == action.referent)


def _target_valid(task: dict[str, Any], target: str | None) -> bool:
    final = task.get("final_state", task["refreshed_state"])
    entity = next((row for row in final if row.get("id") == target), None)
    conditions = task.get("action_schema", {}).get("preconditions", {})
    return entity is not None and all(entity.get(key) == value for key, value in conditions.items())


def score_compilation(method: str, task: dict[str, Any], obj: dict[str, Any]) -> dict[str, Any]:
    expected_mode = "preserve" if task["binding"] == "anchored" else "reevaluate"
    if method == "exact_cta":
        required = {"reference_mode", "selector", "bound_target_id", "invalidity_policy"}
        if set(obj) != required:
            raise ValueError("Exact CTA output has wrong fields")
        mode = obj["reference_mode"]
        bound_id = normalize_target(obj.get("bound_target_id"))
        schema_valid = (
            mode in {"preserve", "reevaluate"}
            and obj["invalidity_policy"] == "reject"
            and ((mode == "preserve" and bound_id is not None) or (mode == "reevaluate" and bound_id is None))
        )
        return {
            "schema_valid": schema_valid,
            "mode_correct": mode == expected_mode,
            "bound_id_correct": (
                bound_id == task["pre_refresh_target"] if expected_mode == "preserve" else bound_id is None
            ),
            "selector_initial_correct": None,
            "selector_final_correct": None,
            "authorized_target_correct": None,
        }

    graph = _parse_graph(obj)
    source = _source_event(graph)
    mode = derive_reference_mode(graph)
    result: dict[str, Any] = {
        "schema_valid": True,
        "mode_correct": mode == expected_mode,
        "bound_id_correct": (
            source.target_id == task["pre_refresh_target"]
            if expected_mode == "preserve" else source.target_id is None
        ),
        "selector_initial_correct": None,
        "selector_final_correct": None,
        "authorized_target_correct": None,
    }
    if method == "event_graph_selector":
        selector = _parse_selector(obj)
        initial_target = execute_selector(selector, task["initial_state"])
        final_target = execute_selector(
            selector, task.get("final_state", task["refreshed_state"])
        )
        predicted = initial_target if mode == "preserve" else final_target
        if mode == "preserve" and not _target_valid(task, predicted):
            predicted = INVALID
        result.update({
            "schema_valid": all(
                event.target_id is None for event in graph.events if event.event_type == "SELECT"
            ),
            "bound_id_correct": (
                initial_target == task["pre_refresh_target"]
                if expected_mode == "preserve" else source.target_id is None
            ),
            "selector_initial_correct": initial_target == task["pre_refresh_target"],
            "selector_final_correct": final_target == task["post_refresh_target"],
            "authorized_target_correct": predicted == task["correct_target"],
        })
    return result


def _execution_outcome(task: dict[str, Any], predicted: str | None) -> dict[str, Any]:
    correct = task["correct_target"]
    valid = _target_valid(task, predicted)
    return {
        "predicted_target": predicted,
        "correct_target": correct,
        "success": predicted == correct,
        "wrong_write": bool(predicted not in {None, INVALID, correct} and valid),
        "false_block": bool(predicted == INVALID and correct != INVALID),
        "invalid_attempt": bool(predicted not in {None, INVALID} and not valid),
    }


def execute_compilation(
    client: Any,
    method: str,
    task: dict[str, Any],
    obj: dict[str, Any],
    temperature: float = 0.0,
) -> tuple[dict[str, Any], str | None, dict[str, Any] | None]:
    if method == "exact_cta":
        return _execution_outcome(task, None), None, None
    graph = _parse_graph(obj)
    source = _source_event(graph)
    mode = derive_reference_mode(graph)
    actor_raw: str | None = None
    actor_obj: dict[str, Any] | None = None
    if method == "event_graph_selector":
        selector = _parse_selector(obj)
        state = task["initial_state"] if source.state == "initial" else task.get(
            "final_state", task["refreshed_state"]
        )
        predicted = execute_selector(selector, state)
    elif mode == "preserve":
        predicted = source.target_id
    else:
        actor_raw = client.chat([
            {"role": "system", "content": EVENT_GRAPH_ACTOR_SYSTEM},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "event_graph": obj,
                "final_state": task.get("final_state", task["refreshed_state"]),
                "action_schema": task.get("action_schema", {}),
            }, ensure_ascii=False)},
        ], temperature)
        actor_obj = parse_json(actor_raw)
        predicted = normalize_target(actor_obj.get("target_id"))
    if mode == "preserve" and not _target_valid(task, predicted):
        predicted = INVALID
    return _execution_outcome(task, predicted), actor_raw, actor_obj


def compile_task(client: Any, method: str, task: dict[str, Any], temperature: float = 0.0) -> dict[str, Any]:
    systems = {
        "exact_cta": EXACT_CTA_SYSTEM,
        "event_graph": EVENT_GRAPH_SYSTEM,
        "event_graph_selector": EVENT_GRAPH_SELECTOR_SYSTEM,
    }
    if method not in systems:
        raise ValueError(f"unknown method: {method}")
    errors: list[str] = []
    raw = ""
    parsed: dict[str, Any] | None = None
    actor_raw: str | None = None
    actor_parsed: dict[str, Any] | None = None
    before_attempts = getattr(client, "request_attempts", 0)
    before_usage = len(getattr(client, "usage_records", []))
    payload = compiler_payload(task)
    try:
        raw = client.chat([
            {"role": "system", "content": systems[method]},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ], temperature)
        parsed = parse_json(raw)
        scores = score_compilation(method, task, parsed)
        execution, actor_raw, actor_parsed = execute_compilation(
            client, method, task, parsed, temperature
        )
    except Exception as exc:
        errors.append(format_exception(exc))
        scores = {
            "schema_valid": False, "mode_correct": False, "bound_id_correct": False,
            "selector_initial_correct": False if method == "event_graph_selector" else None,
            "selector_final_correct": False if method == "event_graph_selector" else None,
            "authorized_target_correct": False if method == "event_graph_selector" else None,
        }
        execution = _execution_outcome(task, None)
    usage = getattr(client, "usage_records", [])[before_usage:]
    return {
        "task_id": task["id"],
        "smoke_index": task.get("smoke_index"),
        "smoke_source": task.get("smoke_source"),
        "method": method,
        "binding": task["binding"],
        "phenomenon": task["phenomenon"],
        "update": task["update"],
        "raw_output": raw,
        "compiled_ir": parsed,
        "actor_raw_output": actor_raw,
        "actor_output": actor_parsed,
        "errors": errors,
        "request_attempts": getattr(client, "request_attempts", 0) - before_attempts,
        "usage": usage,
        "system_prompt_sha256": hashlib.sha256(systems[method].encode()).hexdigest(),
        "task_prompt_sha256": hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest(),
        **scores,
        **execution,
    }
