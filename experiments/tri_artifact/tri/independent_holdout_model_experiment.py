from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from tri.call_matched_authorization_ablation import (
    COMPILER_SYSTEM_PROMPT,
    build_actor_payload,
    build_compiler_payload,
    canonical_json,
    sha256_bytes,
)
from tri.deterministic_discourse_rule_v2 import predict_task_v2
from tri.independent_language_holdout import validate_model_tasks
from tri.revision_matched_audit import parse_actor_exact, parse_compiler_exact
from tri.v3_sqlite_replay import SQLiteWriteEnvironment


RUN_VERSION = "TRI-independent-language-holdout-model-v1"
EVIDENCE_STATUS = "post-primary; protocol and implementations frozen before own calls"
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
    "deepseek": "deepseek-ai/DeepSeek-V4-Pro",
}
ACTOR_CONDITIONS = ("history_only", "decision_visible", "timing_reminder", "cta")
MATCHED_CONDITIONS = ("history_only", "decision_visible")

ACTOR_SYSTEM_PROMPT = (
    "Choose the exact entity ID for the requested action from the supplied states. Follow the "
    "writer's instruction. initial_selected_id is the selector winner in S0 and s1_state is observed "
    "after synchronization. If compiler_decision is present, use it to decide whether to preserve "
    "the initial entity or evaluate the selector in S1. Return one JSON object only with exactly "
    "these keys: action, target_id. Copy target_id exactly from a serialized state ID or use CLARIFY."
)
TIMING_REMINDER_SYSTEM_PROMPT = (
    "Choose the exact entity ID for the requested action from the supplied states. Before choosing, "
    "use the instruction's event order: an entity identified before synchronization remains that "
    "entity afterward, while a selection deliberately placed after synchronization is evaluated in "
    "the resulting state. Return one JSON object only with exactly these keys: action, target_id. "
    "Copy target_id exactly from a serialized state ID or use CLARIFY."
)
CTA_SYSTEM_PROMPT = (
    "Act from the supplied pre-synchronization compiled_plan. A preserve plan carries its concrete "
    "bound_target_id through synchronization; a reevaluate plan resolves its selector in s1_state. "
    "Return one JSON object only with exactly these keys: action, target_id. Copy target_id exactly "
    "from a serialized state ID or use CLARIFY."
)


def actor_base_payload(task: dict[str, Any]) -> dict[str, Any]:
    return build_actor_payload(task, None)


def actor_payload(task: dict[str, Any], condition: str, decision: dict[str, Any]) -> dict[str, Any]:
    payload = actor_base_payload(task)
    if condition == "decision_visible":
        payload["compiler_decision"] = decision
    elif condition == "cta":
        payload["compiled_plan"] = decision
    elif condition not in {"history_only", "timing_reminder"}:
        raise ValueError(f"unknown actor condition: {condition}")
    return payload


def actor_prompt(condition: str) -> str:
    if condition in MATCHED_CONDITIONS:
        return ACTOR_SYSTEM_PROMPT
    if condition == "timing_reminder":
        return TIMING_REMINDER_SYSTEM_PROMPT
    if condition == "cta":
        return CTA_SYSTEM_PROMPT
    raise ValueError(f"unknown actor condition: {condition}")


def parse_actor(text: str, task: dict[str, Any]) -> dict[str, Any]:
    try:
        return parse_actor_exact(text, task)
    except ValueError:
        stripped = text.strip()
        if stripped.startswith("{" ) and stripped.endswith("}"):
            value = json.loads(stripped)
            if set(value) == {"action", "target_id"} and value["target_id"] == "CLARIFY":
                return {"action": str(value["action"]), "target_id": "CLARIFY"}
        raise


def freeze_prompt_hash() -> str:
    return sha256_bytes(
        canonical_json(
            {
                "compiler": COMPILER_SYSTEM_PROMPT,
                "actor": ACTOR_SYSTEM_PROMPT,
                "timing_reminder": TIMING_REMINDER_SYSTEM_PROMPT,
                "cta": CTA_SYSTEM_PROMPT,
            }
        ).encode("utf-8")
    )


def offline_rule(task: dict[str, Any]) -> dict[str, Any]:
    result = predict_task_v2(task)
    return {
        "reference_mode": result["reference_mode"],
        "target_id": result["predicted_target"],
        "error": result["error"],
    }


def sqlite_consistency(task: dict[str, Any], target: str | None) -> dict[str, Any]:
    if task["correct_target"] is None:
        return {"scored": False, "target": target, "status": "unclear_writer_intent"}
    if target == "CLARIFY":
        return {"scored": True, "target": target, "status": "unnecessary_clarification", "acted_ids": []}
    env = SQLiteWriteEnvironment(task)
    try:
        env.query()
        env.refresh()
        action = env.act(target)
        return {
            "scored": True,
            "target": target,
            "status": action["status"],
            "acted_ids": env.acted_ids(),
            "state_diff_kind": "deterministic target-to-write consistency check",
        }
    finally:
        env.close()


def validate_run_row(row: dict[str, Any], require_complete: bool = False) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("run provenance is missing")
    task = row.get("task")
    if not isinstance(task, dict) or task.get("pair_id") is None:
        raise ValueError("run row has no valid task")
    if set(row.get("actors", {})) != set(ACTOR_CONDITIONS):
        raise ValueError("run row lacks a frozen actor condition")
    if row.get("logical_calls_planned") != 5:
        raise ValueError("each row must plan one compiler and four actor calls")
    compiler = row.get("compiler", {}).get("parsed")
    if compiler is not None:
        expected_base = actor_base_payload(task)
        history_attempts = row["actors"]["history_only"].get("attempts", [])
        visible_attempts = row["actors"]["decision_visible"].get("attempts", [])
        if history_attempts and visible_attempts:
            history = json.loads(history_attempts[-1]["request"]["messages"][1]["content"])
            visible = json.loads(visible_attempts[-1]["request"]["messages"][1]["content"])
            decision = visible.pop("compiler_decision", None)
            if history != visible or history != expected_base or decision != compiler:
                raise ValueError("matched actor payloads differ beyond compiler_decision")
    if row.get("rule_star") != offline_rule(task):
        raise ValueError("recorded Rule* output differs from the frozen implementation")
    expected_sqlite = {
        condition: sqlite_consistency(task, row["outcomes"].get(condition))
        for condition in ACTOR_CONDITIONS
    }
    if row.get("sqlite_consistency") != expected_sqlite:
        raise ValueError("SQLite consistency result differs from actor targets")
    if require_complete:
        if not row.get("complete") or row.get("logical_calls_completed") != 5:
            raise ValueError("health smoke contains an incomplete row")


def pairacc(rows: list[dict[str, Any]], condition: str, clear_only: bool = True) -> tuple[int, int]:
    by_pair = defaultdict(list)
    for row in rows:
        task = row["task"]
        if clear_only and not task["clear_complete_pair"]:
            continue
        by_pair[task["pair_id"]].append(row)
    eligible = [members for members in by_pair.values() if len(members) == 2]
    correct = sum(
        all(member["outcomes"].get(condition) == member["task"]["correct_target"] for member in members)
        for members in eligible
    )
    return correct, len(eligible)
