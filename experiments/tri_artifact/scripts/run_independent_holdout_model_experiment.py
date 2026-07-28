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
)
from tri.call_matched_authorization_ablation import (
    COMPILER_SYSTEM_PROMPT,
    build_compiler_payload,
    load_jsonl,
    sha256_path,
)
from tri.independent_holdout_model_experiment import (
    ACTOR_CONDITIONS,
    EVIDENCE_STATUS,
    MODEL_IDS,
    RUN_VERSION,
    actor_payload,
    actor_prompt,
    freeze_prompt_hash,
    offline_rule,
    parse_actor,
    sqlite_consistency,
    validate_run_row,
)
from tri.independent_language_holdout import validate_model_tasks
from tri.revision_matched_audit import parse_compiler_exact


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "independent_language_holdout_v1.jsonl"
MANIFEST = ROOT / "reports" / "independent_language_holdout_model_freeze_v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def api_key_from_environment() -> str:
    """Return only the frozen runtime secret name; aliases are intentionally rejected."""
    return os.environ.get("LLM_API_KEY", "").strip()


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"unknown model: {value}")


def load_frozen() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not TASKS.exists() or not MANIFEST.exists():
        raise ValueError("human returns, annotations, model tasks, and freeze manifest are not complete")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sha256_path(TASKS) != manifest["task_sha256"]:
        raise ValueError("model task hash differs from the freeze manifest")
    if freeze_prompt_hash() != manifest["prompt_sha256"]:
        raise ValueError("model prompts changed after freeze")
    tasks = load_jsonl(TASKS)
    validate_model_tasks(tasks)
    return tasks, manifest


def run_task(client: RecordingChatClient, task: dict[str, Any], index: int, stage: str, manifest: dict[str, Any]):
    compiler = run_component(
        client,
        "compiler",
        COMPILER_SYSTEM_PROMPT,
        build_compiler_payload(task),
        lambda text: parse_compiler_exact(text, task),
    )
    actors = {}
    outcomes = {}
    decision = compiler.get("parsed")
    for condition in ACTOR_CONDITIONS:
        if decision is None and condition in {"decision_visible", "cta"}:
            actors[condition] = {
                "logical_call": condition,
                "parsed": None,
                "error": "skipped_after_compiler_failure",
                "error_kind": "upstream",
                "attempts": [],
                "usage": {},
            }
            outcomes[condition] = None
            continue
        payload_decision = decision or {
            "reference_mode": task["reference_mode_design"],
            "bound_target_id": task["pre_refresh_target"]
            if task["reference_mode_design"] == "preserve"
            else None,
            "selector": task["selector"],
        }
        component = run_component(
            client,
            condition,
            actor_prompt(condition),
            actor_payload(task, condition, payload_decision),
            lambda text, task=task: parse_actor(text, task),
        )
        actors[condition] = component
        outcomes[condition] = (component.get("parsed") or {}).get("target_id")
    components = [compiler, *actors.values()]
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": stage,
        "timestamp_utc": utc_now(),
        "model": client.model,
        "endpoint": ENDPOINT,
        "task_file_sha256": manifest["task_sha256"],
        "protocol_sha256": manifest["protocol_sha256"],
        "prompt_sha256": manifest["prompt_sha256"],
        "task_index": index,
        "task": task,
        "compiler": compiler,
        "actors": actors,
        "outcomes": outcomes,
        "sqlite_consistency": {
            condition: sqlite_consistency(task, outcomes.get(condition))
            for condition in ACTOR_CONDITIONS
        },
        "rule_star": offline_rule(task),
        "logical_calls_planned": 5,
        "logical_calls_attempted": sum(bool(component.get("attempts")) for component in components),
        "logical_calls_completed": sum(
            bool(component.get("attempts")) and component["attempts"][-1].get("status") == "success"
            for component in components
        ),
        "complete": compiler.get("parsed") is not None
        and all(component.get("parsed") is not None for component in actors.values()),
    }
    validate_run_row(row)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("health-smoke", "full"), default="health-smoke")
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    alias, model = resolve_model(args.model)
    tasks, manifest = load_frozen()
    selected = tasks[:4] if args.stage == "health-smoke" else tasks
    if args.dry_run:
        print(json.dumps({"network_calls": 0, "rows": len(selected), "logical_calls": 5 * len(selected), "model": model}, indent=2))
        return
    if args.stage == "full":
        if not args.health_smoke:
            raise SystemExit("full requires --health-smoke")
        smoke = load_jsonl(args.health_smoke)
        if len(smoke) != 4 or any(not row.get("complete") for row in smoke):
            raise SystemExit("health smoke is absent or incomplete")
    key = api_key_from_environment()
    if not key:
        raise SystemExit("Set LLM_API_KEY")
    output = args.output or ROOT / "runs" / f"independent_holdout_{alias}_{args.stage.replace('-', '_')}_v1.jsonl"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite {output}")
    client = RecordingChatClient(
        model=model,
        base_url=ENDPOINT,
        api_key=key,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
        retry_backoff=RETRY_BACKOFF,
        max_tokens=MAX_TOKENS,
        enable_thinking=False,
    )
    with output.open("x", encoding="utf-8") as handle:
        for index, task in enumerate(selected):
            handle.write(json.dumps(run_task(client, task, index, args.stage, manifest), sort_keys=True) + "\n")
            handle.flush()
    rows = load_jsonl(output)
    if args.stage == "health-smoke":
        for row in rows:
            validate_run_row(row, require_complete=True)
    print(json.dumps({"output": str(output), "rows": len(rows), "complete_rows": sum(row["complete"] for row in rows), "http_attempts": client.request_attempts}, indent=2))


if __name__ == "__main__":
    main()
