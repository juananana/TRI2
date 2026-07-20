from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


PARAPHRASES = {
    "p0": {
        "anchored": "First identify {selector} from the current state. After the update, {action} that same {entity}.",
        "dynamic": "Apply the update first. Then identify {selector} in the updated state and {action} it.",
    },
    "p1": {
        "anchored": "Choose {selector} now and keep that exact choice across the update; afterwards {action} the chosen {entity}.",
        "dynamic": "Do not choose now. After the update, choose {selector} and {action} that {entity}.",
    },
    "p2": {
        "anchored": "Bind the target identity before the update. Even if names, rankings, or validity change, {action} the originally bound {entity} when valid.",
        "dynamic": "The target is intentionally late-bound: after the update, {action} whichever {entity} satisfies {selector}.",
    },
}


SCENARIOS = [
    {
        "scenario": "rename_and_flip",
        "domain": "branch_rename",
        "entity": "repository branch",
        "action": "run checks on",
        "selector": "the current default branch",
        "before": [
            {"id": "BR-17", "name": "main", "default": True},
            {"id": "BR-22", "name": "release", "default": False},
            {"id": "BR-35", "name": "dev", "default": False},
        ],
        "after": [
            {"id": "BR-17", "name": "trunk", "default": False},
            {"id": "BR-22", "name": "release", "default": True},
            {"id": "BR-35", "name": "dev", "default": False},
        ],
        "pre": "BR-17",
        "post": "BR-22",
        "anchored_correct": "BR-17",
    },
    {
        "scenario": "action_invalid",
        "domain": "ticket_invalid",
        "entity": "support ticket",
        "action": "download the attachment from",
        "selector": "the currently selected support ticket",
        "before": [
            {"id": "TCK-41", "selected": True, "attachment": "refund.pdf", "downloadable": True},
            {"id": "TCK-52", "selected": False, "attachment": "invoice.png", "downloadable": True},
            {"id": "TCK-63", "selected": False, "attachment": "trace.log", "downloadable": True},
        ],
        "after": [
            {"id": "TCK-41", "selected": False, "attachment": "refund.pdf", "downloadable": False},
            {"id": "TCK-52", "selected": True, "attachment": "invoice.png", "downloadable": True},
            {"id": "TCK-63", "selected": False, "attachment": "trace.log", "downloadable": True},
        ],
        "pre": "TCK-41",
        "post": "TCK-52",
        "anchored_correct": "INVALID_BOUND_ENTITY",
    },
    {
        "scenario": "name_collision",
        "domain": "invoice_collision",
        "entity": "invoice",
        "action": "flag",
        "selector": "the currently largest unpaid invoice",
        "before": [
            {"id": "INV-17", "display": "Acme invoice", "amount": 9400, "status": "unpaid"},
            {"id": "INV-22", "display": "Beta invoice", "amount": 8100, "status": "unpaid"},
            {"id": "INV-31", "display": "Gamma invoice", "amount": 1200, "status": "paid"},
        ],
        "after": [
            {"id": "INV-17", "display": "Acme invoice", "amount": 9400, "status": "unpaid"},
            {"id": "INV-22", "display": "Acme invoice", "amount": 11100, "status": "unpaid"},
            {"id": "INV-31", "display": "Gamma invoice", "amount": 1200, "status": "paid"},
        ],
        "pre": "INV-17",
        "post": "INV-22",
        "anchored_correct": "INV-17",
    },
    {
        "scenario": "multi_refresh_flip",
        "domain": "incident_multirefresh",
        "entity": "incident",
        "action": "escalate",
        "selector": "the currently highest-severity open incident",
        "before": [
            {"id": "INC-104", "severity": 9, "service": "payments"},
            {"id": "INC-205", "severity": 7, "service": "search"},
            {"id": "INC-319", "severity": 5, "service": "email"},
        ],
        "after": [
            {"id": "INC-104", "severity": 8, "service": "payments"},
            {"id": "INC-205", "severity": 10, "service": "search"},
            {"id": "INC-319", "severity": 6, "service": "email"},
        ],
        "pre": "INC-104",
        "post": "INC-205",
        "anchored_correct": "INC-104",
        "update_note": "two refreshes occur before the final action",
    },
    {
        "scenario": "delayed_binding",
        "domain": "experiment_delayed",
        "entity": "experiment run",
        "action": "archive",
        "selector": "the currently active experiment run",
        "before": [
            {"id": "EXP-12", "active": True, "metric": 0.71},
            {"id": "EXP-18", "active": False, "metric": 0.69},
            {"id": "EXP-23", "active": False, "metric": 0.66},
        ],
        "after": [
            {"id": "EXP-12", "active": False, "metric": 0.71},
            {"id": "EXP-18", "active": True, "metric": 0.74},
            {"id": "EXP-23", "active": False, "metric": 0.66},
        ],
        "pre": "EXP-12",
        "post": "EXP-18",
        "anchored_correct": "EXP-12",
    },
]


def task_rows() -> list[dict]:
    rows: list[dict] = []
    for spec in SCENARIOS:
        for para, templates in PARAPHRASES.items():
            for binding in ("anchored", "dynamic"):
                instruction = templates[binding].format(**spec)
                if spec.get("update_note"):
                    instruction += " " + spec["update_note"].capitalize() + "."
                correct = spec["anchored_correct"] if binding == "anchored" else spec["post"]
                bound_after = next((x for x in spec["after"] if x["id"] == spec["pre"]), None)
                bound_actionable = bool(bound_after is not None and bound_after.get("downloadable", True))
                rows.append({
                    "id": f"{spec['domain']}-{para}-{binding}-{spec['scenario']}",
                    "candidate": "temporal_referent_lifecycle",
                    "split": "dev",
                    "domain": spec["domain"],
                    "paraphrase": para,
                    "binding": binding,
                    "update": spec["scenario"],
                    "entity": spec["entity"],
                    "action": spec["action"],
                    "selector": spec["selector"],
                    "instruction": instruction,
                    "initial_state": spec["before"],
                    "refreshed_state": spec["after"],
                    "pre_refresh_target": spec["pre"],
                    "post_refresh_target": spec["post"],
                    "correct_target": correct,
                    "new_leader": spec["post"],
                    "bound_entity_present_after_refresh": any(x["id"] == spec["pre"] for x in spec["after"]),
                    "bound_entity_actionable_after_refresh": bound_actionable,
                    "validity_condition": "bound entity must remain actionable",
                    "lifecycle_scenario": spec["scenario"],
                })
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DATA / "lifecycle_referent.jsonl"))
    args = ap.parse_args()
    rows = task_rows()
    write_jsonl(Path(args.output), rows)
    print(f"wrote {len(rows)} lifecycle tasks to {args.output}")


if __name__ == "__main__":
    main()
