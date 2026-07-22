from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable

from .reference_lifecycle import INVALID


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    state: str | None = None
    role: str | None = None
    referent: str | None = None
    target_id: str | None = None


@dataclass(frozen=True)
class EventGraph:
    events: tuple[Event, ...]
    edges: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class SelectorAST:
    filters: tuple[tuple[str, Any], ...]
    order_field: str | None
    direction: str | None
    limit: int = 1


@dataclass(frozen=True)
class ReferentialCapability:
    target_id: str
    action: str
    source_event: str
    binding_epoch: str
    action_preconditions: tuple[tuple[str, Any], ...]
    release_condition: str = "explicit_user_reauthorization"
    expected_version: int | None = None


@dataclass(frozen=True)
class GateResult:
    status: str
    written_id: str | None = None


def _event(event_id: int, event_type: str, **kwargs: Any) -> Event:
    return Event(f"E{event_id}", event_type, **kwargs)


def compile_oracle_event_graph(task: dict[str, Any]) -> EventGraph:
    anchored = task["binding"] == "anchored"
    multi_refresh = "final_state" in task
    events: list[Event] = []

    if anchored:
        events.append(_event(1, "SELECT", state="initial", role="action_target"))
        events.append(_event(2, "REFRESH", state="intermediate" if multi_refresh else "final"))
        if multi_refresh:
            events.append(_event(3, "OBSERVE", state="intermediate", role="monitoring_reference"))
            events.append(_event(4, "REFRESH", state="final"))
        source = "E1"
    else:
        events.append(_event(1, "REFRESH", state="intermediate" if multi_refresh else "final"))
        if multi_refresh:
            events.append(_event(2, "OBSERVE", state="intermediate", role="monitoring_reference"))
            events.append(_event(3, "REFRESH", state="final"))
            events.append(_event(4, "SELECT", state="final", role="action_target"))
            source = "E4"
        else:
            events.append(_event(2, "SELECT", state="final", role="action_target"))
            source = "E2"

    events.append(_event(len(events) + 1, "ACT", role="action", referent=source))
    edges = tuple(
        (events[index].event_id, events[index + 1].event_id)
        for index in range(len(events) - 1)
    )
    graph = EventGraph(tuple(events), edges)
    validate_event_graph(graph)
    return graph


def validate_event_graph(graph: EventGraph) -> None:
    ids = [event.event_id for event in graph.events]
    if len(ids) != len(set(ids)):
        raise ValueError("event IDs must be unique")
    known = set(ids)
    if any(left not in known or right not in known for left, right in graph.edges):
        raise ValueError("edge references an unknown event")
    positions = {event_id: index for index, event_id in enumerate(ids)}
    if any(positions[left] >= positions[right] for left, right in graph.edges):
        raise ValueError("event graph must be acyclic and forward ordered")
    actions = [event for event in graph.events if event.event_type == "ACT"]
    if len(actions) != 1:
        raise ValueError("event graph must contain exactly one ACT event")
    referent = actions[0].referent
    sources = [
        event
        for event in graph.events
        if event.event_id == referent
        and event.event_type == "SELECT"
        and event.role == "action_target"
    ]
    if len(sources) != 1:
        raise ValueError("ACT must reference exactly one action-target SELECT event")


def derive_reference_mode(graph: EventGraph) -> str:
    action = next(event for event in graph.events if event.event_type == "ACT")
    source_index = next(
        index for index, event in enumerate(graph.events) if event.event_id == action.referent
    )
    refresh_indices = [
        index for index, event in enumerate(graph.events) if event.event_type == "REFRESH"
    ]
    if not refresh_indices:
        raise ValueError("TRI event graph requires at least one REFRESH event")
    return "preserve" if source_index < min(refresh_indices) else "reevaluate"


def _state(task: dict[str, Any], name: str) -> list[dict[str, Any]]:
    if name == "initial":
        return task["initial_state"]
    if name == "intermediate":
        return task.get("intermediate_state", task["refreshed_state"])
    if name == "final":
        return task.get("final_state", task["refreshed_state"])
    raise ValueError(f"unknown state name: {name}")


def _eligible(rows: Iterable[dict[str, Any]], filters: tuple[tuple[str, Any], ...]) -> list[dict[str, Any]]:
    return [row for row in rows if all(row.get(field) == value for field, value in filters)]


def execute_selector(selector: SelectorAST, rows: list[dict[str, Any]]) -> str:
    candidates = _eligible(rows, selector.filters)
    if not candidates:
        return INVALID
    if selector.order_field is None:
        return candidates[0]["id"] if len(candidates) == 1 else INVALID
    reverse = selector.direction == "desc"
    ordered = sorted(candidates, key=lambda row: row[selector.order_field], reverse=reverse)
    return ordered[0]["id"]


