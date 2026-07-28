#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable
from uuid import uuid4

from tri.end_to_end_decision_decomposition import (
    ACTOR_CONDITIONS,
    ACTOR_SYSTEM_PROMPT,
    COMPILER_SYSTEM_PROMPT,
    EVIDENCE_STATUS,
    ENDPOINT,
    MODEL_IDS,
    RUN_SETTINGS,
    RUN_VERSION,
    TASK_FILE_SHA256,
    actor_base_payload_hash,
    actor_order,
    build_actor_payload,
    build_compiler_payload,
    canonical_json,
    load_frozen_tasks,
    load_jsonl,
    model_id_hash,
    parse_actor_output,
    parse_compiler_output,
    prompt_hashes,
    run_implementation_provenance,
    settings_hash,
    sha256_path,
    sha256_text,
    task_hash,
    validate_health_smoke,
    validate_run_inventory,
    validate_run_row,
)
from tri.run_models import ChatClient


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_end_to_end_decision_decomposition_protocol.md"
TEMPERATURE = RUN_SETTINGS["temperature"]
MAX_TOKENS = RUN_SETTINGS["max_tokens"]
TIMEOUT = RUN_SETTINGS["timeout_seconds"]
MAX_RETRIES = RUN_SETTINGS["max_retries"]
RETRY_BACKOFF = RUN_SETTINGS["retry_backoff_seconds"]


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
    """ChatClient-compatible transport retaining credential-free request attempts."""

    def chat_recorded(
        self, messages: list[dict[str, str]], temperature: float, logical_call: str
    ) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        body = build_request_body(self.model, messages, temperature, self.max_tokens)
        attempts: list[dict[str, Any]] = []
        for attempt_index in range(self.max_retries + 1):
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
                "started_at": utc_now(),
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


def skipped_component(logical_call: str, reason: str, compiler_output_id: str) -> dict[str, Any]:
    return {
        "logical_call": logical_call,
        "parsed": None,
        "error": reason,
        "error_kind": "upstream",
        "attempts": [],
        "usage": {},
        "compiler_output_id": compiler_output_id,
    }


def _compiler_output_id(model: str, task_id: str, compiler: dict[str, Any]) -> str:
    value = {"model": model, "task_id": task_id, "compiler": compiler}
    return "sha256:" + sha256_text(canonical_json(value))


def run_task(
    client: RecordingChatClient,
    task: dict[str, Any],
    task_index: int,
    run_scope: str,
    task_file_sha256: str,
    protocol_sha256: str,
    implementation_provenance: dict[str, Any],
    run_session_id: str,
    resumed_after_rows: int,
) -> dict[str, Any]:
    compiler = run_component(
        client,
        "compiler",
        COMPILER_SYSTEM_PROMPT,
        build_compiler_payload(task),
        parse_compiler_output,
    )
    compiler_id = _compiler_output_id(client.model, task["id"], compiler)
    order = actor_order(task_index)
    actors: dict[str, dict[str, Any]] = {}
    for condition in order:
        if condition != "history_only" and compiler["parsed"] is None:
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
    logical_attempted = sum(bool(component["attempts"]) for component in components)
    logical_completed = sum(
        bool(component["attempts"]) and component["attempts"][-1].get("status") == "success"
        for component in components
    )
    complete = all(component.get("parsed") is not None for component in components)
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": run_scope,
        "timestamp_utc": utc_now(),
        "model": client.model,
        "model_id_sha256": model_id_hash(client.model),
        "endpoint": ENDPOINT,
        "api_settings": {
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "timeout_seconds": TIMEOUT,
            "max_retries": MAX_RETRIES,
            "retry_backoff_seconds": RETRY_BACKOFF,
            "thinking_parameter": "disabled",
        },
        "settings_sha256": settings_hash(),
        "task_file_sha256": task_file_sha256,
        "protocol_sha256": protocol_sha256,
        "prompt_sha256": prompt_hashes(),
        "implementation_provenance": implementation_provenance,
        "recording_session": {
            "run_session_id": run_session_id,
            "resumed_after_rows": resumed_after_rows,
        },
        "task": task,
        "task_sha256": task_hash(task),
        "task_index": task_index,
        "actor_order": list(order),
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_output_id": compiler_id,
        "compiler": compiler,
        "actors": actors,
        "outcomes": {
            condition: (actors[condition].get("parsed") or {}).get("target_id")
            for condition in ACTOR_CONDITIONS
        },
        "logical_calls_planned": 6,
        "logical_calls_attempted": logical_attempted,
        "logical_calls_completed": logical_completed,
        "complete": complete,
    }
    validate_run_row(row)
    return row


