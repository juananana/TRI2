from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import json
from typing import Any, Iterator

from .simple_note_scenarios import Scenario


BASE_TASK_ID = "82e2fac_1"
JSON_MARKER = "TRI_JSON:"
TAG = "tri-experiment"


@dataclass
class Runtime:
    scenario: Scenario
    world: Any
    synced: bool = False
    trace: list[dict[str, Any]] = field(default_factory=list)
    initial_snapshot: list[dict[str, Any]] = field(default_factory=list)
    post_sync_snapshot: list[dict[str, Any]] = field(default_factory=list)
    final_snapshot: list[dict[str, Any]] = field(default_factory=list)
    initial_target_id: str | None = None
    refreshed_target_id: str | None = None
    correct_target_id: str | None = None


_runtime: ContextVar[Runtime | None] = ContextVar("appworld_tri_note_runtime", default=None)


def current_runtime() -> Runtime:
    runtime = _runtime.get()
    if runtime is None:
        raise RuntimeError("AppWorld Simple Note TRI scenario is not active")
    return runtime


def _execute_json(world: Any, code: str) -> Any:
    output = world.execute(code)
    marked = [
        line[len(JSON_MARKER) :]
        for line in output.splitlines()
        if line.startswith(JSON_MARKER)
    ]
    if not marked:
        raise RuntimeError(f"AppWorld execution did not return marked JSON: {output[:500]}")
    return json.loads(marked[-1])


def _note_rows(world: Any) -> list[dict[str, Any]]:
    rows = _execute_json(
        world,
        f"""
import json
short = apis.simple_note.search_notes(tags=['{TAG}'], dont_reorder_pinned=True, page_limit=20, access_token=_tri_note_token)
rows = [apis.simple_note.show_note(note_id=row['note_id'], access_token=_tri_note_token) for row in short]
rows = [row for row in rows if row['title'].startswith('TRI::')]
print('{JSON_MARKER}' + json.dumps(rows, sort_keys=True))
""",
    )
    return sorted(rows, key=lambda row: int(row["note_id"]))


