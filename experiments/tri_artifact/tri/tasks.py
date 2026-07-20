from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


DOMAINS = [
    {
        "domain": "incident",
        "split": "dev",
        "entity": "incident",
        "action": "escalate",
        "selector": "the currently highest-severity open incident",
        "criterion": "severity",
        "direction": "highest",
        "before": [
            {"id": "INC-104", "severity": 9, "service": "payments"},
            {"id": "INC-205", "severity": 7, "service": "search"},
            {"id": "INC-319", "severity": 5, "service": "email"},
        ],
        "after_flip": [
            {"id": "INC-104", "severity": 9, "service": "payments"},
            {"id": "INC-205", "severity": 10, "service": "search"},
            {"id": "INC-319", "severity": 5, "service": "email"},
        ],
    },
    {
        "domain": "meeting",
        "split": "dev",
        "entity": "meeting",
        "action": "open the notes for",
        "selector": "the meeting at the front of the current queue",
        "criterion": "queue_position",
        "direction": "front",
        "before": [
            {"id": "MTG-A", "queue_position": 1, "topic": "roadmap"},
            {"id": "MTG-B", "queue_position": 2, "topic": "budget"},
            {"id": "MTG-C", "queue_position": 3, "topic": "hiring"},
        ],
        "after_flip": [
            {"id": "MTG-B", "queue_position": 1, "topic": "budget"},
            {"id": "MTG-A", "queue_position": 2, "topic": "roadmap"},
            {"id": "MTG-C", "queue_position": 3, "topic": "hiring"},
        ],
    },
    {
        "domain": "ticket",
        "split": "dev",
        "entity": "support ticket",
        "action": "download the attachment from",
        "selector": "the currently selected support ticket",
        "criterion": "selected",
        "direction": "true",
        "before": [
            {"id": "TCK-41", "selected": True, "attachment": "refund.pdf"},
            {"id": "TCK-52", "selected": False, "attachment": "invoice.png"},
            {"id": "TCK-63", "selected": False, "attachment": "trace.log"},
        ],
        "after_flip": [
            {"id": "TCK-41", "selected": False, "attachment": "refund.pdf"},
            {"id": "TCK-52", "selected": True, "attachment": "invoice.png"},
            {"id": "TCK-63", "selected": False, "attachment": "trace.log"},
        ],
    },
    {
        "domain": "repo",
        "split": "dev",
        "entity": "repository branch",
        "action": "run checks on",
        "selector": "the current default branch",
        "criterion": "default",
        "direction": "true",
        "before": [
            {"id": "BR-main", "name": "main", "default": True},
            {"id": "BR-release", "name": "release", "default": False},
            {"id": "BR-dev", "name": "dev", "default": False},
        ],
        "after_flip": [
            {"id": "BR-main", "name": "main", "default": False},
            {"id": "BR-release", "name": "release", "default": True},
            {"id": "BR-dev", "name": "dev", "default": False},
        ],
    },
    {
        "domain": "invoice",
        "split": "heldout",
        "entity": "invoice",
        "action": "flag",
        "selector": "the currently largest unpaid invoice",
        "criterion": "amount",
        "direction": "highest",
        "before": [
            {"id": "INV-17", "amount": 9400, "status": "unpaid"},
            {"id": "INV-22", "amount": 8100, "status": "unpaid"},
            {"id": "INV-31", "amount": 1200, "status": "paid"},
        ],
        "after_flip": [
            {"id": "INV-17", "amount": 9400, "status": "unpaid"},
            {"id": "INV-22", "amount": 11100, "status": "unpaid"},
            {"id": "INV-31", "amount": 1200, "status": "paid"},
        ],
    },
    {
        "domain": "device",
        "split": "heldout",
        "entity": "device",
        "action": "schedule maintenance for",
        "selector": "the device currently assigned to the on-call engineer",
        "criterion": "on_call",
        "direction": "true",
        "before": [
            {"id": "DEV-7", "on_call": True, "rack": "A"},
            {"id": "DEV-8", "on_call": False, "rack": "B"},
            {"id": "DEV-9", "on_call": False, "rack": "C"},
        ],
        "after_flip": [
            {"id": "DEV-7", "on_call": False, "rack": "A"},
            {"id": "DEV-8", "on_call": True, "rack": "B"},
            {"id": "DEV-9", "on_call": False, "rack": "C"},
        ],
    },
    {
        "domain": "shipment",
        "split": "dev",
        "entity": "shipment",
        "action": "expedite",
        "selector": "the currently most delayed shipment",
        "criterion": "delay_hours",
        "direction": "highest",
        "before": [
            {"id": "SHP-88", "delay_hours": 18, "destination": "Paris"},
            {"id": "SHP-91", "delay_hours": 11, "destination": "Berlin"},
            {"id": "SHP-94", "delay_hours": 4, "destination": "Rome"},
        ],
        "after_flip": [
            {"id": "SHP-88", "delay_hours": 18, "destination": "Paris"},
            {"id": "SHP-91", "delay_hours": 23, "destination": "Berlin"},
            {"id": "SHP-94", "delay_hours": 4, "destination": "Rome"},
        ],
    },
    {
        "domain": "experiment",
        "split": "dev",
        "entity": "experiment run",
        "action": "archive",
        "selector": "the currently active experiment run",
        "criterion": "active",
        "direction": "true",
        "before": [
            {"id": "EXP-12", "active": True, "metric": 0.71},
            {"id": "EXP-18", "active": False, "metric": 0.69},
            {"id": "EXP-23", "active": False, "metric": 0.66},
        ],
        "after_flip": [
            {"id": "EXP-12", "active": False, "metric": 0.71},
            {"id": "EXP-18", "active": True, "metric": 0.74},
            {"id": "EXP-23", "active": False, "metric": 0.66},
        ],
    },
    {
        "domain": "patient",
        "split": "heldout",
        "entity": "patient case",
        "action": "open",
        "selector": "the patient case currently marked urgent",
        "criterion": "urgent",
        "direction": "true",
        "before": [
            {"id": "PAT-301", "urgent": True, "ward": "north"},
            {"id": "PAT-317", "urgent": False, "ward": "east"},
            {"id": "PAT-322", "urgent": False, "ward": "west"},
        ],
        "after_flip": [
            {"id": "PAT-301", "urgent": False, "ward": "north"},
            {"id": "PAT-317", "urgent": True, "ward": "east"},
            {"id": "PAT-322", "urgent": False, "ward": "west"},
        ],
    },
    {
        "domain": "dataset",
        "split": "heldout",
        "entity": "dataset",
        "action": "snapshot",
        "selector": "the currently largest dataset",
        "criterion": "size_gb",
        "direction": "highest",
        "before": [
            {"id": "DAT-5", "size_gb": 640, "owner": "ml"},
            {"id": "DAT-8", "size_gb": 520, "owner": "search"},
            {"id": "DAT-9", "size_gb": 210, "owner": "ads"},
        ],
        "after_flip": [
            {"id": "DAT-5", "size_gb": 640, "owner": "ml"},
            {"id": "DAT-8", "size_gb": 710, "owner": "search"},
            {"id": "DAT-9", "size_gb": 210, "owner": "ads"},
        ],
    },
]


