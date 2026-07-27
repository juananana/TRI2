#!/usr/bin/env python3
"""Run the frozen source-anchored external transfer model conditions."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from tri.source_anchored_external_transfer import (
    _verify_agentdojo_task,
    _verify_state_task,
    sha256_bytes,
)


RUN_VERSION = "TRI-source-anchored-external-transfer-model-v1"
DEFAULT_ENDPOINT = "https://api.siliconflow.cn/v1"
DEFAULT_MODELS = ("Qwen/Qwen3.5-122B-A10B", "Pro/zai-org/GLM-5.1")
CONTROLLERS = ("ordinary_full_history", "execution_record")
TARGET_PARAMETERS = {
    "add": "product_id",
    "update": "product_id",
    "remove": "product_id",
    "append": "file_id",
    "share": "file_id",
    "delete": "file_id",
    "delete_email": "email_id",
    "reschedule": "event_id",
    "cancel_event": "event_id",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_object(content: str) -> tuple[dict[str, Any] | None, str | None]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_parse_error: {exc}"
    if not isinstance(parsed, dict):
        return None, "schema_error: top-level value is not an object"
    return parsed, None


def _retryable(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or 500 <= exc.code <= 599
    return isinstance(exc, (urllib.error.URLError, TimeoutError, OSError))


def call_chat(
    *,
    endpoint: str,
    api_key: str,
    model: str,
    system_prompt: str,
    payload: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, sort_keys=True, ensure_ascii=True)},
        ],
        "temperature": 0,
        "max_tokens": 500,
        "enable_thinking": False,
    }
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def call_with_retry(**kwargs: Any) -> tuple[dict[str, Any] | None, int, str | None]:
    attempts = 0
    for attempt in range(2):
        attempts += 1
        try:
            return call_chat(**kwargs), attempts, None
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if attempt == 0 and _retryable(exc):
                time.sleep(2)
                continue
            return None, attempts, error
    raise AssertionError("unreachable")


def _response_fields(response: dict[str, Any] | None) -> tuple[str, dict[str, Any], str | None]:
    if response is None:
        return "", {}, None
    try:
        message = response["choices"][0]["message"]
        return str(message.get("content") or ""), response.get("usage", {}) or {}, response.get("id")
    except (KeyError, IndexError, TypeError):
        return "", response.get("usage", {}) or {}, response.get("id")


def _refreshed_entities(task: dict[str, Any]) -> list[dict[str, Any]]:
    rows = json.loads(json.dumps(task["source_entities"]))
    patch = task["refresh_patch"]
    for row in rows:
        if row["entity_id"] == patch["entity_id"]:
            row[patch["field"]] = patch["new_value"]
            return rows
    raise ValueError("refresh target missing from source observation")


def _source_tool_schema(task: dict[str, Any]) -> dict[str, Any]:
    target_parameter = TARGET_PARAMETERS[task["action"]]
    properties: dict[str, Any] = {target_parameter: {"type": "string"}}
    required = [target_parameter]
    if task["repository"] == "STATE-Bench":
        properties["customer_id"] = {"type": "string", "const": task["customer_id"]}
        required.insert(0, "customer_id")
    if task["action"] == "add":
        properties["quantity"] = {"type": "integer", "const": 1}
    elif task["action"] == "update":
        properties["gift_wrap"] = {"type": "boolean", "description": "opposite of the current value"}
    elif task["action"] == "append":
        properties["content"] = {"type": "string", "const": "SOURCE_ANCHORED_TRANSFER_AUDIT"}
    elif task["action"] == "share":
        properties.update(
            {
                "email": {"type": "string", "const": "external.audit@example.com"},
                "permission": {"type": "string", "const": "r"},
            }
        )
    elif task["action"] == "reschedule":
        properties["new_start_time"] = {"type": "string", "description": "seven days after the current start"}
    return {
        "name": task["write_tool"],
        "parameters": {"type": "object", "properties": properties, "required": required},
        "target_parameter": target_parameter,
    }


def _selection_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_message": task["messages"][0]["content"],
        "source_tool_call": {"tool": task["read_tool"], "arguments": {"scope": task.get("scope_query")}},
        "source_tool_result": task["source_entities"],
        "selection_rule": task["selector"],
    }


def _final_payload(
    task: dict[str, Any], controller: str, selection_content: str, selected_id: str | None
) -> dict[str, Any]:
    payload = {
        "first_user_message": task["messages"][0]["content"],
        "first_source_tool_result": task["source_entities"],
        "assistant_selection_response": selection_content,
        "second_user_message": task["messages"][1]["content"],
        "second_source_tool_call": {"tool": task["read_tool"], "arguments": {"scope": task.get("scope_query")}},
        "second_source_tool_result": _refreshed_entities(task),
        "write_tool_schema": _source_tool_schema(task),
    }
    if controller == "execution_record":
        payload["execution_record"] = {
            "selection_time": "before_update" if task["timing"] == "preserve" else "after_update",
            "selected_target_id": selected_id if task["timing"] == "preserve" else None,
            "selection_rule": task["selector"],
        }
    return payload


def _execute_source_write(
    task: dict[str, Any], predicted: str, state_root: Path, agentdojo_root: Path
) -> tuple[bool, str | None]:
    execution_task = dict(task)
    execution_task["expected_target_id"] = predicted
    try:
        if task["repository"] == "STATE-Bench":
            _verify_state_task(execution_task, state_root)
        else:
            _verify_agentdojo_task(execution_task, agentdojo_root)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def run_one(
    *,
    task: dict[str, Any],
    model: str,
    controller: str,
    endpoint: str,
    api_key: str,
    prompts: dict[str, str],
    prompt_hashes: dict[str, str],
    inventory_hash: str,
    timeout: int,
    state_root: Path,
    agentdojo_root: Path,
) -> dict[str, Any]:
    started = time.time()
    first_response, first_attempts, first_transport_error = call_with_retry(
        endpoint=endpoint,
        api_key=api_key,
        model=model,
        system_prompt=prompts["selection"],
        payload=_selection_payload(task),
        timeout=timeout,
    )
    first_content, first_usage, first_response_id = _response_fields(first_response)
    first_object, first_parse_error = parse_object(first_content) if first_content else (None, "missing_response")
    selected_id = None
    if first_object is not None:
        value = first_object.get("selected_target_id")
        if isinstance(value, (str, int)):
            selected_id = str(value)
        else:
            first_parse_error = "schema_error: selected_target_id missing"

    second_response = None
    second_attempts = 0
    second_transport_error = None
    second_content = ""
    second_usage: dict[str, Any] = {}
    second_response_id = None
    second_parse_error = "not_attempted_after_invalid_initial_selection"
    predicted = None
    tool_name = None
    if selected_id is not None and first_transport_error is None and first_parse_error is None:
        second_response, second_attempts, second_transport_error = call_with_retry(
            endpoint=endpoint,
            api_key=api_key,
            model=model,
            system_prompt=prompts[controller],
            payload=_final_payload(task, controller, first_content, selected_id),
            timeout=timeout,
        )
        second_content, second_usage, second_response_id = _response_fields(second_response)
        second_object, second_parse_error = (
            parse_object(second_content) if second_content else (None, "missing_response")
        )
        if second_object is not None:
            tool_name = second_object.get("tool")
            arguments = second_object.get("arguments")
            target_parameter = TARGET_PARAMETERS[task["action"]]
            if not isinstance(arguments, dict) or not isinstance(arguments.get(target_parameter), (str, int)):
                second_parse_error = f"schema_error: arguments.{target_parameter} missing"
            else:
                predicted = str(arguments[target_parameter])
            if tool_name != task["write_tool"]:
                second_parse_error = "schema_error: write tool mismatch"

    write_executed = False
    execution_error = None
    if predicted is not None and second_parse_error is None and second_transport_error is None:
        write_executed, execution_error = _execute_source_write(
            task, predicted, state_root, agentdojo_root
        )
    valid = (
        first_transport_error is None
        and second_transport_error is None
        and first_parse_error is None
        and second_parse_error is None
        and write_executed
    )
    return {
        "run_version": RUN_VERSION,
        "task_id": task["task_id"],
        "cluster_id": task["cluster_id"],
        "repository": task["repository"],
        "domain": task["domain"],
        "timing": task["timing"],
        "transition": task["transition"],
        "model": model,
        "controller": controller,
        "endpoint": endpoint,
        "temperature": 0,
        "max_tokens": 500,
        "enable_thinking": False,
        "inventory_sha256": inventory_hash,
        "prompt_sha256": prompt_hashes,
        "request_attempts": first_attempts + second_attempts,
        "first_transport_error": first_transport_error,
        "second_transport_error": second_transport_error,
        "first_parse_error": first_parse_error,
        "second_parse_error": second_parse_error,
        "selected_target_id": selected_id,
        "initial_binding_correct": selected_id == task["initial_winner_id"],
        "initial_winner_id": task["initial_winner_id"],
        "refreshed_winner_id": task["refreshed_winner_id"],
        "predicted_target_id": predicted,
        "expected_target_id": task["expected_target_id"],
        "old_target_present_after_refresh": task["old_target_present_after_refresh"],
        "old_target_action_valid_after_refresh": task["old_target_action_valid_after_refresh"],
        "write_tool_returned": tool_name,
        "write_executed": write_executed,
        "source_execution_error": execution_error,
        "exact_target_success": valid and predicted == task["expected_target_id"],
        "wrong_entity_write": write_executed and predicted != task["expected_target_id"],
        "status": "ok" if valid else "failed",
        "first_raw_content": first_content,
        "second_raw_content": second_content,
        "first_response_id": first_response_id,
        "second_response_id": second_response_id,
        "usage": {"first": first_usage, "second": second_usage},
        "latency_s": round(time.time() - started, 3),
    }


def select_smoke(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_clusters: list[str] = []
    for repository in sorted({task["repository"] for task in tasks}):
        selected_clusters.append(
            sorted({task["cluster_id"] for task in tasks if task["repository"] == repository})[0]
        )
    return [task for task in tasks if task["cluster_id"] in selected_clusters]


def parse_args() -> argparse.Namespace:
    artifact = Path(__file__).resolve().parents[1]
    project = artifact.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory",
        type=Path,
        default=artifact / "data/source_anchored_external_transfer_tasks_v1.jsonl",
    )
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--controllers", nargs="+", choices=CONTROLLERS, default=list(CONTROLLERS))
    parser.add_argument("--endpoint", default=os.environ.get("LLM_BASE_URL", DEFAULT_ENDPOINT))
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=artifact / "runs/source_anchored_external_transfer_siliconflow_v1.jsonl",
    )
    parser.add_argument(
        "--state-bench-root", type=Path, default=project / "external_sources/state-bench"
    )
    parser.add_argument(
        "--agentdojo-root", type=Path, default=project / "external_sources/agentdojo"
    )
    parser.add_argument(
        "--agentdojo-deps-root", type=Path, default=project / "external_sources/agentdojo-deps"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    missing_roots = [
        str(path)
        for path in (args.state_bench_root, args.agentdojo_root, args.agentdojo_deps_root)
        if not path.is_dir()
    ]
    if missing_roots:
        raise SystemExit(f"Missing source runtime directories: {', '.join(missing_roots)}")
    api_key = os.environ.get("SILICONFLOW_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        raise SystemExit("Set SILICONFLOW_API_KEY or LLM_API_KEY in the environment.")
    for path in (args.agentdojo_deps_root, args.agentdojo_root / "src", args.state_bench_root):
        if str(path) not in os.sys.path:
            os.sys.path.insert(0, str(path))

    inventory_bytes = args.inventory.read_bytes()
    inventory_hash = sha256_bytes(inventory_bytes)
    tasks = load_jsonl(args.inventory)
    if args.smoke:
        tasks = select_smoke(tasks)
    prompt_paths = {
        "selection": args.inventory.parents[1] / "reports/prompts/source_external_selection_v1.txt",
        "ordinary_full_history": args.inventory.parents[1]
        / "reports/prompts/source_external_full_history_v1.txt",
        "execution_record": args.inventory.parents[1]
        / "reports/prompts/source_external_execution_record_v1.txt",
    }
    prompts = {name: path.read_text(encoding="utf-8") for name, path in prompt_paths.items()}
    prompt_hashes = {name: sha256_bytes(text.encode("utf-8")) for name, text in prompts.items()}
    existing: set[tuple[str, str, str]] = set()
    if args.output.exists():
        existing = {
            (row["model"], row["controller"], row["task_id"])
            for row in load_jsonl(args.output)
        }
    jobs = [
        (task, model, controller)
        for task in tasks
        for model in args.models
        for controller in args.controllers
        if (model, controller, task["task_id"]) not in existing
    ]
    print(
        json.dumps(
            {
                "mode": "smoke" if args.smoke else "full",
                "inventory_sha256": inventory_hash,
                "prompt_sha256": prompt_hashes,
                "jobs": len(jobs),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    if not jobs:
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    with args.output.open("a", encoding="utf-8") as stream:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [
                pool.submit(
                    run_one,
                    task=task,
                    model=model,
                    controller=controller,
                    endpoint=args.endpoint,
                    api_key=api_key,
                    prompts=prompts,
                    prompt_hashes=prompt_hashes,
                    inventory_hash=inventory_hash,
                    timeout=args.timeout,
                    state_root=args.state_bench_root,
                    agentdojo_root=args.agentdojo_root,
                )
                for task, model, controller in jobs
            ]
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                row = future.result()
                with lock:
                    stream.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")
                    stream.flush()
                print(
                    json.dumps(
                        {
                            "completed": index,
                            "total": len(jobs),
                            "task_id": row["task_id"],
                            "model": row["model"],
                            "controller": row["controller"],
                            "status": row["status"],
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )


if __name__ == "__main__":
    main()
