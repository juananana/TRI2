#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
from uuid import uuid4

from scripts.run_end_to_end_decision_decomposition import (
    RecordingChatClient,
    append_row_crash_safe,
    load_and_repair_resume_file,
    run_component,
    skipped_component,
    utc_now,
)
from tri.end_to_end_decision_decomposition import canonical_json, sha256_path, sha256_text
from tri.end_to_end_decision_decomposition_v2 import (
    ACTOR_CONDITIONS,
    ACTOR_SYSTEM_PROMPT,
    COMPILER_DEPENDENT,
    COMPILER_SYSTEM_PROMPT,
    EVIDENCE_STATUS,
    ENDPOINT,
    MODEL_IDS,
    RUN_SETTINGS,
    RUN_VERSION,
    TASK_FILE_SHA256,
    actor_order,
    build_actor_base_payload,
    build_actor_payload,
    build_compiler_payload,
    load_frozen_tasks,
    parse_actor_output,
    parse_compiler_output,
    prompt_hashes,
    settings_hash,
    validate_run_inventory,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_end_to_end_decision_decomposition_v2_protocol.md"
SMOKE_ROWS = 8


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"unknown model: {value}")


def implementation_provenance() -> dict[str, str]:
    return {
        "core_sha256": sha256_path(ROOT / "tri" / "end_to_end_decision_decomposition_v2.py"),
        "runner_sha256": sha256_path(Path(__file__)),
    }


def _compiler_output_id(model: str, task_id: str, compiler: dict) -> str:
    return "sha256:" + sha256_text(canonical_json({"model": model, "task": task_id, "compiler": compiler}))


def run_task(
    client: RecordingChatClient,
    task: dict,
    task_index: int,
    scope: str,
    protocol_sha256: str,
    session_id: str,
    resumed_after_rows: int,
) -> dict:
    compiler = run_component(
        client,
        "compiler",
        COMPILER_SYSTEM_PROMPT,
        build_compiler_payload(task),
        parse_compiler_output,
    )
    compiler_id = _compiler_output_id(client.model, task["id"], compiler)
    actors = {}
    for condition in actor_order(task_index):
        if condition in COMPILER_DEPENDENT and compiler["parsed"] is None:
            actors[condition] = skipped_component(
                condition, "skipped_after_compiler_failure", compiler_id
            )
            continue
        component = run_component(
            client,
            condition,
            ACTOR_SYSTEM_PROMPT,
            build_actor_payload(task, compiler["parsed"], condition),
            parse_actor_output,
        )
        component["compiler_output_id"] = compiler_id
        actors[condition] = component
    components = [compiler, *(actors[name] for name in ACTOR_CONDITIONS)]
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": scope,
        "timestamp_utc": utc_now(),
        "model": client.model,
        "task_file_sha256": TASK_FILE_SHA256,
        "protocol_sha256": protocol_sha256,
        "prompt_sha256": prompt_hashes(),
        "settings_sha256": settings_hash(),
        "implementation_provenance": implementation_provenance(),
        "recording_session": {
            "run_session_id": session_id,
            "resumed_after_rows": resumed_after_rows,
        },
        "task": task,
        "task_sha256": sha256_text(canonical_json(task)),
        "task_index": task_index,
        "actor_order": list(actor_order(task_index)),
        "actor_base_payload_sha256": sha256_text(canonical_json(build_actor_base_payload(task))),
        "compiler_output_id": compiler_id,
        "compiler": compiler,
        "actors": actors,
        "outcomes": {
            name: (actors[name].get("parsed") or {}).get("target_id")
            for name in ACTOR_CONDITIONS
        },
        "logical_calls_planned": 9,
        "logical_calls_attempted": sum(bool(item.get("attempts")) for item in components),
        "logical_calls_completed": sum(
            bool(item.get("attempts")) and item["attempts"][-1].get("status") == "success"
            for item in components
        ),
        "complete": all(item.get("parsed") is not None for item in components),
    }
    validate_run_row(row)
    return row


