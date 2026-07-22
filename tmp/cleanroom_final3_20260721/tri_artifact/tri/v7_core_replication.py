from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
UPDATES = ("flip", "stable", "name_collision")
BINDINGS = ("anchored", "dynamic")


SCHEMAS: tuple[dict[str, Any], ...] = (
    {
        "domain": "reminders",
        "app": "reminder_service",
        "entity": "reminder",
        "action": "postpone",
        "selector": "the earliest incomplete reminder",
        "criterion": "due_minutes",
        "direction": "lowest",
        "validity": {"completed": False, "actionable": True},
        "invalidity": {"completed": True},
        "prefix": "REM",
        "names": ("Renewal", "Report", "Call", "Backup", "Review"),
    },
    {
        "domain": "invoices",
        "app": "billing_console",
        "entity": "invoice",
        "action": "approve",
        "selector": "the largest unpaid invoice",
        "criterion": "amount_cents",
        "direction": "highest",
        "validity": {"status": "unpaid", "actionable": True},
        "invalidity": {"status": "paid"},
        "prefix": "INV",
        "names": ("Hosting", "Legal", "Travel", "Office", "Freight"),
    },
    {
        "domain": "applications",
        "app": "application_portal",
        "entity": "application",
        "action": "review",
        "selector": "the highest-scoring pending application",
        "criterion": "score",
        "direction": "highest",
        "validity": {"stage": "pending", "actionable": True},
        "invalidity": {"stage": "archived"},
        "prefix": "APP",
        "names": ("North", "Lake", "Stone", "Cedar", "Vale"),
    },
    {
        "domain": "reservations",
        "app": "reservation_board",
        "entity": "reservation",
        "action": "confirm",
        "selector": "the earliest unconfirmed reservation",
        "criterion": "start_minutes",
        "direction": "lowest",
        "validity": {"status": "unconfirmed", "actionable": True},
        "invalidity": {"status": "cancelled"},
        "prefix": "RSV",
        "names": ("Orchid", "Maple", "Harbor", "Summit", "Garden"),
    },
    {
        "domain": "alerts",
        "app": "alert_console",
        "entity": "alert",
        "action": "acknowledge",
        "selector": "the highest-severity open alert",
        "criterion": "severity",
        "direction": "highest",
        "validity": {"state": "open", "actionable": True},
        "invalidity": {"state": "closed"},
        "prefix": "ALT",
        "names": ("Gateway", "Storage", "Search", "Worker", "Queue"),
    },
    {
        "domain": "batches",
        "app": "batch_manager",
        "entity": "batch",
        "action": "start",
        "selector": "the oldest queued batch",
        "criterion": "age_minutes",
        "direction": "highest",
        "validity": {"status": "queued", "actionable": True},
        "invalidity": {"status": "completed"},
        "prefix": "BAT",
        "names": ("Import", "Export", "Index", "Archive", "Reconcile"),
    },
    {
        "domain": "reviews",
        "app": "review_inbox",
        "entity": "review",
        "action": "respond to",
        "selector": "the lowest-rated unresolved review",
        "criterion": "rating",
        "direction": "lowest",
        "validity": {"resolved": False, "actionable": True},
        "invalidity": {"resolved": True},
        "prefix": "REV",
        "names": ("Delivery", "Support", "Quality", "Billing", "Setup"),
    },
    {
        "domain": "certificates",
        "app": "certificate_registry",
        "entity": "certificate",
        "action": "renew",
        "selector": "the soonest-expiring active certificate",
        "criterion": "days_remaining",
        "direction": "lowest",
        "validity": {"status": "active", "actionable": True},
        "invalidity": {"status": "revoked"},
        "prefix": "CRT",
        "names": ("Gateway", "Portal", "API", "Worker", "Admin"),
    },
    {
        "domain": "bids",
        "app": "bid_board",
        "entity": "bid",
        "action": "accept",
        "selector": "the highest-value open bid",
        "criterion": "value_cents",
        "direction": "highest",
        "validity": {"status": "open", "actionable": True},
        "invalidity": {"status": "withdrawn"},
        "prefix": "BID",
        "names": ("Atlas", "Beacon", "Cobalt", "Delta", "Elm"),
    },
    {
        "domain": "appointments",
        "app": "appointment_queue",
        "entity": "appointment",
        "action": "confirm",
        "selector": "the earliest pending appointment",
        "criterion": "start_minutes",
        "direction": "lowest",
        "validity": {"status": "pending", "actionable": True},
        "invalidity": {"status": "cancelled"},
        "prefix": "APT",
        "names": ("Intake", "Followup", "Screening", "Consult", "Review"),
    },
)


TEMPLATES = {
    "explicit_anchor": (
        "In the current {app}, select {selector}. Refresh the data, then {action} that exact {entity}.",
        "Before synchronizing {app}, record the ID of {selector}. After synchronization, {action} the recorded {entity}.",
        "Choose {selector} from the present view. Reload {app}; the action target remains that chosen {entity}. Now {action} it.",
        "Resolve {selector} now, keep its identity fixed across the refresh, and then {action} that {entity}.",
    ),
    "implicit_anchor": (
        "Find {selector} in {app} as it stands. Refresh the list and then {action} it.",
        "Which {entity} is {selector} right now? Check again for updates, then {action} it.",
        "Pick {selector} from the current records; after the data reloads, {action} it.",
        "Look through {app} and settle on {selector}. Synchronize the records, then {action} it.",
    ),
    "explicit_dynamic": (
        "Refresh {app} first. Only then select {selector} from the updated data and {action} that {entity}.",
        "Do not choose the target from the current records. Synchronize {app}, identify {selector} afterward, and {action} it.",
        "Use the post-refresh view to newly determine {selector}, then {action} the resulting {entity}.",
        "Discard the current ranking, reload {app}, and select {selector} only after the reload before you {action} it.",
    ),
    "implicit_dynamic": (
        "Synchronize {app}; from the resulting records, locate {selector} and {action} it.",
        "Wait for the {app} update to finish before working out {selector}, then {action} it.",
        "Let {app} refresh. Based on what appears afterward, find {selector} and {action} it.",
        "Update the records, then locate {selector} in the new view and {action} it.",
    ),
}


