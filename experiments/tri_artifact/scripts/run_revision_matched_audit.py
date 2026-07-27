#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.run_call_matched_authorization_ablation import (
    ENDPOINT,
    MAX_RETRIES,
    MAX_TOKENS,
    RETRY_BACKOFF,
    TEMPERATURE,
    TIMEOUT,
    RecordingChatClient,
    run_component,
    skipped_component,
)
from tri.call_matched_authorization_ablation import (
    COMPILER_SYSTEM_PROMPT,
    actor_base_payload_hash,
    build_actor_payload,
    build_compiler_payload,
)
from tri.revision_matched_audit import (
    AUDITS,
    EVIDENCE_STATUS,
    RUN_VERSION,
    canonical_json,
    enforced_target,
    exact_target,
    load_jsonl,
    parse_actor_exact,
    parse_compiler_exact,
    sha256_bytes,
    sha256_path,
    validate_inventory,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports" / "revision_matched_audits_manifest_v1.json"
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
    "deepseek": "deepseek-ai/DeepSeek-V4-Pro",
}
REVISION_ACTOR_SYSTEM_PROMPT = (
    "Choose the exact entity ID for the requested action. Use the instruction and supplied states "
    "exactly. The initial_selected_id is the entity selected by the stated selector in S0. S1 is "
    "the state after refresh. If compiler_decision is present, follow it when deciding whether to "
    "preserve the initial entity or reevaluate the selector. If the instruction preserves a target "
    "that is missing or violates the supplied action preconditions in S1, return "
    "INVALID_BOUND_ENTITY rather than substituting another entity. Return one JSON object only with "
    "exactly these keys: action, target_id. Copy target_id exactly from a serialized state ID or use "
    "INVALID_BOUND_ENTITY."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"unknown model: {value}")


def load_frozen(audit: str) -> tuple[list[dict[str, Any]], Path, dict[str, Any]]:
    if not MANIFEST.exists():
        raise ValueError("build the frozen revision manifest before running")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != "TRI-revision-matched-audits-manifest-v1":
        raise ValueError("unexpected revision manifest version")
    entry = manifest["inventories"][audit]
    path = ROOT / entry["path"]
    if sha256_path(path) != entry["sha256"]:
        raise ValueError("frozen revision inventory hash mismatch")
    protocol = ROOT / manifest["protocol"]
    if sha256_path(protocol) != manifest["protocol_sha256"]:
        raise ValueError("frozen revision protocol hash mismatch")
    if sha256_path(ROOT / "tri" / "revision_matched_audit.py") != manifest["parser_sha256"]:
        raise ValueError("revision parser changed after the freeze")
    if sha256_path(ROOT / "tri" / "deterministic_discourse_rule_v2.py") != manifest["frozen_rule_star_sha256"]:
        raise ValueError("Rule* changed after the source-grounded freeze")
    tasks = load_jsonl(path)
    validate_inventory(tasks, audit)
    return tasks, path, manifest


def _decision_id(model: str, task_id: str, compiler: dict[str, Any]) -> str:
    return "sha256:" + sha256_bytes(
        canonical_json({"model": model, "task_id": task_id, "compiler": compiler}).encode("utf-8")
    )


