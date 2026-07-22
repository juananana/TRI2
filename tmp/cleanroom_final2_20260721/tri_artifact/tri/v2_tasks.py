from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


INVALID = "INVALID_BOUND_ENTITY"


DOMAINS: list[dict[str, Any]] = [
    {
        "domain": "mail",
        "app": "mailbox",
        "entity": "email",
        "action": "reply to",
        "selector": "the highest-priority unread email",
        "criterion": "priority",
        "direction": "highest",
        "validity": {"status": "unread", "actionable": True},
        "before": [
            {"id": "EM-104", "display": "Reset request", "priority": 91, "status": "unread", "owner": "USR-A", "actionable": True},
            {"id": "EM-205", "display": "Contract note", "priority": 73, "status": "unread", "owner": "USR-B", "actionable": True},
            {"id": "EM-319", "display": "Digest", "priority": 42, "status": "read", "owner": "USR-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "EM-104", "display": "Reset request", "priority": 91, "status": "unread", "owner": "USR-D", "actionable": True},
            {"id": "EM-205", "display": "Contract note", "priority": 97, "status": "unread", "owner": "USR-B", "actionable": True},
            {"id": "EM-319", "display": "Digest", "priority": 42, "status": "read", "owner": "USR-C", "actionable": True},
        ],
    },
    {
        "domain": "calendar",
        "app": "calendar",
        "entity": "meeting",
        "action": "open notes for",
        "selector": "the earliest upcoming meeting",
        "criterion": "start_minute",
        "direction": "lowest",
        "validity": {"status": "scheduled", "actionable": True},
        "before": [
            {"id": "MTG-10", "display": "Roadmap", "start_minute": 540, "status": "scheduled", "owner": "USR-E", "actionable": True},
            {"id": "MTG-22", "display": "Budget", "start_minute": 630, "status": "scheduled", "owner": "USR-F", "actionable": True},
            {"id": "MTG-37", "display": "Hiring", "start_minute": 720, "status": "scheduled", "owner": "USR-G", "actionable": True},
        ],
        "after_flip": [
            {"id": "MTG-10", "display": "Roadmap", "start_minute": 650, "status": "scheduled", "owner": "USR-H", "actionable": True},
            {"id": "MTG-22", "display": "Budget", "start_minute": 520, "status": "scheduled", "owner": "USR-F", "actionable": True},
            {"id": "MTG-37", "display": "Hiring", "start_minute": 720, "status": "scheduled", "owner": "USR-G", "actionable": True},
        ],
    },
    {
        "domain": "commerce",
        "app": "store",
        "entity": "product",
        "action": "purchase",
        "selector": "the cheapest in-stock product",
        "criterion": "price",
        "direction": "lowest",
        "validity": {"in_stock": True, "actionable": True},
        "before": [
            {"id": "SKU-11", "display": "Blue adapter", "price": 19, "in_stock": True, "owner": "SUP-A", "actionable": True},
            {"id": "SKU-29", "display": "Travel charger", "price": 27, "in_stock": True, "owner": "SUP-B", "actionable": True},
            {"id": "SKU-43", "display": "USB hub", "price": 34, "in_stock": True, "owner": "SUP-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "SKU-11", "display": "Blue adapter", "price": 31, "in_stock": True, "owner": "SUP-D", "actionable": True},
            {"id": "SKU-29", "display": "Travel charger", "price": 17, "in_stock": True, "owner": "SUP-B", "actionable": True},
            {"id": "SKU-43", "display": "USB hub", "price": 34, "in_stock": True, "owner": "SUP-C", "actionable": True},
        ],
    },
    {
        "domain": "support",
        "app": "support_console",
        "entity": "ticket",
        "action": "escalate",
        "selector": "the highest-severity open ticket",
        "criterion": "severity",
        "direction": "highest",
        "validity": {"status": "open", "actionable": True},
        "before": [
            {"id": "TCK-41", "display": "Refund blocked", "severity": 9, "status": "open", "owner": "AG-1", "actionable": True},
            {"id": "TCK-52", "display": "Invoice missing", "severity": 6, "status": "open", "owner": "AG-2", "actionable": True},
            {"id": "TCK-63", "display": "Trace upload", "severity": 3, "status": "closed", "owner": "AG-3", "actionable": True},
        ],
        "after_flip": [
            {"id": "TCK-41", "display": "Refund blocked", "severity": 8, "status": "open", "owner": "AG-4", "actionable": True},
            {"id": "TCK-52", "display": "Invoice missing", "severity": 10, "status": "open", "owner": "AG-2", "actionable": True},
            {"id": "TCK-63", "display": "Trace upload", "severity": 3, "status": "closed", "owner": "AG-3", "actionable": True},
        ],
    },
    {
        "domain": "docs",
        "app": "drive",
        "entity": "document",
        "action": "share",
        "selector": "the most recently edited active document",
        "criterion": "edited_at",
        "direction": "highest",
        "validity": {"status": "active", "actionable": True},
        "before": [
            {"id": "DOC-7", "display": "Launch plan", "edited_at": 200, "status": "active", "owner": "USR-I", "actionable": True},
            {"id": "DOC-8", "display": "Risk log", "edited_at": 160, "status": "active", "owner": "USR-J", "actionable": True},
            {"id": "DOC-9", "display": "Archive", "edited_at": 140, "status": "archived", "owner": "USR-K", "actionable": True},
        ],
        "after_flip": [
            {"id": "DOC-7", "display": "Launch plan", "edited_at": 200, "status": "active", "owner": "USR-L", "actionable": True},
            {"id": "DOC-8", "display": "Risk log", "edited_at": 230, "status": "active", "owner": "USR-J", "actionable": True},
            {"id": "DOC-9", "display": "Archive", "edited_at": 140, "status": "archived", "owner": "USR-K", "actionable": True},
        ],
    },
    {
        "domain": "crm",
        "app": "crm",
        "entity": "lead",
        "action": "assign",
        "selector": "the largest active sales lead",
        "criterion": "value",
        "direction": "highest",
        "validity": {"status": "active", "actionable": True},
        "before": [
            {"id": "LEAD-17", "display": "Acme", "value": 9400, "status": "active", "owner": "REP-A", "actionable": True},
            {"id": "LEAD-22", "display": "Beta", "value": 8100, "status": "active", "owner": "REP-B", "actionable": True},
            {"id": "LEAD-31", "display": "Gamma", "value": 1200, "status": "closed", "owner": "REP-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "LEAD-17", "display": "Acme", "value": 9400, "status": "active", "owner": "REP-D", "actionable": True},
            {"id": "LEAD-22", "display": "Beta", "value": 11100, "status": "active", "owner": "REP-B", "actionable": True},
            {"id": "LEAD-31", "display": "Gamma", "value": 1200, "status": "closed", "owner": "REP-C", "actionable": True},
        ],
    },
    {
        "domain": "repo",
        "app": "code_host",
        "entity": "branch",
        "action": "run checks on",
        "selector": "the default branch",
        "criterion": "default",
        "direction": "true",
        "validity": {"status": "active", "actionable": True},
        "before": [
            {"id": "BR-main", "display": "main", "default": True, "status": "active", "owner": "DEV-A", "actionable": True},
            {"id": "BR-rel", "display": "release", "default": False, "status": "active", "owner": "DEV-B", "actionable": True},
            {"id": "BR-dev", "display": "dev", "default": False, "status": "active", "owner": "DEV-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "BR-main", "display": "trunk", "default": False, "status": "active", "owner": "DEV-D", "actionable": True},
            {"id": "BR-rel", "display": "release", "default": True, "status": "active", "owner": "DEV-B", "actionable": True},
            {"id": "BR-dev", "display": "dev", "default": False, "status": "active", "owner": "DEV-C", "actionable": True},
        ],
    },
    {
        "domain": "shipping",
        "app": "logistics",
        "entity": "shipment",
        "action": "expedite",
        "selector": "the most delayed active shipment",
        "criterion": "delay_hours",
        "direction": "highest",
        "validity": {"status": "active", "actionable": True},
        "before": [
            {"id": "SHP-88", "display": "Paris crate", "delay_hours": 18, "status": "active", "owner": "OPS-A", "actionable": True},
            {"id": "SHP-91", "display": "Berlin box", "delay_hours": 11, "status": "active", "owner": "OPS-B", "actionable": True},
            {"id": "SHP-94", "display": "Rome case", "delay_hours": 4, "status": "delivered", "owner": "OPS-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "SHP-88", "display": "Paris crate", "delay_hours": 18, "status": "active", "owner": "OPS-D", "actionable": True},
            {"id": "SHP-91", "display": "Berlin box", "delay_hours": 23, "status": "active", "owner": "OPS-B", "actionable": True},
            {"id": "SHP-94", "display": "Rome case", "delay_hours": 4, "status": "delivered", "owner": "OPS-C", "actionable": True},
        ],
    },
]


STYLE_TEMPLATES = {
    "explicit_anchor": {
        "binding": "anchored",
        "phenomenon": "explicit",
        "template": "From the current {app} state, identify {selector}. After refreshing the app, {action} that same {entity}.",
    },
    "implicit_anchor": {
        "binding": "anchored",
        "phenomenon": "implicit",
        "template": "Check which {entity} needs action as {selector}. Refresh the {app}, then {action} it.",
    },
    "explicit_dynamic": {
        "binding": "dynamic",
        "phenomenon": "explicit",
        "template": "Refresh the {app} first. Then identify {selector} and {action} that {entity}.",
    },
    "implicit_dynamic": {
        "binding": "dynamic",
        "phenomenon": "implicit",
        "template": "Update the {app} view before deciding. Use the refreshed list to find {selector} and {action} it.",
    },
}


def _copy(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return deepcopy(items)


def _passes_validity(item: dict[str, Any], validity: dict[str, Any]) -> bool:
    return all(item.get(k) == v for k, v in validity.items())


def selected(items: list[dict[str, Any]], spec: dict[str, Any]) -> str:
    candidates = [x for x in items if _passes_validity(x, spec["validity"])]
    if spec["direction"] == "highest":
        return max(candidates, key=lambda x: x[spec["criterion"]])["id"]
    if spec["direction"] == "lowest":
        return min(candidates, key=lambda x: x[spec["criterion"]])["id"]
    if spec["direction"] == "true":
        return next(x["id"] for x in candidates if x[spec["criterion"]] is True)
    raise ValueError(spec["direction"])


def selected_top_k(items: list[dict[str, Any]], spec: dict[str, Any], k: int) -> list[str]:
    candidates = [x for x in items if _passes_validity(x, spec["validity"])]
    reverse = spec["direction"] == "highest"
    ordered = sorted(candidates, key=lambda x: x[spec["criterion"]], reverse=reverse)
    return [x["id"] for x in ordered[:k]]


def after_for_update(spec: dict[str, Any], update: str) -> list[dict[str, Any]]:
    pre = selected(spec["before"], spec)
    after = _copy(spec["after_flip"])
    if update == "stable":
        return _copy(spec["before"])
    if update == "flip":
        return after
    if update == "remove":
        return [x for x in after if x["id"] != pre]
    if update == "invalidate":
        for item in after:
            if item["id"] == pre:
                for key in spec["validity"]:
                    if isinstance(item.get(key), bool):
                        item[key] = False
                    elif key == "status":
                        item[key] = "closed"
                    else:
                        item[key] = None
                item["actionable"] = False
        return after
    if update == "name_collision":
        pre_display = next(x["display"] for x in spec["before"] if x["id"] == pre)
        post = selected(after, spec)
        for item in after:
            if item["id"] == post:
                item["display"] = pre_display
        return after
    raise ValueError(update)


def _entity(items: list[dict[str, Any]], target_id: str) -> dict[str, Any] | None:
    return next((x for x in items if x["id"] == target_id), None)


def _target_valid_after(spec: dict[str, Any], after: list[dict[str, Any]], target_id: str) -> bool:
    item = _entity(after, target_id)
    return bool(item is not None and _passes_validity(item, spec["validity"]))


def scalar_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    updates = ["flip", "stable", "remove", "invalidate", "name_collision"]
    for spec in DOMAINS:
        pre = selected(spec["before"], spec)
        for style, template in STYLE_TEMPLATES.items():
            binding = template["binding"]
            for update in updates:
                after = after_for_update(spec, update)
                post = selected(after, spec)
                if binding == "anchored":
                    correct: str | list[str] = pre if _target_valid_after(spec, after, pre) else INVALID
                else:
                    correct = post
                rows.append({
                    "id": f"v2-{spec['domain']}-{style}-{update}",
                    "candidate": "temporal_referent_v2",
                    "task_type": "scalar",
                    "phenomenon": template["phenomenon"],
                    "split": "dev",
                    "domain": spec["domain"],
                    "app": spec["app"],
                    "style": style,
                    "paraphrase": style,
                    "binding": binding,
                    "update": update,
                    "entity": spec["entity"],
                    "action": spec["action"],
                    "selector": spec["selector"],
                    "instruction": template["template"].format(**spec),
                    "initial_state": _copy(spec["before"]),
                    "refreshed_state": after,
                    "pre_refresh_target": pre,
                    "post_refresh_target": post,
                    "correct_target": correct,
                    "new_leader": post,
                    "action_schema": {"preconditions": spec["validity"]},
                    "bound_entity_present_after_refresh": _entity(after, pre) is not None,
                    "bound_entity_actionable_after_refresh": _target_valid_after(spec, after, pre),
                })
    return rows


def conditional_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    updates = ["stable", "flip", "invalidate"]
    for spec in DOMAINS:
        pre = selected(spec["before"], spec)
        for update in updates:
            after = after_for_update(spec, update)
            post = selected(after, spec)
            still_selected = pre == post
            correct = pre if still_selected and _target_valid_after(spec, after, pre) else post
            rows.append({
                "id": f"v2-{spec['domain']}-conditional-{update}",
                "candidate": "temporal_referent_v2",
                "task_type": "conditional",
                "phenomenon": "conditional_rebinding",
                "split": "dev",
                "domain": spec["domain"],
                "app": spec["app"],
                "style": "conditional",
                "paraphrase": "conditional",
                "binding": "conditional",
                "update": update,
                "entity": spec["entity"],
                "action": spec["action"],
                "selector": spec["selector"],
                "instruction": (
                    "Identify {selector} in the current {app}. Refresh the app. "
                    "If that exact {entity} is still the refreshed {selector}, {action} it; "
                    "otherwise {action} the refreshed target."
                ).format(**spec),
                "initial_state": _copy(spec["before"]),
                "refreshed_state": after,
                "pre_refresh_target": pre,
                "post_refresh_target": post,
                "correct_target": correct,
                "new_leader": post,
                "action_schema": {"preconditions": spec["validity"]},
                "bound_entity_present_after_refresh": _entity(after, pre) is not None,
                "bound_entity_actionable_after_refresh": _target_valid_after(spec, after, pre),
            })
        for update in ["stable", "flip", "invalidate", "remove"]:
            after = after_for_update(spec, update)
            post = selected(after, spec)
            correct = pre if _target_valid_after(spec, after, pre) else post
            rows.append({
                "id": f"v2-{spec['domain']}-conditional-valid-{update}",
                "candidate": "temporal_referent_v2",
                "task_type": "conditional",
                "phenomenon": "conditional_validity",
                "split": "dev",
                "domain": spec["domain"],
                "app": spec["app"],
                "style": "conditional_validity",
                "paraphrase": "conditional_validity",
                "binding": "conditional",
                "conditional_policy": "prefer_bound_if_valid_else_rebind",
                "update": update,
                "entity": spec["entity"],
                "action": spec["action"],
                "selector": spec["selector"],
                "instruction": (
                    "Identify {selector} in the current {app}. Refresh the app. "
                    "Prefer that same {entity} for the action if it is still actionable; "
                    "if it is no longer actionable, {action} the refreshed target instead."
                ).format(**spec),
                "initial_state": _copy(spec["before"]),
                "refreshed_state": after,
                "pre_refresh_target": pre,
                "post_refresh_target": post,
                "correct_target": correct,
                "new_leader": post,
                "action_schema": {"preconditions": spec["validity"]},
                "bound_entity_present_after_refresh": _entity(after, pre) is not None,
                "bound_entity_actionable_after_refresh": _target_valid_after(spec, after, pre),
            })
    return rows


def collection_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in DOMAINS:
        if spec["direction"] == "true":
            continue
        pre = selected_top_k(spec["before"], spec, 2)
        after = after_for_update(spec, "flip")
        post = selected_top_k(after, spec, 2)
        for binding in ("anchored", "dynamic"):
            correct: str | list[str] = pre if binding == "anchored" else post
            rows.append({
                "id": f"v2-{spec['domain']}-collection-{binding}",
                "candidate": "temporal_referent_v2",
                "task_type": "collection",
                "phenomenon": "collection_reference",
                "split": "dev",
                "domain": spec["domain"],
                "app": spec["app"],
                "style": "collection",
                "paraphrase": "collection",
                "binding": binding,
                "update": "flip",
                "entity": spec["entity"],
                "action": spec["action"],
                "selector": f"the top two matching: {spec['selector']}",
                "instruction": (
                    f"Before refreshing {spec['app']}, identify the top two {spec['entity']}s under this rule: "
                    f"{spec['selector']}. Refresh, then {spec['action']} "
                    + ("those same entities." if binding == "anchored" else "the top two entities in the refreshed state.")
                ),
                "initial_state": _copy(spec["before"]),
                "refreshed_state": after,
                "pre_refresh_target": pre,
                "post_refresh_target": post,
                "correct_target": correct,
                "new_leader": post,
                "action_schema": {"preconditions": spec["validity"]},
            })
    return rows


def nested_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in DOMAINS:
        pre = selected(spec["before"], spec)
        after = after_for_update(spec, "flip")
        post = selected(after, spec)
        pre_owner = next(x["owner"] for x in spec["before"] if x["id"] == pre)
        post_owner = next(x["owner"] for x in after if x["id"] == post)
        for binding in ("anchored", "dynamic"):
            correct = pre_owner if binding == "anchored" else post_owner
            rows.append({
                "id": f"v2-{spec['domain']}-nested-{binding}",
                "candidate": "temporal_referent_v2",
                "task_type": "nested",
                "phenomenon": "nested_reference",
                "split": "dev",
                "domain": spec["domain"],
                "app": spec["app"],
                "style": "nested",
                "paraphrase": "nested",
                "binding": binding,
                "update": "flip",
                "entity": "owner",
                "action": "notify",
                "selector": f"the owner of {spec['selector']}",
                "instruction": (
                    f"Find {spec['selector']} in the current {spec['app']} and note its owner. "
                    f"Refresh the app, then notify "
                    + ("that same owner." if binding == "anchored" else "the owner of the refreshed target.")
                ),
                "initial_state": _copy(spec["before"]),
                "refreshed_state": after,
                "pre_refresh_target": pre_owner,
                "post_refresh_target": post_owner,
                "pre_refresh_entity_target": pre,
                "post_refresh_entity_target": post,
                "correct_target": correct,
                "new_leader": post_owner,
                "action_schema": {"preconditions": {}},
            })
    return rows


def task_rows() -> list[dict[str, Any]]:
    rows = scalar_rows() + conditional_rows() + collection_rows() + nested_rows()
    ids = {r["id"] for r in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate v2 task ids")
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DATA / "temporal_referent_v2.jsonl"))
    args = ap.parse_args()
    rows = task_rows()
    write_jsonl(Path(args.output), rows)
    print(f"wrote {len(rows)} v2 tasks to {args.output}")


if __name__ == "__main__":
    main()
