from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .v2_tasks import (
    DATA,
    DOMAINS,
    INVALID,
    _target_valid_after,
    after_for_update,
    scalar_rows,
    selected,
)


UPDATES = ["flip", "stable", "remove", "invalidate", "name_collision"]


TEMPLATE_FAMILIES: dict[str, list[str]] = {
    "explicit_anchor": [
        "Select {selector} from the {app} now. After refreshing, {action} that exact {entity}.",
        "Using the pre-refresh view, choose {selector}. Reload the {app}; then {action} the one chosen earlier.",
        "Record the identity of {selector} before synchronization. Once the {app} sync completes, {action} that recorded {entity}.",
        "Mark {selector} in the current {app} list. Update the view and {action} that marked {entity}.",
        "Resolve {selector} at this point. Following a reload of the {app}, {action} the previously resolved {entity}.",
    ],
    "implicit_anchor": [
        "Look over the current {app} and note {selector}. Refresh the view, then {action} it.",
        "Which {entity} is {selector} right now? Keep it in mind, reload the {app}, and {action} it.",
        "Pick {selector} from the current list; after syncing the {app}, {action} it.",
        "Find {selector} in the {app} as it stands. Update the view, then {action} it.",
        "Inspect the current {app} and settle on {selector}. Reload the view, then {action} it.",
    ],
    "explicit_dynamic": [
        "Reload the {app} first; select {selector} only from the updated view and {action} that {entity}.",
        "Do not choose a target until after the {app} synchronizes. Then determine {selector} and {action} that {entity}.",
        "Once the {app} has refreshed, determine {selector} and {action} the resulting {entity}.",
        "Discard the pre-refresh ranking. Refresh the {app}, identify {selector} anew, and {action} that {entity}.",
        "Update the {app} data, then newly identify {selector} and {action} that {entity}.",
    ],
    "implicit_dynamic": [
        "Synchronize the {app}; then, from what is displayed afterward, locate {selector} and {action} it.",
        "Wait for the {app} reload to finish before working out {selector}, then {action} it.",
        "Use only the post-update {app} list to locate {selector} and {action} it.",
        "Let the {app} refresh. Based on the resulting list, work out {selector} and {action} it.",
        "The refresh must happen before the target is settled. In the updated {app}, locate {selector} and {action} it.",
    ],
}


UNSEEN_DOMAINS: list[dict[str, Any]] = [
    {
        "domain": "projects",
        "app": "project_board",
        "entity": "project",
        "action": "flag",
        "selector": "the highest-risk active project",
        "criterion": "risk_score",
        "direction": "highest",
        "validity": {"status": "active", "actionable": True},
        "before": [
            {"id": "PRJ-A7", "display": "Migration", "risk_score": 86, "status": "active", "owner": "TEAM-1", "actionable": True},
            {"id": "PRJ-C2", "display": "Billing", "risk_score": 64, "status": "active", "owner": "TEAM-2", "actionable": True},
            {"id": "PRJ-F9", "display": "Archive", "risk_score": 40, "status": "closed", "owner": "TEAM-3", "actionable": True},
        ],
        "after_flip": [
            {"id": "PRJ-A7", "display": "Migration", "risk_score": 78, "status": "active", "owner": "TEAM-4", "actionable": True},
            {"id": "PRJ-C2", "display": "Billing", "risk_score": 93, "status": "active", "owner": "TEAM-2", "actionable": True},
            {"id": "PRJ-F9", "display": "Archive", "risk_score": 40, "status": "closed", "owner": "TEAM-3", "actionable": True},
        ],
    },
    {
        "domain": "expenses",
        "app": "expense_console",
        "entity": "claim",
        "action": "approve",
        "selector": "the largest pending expense claim",
        "criterion": "amount_cents",
        "direction": "highest",
        "validity": {"status": "pending", "actionable": True},
        "before": [
            {"id": "EXP-804", "display": "Conference", "amount_cents": 248000, "status": "pending", "owner": "EMP-8", "actionable": True},
            {"id": "EXP-917", "display": "Equipment", "amount_cents": 173000, "status": "pending", "owner": "EMP-9", "actionable": True},
            {"id": "EXP-102", "display": "Transit", "amount_cents": 2400, "status": "paid", "owner": "EMP-1", "actionable": True},
        ],
        "after_flip": [
            {"id": "EXP-804", "display": "Conference", "amount_cents": 248000, "status": "pending", "owner": "EMP-4", "actionable": True},
            {"id": "EXP-917", "display": "Equipment", "amount_cents": 319000, "status": "pending", "owner": "EMP-9", "actionable": True},
            {"id": "EXP-102", "display": "Transit", "amount_cents": 2400, "status": "paid", "owner": "EMP-1", "actionable": True},
        ],
    },
    {
        "domain": "inventory",
        "app": "warehouse",
        "entity": "item",
        "action": "reorder",
        "selector": "the lowest-stock reorderable item",
        "criterion": "units",
        "direction": "lowest",
        "validity": {"reorderable": True, "actionable": True},
        "before": [
            {"id": "ITM-K4", "display": "Sensor", "units": 7, "reorderable": True, "owner": "WH-N", "actionable": True},
            {"id": "ITM-P8", "display": "Cable", "units": 13, "reorderable": True, "owner": "WH-S", "actionable": True},
            {"id": "ITM-R3", "display": "Legacy rack", "units": 2, "reorderable": False, "owner": "WH-E", "actionable": True},
        ],
        "after_flip": [
            {"id": "ITM-K4", "display": "Sensor", "units": 16, "reorderable": True, "owner": "WH-W", "actionable": True},
            {"id": "ITM-P8", "display": "Cable", "units": 4, "reorderable": True, "owner": "WH-S", "actionable": True},
            {"id": "ITM-R3", "display": "Legacy rack", "units": 2, "reorderable": False, "owner": "WH-E", "actionable": True},
        ],
    },
    {
        "domain": "deployments",
        "app": "cloud_console",
        "entity": "deployment",
        "action": "roll back",
        "selector": "the oldest failing deployment",
        "criterion": "age_minutes",
        "direction": "highest",
        "validity": {"status": "failing", "actionable": True},
        "before": [
            {"id": "DEP-X12", "display": "Gateway", "age_minutes": 74, "status": "failing", "owner": "SRE-A", "actionable": True},
            {"id": "DEP-Z05", "display": "Search", "age_minutes": 39, "status": "failing", "owner": "SRE-B", "actionable": True},
            {"id": "DEP-Q44", "display": "Worker", "age_minutes": 120, "status": "healthy", "owner": "SRE-C", "actionable": True},
        ],
        "after_flip": [
            {"id": "DEP-X12", "display": "Gateway", "age_minutes": 81, "status": "failing", "owner": "SRE-D", "actionable": True},
            {"id": "DEP-Z05", "display": "Search", "age_minutes": 96, "status": "failing", "owner": "SRE-B", "actionable": True},
            {"id": "DEP-Q44", "display": "Worker", "age_minutes": 120, "status": "healthy", "owner": "SRE-C", "actionable": True},
        ],
    },
]


