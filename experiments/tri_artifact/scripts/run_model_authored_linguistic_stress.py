#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scripts.run_call_matched_authorization_ablation import (
    RecordedCallError,
    RecordingChatClient,
    run_component,
)
from tri.model_authored_linguistic_stress import (
    AUTHOR_MODEL,
    AUTHOR_SYSTEM_PROMPT,
    CONTROLLERS,
    ENDPOINT,
    EVIDENCE_STATUS,
    JUDGE_SYSTEM_PROMPT,
    MAX_RETRIES,
    MAX_TOKENS,
    MODEL_IDS,
    RETRY_BACKOFF,
    RUN_VERSION,
    SEMANTIC_SPECS_SHA256,
    TEMPERATURE,
    TIMEOUT,
    build_author_payload,
    build_judge_payload,
    canonical_json,
    load_jsonl,
    parse_author_output,
    parse_judge_output,
    sha256_path,
    validate_semantic_specs,
    validate_tasks,
)
from tri.run_models import (
    has_internal_api_error,
    run_compile_then_act,
    run_generic_structured_ledger_then_act,
)


ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "data/model_authored_linguistic_semantics_v1.jsonl"
TASKS = ROOT / "data/model_authored_linguistic_stress_v1.jsonl"
PROTOCOL = ROOT / "reports/TRI_model_authored_linguistic_stress_protocol.md"
RUNS = ROOT / "runs"
FREEZE_MANIFEST = ROOT / "reports/model_authored_linguistic_stress_freeze_manifest_v1.json"
RUN_MODELS = ROOT / "tri/run_models.py"
RULE = ROOT / "tri/deterministic_discourse_rule_v2.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def messages(system: str, payload: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": canonical_json(payload)},
    ]


class RetainedControllerClient(RecordingChatClient):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.task_calls: list[dict[str, Any]] = []

    def begin_task(self) -> None:
        self.task_calls = []

    def chat(self, messages_value: list[dict[str, str]], temperature: float = 0.0) -> str:
        logical_call = f"controller_call_{len(self.task_calls) + 1}"
        try:
            raw, attempts, usage = self.chat_recorded(messages_value, temperature, logical_call)
        except RecordedCallError as exc:
            self.task_calls.append({
                "logical_call": logical_call,
                "attempts": exc.attempts,
                "status": "api_error",
                "error": str(exc),
            })
            raise RuntimeError(f"api_call_error: {exc}") from exc
        self.task_calls.append({
            "logical_call": logical_call,
            "attempts": attempts,
            "status": "ok",
            "usage": usage,
            "raw_content": raw,
        })
        return raw


def make_client(model: str, key: str) -> RecordingChatClient:
    return RecordingChatClient(
        model,
        ENDPOINT,
        key,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
        retry_backoff=RETRY_BACKOFF,
        max_tokens=MAX_TOKENS,
        enable_thinking=False,
    )


def validate_gate(path: Path, kind: str, model: str | None, controller: str | None) -> None:
    rows = load_jsonl(path)
    expected = 2 if kind == "author" else 4
    if len(rows) != expected:
        raise ValueError(f"{kind} smoke must contain {expected} rows")
    for row in rows:
        if row.get("run_version") != RUN_VERSION or row.get("run_scope") != "smoke":
            raise ValueError("smoke provenance mismatch")
        if row.get("kind") != kind or row.get("model_alias") != model or row.get("controller") != controller:
            raise ValueError("smoke condition mismatch")
        if row.get("status") != "ok":
            raise ValueError("smoke contains a failed row")
        if kind in {"author", "judge"} and row.get("parsed") is None:
            raise ValueError("smoke contains an unparsed row")
        if kind == "evaluate" and len(row.get("calls", [])) != 2:
            raise ValueError("controller smoke did not complete two logical calls")


def validate_second_stage_freeze() -> None:
    if not FREEZE_MANIFEST.exists():
        raise ValueError("second-stage freeze manifest is missing; build tasks after full authoring")
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    checks = (
        (TASKS, manifest["task_inventory"]["sha256"], "task inventory"),
        (PROTOCOL, manifest["protocol"]["sha256"], "protocol"),
        (RUN_MODELS, manifest["frozen_implementations"]["controllers_sha256"], "controller implementation"),
        (RULE, manifest["frozen_implementations"]["rule_v2_sha256"], "Rule* implementation"),
    )
    for path, expected, label in checks:
        if not path.exists() or sha256_path(path) != expected:
            raise ValueError(f"{label} does not match the second-stage freeze manifest")


def author_rows(client: RecordingChatClient, specs: list[dict[str, Any]], scope: str, on_row: Callable[[dict[str, Any]], None] | None = None) -> list[dict[str, Any]]:
    selected = specs[:2] if scope == "smoke" else specs
    rows = []
    for index, spec in enumerate(selected, 1):
        component = run_component(
            client,
            f"author_{index:02d}",
            AUTHOR_SYSTEM_PROMPT,
            build_author_payload(spec),
            parse_author_output,
        )
        row = {
            "run_version": RUN_VERSION,
            "evidence_status": EVIDENCE_STATUS,
            "kind": "author",
            "run_scope": scope,
            "model": AUTHOR_MODEL,
            "model_alias": None,
            "controller": None,
            "spec_index": index,
            "spec": spec,
            "status": "ok" if component["parsed"] is not None else component.get("error_kind", "error"),
            "parsed": component["parsed"],
            "error": component["error"],
            "attempts": component["attempts"],
            "usage": component["usage"],
            "recorded_at": utc_now(),
        }
        rows.append(row)
        if on_row:
            on_row(row)
    return rows