def load_and_repair_resume_file(handle: BinaryIO) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Read complete JSONL rows and repair only a crash-torn final fragment."""
    handle.seek(0)
    data = handle.read()
    rows: list[dict[str, Any]] = []
    parts = data.split(b"\n")
    complete_parts = parts[:-1]
    for line_number, raw in enumerate(complete_parts, start=1):
        if not raw:
            raise ValueError(f"blank JSONL record at line {line_number}")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid completed JSONL record at line {line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"JSONL record at line {line_number} is not an object")
        rows.append(value)

    recovery = {"action": "none", "bytes_discarded": 0}
    tail = parts[-1]
    if tail:
        try:
            value = json.loads(tail.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            keep = len(data) - len(tail)
            handle.seek(keep)
            handle.truncate()
            handle.flush()
            os.fsync(handle.fileno())
            recovery = {"action": "discarded_torn_tail", "bytes_discarded": len(tail)}
        else:
            if not isinstance(value, dict):
                raise ValueError("unterminated final JSONL record is not an object")
            rows.append(value)
            handle.seek(0, os.SEEK_END)
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
            recovery = {"action": "completed_unterminated_row", "bytes_discarded": 0}
    return rows, recovery


def append_row_crash_safe(handle: BinaryIO, row: dict[str, Any]) -> None:
    encoded = (json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    handle.seek(0, os.SEEK_END)
    handle.write(encoded)
    handle.flush()
    os.fsync(handle.fileno())


def resolve_model(value: str) -> tuple[str, str]:
    lowered = value.lower()
    if lowered in MODEL_IDS:
        return lowered, MODEL_IDS[lowered]
    for alias, model in MODEL_IDS.items():
        if value == model:
            return alias, model
    raise ValueError(f"model must be one of: {', '.join([*MODEL_IDS, *MODEL_IDS.values()])}")


def dry_run_plan(
    tasks: list[dict[str, Any]], model: str, stage: str, output: Path
) -> dict[str, Any]:
    selected = tasks[:4] if stage == "smoke" else tasks
    sample_compiler = {
        "reference_mode": "preserve",
        "bound_target_id": "DRY-RUN-ID",
        "selector": selected[0]["selector"],
    }
    payloads = {
        condition: build_actor_payload(selected[0], sample_compiler, condition)
        for condition in ACTOR_CONDITIONS
    }
    bases = []
    for condition, payload in payloads.items():
        base = dict(payload)
        base.pop("compiler_fragment", None)
        base.pop("follow_instruction", None)
        bases.append(base)
    return {
        "dry_run": True,
        "network_calls": 0,
        "model": model,
        "stage": stage,
        "output": str(output),
        "rows": len(selected),
        "pairs": len({task["state_cluster_id"] for task in selected}),
        "logical_calls": {"compiler": len(selected), **{
            condition: len(selected) for condition in ACTOR_CONDITIONS
        }},
        "total_logical_calls": 6 * len(selected),
        "actor_base_payloads_identical": all(base == bases[0] for base in bases),
        "actor_order_first_five": [list(actor_order(index)) for index in range(5)],
        "task_file_sha256": TASK_FILE_SHA256,
        "prompt_sha256": prompt_hashes(),
        "settings_sha256": settings_hash(),
        "protocol_sha256": sha256_path(PROTOCOL),
        "implementation_provenance": run_implementation_provenance(ROOT),
        "task_ids": [task["id"] for task in selected],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the frozen end-to-end decision decomposition.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--stage", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--health-smoke", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    alias, model = resolve_model(args.model)
    tasks = load_frozen_tasks(args.tasks)
    selected = tasks[:4] if args.stage == "smoke" else tasks
    default_output = ROOT / "runs" / f"end_to_end_decision_decomposition_{alias}_{args.stage}_v1.jsonl"
    output = args.output or default_output
    protocol_sha256 = sha256_path(PROTOCOL)
    implementation_provenance = run_implementation_provenance(ROOT)

    if args.dry_run:
        print(json.dumps(dry_run_plan(tasks, model, args.stage, output), indent=2, ensure_ascii=False))
        return
    if args.stage == "full":
        if args.health_smoke is None:
            raise SystemExit("A full run requires --health-smoke with the matching four-row smoke JSONL.")
        validate_health_smoke(
            load_jsonl(args.health_smoke),
            model,
            tasks,
            protocol_sha256,
            implementation_provenance,
        )

    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not output.exists() and not api_key:
        raise SystemExit("Set LLM_API_KEY in the runtime environment; no other credential source is accepted.")
    output.parent.mkdir(parents=True, exist_ok=True)
    task_file_sha256 = sha256_path(args.tasks)
    run_session_id = str(uuid4())
    client: RecordingChatClient | None = None
    recovery: dict[str, Any]
    resumed_rows: int
    with output.open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit(f"Another process holds the run-file lock: {output}") from exc
        rows, recovery = load_and_repair_resume_file(handle)
        validate_run_inventory(
            rows,
            model,
            tasks,
            args.stage,
            protocol_sha256,
            implementation_provenance,
            require_exact=False,
        )
        resumed_rows = len(rows)
        if resumed_rows < len(selected):
            if not api_key:
                raise SystemExit(
                    "Set LLM_API_KEY to resume the incomplete run; persisted rows were validated "
                    "and will not be rerun."
                )
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
        for index in range(resumed_rows, len(selected)):
            task = selected[index]
            assert client is not None
            row = run_task(
                client,
                task,
                index,
                args.stage,
                task_file_sha256,
                protocol_sha256,
                implementation_provenance,
                run_session_id,
                resumed_rows,
            )
            append_row_crash_safe(handle, row)
            rows.append(row)
        validate_run_inventory(
            rows,
            model,
            tasks,
            args.stage,
            protocol_sha256,
            implementation_provenance,
            require_exact=True,
            require_complete=args.stage == "smoke",
        )

    rows = load_jsonl(output)
    if args.stage == "smoke":
        validate_health_smoke(
            rows, model, tasks, protocol_sha256, implementation_provenance
        )
    components = [
        component
        for row in rows
        for component in [
            row["compiler"],
            *(row["actors"][condition] for condition in ACTOR_CONDITIONS),
        ]
    ]
    print(json.dumps({
        "output": str(output),
        "sha256": sha256_path(output),
        "model": model,
        "rows": len(rows),
        "resumed_rows": resumed_rows,
        "new_rows": len(rows) - resumed_rows,
        "tail_recovery": recovery,
        "complete_rows": sum(bool(row["complete"]) for row in rows),
        "logical_calls_planned": 6 * len(rows),
        "logical_calls_attempted": sum(row["logical_calls_attempted"] for row in rows),
        "http_attempts": sum(len(component.get("attempts", [])) for component in components),
        "retries": sum(
            max(0, len(component.get("attempts", [])) - 1) for component in components
        ),
        "settings_sha256": settings_hash(),
        "protocol_sha256": protocol_sha256,
        "implementation_provenance": implementation_provenance,
    }, indent=2))


if __name__ == "__main__":
    main()
