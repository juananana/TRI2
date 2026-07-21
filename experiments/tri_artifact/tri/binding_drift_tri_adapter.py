"""Author adaptation of Binding Drift re-verification to paired TRI tasks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tri.run_models import ChatClient, format_exception, normalize_target, parse_json


INVALID = "INVALID_BOUND_ENTITY"
OFFICIAL_COMMIT = "0e040e0954b18d4621a6f9b16f6e6e9591c822e1"
REVERIFY_PROMPT = """You are an independent entity resolver. Given the original user request and candidate entities, determine which entity the request refers to.

Original request: {referent}

Candidate entities:
{entities_json}

Which entity ID does the original request refer to? Return ONLY a JSON object:
{{"entity_id": "the_correct_id"}}

If genuinely ambiguous (multiple equally plausible), return:
{{"entity_id": "AMBIGUOUS"}}
"""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def freeze_smoke(source: Path) -> list[dict]:
    """Select one Flip cluster per domain and its Preserve/Reevaluate pair."""
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line]
    domains = sorted({row["domain"] for row in rows})
    selected: list[dict] = []
    for domain in domains:
        domain_rows = [row for row in rows if row["domain"] == domain and row["update"] == "flip"]
        cluster = sorted({row["state_cluster_id"] for row in domain_rows})[0]
        pair = [row for row in domain_rows if row["state_cluster_id"] == cluster]
        pair = sorted(pair, key=lambda row: (row["binding"] != "anchored", row["id"]))
        if len(pair) != 2 or {row["binding"] for row in pair} != {"anchored", "dynamic"}:
            raise ValueError(f"{domain}/{cluster}: expected one anchored/dynamic Flip pair")
        if pair[0]["initial_state"] != pair[1]["initial_state"] or pair[0]["refreshed_state"] != pair[1]["refreshed_state"]:
            raise ValueError(f"{domain}/{cluster}: pair states differ")
        if pair[0]["selector"] != pair[1]["selector"] or pair[0]["action"] != pair[1]["action"]:
            raise ValueError(f"{domain}/{cluster}: pair selector/action differs")
        for row in pair:
            frozen = dict(row)
            frozen["binding_drift_smoke_index"] = len(selected) + 1
            frozen["binding_drift_smoke_source"] = "v7 first sorted Flip cluster per domain"
            selected.append(frozen)
    if len(selected) != 20:
        raise ValueError(f"Expected 20 tasks, found {len(selected)}")
    return selected


def entity_lock_target(task: dict) -> str:
    return task["pre_refresh_target"] if task["bound_entity_actionable_after_refresh"] else INVALID


def reverify_prompt(task: dict) -> str:
    return REVERIFY_PROMPT.format(
        referent=task["instruction"],
        entities_json=json.dumps(task["refreshed_state"], ensure_ascii=False, indent=1),
    )


def run_reverify(client: ChatClient, task: dict, temperature: float = 0.0) -> dict:
    raw = ""
    errors: list[str] = []
    target = None
    ambiguous = False
    try:
        raw = client.chat([{"role": "user", "content": reverify_prompt(task)}], temperature)
        value = parse_json(raw).get("entity_id")
        ambiguous = str(value).strip().upper() == "AMBIGUOUS"
        target = INVALID if ambiguous else normalize_target(value)
    except Exception as exc:
        errors.append(format_exception(exc))
    return {
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": target == task["correct_target"],
        "ambiguous_or_clarify": ambiguous,
        "drift_to_refreshed_winner": (
            task["binding"] == "anchored"
            and task["post_refresh_target"] != task["correct_target"]
            and target == task["post_refresh_target"]
        ),
        "premature_lock": task["binding"] == "dynamic" and target == task["pre_refresh_target"],
        "other_visible_target": target in {entity["id"] for entity in task["refreshed_state"]}
        and target not in {task["pre_refresh_target"], task["post_refresh_target"]},
        "errors": errors,
        "raw_output": raw,
    }


def score_target(task: dict, target: str | None) -> dict:
    return {
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": target == task["correct_target"],
        "ambiguous_or_clarify": target == INVALID,
        "drift_to_refreshed_winner": (
            task["binding"] == "anchored"
            and task["post_refresh_target"] != task["correct_target"]
            and target == task["post_refresh_target"]
        ),
        "premature_lock": task["binding"] == "dynamic" and target == task["pre_refresh_target"],
        "other_visible_target": target in {entity["id"] for entity in task["refreshed_state"]}
        and target not in {task["pre_refresh_target"], task["post_refresh_target"]},
        "errors": [],
    }


def load_predictions(path: Path) -> dict[str, str | None]:
    output = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            output[row["task"]["id"]] = row["result"].get("predicted_target")
    return output


def summarize(rows: list[dict]) -> dict:
    result = {"n": len(rows), "correct": sum(row["result"]["success"] for row in rows)}
    result["accuracy"] = result["correct"] / result["n"] if result["n"] else 0.0
    for binding in ("anchored", "dynamic"):
        subset = [row for row in rows if row["task"]["binding"] == binding]
        result[binding] = {
            "n": len(subset),
            "correct": sum(row["result"]["success"] for row in subset),
            "drift_to_refreshed_winner": sum(row["result"]["drift_to_refreshed_winner"] for row in subset),
            "premature_lock": sum(row["result"]["premature_lock"] for row in subset),
        }
    result["clarify"] = sum(row["result"]["ambiguous_or_clarify"] for row in rows)
    result["other_visible_target"] = sum(row["result"].get("other_visible_target", False) for row in rows)
    result["api_or_parse_errors"] = sum(bool(row["result"]["errors"]) for row in rows)
    return result
