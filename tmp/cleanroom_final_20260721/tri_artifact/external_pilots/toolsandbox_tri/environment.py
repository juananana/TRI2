from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Iterator

import polars as pl
from polars.exceptions import NoDataError
from tool_sandbox.common.execution_context import (
    DatabaseNamespace,
    ExecutionContext,
    get_current_context,
    new_context,
)
from tool_sandbox.tools.reminder import modify_reminder, search_reminder

from .scenarios import Scenario


def _scenario_rows(scenario: Scenario) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    values: dict[str, tuple[Any, Any, Any]] = {
        "reminder_timestamp": (
            (1_800_100_000.0, 1_800_300_000.0, 1_800_050_000.0)
            if not scenario.descending
            else (1_800_300_000.0, 1_800_100_000.0, 1_800_350_000.0)
        ),
        "creation_timestamp": (
            (1_799_000_000.0, 1_799_000_200.0, 1_798_999_900.0)
            if not scenario.descending
            else (1_799_000_200.0, 1_799_000_000.0, 1_799_000_300.0)
        ),
        "content": (
            ("Alpha planning", "Mango renewal", "Aardvark confirmation")
            if not scenario.descending
            else ("Zulu planning", "Mango renewal", "Zz-top confirmation")
        ),
    }
    due = values["reminder_timestamp"]
    created = values["creation_timestamp"]
    content = values["content"]
    rows = [
        {
            "reminder_id": "REM-A",
            "content": content[0],
            "creation_timestamp": created[0],
            "reminder_timestamp": due[0],
            "latitude": None,
            "longitude": None,
        },
        {
            "reminder_id": "REM-C",
            "content": content[1],
            "creation_timestamp": created[1],
            "reminder_timestamp": due[1],
            "latitude": None,
            "longitude": None,
        },
    ]
    flip_row = {
        "reminder_id": "REM-B",
        "content": content[2],
        "creation_timestamp": created[2],
        "reminder_timestamp": due[2],
        "latitude": None,
        "longitude": None,
    }
    return rows, flip_row


@dataclass
class Runtime:
    scenario: Scenario
    synced: bool = False
    locked_ids: set[str] = field(default_factory=set)
    trace: list[dict[str, Any]] = field(default_factory=list)
    initial_snapshot: list[dict[str, Any]] = field(default_factory=list)
    post_sync_snapshot: list[dict[str, Any]] = field(default_factory=list)


_runtime: ContextVar[Runtime | None] = ContextVar("toolsandbox_tri_runtime", default=None)


def current_runtime() -> Runtime:
    runtime = _runtime.get()
    if runtime is None:
        raise RuntimeError("ToolSandbox TRI tool called outside an active scenario")
    return runtime


def reminder_rows() -> list[dict[str, Any]]:
    return (
        get_current_context()
        .get_database(DatabaseNamespace.REMINDER)
        .sort("reminder_id")
        .to_dicts()
    )


def make_context(scenario: Scenario) -> ExecutionContext:
    context = ExecutionContext(
        tool_allow_list=[
            "search_reminder",
            "record_binding",
            "sync_reminders",
            "postpone_reminder",
        ]
    )
    rows, _ = _scenario_rows(scenario)
    context.add_to_database(DatabaseNamespace.REMINDER, rows)
    return context


@contextmanager
def active_scenario(scenario: Scenario) -> Iterator[Runtime]:
    runtime = Runtime(scenario=scenario)
    token = _runtime.set(runtime)
    with new_context(make_context(scenario)):
        runtime.initial_snapshot = reminder_rows()
        try:
            yield runtime
        finally:
            _runtime.reset(token)


def search_all_reminders() -> list[dict[str, Any]]:
    """Use ToolSandbox's native search tool to return the current reminder set."""
    rows = search_reminder(reminder_timestamp_upperbound=2_524_604_400.0)
    rows = sorted(rows, key=lambda row: (row["reminder_timestamp"], row["reminder_id"]))
    runtime = current_runtime()
    public_rows = [
        {**row, "editable": row["reminder_id"] not in runtime.locked_ids}
        for row in rows
    ]
    runtime.trace.append(
        {
            "tool": "search_reminder",
            "arguments": {"reminder_timestamp_upperbound": 2_524_604_400.0},
            "result_ids": [row["reminder_id"] for row in rows],
        }
    )
    return public_rows