def judge_rows(client: RecordingChatClient, tasks: list[dict[str, Any]], scope: str, alias: str, on_row: Callable[[dict[str, Any]], None] | None = None) -> list[dict[str, Any]]:
    selected = tasks[:4] if scope == "smoke" else tasks
    rows = []
    for index, task in enumerate(selected, 1):
        if not task.get("generation_valid"):
            component = {"parsed": None, "error": "authoring_failure", "error_kind": "upstream", "attempts": [], "usage": {}}
        else:
            component = run_component(
                client,
                f"judge_{index:02d}",
                JUDGE_SYSTEM_PROMPT,
                build_judge_payload(task),
                parse_judge_output,
            )
        row = {
            "run_version": RUN_VERSION,
            "evidence_status": EVIDENCE_STATUS,
            "kind": "judge",
            "run_scope": scope,
            "model": MODEL_IDS[alias],
            "model_alias": alias,
            "controller": None,
            "task_index": index,
            "task": task,
            "status": "ok" if component["parsed"] is not None else component.get("error_kind", "error"),
            "parsed": component["parsed"],
            "error": component["error"],
            "attempts": component["attempts"],
            "usage": component["usage"],
            "recorded_at": utc_now(),
        }
        rows.append(row)
        if on_row:
            on_row(row)
    return rows


def evaluate_rows(client: RetainedControllerClient, tasks: list[dict[str, Any]], scope: str, alias: str, controller: str, on_row: Callable[[dict[str, Any]], None] | None = None) -> list[dict[str, Any]]:
    selected = tasks[:4] if scope == "smoke" else tasks
    rows = []
    runner = run_generic_structured_ledger_then_act if controller == "generic" else run_compile_then_act
    for index, task in enumerate(selected, 1):
        client.begin_task()
        if not task.get("generation_valid"):
            result = {"predicted_target": None, "success": False, "errors": ["authoring_failure"], "compiled_ledger": None}
            status = "authoring_failure"
        else:
            result = runner(client, task, TEMPERATURE)
            status = "api_or_parse_error" if has_internal_api_error(result) or result.get("errors") else "ok"
        row = {
            "run_version": RUN_VERSION,
            "evidence_status": EVIDENCE_STATUS,
            "kind": "evaluate",
            "run_scope": scope,
            "model": MODEL_IDS[alias],
            "model_alias": alias,
            "controller": controller,
            "task_index": index,
            "task": task,
            "status": status,
            "result": result,
            "calls": list(client.task_calls),
            "recorded_at": utc_now(),
        }
        rows.append(row)
        if on_row:
            on_row(row)
    return rows


def default_output(kind: str, scope: str, model: str | None, controller: str | None) -> Path:
    suffix = "_".join(value for value in (kind, model, controller, scope, "v1") if value)
    return RUNS / f"model_authored_linguistic_{suffix}.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("author", "judge", "evaluate"), required=True)
    parser.add_argument("--scope", choices=("smoke", "full"), required=True)
    parser.add_argument("--model", choices=tuple(MODEL_IDS))
    parser.add_argument("--controller", choices=CONTROLLERS)
    parser.add_argument("--smoke", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.kind == "author" and (args.model or args.controller):
        raise SystemExit("authoring takes neither --model nor --controller")
    if args.kind == "judge" and (not args.model or args.controller):
        raise SystemExit("judge requires --model and takes no --controller")
    if args.kind == "evaluate" and (not args.model or not args.controller):
        raise SystemExit("evaluate requires --model and --controller")
    if args.scope == "full":
        if args.smoke is None:
            raise SystemExit("full execution requires --smoke")
        validate_gate(args.smoke, args.kind, args.model, args.controller)

    key = os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("LLM_API_KEY")
    if not key or not key.strip():
        raise SystemExit("Set SILICONFLOW_API_KEY or LLM_API_KEY in the runtime environment.")
    if not PROTOCOL.exists():
        raise SystemExit(f"Frozen protocol is missing: {PROTOCOL}")

    output = args.output or default_output(args.kind, args.scope, args.model, args.controller)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("", encoding="utf-8")

    def persist(row: dict[str, Any]) -> None:
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    if args.kind == "author":
        specs = load_jsonl(SPECS)
        validate_semantic_specs(specs)
        if sha256_path(SPECS) != SEMANTIC_SPECS_SHA256:
            raise SystemExit("semantic inventory hash mismatch")
        client = make_client(AUTHOR_MODEL, key.strip())
        rows = author_rows(client, specs, args.scope, persist)
    else:
        validate_second_stage_freeze()
        tasks = load_jsonl(TASKS)
        validate_tasks(tasks)
        client = make_client(MODEL_IDS[args.model], key.strip())
        if args.kind == "judge":
            rows = judge_rows(client, tasks, args.scope, args.model, persist)
        else:
            retained = RetainedControllerClient(
                MODEL_IDS[args.model], ENDPOINT, key.strip(), timeout=TIMEOUT,
                max_retries=MAX_RETRIES, retry_backoff=RETRY_BACKOFF,
                max_tokens=MAX_TOKENS, enable_thinking=False,
            )
            rows = evaluate_rows(retained, tasks, args.scope, args.model, args.controller, persist)
    complete = sum(row["status"] == "ok" for row in rows)
    attempts = sum(len(row.get("attempts", [])) for row in rows)
    attempts += sum(len(call.get("attempts", [])) for row in rows for call in row.get("calls", []))
    print(json.dumps({
        "output": str(output),
        "sha256": sha256_path(output),
        "protocol_sha256": sha256_path(PROTOCOL),
        "rows": len(rows),
        "complete_rows": complete,
        "http_attempts": attempts,
    }, indent=2))
    if args.scope == "smoke" and complete != len(rows):
        raise SystemExit("health smoke failed; full execution is blocked")


if __name__ == "__main__":
    main()
