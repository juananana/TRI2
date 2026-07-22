from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INVALID = "INVALID_BOUND_ENTITY"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ReferentRecord:
    expression: str
    binding_time: str
    target: str | list[str] | None
    selector: str
    validity: dict[str, Any]
    provenance: str
    lifecycle_state: str


def _entity(items: list[dict[str, Any]], target_id: str) -> dict[str, Any] | None:
    return next((x for x in items if x.get("id") == target_id), None)


def _passes(item: dict[str, Any] | None, preconditions: dict[str, Any]) -> bool:
    if item is None:
        return False
    return all(item.get(k) == v for k, v in preconditions.items())


def target_valid(task: dict[str, Any], target_id: str) -> bool:
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    return _passes(_entity(task["refreshed_state"], target_id), preconditions)


def compile_oracle_record(task: dict[str, Any]) -> ReferentRecord:
    binding = task["binding"]
    if binding == "dynamic":
        binding_time = "post"
        target: str | list[str] | None = None
        state = "UNBOUND_DYNAMIC"
    elif binding == "conditional":
        binding_time = "conditional"
        target = task["pre_refresh_target"]
        state = "BOUND_CONDITIONAL"
    else:
        binding_time = "pre"
        target = task["pre_refresh_target"]
        state = "BOUND"
    return ReferentRecord(
        expression=task["selector"],
        binding_time=binding_time,
        target=target,
        selector=task["selector"],
        validity=task.get("action_schema", {}).get("preconditions", {}),
        provenance="initial_state" if binding_time != "post" else "refreshed_state",
        lifecycle_state=state,
    )


def lifecycle_act(task: dict[str, Any], record: ReferentRecord | None = None) -> str | list[str]:
    record = record or compile_oracle_record(task)
    task_type = task.get("task_type", "scalar")
    if task_type == "nested":
        return task["post_refresh_target"] if task["binding"] == "dynamic" else task["pre_refresh_target"]
    if task_type == "collection":
        return task["post_refresh_target"] if task["binding"] == "dynamic" else task["pre_refresh_target"]
    if task["binding"] == "dynamic":
        return task["post_refresh_target"]
    if task["binding"] == "conditional":
        pre = task["pre_refresh_target"]
        post = task["post_refresh_target"]
        if task.get("conditional_policy") == "prefer_bound_if_valid_else_rebind":
            return pre if target_valid(task, pre) else post
        return pre if pre == post and target_valid(task, pre) else post
    pre = task["pre_refresh_target"]
    return pre if target_valid(task, pre) else INVALID


def _name_fields(item: dict[str, Any]) -> set[str]:
    return {str(item[k]) for k in ("display", "name", "title", "subject") if k in item}


def _resolve_name(task: dict[str, Any], target_id: str) -> str:
    before = _entity(task["initial_state"], target_id)
    if before is None:
        return task["post_refresh_target"]
    names = _name_fields(before)
    if not names:
        return task["post_refresh_target"]
    matches = [
        x["id"]
        for x in task["refreshed_state"]
        if names.intersection(_name_fields(x))
    ]
    if len(matches) == 1:
        return matches[0]
    return task["post_refresh_target"]


def predict(task: dict[str, Any], representation: str) -> str | list[str]:
    binding = task["binding"]
    task_type = task.get("task_type", "scalar")
    pre = task["pre_refresh_target"]
    post = task["post_refresh_target"]

    if representation == "latest_state":
        return post
    if representation == "binding_time_only":
        return post if binding in {"dynamic", "conditional"} else UNKNOWN
    if representation == "bound_id_only":
        return pre
    if representation == "bound_name_only":
        if task_type != "scalar" or isinstance(pre, list):
            return post
        return _resolve_name(task, pre)
    if representation == "time_plus_id":
        if binding == "dynamic":
            return post
        return pre
    if representation == "schema_lifecycle":
        return lifecycle_act(task)
    raise ValueError(f"unknown representation: {representation}")


REPRESENTATIONS = [
    "latest_state",
    "bound_name_only",
    "bound_id_only",
    "binding_time_only",
    "time_plus_id",
    "schema_lifecycle",
]