def _candidate_order_fields(task: dict[str, Any]) -> list[str]:
    ignored = {
        "id", "display", "name", "title", "subject", "owner",
        *task.get("action_schema", {}).get("preconditions", {}).keys(),
    }
    rows = task["initial_state"] + task.get("final_state", task["refreshed_state"])
    common = set.intersection(*(set(row) for row in rows))
    return sorted(
        field
        for field in common - ignored
        if all(isinstance(row[field], (int, float)) and not isinstance(row[field], bool) for row in rows)
    )


def compile_oracle_selector(task: dict[str, Any]) -> SelectorAST:
    filters = tuple(sorted(task.get("action_schema", {}).get("preconditions", {}).items()))
    matches: list[SelectorAST] = []
    final_state = task.get("final_state", task["refreshed_state"])
    for field in _candidate_order_fields(task):
        for direction in ("asc", "desc"):
            selector = SelectorAST(filters, field, direction)
            if (
                execute_selector(selector, task["initial_state"]) == task["pre_refresh_target"]
                and execute_selector(selector, final_state) == task["post_refresh_target"]
            ):
                matches.append(selector)
    if not matches:
        ignored = {
            "id", "display", "name", "title", "subject", "owner",
            *dict(filters).keys(),
        }
        initial_target = next(
            row for row in task["initial_state"] if row["id"] == task["pre_refresh_target"]
        )
        final_target = next(
            row for row in final_state if row["id"] == task["post_refresh_target"]
        )
        for field in sorted(set(initial_target) & set(final_target) - ignored):
            if initial_target[field] != final_target[field]:
                continue
            selector = SelectorAST(filters + ((field, initial_target[field]),), None, None)
            if (
                execute_selector(selector, task["initial_state"]) == task["pre_refresh_target"]
                and execute_selector(selector, final_state) == task["post_refresh_target"]
            ):
                matches.append(selector)
    if len(matches) != 1:
        raise ValueError(f"expected one oracle selector for {task['id']}, found {len(matches)}")
    return matches[0]


def execute_event_graph(
    task: dict[str, Any], graph: EventGraph, selector: SelectorAST
) -> str:
    validate_event_graph(graph)
    action = next(event for event in graph.events if event.event_type == "ACT")
    source = next(event for event in graph.events if event.event_id == action.referent)
    target = execute_selector(selector, _state(task, source.state or "final"))
    final_rows = task.get("final_state", task["refreshed_state"])
    final_entity = next((row for row in final_rows if row.get("id") == target), None)
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    if final_entity is None or any(final_entity.get(key) != value for key, value in preconditions.items()):
        return INVALID
    return target


def issue_capability(
    task: dict[str, Any], graph: EventGraph, selector: SelectorAST,
    expected_version: int | None = None,
) -> ReferentialCapability:
    action = next(event for event in graph.events if event.event_type == "ACT")
    source = next(event for event in graph.events if event.event_id == action.referent)
    target = execute_selector(selector, _state(task, source.state or "final"))
    return ReferentialCapability(
        target_id=target,
        action=task["action"],
        source_event=source.event_id,
        binding_epoch=source.state or "final",
        action_preconditions=tuple(
            sorted(task.get("action_schema", {}).get("preconditions", {}).items())
        ),
        expected_version=expected_version,
    )


class VersionedEntityStore:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = {row["id"]: deepcopy(row) for row in rows}
        for row in self.rows.values():
            row.setdefault("version", 1)
        self.writes: list[tuple[str, str]] = []

    def version(self, target_id: str) -> int:
        return int(self.rows[target_id]["version"])

    def update(self, target_id: str, **changes: Any) -> None:
        self.rows[target_id].update(changes)
        self.rows[target_id]["version"] += 1

    def delete(self, target_id: str) -> None:
        self.rows.pop(target_id, None)

    def add(self, row: dict[str, Any]) -> None:
        item = deepcopy(row)
        item.setdefault("version", 1)
        self.rows[item["id"]] = item

    def atomic_write(self, capability: ReferentialCapability, action: str) -> GateResult:
        if action != capability.action:
            return GateResult("scope_mismatch")
        row = self.rows.get(capability.target_id)
        if row is None:
            return GateResult("missing_target")
        if capability.expected_version is not None and row["version"] != capability.expected_version:
            return GateResult("stale_version")
        if any(row.get(field) != value for field, value in capability.action_preconditions):
            return GateResult("invalid_target")
        row["version"] += 1
        self.writes.append((action, capability.target_id))
        return GateResult("written", capability.target_id)
