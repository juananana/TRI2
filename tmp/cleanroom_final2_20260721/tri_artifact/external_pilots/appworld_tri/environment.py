from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import json
from typing import Any, Iterator

from .scenarios import Scenario


BASE_TASK_ID = "82e2fac_1"
JSON_MARKER = "TRI_JSON:"


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


_runtime: ContextVar[Runtime | None] = ContextVar("appworld_tri_runtime", default=None)


def current_runtime() -> Runtime:
    runtime = _runtime.get()
    if runtime is None:
        raise RuntimeError("AppWorld TRI scenario is not active")
    return runtime


def _execute_json(world: Any, code: str) -> Any:
    output = world.execute(code)
    marked = [line[len(JSON_MARKER) :] for line in output.splitlines() if line.startswith(JSON_MARKER)]
    if not marked:
        raise RuntimeError(f"AppWorld execution did not return marked JSON: {output[:500]}")
    return json.loads(marked[-1])


def _task_rows(world: Any) -> list[dict[str, Any]]:
    rows = _execute_json(
        world,
        f"""
import json
result = apis.todoist.show_tasks(project_id=0, sort_by='+due_date', access_token=_tri_token)
rows = result['no_section_tasks']
for section in result['sections']:
    rows.extend(section['tasks'])
rows = [row for row in rows if row['title'].startswith('TRI::')]
print('{JSON_MARKER}' + json.dumps(rows, sort_keys=True))
""",
    )
    return sorted(rows, key=lambda row: int(row["task_id"]))


def _winner(rows: list[dict[str, Any]]) -> str:
    candidates = [row for row in rows if not row["is_completed"] and row["due_date"]]
    if not candidates:
        raise RuntimeError("no eligible Todoist task")
    return str(min(candidates, key=lambda row: (row["due_date"], row["task_id"]))["task_id"])


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
todo_pw = [item['password'] for item in passwords if item['account_name'] == 'todoist'][0]
_tri_token = apis.todoist.login(username=profile['email'], password=todo_pw)['access_token']
_tri_a = apis.todoist.create_task(project_id=0, title='TRI::{scenario.scenario_id}::A', due_date='2023-05-20', priority='high', access_token=_tri_token)['task_id']
_tri_c = apis.todoist.create_task(project_id=0, title='TRI::{scenario.scenario_id}::C', due_date='2023-05-22', priority='medium', access_token=_tri_token)['task_id']
print('{JSON_MARKER}' + json.dumps({{'a': _tri_a, 'c': _tri_c}}, sort_keys=True))
""",
        )
        runtime = Runtime(scenario=scenario, world=world)
        runtime.initial_snapshot = _task_rows(world)
        runtime.initial_target_id = str(ids["a"])
        if _winner(runtime.initial_snapshot) != runtime.initial_target_id:
            raise RuntimeError("controlled AppWorld setup has wrong initial winner")
        token = _runtime.set(runtime)
        try:
            yield runtime
        finally:
            try:
                runtime.final_snapshot = _task_rows(world)
            finally:
                _runtime.reset(token)


def search_tasks() -> list[dict[str, Any]]:
    runtime = current_runtime()
    rows = _task_rows(runtime.world)
    public_rows = [
        {
            "task_id": str(row["task_id"]),
            "title": row["title"],
            "due_date": row["due_date"],
            "priority": row["priority"],
            "is_completed": row["is_completed"],
        }
        for row in sorted(rows, key=lambda row: (row["due_date"], row["task_id"]))
    ]
    runtime.trace.append(
        {
            "tool": "search_tasks",
            "status": "ok",
            "synced": runtime.synced,
            "result_ids": [row["task_id"] for row in public_rows],
        }
    )
    return public_rows


def find_earliest_incomplete_task() -> dict[str, Any]:
    """Selector-style API whose returned stable ID is observable without a sidecar tool."""
    runtime = current_runtime()
    rows = _task_rows(runtime.world)
    task_id = _winner(rows)
    row = next(row for row in rows if str(row["task_id"]) == task_id)
    result = {
        "task_id": task_id,
        "title": row["title"],
        "due_date": row["due_date"],
        "priority": row["priority"],
        "is_completed": row["is_completed"],
    }
    runtime.trace.append(
        {
            "tool": "find_earliest_incomplete_task",
            "status": "ok",
            "synced": runtime.synced,
            "returned_id": task_id,
        }
    )
    return result


def record_binding(task_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {
        "tool": "record_binding",
        "arguments": {"task_id": task_id},
        "synced_at_binding": runtime.synced,
    }
    searches = [item for item in runtime.trace if item["tool"] == "search_tasks"]
    bindings = [
        item
        for item in runtime.trace
        if item["tool"] == "record_binding" and item.get("status") == "ok"
    ]
    if bindings:
        event.update(status="rejected", error="binding may be recorded only once")
    elif not searches:
        event.update(status="rejected", error="search before recording a binding")
    elif task_id not in searches[-1]["result_ids"]:
        event.update(status="rejected", error="bound ID absent from latest search")
    else:
        event.update(status="ok")
    runtime.trace.append(event)
    return event


def sync_tasks() -> dict[str, Any]:
    runtime = current_runtime()
    if runtime.synced:
        raise RuntimeError("sync_tasks may be called only once")
    due_date = "2023-05-25" if runtime.scenario.transition == "stable" else "2023-05-19"
    result = _execute_json(
        runtime.world,
        f"""
