#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tri.call_matched_authorization_ablation import (
    ACTOR_CONDITIONS,
    ACTOR_SYSTEM_PROMPT,
    COMPILER_SYSTEM_PROMPT,
    EVIDENCE_STATUS,
    MODEL_IDS,
    RUN_VERSION,
    TASK_FILE_SHA256,
    actor_base_payload_hash,
    build_actor_payload,
    build_compiler_payload,
    build_tasks,
    canonical_json,
    decision_enforced_target,
    load_jsonl,
    parse_actor_output,
    parse_compiler_output,
    sha256_bytes,
    sha256_path,
    validate_health_smoke,
    validate_run_row,
)
from tri.run_models import ChatClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_call_matched_authorization_ablation_protocol.md"
ENDPOINT = "https://api.siliconflow.cn/v1"
TEMPERATURE = 0.0
MAX_TOKENS = 500
TIMEOUT = 180
MAX_RETRIES = 2
RETRY_BACKOFF = 2.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_request_body(
    model: str, messages: list[dict[str, str]], temperature: float, max_tokens: int
) -> dict[str, Any]:
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_thinking": False,
    }


class RecordedCallError(RuntimeError):
    def __init__(self, message: str, attempts: list[dict[str, Any]]):
        super().__init__(message)
        self.attempts = attempts


class RecordingChatClient(ChatClient):
    """ChatClient-compatible caller that retains each credential-free HTTP attempt."""

    def chat_recorded(
        self, messages: list[dict[str, str]], temperature: float, logical_call: str
    ) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        body = build_request_body(self.model, messages, temperature, self.max_tokens)
        attempts: list[dict[str, Any]] = []
        for attempt_index in range(self.max_retries + 1):
            started = utc_now()
            request = urllib.request.Request(
                self.url,
                data=json.dumps(body).encode("utf-8"),
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            record: dict[str, Any] = {
                "logical_call": logical_call,
                "attempt_index": attempt_index,
                "started_at": started,
                "request": body,
            }
            self.request_attempts += 1
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    payload = json.load(response)
                    status_code = response.status
                content = payload["choices"][0]["message"]["content"]
                usage = payload.get("usage", {})
                self.usage_records.append(usage)
                record.update({
                    "finished_at": utc_now(),
                    "status": "success",
                    "http_status": status_code,
                    "raw_content": content,
                    "usage": usage,
                })
                attempts.append(record)
                return content, attempts, usage
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                record.update({
                    "finished_at": utc_now(),
                    "status": "error",
                    "error_kind": "api_response_schema",
                    "error": f"{type(exc).__name__}: malformed chat-completions response",
                    "retryable": False,
                })
                attempts.append(record)
                raise RecordedCallError(record["error"], attempts) from exc
            except urllib.error.HTTPError as exc:
                retryable = exc.code in self.RETRYABLE_HTTP_CODES
                record.update({
                    "finished_at": utc_now(),
                    "status": "error",
                    "error_kind": "api_http",
                    "http_status": exc.code,
                    "error": f"HTTP {exc.code}: {exc.reason}",
                    "retryable": retryable,
                })
                exc.close()
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                retryable = True
                record.update({
                    "finished_at": utc_now(),
                    "status": "error",
                    "error_kind": "api_network",
                    "error": f"{type(exc).__name__}: {exc}",
                    "retryable": True,
                })
            attempts.append(record)
            if not retryable or attempt_index == self.max_retries:
                raise RecordedCallError(record["error"], attempts)
            self.retry_events += 1
            time.sleep(min(self.retry_backoff * (2**attempt_index), 60.0))
        raise RecordedCallError("unreachable retry state", attempts)


def _messages(system_prompt: str, payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, sort_keys=True, ensure_ascii=False)},
    ]