def record_binding(reminder_id: str) -> dict[str, Any]:
    """Record the agent's selected identity without changing environment state."""
    runtime = current_runtime()
    event: dict[str, Any] = {
        "tool": "record_binding",
        "arguments": {"reminder_id": reminder_id},
        "synced_at_binding": runtime.synced,
    }
    prior_searches = [event for event in runtime.trace if event["tool"] == "search_reminder"]
    prior_bindings = [
        event
        for event in runtime.trace
        if event["tool"] == "record_binding" and event.get("status") == "ok"
    ]
    if prior_bindings:
        event.update(status="rejected", error="binding may be recorded only once")
    elif not prior_searches:
        event.update(status="rejected", error="search before recording a binding")
    elif reminder_id not in prior_searches[-1]["result_ids"]:
        event.update(status="rejected", error="bound ID was absent from the latest search")
    else:
        event.update(status="ok")
    runtime.trace.append(event)
    return event


def observe_state_binding(reminder_id: str) -> dict[str, Any]:
    """Log a binding already emitted in controller state without adding an agent step."""
    runtime = current_runtime()
    prior_bindings = [
        event
        for event in runtime.trace
        if event["tool"] in {"record_binding", "observe_binding"}
        and event.get("status") == "ok"
    ]
    event: dict[str, Any] = {
        "tool": "observe_binding",
        "arguments": {"reminder_id": reminder_id},
        "synced_at_binding": runtime.synced,
        "source": "controller_state",
    }
    if prior_bindings:
        event.update(status="rejected", error="binding was already observed")
    elif reminder_id not in {str(row["reminder_id"]) for row in reminder_rows()}:
        event.update(status="rejected", error="state ID is absent from the current database")
    else:
        event.update(status="ok")
    runtime.trace.append(event)
    return event


def sync_reminders() -> dict[str, Any]:
    runtime = current_runtime()
    if runtime.synced:
        raise RuntimeError("sync_reminders may be called only once")
    context = get_current_context()
    transition = runtime.scenario.transition
    if transition == "flip":
        _, flip_row = _scenario_rows(runtime.scenario)
        context.add_to_database(DatabaseNamespace.REMINDER, [flip_row])
    elif transition == "stable":
        context.update_database(
            DatabaseNamespace.REMINDER,
            context.get_database(DatabaseNamespace.REMINDER),
        )
    elif transition == "invalidate":
        runtime.locked_ids.add(runtime.scenario.initial_target_id)
        context.update_database(
            DatabaseNamespace.REMINDER,
            context.get_database(DatabaseNamespace.REMINDER),
        )
    elif transition == "remove":
        context.remove_from_database(
            DatabaseNamespace.REMINDER,
            pl.col("reminder_id") == runtime.scenario.initial_target_id,
        )
    else:
        raise ValueError(f"unsupported transition: {transition}")
    runtime.synced = True
    runtime.post_sync_snapshot = reminder_rows()
    runtime.trace.append(
        {"tool": "sync_reminders", "transition": transition, "status": "ok"}
    )
    return {"status": "ok", "message": "Reminder synchronization completed."}


def postpone_reminder(reminder_id: str, seconds: float = 86_400.0) -> dict[str, Any]:
    """Policy-aware extension that delegates valid writes to ToolSandbox's native tool."""
    runtime = current_runtime()
    event: dict[str, Any] = {
        "tool": "postpone_reminder",
        "arguments": {"reminder_id": reminder_id, "seconds": seconds},
    }
    try:
        if not runtime.synced:
            raise RuntimeError("reminders must be synced before postponement")
        if runtime.scenario.require_binding_record:
            bindings = [
                item
                for item in runtime.trace
                if item["tool"] in {"record_binding", "observe_binding"}
                and item["status"] == "ok"
            ]
            if len(bindings) != 1:
                raise RuntimeError("exactly one successful binding record is required")
        if reminder_id in runtime.locked_ids:
            raise PermissionError(f"reminder {reminder_id} is locked")
        rows = search_reminder(reminder_id=reminder_id)
        if not rows:
            raise NoDataError(f"reminder {reminder_id} does not exist")
        old_timestamp = float(rows[0]["reminder_timestamp"])
        modify_reminder(
            reminder_id=reminder_id,
            reminder_timestamp=old_timestamp + seconds,
        )
        event.update(status="ok", old_timestamp=old_timestamp)
    except Exception as exc:
        event.update(status="rejected", error=f"{type(exc).__name__}: {exc}")
    runtime.trace.append(event)
    return event