import json
result = apis.todoist.create_task(project_id=0, title='TRI::{runtime.scenario.scenario_id}::B', due_date='{due_date}', priority='low', access_token=_tri_token)
print('{JSON_MARKER}' + json.dumps(result, sort_keys=True))
""",
    )
    runtime.synced = True
    runtime.post_sync_snapshot = _task_rows(runtime.world)
    runtime.refreshed_target_id = _winner(runtime.post_sync_snapshot)
    runtime.correct_target_id = (
        runtime.initial_target_id
        if runtime.scenario.reference_mode == "preserve"
        else runtime.refreshed_target_id
    )
    event = {
        "tool": "sync_tasks",
        "status": "ok",
        "transition": runtime.scenario.transition,
        "created_task_id": str(result["task_id"]),
    }
    runtime.trace.append(event)
    return {"status": "ok", "message": "Todoist synchronization completed."}


def postpone_task(task_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {"tool": "postpone_task", "arguments": {"task_id": task_id}}
    try:
        if not runtime.synced:
            raise RuntimeError("synchronize before postponing")
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
from datetime import datetime, timedelta
task = apis.todoist.show_task(task_id={int(task_id)}, access_token=_tri_token)
old_due = task['due_date']
new_due = (datetime.fromisoformat(old_due) + timedelta(days=1)).date().isoformat()
response = apis.todoist.update_task(task_id={int(task_id)}, due_date=new_due, access_token=_tri_token)
print('{JSON_MARKER}' + json.dumps({{'response': response, 'old_due': old_due, 'new_due': new_due}}, sort_keys=True))
""",
        )
        event.update(status="ok", old_due=result["old_due"], new_due=result["new_due"])
    except Exception as exc:
        event.update(status="rejected", error=f"{type(exc).__name__}: {exc}")
    runtime.trace.append(event)
    return event


def postpone_task_without_sidecar(task_id: str) -> dict[str, Any]:
    runtime = current_runtime()
    event: dict[str, Any] = {"tool": "postpone_task", "arguments": {"task_id": task_id}}
    try:
        if not runtime.synced:
            raise RuntimeError("synchronize before postponing")
        result = _execute_json(
            runtime.world,
            f"""
import json
from datetime import datetime, timedelta
task = apis.todoist.show_task(task_id={int(task_id)}, access_token=_tri_token)
old_due = task['due_date']
new_due = (datetime.fromisoformat(old_due) + timedelta(days=1)).date().isoformat()
response = apis.todoist.update_task(task_id={int(task_id)}, due_date=new_due, access_token=_tri_token)
print('{JSON_MARKER}' + json.dumps({{'response': response, 'old_due': old_due, 'new_due': new_due}}, sort_keys=True))
""",
        )
        event.update(status="ok", old_due=result["old_due"], new_due=result["new_due"])
    except Exception as exc:
        event.update(status="rejected", error=f"{type(exc).__name__}: {exc}")
    runtime.trace.append(event)
    return event