def run_component(
    client: RecordingChatClient,
    logical_call: str,
    system_prompt: str,
    payload: dict[str, Any],
    parser: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    try:
        raw, attempts, usage = client.chat_recorded(
            _messages(system_prompt, payload), TEMPERATURE, logical_call
        )
    except RecordedCallError as exc:
        return {
            "logical_call": logical_call,
            "parsed": None,
            "error": f"api_call_error: {exc}",
            "error_kind": "api",
            "attempts": exc.attempts,
            "usage": {},
        }
    try:
        parsed = parser(raw)
        error = None
        error_kind = None
    except ValueError as exc:
        parsed = None
        error = str(exc)
        error_kind = "parse_or_schema"
    return {
        "logical_call": logical_call,
        "parsed": parsed,
        "error": error,
        "error_kind": error_kind,
        "attempts": attempts,
        "usage": usage,
    }


def skipped_component(logical_call: str, reason: str, decision_id: str | None = None) -> dict[str, Any]:
    component = {
        "logical_call": logical_call,
        "parsed": None,
        "error": reason,
        "error_kind": "upstream_or_stopping_rule",
        "attempts": [],
        "usage": {},
    }
    if decision_id is not None:
        component["compiler_decision_id"] = decision_id
    return component


def _decision_id(model: str, task_id: str, compiler: dict[str, Any]) -> str:
    payload = {"model": model, "task_id": task_id, "compiler": compiler}
    return "sha256:" + sha256_bytes(canonical_json(payload).encode("utf-8"))


def run_task(
    client: RecordingChatClient,
    task: dict[str, Any],
    task_index: int,
    run_scope: str,
    task_file_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    compiler = run_component(
        client,
        "compiler",
        COMPILER_SYSTEM_PROMPT,
        build_compiler_payload(task),
        parse_compiler_output,
    )
    decision_id = _decision_id(client.model, task["id"], compiler)
    actors: dict[str, dict[str, Any]] = {}
    if compiler["parsed"] is None:
        for condition in ACTOR_CONDITIONS:
            actors[condition] = skipped_component(
                condition, "skipped_after_compiler_failure", decision_id
            )
    else:
        order = ACTOR_CONDITIONS if task_index % 2 == 0 else tuple(reversed(ACTOR_CONDITIONS))
        for condition in order:
            decision = compiler["parsed"] if condition == "decision_visible" else None
            component = run_component(
                client,
                condition,
                ACTOR_SYSTEM_PROMPT,
                build_actor_payload(task, decision),
                parse_actor_output,
            )
            component["compiler_decision_id"] = decision_id
            actors[condition] = component

    history_target = (actors["history_only"].get("parsed") or {}).get("target_id")
    visible_target = (actors["decision_visible"].get("parsed") or {}).get("target_id")
    enforced_target = decision_enforced_target(
        compiler.get("parsed"), visible_target
    )
    components = [compiler, *(actors[name] for name in ACTOR_CONDITIONS)]
    logical_attempted = sum(bool(component["attempts"]) for component in components)
    logical_completed = sum(
        bool(component["attempts"]) and component["attempts"][-1].get("status") == "success"
        for component in components
    )
    complete = compiler["parsed"] is not None and all(
        actors[name]["parsed"] is not None for name in ACTOR_CONDITIONS
    )
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
        "task_file_sha256": task_file_sha256,
        "protocol_sha256": protocol_sha256,
        "task": task,
        "task_index": task_index,
        "actor_order": list(order) if compiler["parsed"] is not None else [],
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_decision_id": decision_id,
        "compiler": compiler,
        "actors": actors,
        "outcomes": {
            "history_only": history_target,
            "decision_visible": visible_target,
            "decision_enforced": enforced_target,
        },
        "shadow_actor_disagreement": (
            history_target != visible_target
            if actors["history_only"]["parsed"] is not None
            and actors["decision_visible"]["parsed"] is not None
            else None
        ),
        "enforcement_correct": visible_target != task["correct_target"]
        and enforced_target == task["correct_target"],
        "enforcement_harm": visible_target == task["correct_target"]
        and enforced_target != task["correct_target"],
        "logical_calls_planned": 3,
        "logical_calls_attempted": logical_attempted,
        "logical_calls_completed": logical_completed,
        "complete": complete,
    }
    validate_run_row(row)
    return row


def stopping_rule_row(
    task: dict[str, Any],
    model: str,
    task_index: int,
    run_scope: str,
    task_file_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    decision_id = _decision_id(model, task["id"], {"stopped": True})
    actors = {
        condition: skipped_component(condition, "not_run_after_stopping_rule", decision_id)
        for condition in ACTOR_CONDITIONS
    }
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
        "task_file_sha256": task_file_sha256,
        "protocol_sha256": protocol_sha256,
        "task": task,
        "task_index": task_index,
        "actor_order": [],
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_decision_id": decision_id,
        "compiler": skipped_component("compiler", "not_run_after_stopping_rule"),
        "actors": actors,
        "outcomes": {
            "history_only": None,
            "decision_visible": None,
            "decision_enforced": None,
        },
        "shadow_actor_disagreement": None,
        "enforcement_correct": False,
        "enforcement_harm": False,
        "logical_calls_planned": 3,
        "logical_calls_attempted": 0,
        "logical_calls_completed": 0,
        "complete": False,
    }
    validate_run_row(row)
    return row


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"model must be one of: {', '.join([*MODEL_IDS, *MODEL_IDS.values()])}")