def _winner(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise RuntimeError("no eligible Simple Note record")
    return str(min(rows, key=lambda row: (row["title"].casefold(), row["note_id"]))["note_id"])


@contextmanager
def active_scenario(scenario: Scenario, experiment_name: str) -> Iterator[Runtime]:
    from appworld import AppWorld

    with AppWorld(task_id=BASE_TASK_ID, experiment_name=experiment_name) as world:
        ids = _execute_json(
            world,
            f"""
import json
profile = apis.supervisor.show_profile()
passwords = apis.supervisor.show_account_passwords()
note_pw = [item['password'] for item in passwords if item['account_name'] == 'simple_note'][0]
_tri_note_token = apis.simple_note.login(username=profile['email'], password=note_pw)['access_token']
_tri_note_a = apis.simple_note.create_note(title='TRI::BRAVO::{scenario.scenario_id}', content='controlled note A', tags=['{TAG}'], access_token=_tri_note_token)['note_id']
_tri_note_c = apis.simple_note.create_note(title='TRI::CHARLIE::{scenario.scenario_id}', content='controlled note C', tags=['{TAG}'], access_token=_tri_note_token)['note_id']
print('{JSON_MARKER}' + json.dumps({{'a': _tri_note_a, 'c': _tri_note_c}}, sort_keys=True))
""",
        )
        runtime = Runtime(scenario=scenario, world=world)
        runtime.initial_snapshot = _note_rows(world)
        runtime.initial_target_id = str(ids["a"])
        if _winner(runtime.initial_snapshot) != runtime.initial_target_id:
            raise RuntimeError("controlled Simple Note setup has wrong initial winner")
        token = _runtime.set(runtime)
        try:
            yield runtime
        finally:
            try:
                runtime.final_snapshot = _note_rows(world)
            finally:
                _runtime.reset(token)


def search_notes() -> list[dict[str, Any]]:
    runtime = current_runtime()
    rows = _note_rows(runtime.world)
    public_rows = [
        {
            "note_id": str(row["note_id"]),
            "title": row["title"],
            "tags": row["tags"],
        }
        for row in sorted(rows, key=lambda row: (row["title"].casefold(), row["note_id"]))
    ]
    runtime.trace.append(
        {
            "tool": "search_notes",
            "status": "ok",
            "synced": runtime.synced,
            "result_ids": [row["note_id"] for row in public_rows],
        }
    )
    return public_rows


def find_alphabetically_first_note() -> dict[str, Any]:
    """Selector-style API whose returned stable ID is observable without a sidecar tool."""
    runtime = current_runtime()
    rows = _note_rows(runtime.world)
    note_id = _winner(rows)
    row = next(row for row in rows if str(row["note_id"]) == note_id)
    result = {
        "note_id": note_id,
        "title": row["title"],
        "tags": row["tags"],
    }
    runtime.trace.append(
        {
            "tool": "find_alphabetically_first_note",
            "status": "ok",
            "synced": runtime.synced,
            "returned_id": note_id,
        }
    )
    return result


def record_binding(note_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {
        "tool": "record_binding",
        "arguments": {"note_id": note_id},
        "synced_at_binding": runtime.synced,
    }
    searches = [item for item in runtime.trace if item["tool"] == "search_notes"]
    bindings = [
        item
        for item in runtime.trace
        if item["tool"] == "record_binding" and item.get("status") == "ok"
    ]
    if bindings:
        event.update(status="rejected", error="binding may be recorded only once")
    elif not searches:
        event.update(status="rejected", error="search before recording a binding")
    elif note_id not in searches[-1]["result_ids"]:
        event.update(status="rejected", error="bound ID absent from latest search")
    else:
        event.update(status="ok")
    runtime.trace.append(event)
    return event


def sync_notes() -> dict[str, Any]:
    runtime = current_runtime()
    if runtime.synced:
        raise RuntimeError("sync_notes may be called only once")
    prefix = "DELTA" if runtime.scenario.transition == "stable" else "ALPHA"
    result = _execute_json(
        runtime.world,
        f"""
import json
result = apis.simple_note.create_note(title='TRI::{prefix}::{runtime.scenario.scenario_id}', content='synchronized note B', tags=['{TAG}'], access_token=_tri_note_token)
print('{JSON_MARKER}' + json.dumps(result, sort_keys=True))
""",
    )
    runtime.synced = True
    runtime.post_sync_snapshot = _note_rows(runtime.world)
    runtime.refreshed_target_id = _winner(runtime.post_sync_snapshot)
    runtime.correct_target_id = (
        runtime.initial_target_id
        if runtime.scenario.reference_mode == "preserve"
        else runtime.refreshed_target_id
    )
    event = {
        "tool": "sync_notes",
        "status": "ok",
        "transition": runtime.scenario.transition,
        "created_note_id": str(result["note_id"]),
    }
    runtime.trace.append(event)
    return {"status": "ok", "message": "Simple Note synchronization completed."}


def append_to_note(note_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {"tool": "append_to_note", "arguments": {"note_id": note_id}}
    try:
        if not runtime.synced:
            raise RuntimeError("synchronize before appending")
        bindings = [
            item
            for item in runtime.trace
            if item["tool"] == "record_binding" and item.get("status") == "ok"
        ]
        if len(bindings) != 1:
            raise RuntimeError("exactly one successful binding record is required")
        result = _execute_json(
            runtime.world,
            f"""
import json
before = apis.simple_note.show_note(note_id={int(note_id)}, access_token=_tri_note_token)
response = apis.simple_note.add_content_to_note(note_id={int(note_id)}, append_or_prepend='append', added_content='reviewed', access_token=_tri_note_token)
after = apis.simple_note.show_note(note_id={int(note_id)}, access_token=_tri_note_token)
print('{JSON_MARKER}' + json.dumps({{'response': response, 'old_content': before['content'], 'new_content': after['content']}}, sort_keys=True))
""",
        )
        event.update(
            status="ok",
            old_content=result["old_content"],
            new_content=result["new_content"],
        )
    except Exception as exc:
        event.update(status="rejected", error=f"{type(exc).__name__}: {exc}")
    runtime.trace.append(event)
    return event


def append_to_note_without_sidecar(note_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {"tool": "append_to_note", "arguments": {"note_id": note_id}}
    try:
        if not runtime.synced:
            raise RuntimeError("synchronize before appending")
        result = _execute_json(
            runtime.world,
            f"""
import json
before = apis.simple_note.show_note(note_id={int(note_id)}, access_token=_tri_note_token)
response = apis.simple_note.add_content_to_note(note_id={int(note_id)}, append_or_prepend='append', added_content='reviewed', access_token=_tri_note_token)
after = apis.simple_note.show_note(note_id={int(note_id)}, access_token=_tri_note_token)
print('{JSON_MARKER}' + json.dumps({{'response': response, 'old_content': before['content'], 'new_content': after['content']}}, sort_keys=True))
""",
        )
        event.update(
            status="ok",
            old_content=result["old_content"],
            new_content=result["new_content"],
        )
    except Exception as exc:
        event.update(status="rejected", error=f"{type(exc).__name__}: {exc}")
    runtime.trace.append(event)
    return event