def _task_from_spec(
    spec: dict[str, Any], style: str, template_index: int, update: str, prefix: str
) -> dict[str, Any]:
    binding = "anchored" if style.endswith("anchor") else "dynamic"
    phenomenon = "explicit" if style.startswith("explicit") else "implicit"
    before = deepcopy(spec["before"])
    after = after_for_update(spec, update)
    pre = selected(before, spec)
    post = selected(after, spec)
    correct = pre if binding == "anchored" and _target_valid_after(spec, after, pre) else (
        INVALID if binding == "anchored" else post
    )
    template_id = f"{style}-t{template_index + 1}"
    return {
        "id": f"{prefix}-{spec['domain']}-{template_id}-{update}",
        "candidate": prefix,
        "task_type": "scalar",
        "phenomenon": phenomenon,
        "split": "test",
        "domain": spec["domain"],
        "app": spec["app"],
        "style": style,
        "paraphrase": template_id,
        "template_id": template_id,
        "binding": binding,
        "update": update,
        "entity": spec["entity"],
        "action": spec["action"],
        "selector": spec["selector"],
        "instruction": TEMPLATE_FAMILIES[style][template_index].format(**spec),
        "initial_state": before,
        "refreshed_state": after,
        "pre_refresh_target": pre,
        "post_refresh_target": post,
        "correct_target": correct,
        "new_leader": post,
        "action_schema": {"preconditions": deepcopy(spec["validity"])},
        "bound_entity_present_after_refresh": any(x["id"] == pre for x in after),
        "bound_entity_actionable_after_refresh": _target_valid_after(spec, after, pre),
    }


def language_cluster_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for style in TEMPLATE_FAMILIES:
        for template_index in range(5):
            for domain_index, spec in enumerate(DOMAINS):
                update = UPDATES[(template_index + domain_index) % len(UPDATES)]
                rows.append(_task_from_spec(
                    spec, style, template_index, update, "tri-v3-language"
                ))
    return rows


def unseen_domain_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for style in TEMPLATE_FAMILIES:
        for update_index, update in enumerate(UPDATES):
            for spec in UNSEEN_DOMAINS:
                rows.append(_task_from_spec(
                    spec, style, update_index, update, "tri-v3-unseen"
                ))
    return rows


def balanced_smoke_rows() -> list[dict[str, Any]]:
    by_key = {
        (row["style"], row["template_id"], row["domain"]): row
        for row in language_cluster_rows()
    }
    rows: list[dict[str, Any]] = []
    for style_index, style in enumerate(TEMPLATE_FAMILIES):
        domain = DOMAINS[(2 * style_index) % len(DOMAINS)]["domain"]
        for template_index in range(5):
            rows.append(by_key[(style, f"{style}-t{template_index + 1}", domain)])
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--language-output", default=str(DATA / "temporal_referent_v3_language_clusters.jsonl")
    )
    ap.add_argument(
        "--unseen-output", default=str(DATA / "temporal_referent_v3_unseen_domains.jsonl")
    )
    ap.add_argument(
        "--smoke-output", default=str(DATA / "temporal_referent_v3_balanced_smoke.jsonl")
    )
    args = ap.parse_args()
    language = language_cluster_rows()
    unseen = unseen_domain_rows()
    smoke = balanced_smoke_rows()
    write_jsonl(Path(args.language_output), language)
    write_jsonl(Path(args.unseen_output), unseen)
    write_jsonl(Path(args.smoke_output), smoke)
    print(json.dumps({
        "language_output": args.language_output,
        "language_rows": len(language),
        "unseen_output": args.unseen_output,
        "unseen_rows": len(unseen),
        "smoke_output": args.smoke_output,
        "smoke_rows": len(smoke),
    }, indent=2))


if __name__ == "__main__":
    main()