def run_task(
    client: RecordingChatClient,
    task: dict[str, Any],
    task_index: int,
    run_scope: str,
    task_hash: str,
    protocol_hash: str,
) -> dict[str, Any]:
    compiler = run_component(
        client,
        "compiler",
        COMPILER_SYSTEM_PROMPT,
        build_compiler_payload(task),
        lambda text: parse_compiler_exact(text, task),
    )
    decision_id = _decision_id(client.model, task["id"], compiler)
    actors: dict[str, dict[str, Any]] = {}
    actor_order: list[str] = []
    if compiler["parsed"] is None:
        for condition in ("history_only", "decision_visible"):
            actors[condition] = skipped_component(
                condition, "skipped_after_compiler_failure", decision_id
            )
    else:
        order = (
            ("history_only", "decision_visible")
            if task_index % 2 == 0
            else ("decision_visible", "history_only")
        )
        actor_order = list(order)
        for condition in order:
            decision = compiler["parsed"] if condition == "decision_visible" else None
            component = run_component(
                client,
                condition,
                REVISION_ACTOR_SYSTEM_PROMPT,
                build_actor_payload(task, decision),
                lambda text: parse_actor_exact(text, task),
            )
            component["compiler_decision_id"] = decision_id
            actors[condition] = component
    for condition in ("history_only", "decision_visible"):
        actors[condition].setdefault("compiler_decision_id", decision_id)
    history = (actors["history_only"].get("parsed") or {}).get("target_id")
    visible = (actors["decision_visible"].get("parsed") or {}).get("target_id")
    enforced = enforced_target(compiler.get("parsed"), exact_target(visible), task)
    components = [compiler, actors["history_only"], actors["decision_visible"]]
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": run_scope,
        "timestamp_utc": utc_now(),
        "model": client.model,
        "endpoint": ENDPOINT,
        "api_settings": {
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "timeout_seconds": TIMEOUT,
            "max_retries": MAX_RETRIES,
            "retry_backoff_seconds": RETRY_BACKOFF,
            "thinking_parameter": "disabled",
        },
        "task_file_sha256": task_hash,
        "protocol_sha256": protocol_hash,
        "task": task,
        "task_index": task_index,
        "actor_order": actor_order,
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_decision_id": decision_id,
        "compiler": compiler,
        "actors": actors,
        "outcomes": {
            "history_only": exact_target(history),
            "decision_visible": exact_target(visible),
            "decision_enforced": exact_target(enforced),
        },
        "logical_calls_planned": 3,
        "logical_calls_attempted": sum(bool(component.get("attempts")) for component in components),
        "logical_calls_completed": sum(
            bool(component.get("attempts"))
            and component["attempts"][-1].get("status") == "success"
            for component in components
        ),
        "complete": compiler.get("parsed") is not None
        and all(actor.get("parsed") is not None for actor in actors.values()),
    }
    validate_run_row(row)
    return row


def stopped_row(
    task: dict[str, Any], model: str, task_index: int, run_scope: str, task_hash: str, protocol_hash: str
) -> dict[str, Any]:
    decision_id = _decision_id(model, task["id"], {"stopped": True})
    actors = {
        condition: skipped_component(condition, "not_run_after_stopping_rule", decision_id)
        for condition in ("history_only", "decision_visible")
    }
    for actor in actors.values():
        actor["compiler_decision_id"] = decision_id
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": run_scope,
        "timestamp_utc": utc_now(),
        "model": model,
        "endpoint": ENDPOINT,
        "api_settings": {
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "timeout_seconds": TIMEOUT,
            "max_retries": MAX_RETRIES,
            "retry_backoff_seconds": RETRY_BACKOFF,
            "thinking_parameter": "disabled",
        },
        "task_file_sha256": task_hash,
        "protocol_sha256": protocol_hash,
        "task": task,
        "task_index": task_index,
        "actor_order": [],
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_decision_id": decision_id,
        "compiler": skipped_component("compiler", "not_run_after_stopping_rule"),
        "actors": actors,
        "outcomes": {condition: None for condition in ("history_only", "decision_visible", "decision_enforced")},
        "logical_calls_planned": 3,
        "logical_calls_attempted": 0,
        "logical_calls_completed": 0,
        "complete": False,
    }
    validate_run_row(row)
    return row


def validate_smoke(rows: list[dict[str, Any]], tasks: list[dict[str, Any]], model: str) -> None:
    if len(rows) != 4 or [row["task"]["id"] for row in rows] != [task["id"] for task in tasks[:4]]:
        raise ValueError("health smoke does not match the first four frozen tasks")
    for row in rows:
        if row["model"] != model:
            raise ValueError("health-smoke model mismatch")
        validate_run_row(row, require_complete=True)


def validate_resume_prefix(
    rows: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    model: str,
    run_scope: str,
    task_hash: str,
    protocol_hash: str,
) -> None:
    if len(rows) >= len(tasks):
        raise ValueError("resume output is already complete or longer than the frozen inventory")
    expected_ids = [task["id"] for task in tasks[: len(rows)]]
    observed_ids = [row.get("task", {}).get("id") for row in rows]
    if observed_ids != expected_ids or len(set(observed_ids)) != len(observed_ids):
        raise ValueError("resume output is not the exact ordered frozen prefix")
    for index, row in enumerate(rows):
        validate_run_row(row, require_complete=True)
        if row.get("model") != model or row.get("run_scope") != run_scope:
            raise ValueError("resume output model or stage mismatch")
        if row.get("task_index") != index:
            raise ValueError("resume output task index mismatch")
        if row.get("task_file_sha256") != task_hash or row.get("protocol_sha256") != protocol_hash:
            raise ValueError("resume output freeze hash mismatch")