def validate_prefix(rows: list[dict], model: str, selected: list[dict]) -> None:
    if len(rows) > len(selected):
        raise ValueError("resume file is longer than the frozen scope")
    if [row.get("task", {}).get("id") for row in rows] != [task["id"] for task in selected[: len(rows)]]:
        raise ValueError("resume file is not a frozen task prefix")
    for row in rows:
        if row.get("model") != model:
            raise ValueError("resume file model mismatch")
        validate_run_row(row)


def dry_run_plan(tasks: list[dict], model: str, stage: str, output: Path) -> dict:
    selected = tasks[:SMOKE_ROWS] if stage == "smoke" else tasks
    compiler = {
        "reference_mode": "preserve",
        "pre_refresh_candidate_id": "DRY-RUN-ID",
        "bound_target_id": "DRY-RUN-ID",
        "selector": selected[0]["selector"],
    }
    payloads = {
        condition: build_actor_payload(selected[0], compiler, condition)
        for condition in ACTOR_CONDITIONS
    }
    stripped = []
    for payload in payloads.values():
        base = dict(payload)
        base.pop("context_summary", None)
        base.pop("compiler_fragment", None)
        base.pop("follow_instruction", None)
        stripped.append(base)
    return {
        "dry_run": True,
        "network_calls": 0,
        "model": model,
        "stage": stage,
        "output": str(output),
        "rows": len(selected),
        "total_logical_calls": 9 * len(selected),
        "actor_base_payloads_identical": all(item == stripped[0] for item in stripped),
        "actor_order_first_eight": [list(actor_order(index)) for index in range(8)],
        "task_file_sha256": TASK_FILE_SHA256,
        "protocol_sha256": sha256_path(PROTOCOL),
        "prompt_sha256": prompt_hashes(),
        "settings_sha256": settings_hash(),
        "implementation_provenance": implementation_provenance(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run frozen Decision Decomposition v2.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    alias, model = resolve_model(args.model)
    tasks = load_frozen_tasks(TASKS)
    selected = tasks[:SMOKE_ROWS] if args.stage == "smoke" else tasks
    output = args.output or ROOT / "runs" / f"end_to_end_decision_decomposition_v2_{alias}_{args.stage}.jsonl"
    if args.dry_run:
        print(json.dumps(dry_run_plan(tasks, model, args.stage, output), indent=2))
        return
    if args.stage == "full":
        if args.health_smoke is None:
            raise SystemExit("full run requires --health-smoke")
        smoke_rows = [json.loads(line) for line in args.health_smoke.read_text().splitlines() if line.strip()]
        validate_run_inventory(smoke_rows, model, tasks[:SMOKE_ROWS])
        if any(not row.get("complete") for row in smoke_rows):
            raise SystemExit("health smoke contains incomplete rows")

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not output.exists() and not api_key:
        raise SystemExit("Set LLM_API_KEY at runtime; credentials are never read from files.")
    output.parent.mkdir(parents=True, exist_ok=True)
    protocol_sha256 = sha256_path(PROTOCOL)
    session_id = str(uuid4())
    with output.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        rows, recovery = load_and_repair_resume_file(handle)
        validate_prefix(rows, model, selected)
        resumed = len(rows)
        client = None
        if resumed < len(selected):
            if not api_key:
                raise SystemExit("Set LLM_API_KEY to resume the validated incomplete run.")
            client = RecordingChatClient(
                model=model,
                base_url=ENDPOINT,
                api_key=api_key,
                timeout=RUN_SETTINGS["timeout_seconds"],
                max_retries=RUN_SETTINGS["max_retries"],
                retry_backoff=RUN_SETTINGS["retry_backoff_seconds"],
                max_tokens=RUN_SETTINGS["max_tokens"],
                enable_thinking=False,
            )
        for index in range(resumed, len(selected)):
            assert client is not None
            row = run_task(
                client, selected[index], index, args.stage, protocol_sha256, session_id, resumed
            )
            append_row_crash_safe(handle, row)
            rows.append(row)
        validate_run_inventory(rows, model, selected)
    print(json.dumps({
        "output": str(output),
        "rows": len(rows),
        "new_rows": len(rows) - resumed,
        "complete_rows": sum(bool(row.get("complete")) for row in rows),
        "logical_calls_planned": 9 * len(rows),
        "tail_recovery": recovery,
        "sha256": sha256_path(output),
    }, indent=2))


if __name__ == "__main__":
    main()