def _values(instance: int, direction: str) -> tuple[int, int, int, int, int]:
    base = 100 + 23 * instance
    if direction == "highest":
        return base + 50, base + 30, base + 10, base + 90, base - 10
    return base + 10, base + 30, base + 50, base - 20, base + 90


def _entity(
    schema: dict[str, Any], instance: int, slot: int, value: int, valid: bool
) -> dict[str, Any]:
    row = {
        "id": f"{schema['prefix']}-{instance + 1}{chr(65 + slot)}",
        "display": schema["names"][slot],
        schema["criterion"]: value,
        "owner": f"TEAM-{slot + 1}",
        "actionable": True,
    }
    row.update(schema["validity"])
    if not valid:
        row.update(schema["invalidity"])
    return row


def _select(state: list[dict[str, Any]], schema: dict[str, Any]) -> str:
    eligible = [
        row
        for row in state
        if all(row.get(key) == value for key, value in schema["validity"].items())
    ]
    reverse = schema["direction"] == "highest"
    return sorted(eligible, key=lambda row: row[schema["criterion"]], reverse=reverse)[0]["id"]


def _states(schema: dict[str, Any], instance: int, update: str) -> tuple[list[dict], list[dict]]:
    values = _values(instance, schema["direction"])
    initial = [
        _entity(schema, instance, slot, value, slot < 3)
        for slot, value in enumerate(values)
    ]
    refreshed = deepcopy(initial)
    a = refreshed[0]
    b = refreshed[1]
    if update in {"flip", "name_collision"}:
        if schema["direction"] == "highest":
            b[schema["criterion"]] = a[schema["criterion"]] + 17 + instance
        else:
            b[schema["criterion"]] = a[schema["criterion"]] - 7 - instance
    else:
        if schema["direction"] == "highest":
            b[schema["criterion"]] = a[schema["criterion"]] - 9 - instance
        else:
            b[schema["criterion"]] = a[schema["criterion"]] + 9 + instance
    if update == "name_collision":
        b["display"] = a["display"]
    a["owner"] = f"TEAM-R{instance + 1}"
    return initial, refreshed


def task_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for schema_index, schema in enumerate(SCHEMAS):
        for instance in range(4):
            for update_index, update in enumerate(UPDATES):
                for binding_index, binding in enumerate(BINDINGS):
                    explicit = (schema_index + instance + update_index + binding_index) % 2 == 0
                    style = ("explicit_" if explicit else "implicit_") + (
                        "anchor" if binding == "anchored" else "dynamic"
                    )
                    template_index = (schema_index + 2 * instance + update_index) % 4
                    initial, refreshed = _states(schema, instance, update)
                    pre = _select(initial, schema)
                    post = _select(refreshed, schema)
                    correct = pre if binding == "anchored" else post
                    instruction = TEMPLATES[style][template_index].format(**schema)
                    state_cluster = f"{schema['domain']}-s{instance + 1}"
                    rows.append(
                        {
                            "id": f"tri-v7-core-{state_cluster}-{style}-{update}",
                            "candidate": "tri-v7-core-replication",
                            "task_type": "scalar",
                            "phenomenon": "explicit" if explicit else "implicit",
                            "split": "heldout",
                            "domain": schema["domain"],
                            "app": schema["app"],
                            "style": style,
                            "paraphrase": f"v7-{style}-t{template_index + 1}",
                            "template_id": f"v7-{style}-t{template_index + 1}",
                            "state_cluster_id": state_cluster,
                            "binding": binding,
                            "update": update,
                            "entity": schema["entity"],
                            "action": schema["action"],
                            "selector": schema["selector"],
                            "instruction": instruction,
                            "initial_state": initial,
                            "refreshed_state": refreshed,
                            "pre_refresh_target": pre,
                            "post_refresh_target": post,
                            "correct_target": correct,
                            "new_leader": post,
                            "action_schema": {"preconditions": deepcopy(schema["validity"])},
                            "bound_entity_present_after_refresh": True,
                            "bound_entity_actionable_after_refresh": True,
                        }
                    )
    return rows


def smoke_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for update in UPDATES:
        for binding in BINDINGS:
            candidates = [
                row for row in rows if row["update"] == update and row["binding"] == binding
            ]
            selected.extend(candidates[:2])
    return selected


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> str:
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DATA / "temporal_referent_v7_core_replication.jsonl")
    parser.add_argument("--smoke-output", type=Path, default=DATA / "temporal_referent_v7_core_replication_smoke.jsonl")
    args = parser.parse_args()
    rows = task_rows()
    smoke = smoke_rows(rows)
    print(json.dumps({
        "output": str(args.output),
        "rows": len(rows),
        "sha256": write_jsonl(args.output, rows),
        "smoke_output": str(args.smoke_output),
        "smoke_rows": len(smoke),
        "smoke_sha256": write_jsonl(args.smoke_output, smoke),
    }, indent=2))


if __name__ == "__main__":
    main()
