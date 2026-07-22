from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .v2_tasks import _target_valid_after, after_for_update, selected
from .v3_eval import UNSEEN_DOMAINS, UPDATES


POLICY_TEMPLATES: dict[str, list[str]] = {
    "action_validity": [
        "Choose {selector} in the current {app}. Refresh the {app}. Keep that same {entity} if it remains valid for the requested action; otherwise resolve {selector} after refresh and {action} that {entity}.",
        "Before synchronizing the {app}, note {selector}. After synchronization, prefer the noted {entity} while the action preconditions still hold; if they do not, resolve {selector} in the updated {app} and {action} that {entity}.",
        "Pick {selector} now, then reload the {app}. Continue with that choice if it can still be acted on; otherwise resolve {selector} after the reload and {action} that {entity}.",
        "Resolve {selector} from the present {app}. Following refresh, retain its identity when it is still eligible for the requested action; if it is ineligible, resolve the selector again and {action} the result.",
        "Mark {selector} before the {app} update. Once the update finishes, {action} the marked {entity} if it remains action-valid; otherwise resolve {selector} and {action} that {entity}.",
    ],
    "selector_match": [
        "Choose {selector} in the current {app}. Refresh the {app}. Keep that same {entity} only if it is still selected by that description; otherwise resolve {selector} after refresh and {action} that {entity}.",
        "Before synchronizing the {app}, note {selector}. After synchronization, retain the noted {entity} if it still satisfies that description; if not, resolve {selector} in the updated {app} and {action} that {entity}.",
        "Pick {selector} now, then reload the {app}. Continue with that choice only while it remains the selector result; otherwise resolve {selector} after reload and {action} that {entity}.",
        "Resolve {selector} from the present {app}. Following refresh, keep its identity if the selector still chooses it; if the selector chooses something else, {action} that new result.",
        "Mark {selector} before the {app} update. Once the update finishes, {action} the marked {entity} only if the selector still chooses it; otherwise resolve {selector} and {action} that {entity}.",
    ],
}


def task_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for guard_type, templates in POLICY_TEMPLATES.items():
        for template_index, template in enumerate(templates):
            for domain_index, spec in enumerate(UNSEEN_DOMAINS):
                update = UPDATES[(template_index + domain_index) % len(UPDATES)]
                before = deepcopy(spec["before"])
                after = after_for_update(spec, update)
                pre = selected(before, spec)
                post = selected(after, spec)
                valid = _target_valid_after(spec, after, pre)
                if guard_type == "action_validity":
                    correct = pre if valid else post
                else:
                    correct = pre if valid and pre == post else post
                template_id = f"{guard_type}-t{template_index + 1}"
                rows.append({
                    "id": f"tri-v4-policy-{spec['domain']}-{template_id}-{update}",
                    "candidate": "tri-v4-policy",
                    "task_type": "conditional",
                    "phenomenon": "guarded_reference_policy",
                    "split": "test",
                    "domain": spec["domain"],
                    "app": spec["app"],
                    "style": guard_type,
                    "paraphrase": template_id,
                    "template_id": template_id,
                    "binding": "conditional",
                    "reference_mode": "conditional",
                    "guard_type": guard_type,
                    "fallback_policy": "reevaluate_selector",
                    "update": update,
                    "entity": spec["entity"],
                    "action": spec["action"],
                    "selector": spec["selector"],
                    "instruction": template.format(**spec),
                    "initial_state": before,
                    "refreshed_state": after,
                    "pre_refresh_target": pre,
                    "post_refresh_target": post,
                    "correct_target": correct,
                    "new_leader": post,
                    "action_schema": {"preconditions": deepcopy(spec["validity"])},
                    "bound_entity_present_after_refresh": any(row["id"] == pre for row in after),
                    "bound_entity_actionable_after_refresh": valid,
                })
    return rows


def smoke_rows() -> list[dict[str, Any]]:
    rows = task_rows()
    by_template: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_template.setdefault(row["template_id"], []).append(row)
    return [
        by_template[template_id][index % len(UNSEEN_DOMAINS)]
        for index, template_id in enumerate(sorted(by_template))
    ]


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/temporal_referent_v4_policy.jsonl")
    ap.add_argument("--smoke-output", default="data/temporal_referent_v4_policy_smoke.jsonl")
    args = ap.parse_args()
    write_rows(Path(args.output), task_rows())
    write_rows(Path(args.smoke_output), smoke_rows())
    print(f"wrote {len(task_rows())} policy tasks to {args.output}")
    print(f"wrote {len(smoke_rows())} policy smoke tasks to {args.smoke_output}")


if __name__ == "__main__":
    main()