def dry_run(tasks: list[dict[str, Any]], audit: str, model: str, stage: str) -> dict[str, Any]:
    selected = tasks[:4] if stage == "health-smoke" else tasks
    sample = selected[0]
    decision = {
        "reference_mode": sample["reference_mode_gold"],
        "bound_target_id": sample["pre_refresh_target"]
        if sample["reference_mode_gold"] == "preserve"
        else None,
        "selector": sample["selector"],
    }
    history = build_actor_payload(sample, None)
    visible = build_actor_payload(sample, decision)
    visible_without_decision = dict(visible)
    visible_without_decision.pop("compiler_decision")
    return {
        "dry_run": True,
        "network_calls": 0,
        "audit": audit,
        "model": model,
        "stage": stage,
        "rows": len(selected),
        "clusters": len({task["pair_id"] for task in selected}),
        "logical_calls": 3 * len(selected),
        "actor_base_payloads_identical": history == visible_without_decision,
        "visible_only_field": "compiler_decision",
        "first_task_ids": [task["id"] for task in selected[:4]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one frozen revision matched audit.")
    parser.add_argument("--audit", required=True, choices=AUDITS)
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("health-smoke", "full"), default="health-smoke")
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="append only the missing suffix after validating an existing complete-row prefix",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    alias, model = resolve_model(args.model)
    if alias == "deepseek" and args.audit != "source_grounded":
        raise SystemExit("DeepSeek is frozen only for the source-grounded replication.")
    tasks, task_path, manifest = load_frozen(args.audit)
    output = args.output or ROOT / "runs" / f"revision_{args.audit}_{alias}_{args.stage.replace('-', '_')}_v1.jsonl"
    if args.dry_run:
        print(json.dumps(dry_run(tasks, args.audit, model, args.stage), indent=2))
        return
    if args.stage == "full":
        if args.health_smoke is None:
            raise SystemExit("A full run requires --health-smoke.")
        validate_smoke(load_jsonl(args.health_smoke), tasks, model)
    api_key = (os.environ.get("LLM_API_KEY") or os.environ.get("SILICONFLOW_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("Set LLM_API_KEY or SILICONFLOW_API_KEY; credentials are never serialized.")
    selected = tasks[:4] if args.stage == "health-smoke" else tasks
    output.parent.mkdir(parents=True, exist_ok=True)
    protocol_hash = manifest["protocol_sha256"]
    task_hash = sha256_path(task_path)
    existing: list[dict[str, Any]] = []
    if args.resume:
        if not output.exists():
            raise SystemExit("--resume requires an existing output file")
        existing = load_jsonl(output)
        validate_resume_prefix(existing, selected, model, args.stage, task_hash, protocol_hash)
    elif output.exists():
        raise SystemExit(f"Refusing to overwrite raw output: {output}; use --resume for a validated prefix")
    client = RecordingChatClient(
        model=model,
        base_url=ENDPOINT,
        api_key=api_key,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
        retry_backoff=RETRY_BACKOFF,
        max_tokens=MAX_TOKENS,
        enable_thinking=False,
    )
    stopped = False
    with output.open("a" if args.resume else "x", encoding="utf-8") as handle:
        for index, task in enumerate(selected[len(existing) :], start=len(existing)):
            row = (
                stopped_row(task, model, index, args.stage, task_hash, protocol_hash)
                if stopped
                else run_task(client, task, index, args.stage, task_hash, protocol_hash)
            )
            if not row["complete"]:
                stopped = True
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")
            handle.flush()
    rows = load_jsonl(output)
    if args.stage == "health-smoke":
        validate_smoke(rows, tasks, model)
    print(
        json.dumps(
            {
                "audit": args.audit,
                "output": str(output),
                "sha256": sha256_path(output),
                "model": model,
                "rows": len(rows),
                "complete_rows": sum(row["complete"] for row in rows),
                "full_stopped": stopped,
                "http_attempts": client.request_attempts,
                "retries": client.retry_events,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