def load_frozen_tasks(path: Path) -> list[dict[str, Any]]:
    if sha256_path(path) != TASK_FILE_SHA256:
        raise ValueError("task file hash does not match the frozen protocol manifest")
    tasks = load_jsonl(path)
    expected = build_tasks(SOURCE)
    if tasks != expected:
        raise ValueError("task file does not match automatic selection from the frozen source")
    return tasks


def dry_run_plan(
    tasks: list[dict[str, Any]], model: str, stage: str, output: Path, limit: int | None
) -> dict[str, Any]:
    selected = tasks[:4] if stage == "health-smoke" else tasks
    if limit is not None:
        selected = selected[:limit]
    sample = selected[0]
    decision = {
        "reference_mode": sample["reference_mode_gold"],
        "bound_target_id": sample["pre_refresh_target"] if sample["reference_mode_gold"] == "preserve" else None,
        "selector": sample["selector"],
    }
    history = build_actor_payload(sample, None)
    visible = build_actor_payload(sample, decision)
    visible_without_decision = dict(visible)
    visible_without_decision.pop("compiler_decision")
    return {
        "dry_run": True,
        "network_calls": 0,
        "model": model,
        "stage": stage,
        "output": str(output),
        "tasks": len(selected),
        "state_clusters": len({task["state_cluster_id"] for task in selected}),
        "logical_calls": {"compiler": len(selected), "history_only": len(selected), "decision_visible": len(selected)},
        "total_logical_calls": 3 * len(selected),
        "actor_base_payloads_identical": history == visible_without_decision,
        "visible_only_field": "compiler_decision",
        "shared_compiler_decisions": len(selected),
        "task_ids": [task["id"] for task in selected],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the frozen matched authorization ablation.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("health-smoke", "full"), default="health-smoke")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    alias, model = resolve_model(args.model)
    tasks = load_frozen_tasks(args.tasks)
    default_output = ROOT / "runs" / f"call_matched_authorization_{alias}_{args.stage.replace('-', '_')}_v2.jsonl"
    output = args.output or default_output
    selected = tasks[:4] if args.stage == "health-smoke" else tasks
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit("--limit must be positive")
        selected = selected[: args.limit]

    if args.dry_run:
        print(json.dumps(dry_run_plan(tasks, model, args.stage, output, args.limit), indent=2, ensure_ascii=False))
        return

    if args.stage == "health-smoke" and len(selected) != 4:
        raise SystemExit("A real health smoke must contain exactly four tasks; omit --limit or use --limit 4.")
    if args.stage == "full":
        if args.health_smoke is None:
            raise SystemExit("A full run requires --health-smoke with the matching four-task run JSONL.")
        validate_health_smoke(load_jsonl(args.health_smoke), model, tasks)

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set LLM_API_KEY in the runtime environment; no other credential source is accepted.")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite an existing raw run: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    task_hash = sha256_path(args.tasks)
    protocol_hash = sha256_path(PROTOCOL)
    run_scope = args.stage if args.limit is None else f"limited-{args.stage}"
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
    stop = False
    with output.open("x", encoding="utf-8") as handle:
        for index, task in enumerate(selected):
            if stop:
                row = stopping_rule_row(task, model, index, run_scope, task_hash, protocol_hash)
            else:
                row = run_task(client, task, index, run_scope, task_hash, protocol_hash)
                if not row["complete"]:
                    stop = True
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
            handle.flush()

    rows = load_jsonl(output)
    if args.stage == "health-smoke":
        validate_health_smoke(rows, model, tasks)
    print(json.dumps({
        "output": str(output),
        "sha256": sha256_path(output),
        "model": model,
        "rows": len(rows),
        "complete_rows": sum(row["complete"] for row in rows),
        "full_stopped": stop,
        "http_attempts": client.request_attempts,
        "retries": client.retry_events,
    }, indent=2))


if __name__ == "__main__":
    main()