PARAPHRASES = {
    "p0": {
        "anchored": "First identify {selector} from the state shown now. After refreshing, {action} that same {entity}.",
        "dynamic": "Refresh first. Then identify {selector} in the refreshed state and {action} it.",
    },
    "p1": {
        "anchored": "Using the current state, choose {selector}; after the refresh, keep that choice and {action} the same {entity}.",
        "dynamic": "Do not choose yet. Once the refreshed state arrives, choose {selector} and {action} that {entity}.",
    },
    "p2": {
        "anchored": "Bind the identity of {selector} before any refresh. Even if the refreshed state changes, {action} the originally bound {entity}.",
        "dynamic": "The target is intentionally evaluated after refresh: {action} whichever {entity} is {selector} in the new state.",
    },
    "p3": {
        "anchored": "Look at the present state and remember exactly which {entity} matches: {selector}. Refresh may change the list, but afterwards {action} the remembered one.",
        "dynamic": "Wait until after the refresh to decide. Then find {selector} and {action} that {entity}.",
    },
    "p4": {
        "anchored": "Before refreshing, select {selector}. The later action should apply to this selected {entity}, not to a newly selected one.",
        "dynamic": "The selection should be made from the later refreshed state: find {selector} then {action} it.",
    },
}


def selected_id(items: list[dict], spec: dict) -> str:
    criterion = spec["criterion"]
    if spec["direction"] == "highest":
        candidates = items
        if criterion == "amount":
            candidates = [x for x in items if x.get("status") == "unpaid"]
        return max(candidates, key=lambda x: x[criterion])["id"]
    if spec["direction"] == "front":
        return min(items, key=lambda x: x[criterion])["id"]
    if spec["direction"] == "true":
        return next(x["id"] for x in items if x[criterion] is True)
    raise ValueError(f"unknown selector direction: {spec['direction']}")


def stable_after(spec: dict) -> list[dict]:
    return [dict(x) for x in spec["before"]]


def removed_after(spec: dict) -> list[dict]:
    before_id = selected_id(spec["before"], spec)
    return [dict(x) for x in spec["after_flip"] if x["id"] != before_id]


def task_rows() -> list[dict]:
    rows: list[dict] = []
    for spec in DOMAINS:
        before_id = selected_id(spec["before"], spec)
        flip_id = selected_id(spec["after_flip"], spec)
        assert before_id != flip_id
        for para, templates in PARAPHRASES.items():
            for binding in ("anchored", "dynamic"):
                for update in ("flip", "stable", "removed"):
                    if update == "flip":
                        after = spec["after_flip"]
                    elif update == "stable":
                        after = stable_after(spec)
                    else:
                        after = removed_after(spec)
                    if binding == "anchored" and update == "removed":
                        correct_id = "INVALID_BOUND_ENTITY"
                    else:
                        correct_id = before_id if binding == "anchored" else selected_id(after, spec)
                    row = {
                        "id": f"{spec['domain']}-{para}-{binding}-{update}",
                        "candidate": "temporal_referent",
                        "split": spec["split"],
                        "domain": spec["domain"],
                        "paraphrase": para,
                        "binding": binding,
                        "update": update,
                        "entity": spec["entity"],
                        "action": spec["action"],
                        "selector": spec["selector"],
                        "instruction": templates[binding].format(**spec),
                        "initial_state": spec["before"],
                        "refreshed_state": after,
                        "pre_refresh_target": before_id,
                        "post_refresh_target": selected_id(after, spec),
                        "correct_target": correct_id,
                        "new_leader": flip_id,
                        "bound_entity_present_after_refresh": any(x["id"] == before_id for x in after),
                    }
                    rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DATA / "temporal_referent.jsonl"))
    args = ap.parse_args()
    rows = task_rows()
    write_jsonl(Path(args.output), rows)
    print(f"wrote {len(rows)} tasks to {args.output}")


if __name__ == "__main__":
    main()
