from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RUNS = ROOT / "runs"


class ChatClient:
    RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str,
        timeout: int = 180,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
        max_tokens: int = 800,
        enable_thinking: bool | None = None,
    ):
        self.model = model
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.request_attempts = 0
        self.retry_events = 0
        self.usage_records: list[dict] = []

    def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_tokens,
        }
        if self.enable_thinking is not None:
            body["enable_thinking"] = self.enable_thinking
        payload = json.dumps(body).encode()
        req = urllib.request.Request(
            self.url,
            data=payload,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(self.max_retries + 1):
            self.request_attempts += 1
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    result = json.load(resp)
                self.usage_records.append(result.get("usage", {}))
                return result["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as exc:
                retryable = exc.code in self.RETRYABLE_HTTP_CODES
                if not retryable or attempt == self.max_retries:
                    raise
                exc.close()
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt == self.max_retries:
                    raise

            self.retry_events += 1
            time.sleep(min(self.retry_backoff * (2 ** attempt), 60.0))

        raise RuntimeError("unreachable API retry state")


def format_exception(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        detail = ""
        try:
            detail = exc.read(1000).decode("utf-8", errors="replace").strip()
        except Exception:
            pass
        finally:
            exc.close()
        suffix = f"; response={detail}" if detail else ""
        return f"api_call_error: HTTP Error {exc.code}: {exc.reason}{suffix}"
    if isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError)):
        return f"api_call_error: {exc}"
    return str(exc)


def has_internal_api_error(result: dict) -> bool:
    return any(str(err).startswith("api_call_error:") for err in result.get("errors", []))


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object")
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(text[start:])
        return obj


def normalize_target(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in {"invalid", "invalid_bound_entity", "unavailable", "missing"}:
        return "INVALID_BOUND_ENTITY"
    match = re.search(r"[A-Z]{2,5}-[A-Za-z0-9]+", text)
    return match.group(0) if match else text


def is_success(target: str | None, task: dict) -> bool:
    return target == task["correct_target"]


def target_satisfies_schema(target: str | None, task: dict) -> bool:
    if target is None or target == "INVALID_BOUND_ENTITY":
        return False
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    entity = next((x for x in task["refreshed_state"] if x.get("id") == target), None)
    if entity is None:
        return False
    return all(entity.get(k) == v for k, v in preconditions.items())


def drifted_to_new_leader(target: str | None, task: dict) -> bool:
    return (
        task["correct_target"] != "INVALID_BOUND_ENTITY"
        and target == task["post_refresh_target"]
        and task["correct_target"] != task["post_refresh_target"]
    )


def load_tasks(
    split: str,
    paraphrase: str,
    limit: int | None,
    condition: str = "all",
    domains: str = "all",
    data_path: str | None = None,
) -> list[dict]:
    path = Path(data_path) if data_path else DATA / "temporal_referent.jsonl"
    with path.open(encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if split != "all":
        rows = [r for r in rows if r["split"] == split]
    if paraphrase != "all":
        rows = [r for r in rows if r["paraphrase"] == paraphrase]
    if condition != "all":
        binding, update = condition.split("-")
        rows = [r for r in rows if r["binding"] == binding and r["update"] == update]
    if domains != "all":
        allowed = set(domains.split(","))
        rows = [r for r in rows if r["domain"] in allowed]
    return rows[:limit] if limit else rows


def common_payload(task: dict) -> dict:
    return {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "refreshed_state_is_hidden_until_after_refresh": True,
        "available_actions": [
            {"name": "refresh", "arguments": {}},
            {"name": "process", "arguments": {"target_id": "one id from the state"}},
        ],
        "required_response_format": "JSON only",
    }


def run_interactive(
    client: ChatClient,
    task: dict,
    temperature: float,
    compiler: bool = False,
    state_overwrite: bool = False,
) -> dict:
    if compiler:
        system = (
            "You are an agent with a temporal reference ledger. First infer whether the target "
            "must be bound before refresh or evaluated after refresh. If bound before refresh, "
            "store the concrete target_id from the initial state and keep it after refresh. "
            "If evaluated after refresh, wait for the refreshed state before choosing. "
            "Turn 1 must return JSON {\"action\":\"refresh\",\"ledger\":{...}}. "
            "Turn 2 must return JSON {\"action\":\"process\",\"target_id\":\"...\",\"ledger\":{...}}."
        )
    else:
        system = (
            "You operate a tool environment. Follow the user instruction exactly. "
            "Turn 1 must return JSON {\"action\":\"refresh\"}. "
            "After the refreshed state is shown, return JSON {\"action\":\"process\",\"target_id\":\"...\"}. "
            "Use only ids present in the states."
        )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(common_payload(task), ensure_ascii=False)},
    ]
    raw: list[str] = []
    errors: list[str] = []
    try:
        first = client.chat(messages, temperature)
        raw.append(first)
        first_obj = parse_json(first)
        if first_obj.get("action") != "refresh":
            errors.append("first action was not refresh")
        ledger = first_obj.get("ledger")
        if state_overwrite:
            messages = [
                {"role": "system", "content": (
                    "You are continuing after a refresh. You only have the current refreshed "
                    "state and the original user instruction as your controller state. "
                    "Return JSON {\"action\":\"process\",\"target_id\":\"...\"}."
                )},
                {"role": "user", "content": json.dumps({
                    "original_instruction": task["instruction"],
                    "current_refreshed_state": task["refreshed_state"],
                    "available_action": {"name": "process", "arguments": {"target_id": "one id from current state"}},
                }, ensure_ascii=False)},
            ]
        elif compiler:
            messages = [
                {"role": "system", "content": (
                    "Continue from the persisted temporal reference ledger. Do not reinterpret "
                    "anchored references from the refreshed state. Dynamic references should be "
                    "evaluated from the refreshed state. Return JSON "
                    "{\"action\":\"process\",\"target_id\":\"...\",\"ledger\":{...}}."
                )},
                {"role": "user", "content": json.dumps({
                    "ledger": ledger,
                    "original_instruction": task["instruction"],
                    "refreshed_state": task["refreshed_state"],
                }, ensure_ascii=False)},
            ]
        else:
            messages.append({"role": "assistant", "content": first})
            messages.append({
                "role": "user",
                "content": json.dumps({"tool_result": {"ok": True, "refreshed_state": task["refreshed_state"]}}, ensure_ascii=False),
            })
        second = client.chat(messages, temperature)
        raw.append(second)
        second_obj = parse_json(second)
        target = normalize_target(second_obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "compiler" if compiler else ("state_overwrite" if state_overwrite else "interactive"),
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_direct(client: ChatClient, task: dict, temperature: float) -> dict:
    system = (
        "Resolve the user's temporal reference. Return only JSON "
        "{\"target_id\":\"...\", \"binding\":\"anchored or dynamic\"}. "
        "Anchored references bind before refresh; dynamic references are evaluated after refresh."
    )
    prompt = {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "refreshed_state": task["refreshed_state"],
        "question": "Which target_id should be processed?",
    }
    raw: list[str] = []
    errors: list[str] = []
    try:
        text = client.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
        predicted_binding = obj.get("binding")
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        predicted_binding = None
    return {
        "mode": "direct",
        "predicted_target": target,
        "predicted_binding": predicted_binding,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_state_overwrite_once(client: ChatClient, task: dict, temperature: float) -> dict:
    system = (
        "You are an agent controller after an environment refresh. Your controller state "
        "contains only the original user instruction and the current refreshed state. "
        "Choose the target for the final action. If the original instruction requires "
        "acting on a previously selected entity that is no longer present, return "
        "JSON {\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. "
        "Otherwise return JSON {\"action\":\"process\",\"target_id\":\"...\"}."
    )
    prompt = {
        "original_instruction": task["instruction"],
        "current_refreshed_state": task["refreshed_state"],
    }
    raw: list[str] = []
    errors: list[str] = []
    try:
        text = client.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "state_overwrite_once",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_full_history_once(client: ChatClient, task: dict, temperature: float) -> dict:
    system = (
        "You are an agent controller deciding the final target after an environment refresh. "
        "You receive the original user instruction, the initial state observed before refresh, "
        "and the refreshed state. Use the full history to decide whether the user instruction "
        "requires preserving an initially identified target, re-evaluating a selector after "
        "refresh, or rejecting an invalid target. Return JSON only: "
        "{\"action\":\"process\",\"target_id\":\"...\"} or "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
    )
    prompt = {
        "original_instruction": task["instruction"],
        "initial_state_before_refresh": task["initial_state"],
        "current_refreshed_state": task["refreshed_state"],
        "question": "Which target_id should be processed now?",
    }
    raw: list[str] = []
    errors: list[str] = []
    try:
        text = client.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "full_history_once",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_generic_plan_then_act(client: ChatClient, task: dict, temperature: float) -> dict:
    plan_system = (
        "You are planning a tool-use task. Read the user instruction and initial state, "
        "then write a concise JSON execution plan for a future controller. Do not use any "
        "special temporal-reference schema; just preserve whatever details a careful agent "
        "would need after the environment refreshes. Return JSON only: "
        "{\"plan\":\"...\",\"important_facts\":[\"...\"]}."
    )
    act_system = (
        "You are executing after an environment refresh. Use the generic plan, the original "
        "instruction, and the refreshed state to choose the final target. Return JSON only: "
        "{\"action\":\"process\",\"target_id\":\"...\"} or "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        plan_text = client.chat([
            {"role": "system", "content": plan_system},
            {"role": "user", "content": json.dumps({
                "original_instruction": task["instruction"],
                "initial_state_before_refresh": task["initial_state"],
                "future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(plan_text)
        plan = parse_json(plan_text)
        act_text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "generic_plan": plan,
                "original_instruction": task["instruction"],
                "current_refreshed_state": task["refreshed_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(act_text)
        obj = parse_json(act_text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        plan = None
    return {
        "mode": "generic_plan_then_act",
        "generic_plan": plan,
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_generic_structured_ledger_then_act(
    client: ChatClient,
    task: dict,
    temperature: float,
    validity_gate: bool = False,
    reference_mode_field: bool = False,
) -> dict:
    temporal_field_instruction = (
        " Also record reference_mode as preserve when the instruction selected the action "
        "target before refresh, or reevaluate when selection is intentionally deferred until "
        "after refresh."
        if reference_mode_field else
        " Do not add specialized temporal-reference fields such as binding_time, "
        "reference_mode, or invalidity_policy."
    )
    ledger_schema = (
        "{\"task_goal\":\"...\",\"selected_entity_id\":\"...\"," 
        "\"selected_entity_snapshot\":{},\"selector\":\"...\",\"action\":\"...\"," 
        "\"action_preconditions\":{},\"reference_mode\":\"preserve or reevaluate\"}."
        if reference_mode_field else
        "{\"task_goal\":\"...\",\"selected_entity_id\":\"...\"," 
        "\"selected_entity_snapshot\":{},\"selector\":\"...\",\"action\":\"...\"," 
        "\"action_preconditions\":{}}."
    )
    ledger_system = (
        "Create a generic structured task-state record for a later agent step. Record the "
        "entity selected by the target description in the current initial state, its complete "
        "snapshot, the selector, the requested action, and the action preconditions."
        + temporal_field_instruction + " Return JSON only: " + ledger_schema
    )
    actor_system = (
        "You are the final step of a tool agent after an environment refresh. Use the original "
        "instruction, a generic structured task-state record, the refreshed state, and the "
        "action schema to decide the target. Reason normally about whether the old selected "
        "entity or the current selector result should be used. If the correct target cannot be "
        "acted on, return INVALID_BOUND_ENTITY. Return JSON only: "
        "{\"action\":\"process\",\"target_id\":\"...\"} or "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
    )
    if reference_mode_field:
        actor_system += (
            " Treat reference_mode=preserve as an instruction to retain selected_entity_id "
            "across refresh, and reference_mode=reevaluate as an instruction to apply the "
            "selector to refreshed_state. This field does not override action preconditions."
        )
    raw: list[str] = []
    errors: list[str] = []
    try:
        ledger_text = client.chat([
            {"role": "system", "content": ledger_system},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
                "action_schema": task.get("action_schema", {}),
                "future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(ledger_text)
        ledger = parse_json(ledger_text)
        actor_text = client.chat([
            {"role": "system", "content": actor_system},
            {"role": "user", "content": json.dumps({
                "original_instruction": task["instruction"],
                "generic_ledger": ledger,
                "refreshed_state": task["refreshed_state"],
                "action_schema": task.get("action_schema", {}),
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(actor_text)
        obj = parse_json(actor_text)
        target = normalize_target(obj.get("target_id"))
        if validity_gate and target != "INVALID_BOUND_ENTITY" and not target_satisfies_schema(target, task):
            target = "INVALID_BOUND_ENTITY"
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        ledger = None
    return {
        "mode": (
            "generic_validity_gated_ledger_then_act"
            if validity_gate else (
                "generic_reference_mode_ledger_then_act"
                if reference_mode_field else "generic_structured_ledger_then_act"
            )
        ),
        "compiled_ledger": ledger,
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_ledger(client: ChatClient, task: dict, temperature: float, safe: bool = False) -> dict:
    bound_target = task["pre_refresh_target"] if task["binding"] == "anchored" else None
    ledger = {
        "binding_time": "pre_refresh" if task["binding"] == "anchored" else "post_refresh",
        "selector": task["selector"],
        "bound_target_id": bound_target,
    }
    if safe:
        system = (
            "Use the temporal reference ledger. If binding_time is pre_refresh, process "
            "bound_target_id only if that id is still present in the refreshed state. If it is "
            "missing, return JSON {\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. "
            "If binding_time is post_refresh, choose from the refreshed state. Return JSON only."
        )
    else:
        system = (
            "Use the temporal reference ledger. If binding_time is pre_refresh, process "
            "bound_target_id even if another item now satisfies the selector. If binding_time "
            "is post_refresh, choose from the refreshed state. Return JSON "
            "{\"action\":\"process\",\"target_id\":\"...\"}."
        )
    prompt = {
        "ledger": ledger,
        "original_instruction": task["instruction"],
        "refreshed_state": task["refreshed_state"],
    }
    raw: list[str] = []
    errors: list[str] = []
    try:
        text = client.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "ledger_safe" if safe else "ledger",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_natural_memory(client: ChatClient, task: dict, temperature: float) -> dict:
    summarize_system = (
        "Summarize the user's goal and the initial state for a future controller. "
        "Write a concise natural-language memory note. Do not use JSON."
    )
    act_system = (
        "You are continuing after refresh. You have only a natural-language memory note "
        "and the refreshed state. Choose the target. If the note requires a previously "
        "selected entity that is no longer present, return JSON "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. Otherwise return JSON "
        "{\"action\":\"process\",\"target_id\":\"...\"}."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        note = client.chat([
            {"role": "system", "content": summarize_system},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
                "future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(note)
        text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "memory_note": note,
                "refreshed_state": task["refreshed_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "natural_memory",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_compressed_memory(client: ChatClient, task: dict, temperature: float) -> dict:
    summarize_system = (
        "Compress the user's goal and initial state into a short controller memory note. "
        "Important constraint: do NOT include entity IDs, exact names, or exact numeric values. "
        "Use at most 18 words. Do not use JSON."
    )
    act_system = (
        "You are continuing after refresh. You have only a compressed natural-language memory "
        "note and the refreshed state. Choose the target. If the note clearly requires a "
        "previously selected entity that is no longer present, return JSON "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. Otherwise return JSON "
        "{\"action\":\"process\",\"target_id\":\"...\"}."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        note = client.chat([
            {"role": "system", "content": summarize_system},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
                "future_event": "the environment will refresh before the final action",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(note)
        text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "compressed_memory_note": note,
                "refreshed_state": task["refreshed_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "compressed_memory",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_summary_controller(client: ChatClient, task: dict, temperature: float, lossy: bool = False) -> dict:
    first_system = (
        "You are a tool-using agent. Read the instruction and initial state. "
        "The only available first action is refresh. Return JSON {\"action\":\"refresh\"}."
    )
    if lossy:
        summary_system = (
            "You are the agent controller's bounded memory module. Summarize the transcript "
            "for the next step in at most 18 words. Do NOT include entity IDs, exact names, "
            "or exact numeric values. Do not use JSON."
        )
    else:
        summary_system = (
            "You are the agent controller's memory module. Summarize the transcript for the "
            "next step. Preserve any entity identity, binding decision, and validity-relevant "
            "facts needed to complete the user's instruction. Do not use JSON."
        )
    act_system = (
        "You are the next controller step after refresh. You receive only the controller "
        "memory summary and the refreshed state. Choose the final target. If the memory "
        "requires a previously selected entity that is no longer present, return JSON "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. Otherwise return JSON "
        "{\"action\":\"process\",\"target_id\":\"...\"}."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        first = client.chat([
            {"role": "system", "content": first_system},
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "initial_state": task["initial_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(first)
        transcript = {
            "instruction": task["instruction"],
            "initial_state": task["initial_state"],
            "assistant_action": first,
            "tool_result": {"refreshed_state": task["refreshed_state"]},
        }
        memory = client.chat([
            {"role": "system", "content": summary_system},
            {"role": "user", "content": json.dumps(transcript, ensure_ascii=False)},
        ], temperature)
        raw.append(memory)
        text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "controller_memory": memory,
                "refreshed_state": task["refreshed_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(text)
        obj = parse_json(text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
    return {
        "mode": "lossy_summary_controller" if lossy else "summary_controller",
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_compile_then_act(client: ChatClient, task: dict, temperature: float) -> dict:
    compile_system = (
        "Compile the user's instruction into a temporal reference ledger. "
        "Decide whether the target should be bound from the initial state before refresh "
        "or selected after refresh. If it should be bound before refresh, include the concrete "
        "bound_target_id from the initial state. Return JSON only: "
        "{\"binding_time\":\"pre_refresh or post_refresh\","
        "\"selector\":\"...\",\"bound_target_id\":\"id or null\",\"reason\":\"...\"}."
    )
    compile_prompt = {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "available_future_update": "a refresh will happen before the final action",
    }
    act_system = (
        "Act using only the compiled temporal reference ledger and the refreshed state. "
        "If binding_time is pre_refresh, process bound_target_id only if it is still present. "
        "If it is missing, return JSON {\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. "
        "If binding_time is post_refresh, use the selector to choose from the refreshed state. "
        "Return JSON {\"action\":\"process\",\"target_id\":\"...\"} or invalid."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        compile_text = client.chat([
            {"role": "system", "content": compile_system},
            {"role": "user", "content": json.dumps(compile_prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(compile_text)
        ledger = parse_json(compile_text)
        act_text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "ledger": ledger,
                "refreshed_state": task["refreshed_state"],
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(act_text)
        obj = parse_json(act_text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        ledger = None
    return {
        "mode": "compile_then_act",
        "compiled_ledger": ledger,
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def run_schema_compile_then_act(client: ChatClient, task: dict, temperature: float) -> dict:
    compile_system = (
        "Compile the user's instruction into a temporal reference lifecycle record. "
        "Decide whether the target is bound before refresh, selected after refresh, or conditional. "
        "For pre-refresh or conditional binding, include the concrete bound_target_id from the initial state. "
        "Return JSON only: {\"binding_time\":\"pre_refresh or post_refresh or conditional\","
        "\"selector\":\"...\",\"bound_target_id\":\"id or null\","
        "\"validity_policy\":\"use bound target only if it satisfies action preconditions\","
        "\"reason\":\"...\"}."
    )
    compile_prompt = {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "action_schema": task.get("action_schema", {}),
        "available_future_update": "a refresh will happen before the final action",
    }
    act_system = (
        "Act using the compiled lifecycle record, refreshed state, and action schema. "
        "A target is actionable only if it is present in refreshed_state and satisfies every "
        "action_schema.preconditions field exactly. If binding_time is pre_refresh, use "
        "bound_target_id only when it is actionable; otherwise return "
        "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}. "
        "If binding_time is post_refresh, choose the entity satisfying the selector in refreshed_state. "
        "If binding_time is conditional, prefer bound_target_id if actionable; otherwise choose the "
        "refreshed selector target. Return JSON only: {\"action\":\"process\",\"target_id\":\"...\"} "
        "or {\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
    )
    raw: list[str] = []
    errors: list[str] = []
    try:
        compile_text = client.chat([
            {"role": "system", "content": compile_system},
            {"role": "user", "content": json.dumps(compile_prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(compile_text)
        ledger = parse_json(compile_text)
        act_text = client.chat([
            {"role": "system", "content": act_system},
            {"role": "user", "content": json.dumps({
                "ledger": ledger,
                "refreshed_state": task["refreshed_state"],
                "action_schema": task.get("action_schema", {}),
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(act_text)
        obj = parse_json(act_text)
        target = normalize_target(obj.get("target_id"))
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        ledger = None
    return {
        "mode": "schema_compile_then_act",
        "compiled_ledger": ledger,
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


FACTORIZED_LIFECYCLE_ACTOR_SYSTEM = (
    "Act using the factorized lifecycle record, refreshed state, and action schema. "
    "An entity is actionable only if it is present and satisfies every action precondition. "
    "For a preserved entity, do not reapply the selector after refresh: the selector was "
    "used to establish identity, and its descriptive property may legitimately change. "
    "Only action_schema.preconditions determine post-refresh validity. "
    "For reference_mode preserve, use bound_target_id when actionable. If it is not "
    "actionable, follow invalidity_policy: reject returns INVALID_BOUND_ENTITY, while "
    "reevaluate_selector selects an actionable refreshed entity matching the selector. "
    "For reference_mode reevaluate, evaluate the selector in refreshed_state regardless of "
    "the old bound_target_id. Return JSON only: {\"action\":\"process\","
    "\"target_id\":\"...\"} or {\"action\":\"invalid\","
    "\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)


def run_factorized_actor_from_ledger(
    client: ChatClient,
    task: dict,
    ledger: dict,
    temperature: float,
) -> tuple[str, str | None]:
    act_text = client.chat([
        {"role": "system", "content": FACTORIZED_LIFECYCLE_ACTOR_SYSTEM},
        {"role": "user", "content": json.dumps({
            "ledger": ledger,
            "refreshed_state": task["refreshed_state"],
            "action_schema": task.get("action_schema", {}),
        }, ensure_ascii=False)},
    ], temperature)
    return act_text, normalize_target(parse_json(act_text).get("target_id"))


def run_factorized_schema_compile_then_act(
    client: ChatClient, task: dict, temperature: float, hybrid_gate: bool = False
) -> dict:
    compile_system = (
        "Compile the user's instruction into a factorized reference lifecycle record. "
        "Keep reference identity semantics separate from invalid-target handling. "
        "Set reference_mode to preserve when the instruction commits to an entity selected "
        "before refresh; set it to reevaluate when the description must be evaluated after "
        "refresh. Infer commitment from discourse order, not from the time of the final action: "
        "an instruction that first asks to identify, check, or find an entity and later says "
        "refresh and act on it preserves that entity even without words such as same or previous. "
        "Use reevaluate only when the instruction says to refresh before deciding, finding, or "
        "selecting, or explicitly says to use the refreshed state. The mere fact that refresh "
        "precedes the final action does not license reevaluation. For preserve, include "
        "bound_target_id from the initial state. "
        "Set invalidity_policy to reject unless the instruction explicitly authorizes selecting "
        "a replacement when the preserved entity becomes invalid; only then use "
        "reevaluate_selector. Return JSON only: "
        "{\"reference_mode\":\"preserve or reevaluate\",\"selector\":\"...\","
        "\"bound_target_id\":\"id or null\","
        "\"invalidity_policy\":\"reject or reevaluate_selector\",\"reason\":\"...\"}."
    )
    compile_prompt = {
        "instruction": task["instruction"],
        "initial_state": task["initial_state"],
        "action_schema": task.get("action_schema", {}),
        "available_future_update": "a refresh will happen before the final action",
    }
    raw: list[str] = []
    errors: list[str] = []
    try:
        compile_text = client.chat([
            {"role": "system", "content": compile_system},
            {"role": "user", "content": json.dumps(compile_prompt, ensure_ascii=False)},
        ], temperature)
        raw.append(compile_text)
        ledger = parse_json(compile_text)
        use_gate = hybrid_gate and ledger.get("reference_mode") == "preserve"
        if use_gate:
            bound_id = normalize_target(ledger.get("bound_target_id"))
            if target_satisfies_schema(bound_id, task):
                target = bound_id
            elif ledger.get("invalidity_policy") == "reject":
                target = "INVALID_BOUND_ENTITY"
            else:
                use_gate = False
        if not use_gate:
            act_text, target = run_factorized_actor_from_ledger(
                client, task, ledger, temperature
            )
            raw.append(act_text)
    except Exception as exc:
        errors.append(format_exception(exc))
        target = None
        ledger = None
    return {
        "mode": (
            "factorized_hybrid_compile_then_act"
            if hybrid_gate else "factorized_schema_compile_then_act"
        ),
        "compiled_ledger": ledger,
        "predicted_target": target,
        "target_schema_valid": target_satisfies_schema(target, task),
        "symbolic_preserve_gate": bool(
            hybrid_gate and ledger and ledger.get("reference_mode") == "preserve"
        ),
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=[
        "interactive",
        "direct",
        "compiler",
        "state_overwrite",
        "state_overwrite_once",
        "full_history_once",
        "generic_plan_then_act",
        "generic_structured_ledger_then_act",
        "generic_reference_mode_ledger_then_act",
        "generic_validity_gated_ledger_then_act",
        "ledger",
        "ledger_safe",
        "natural_memory",
        "compressed_memory",
        "summary_controller",
        "lossy_summary_controller",
        "compile_then_act",
        "schema_compile_then_act",
        "factorized_schema_compile_then_act",
        "factorized_hybrid_compile_then_act",
    ], required=True)
    ap.add_argument("--split", choices=["all", "dev", "heldout"], default="dev")
    ap.add_argument("--paraphrase", choices=["all", "p0", "p1", "p2", "p3", "p4"], default="p0")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--max-api-retries", type=int, default=3)
    ap.add_argument("--retry-backoff", type=float, default=2.0)
    ap.add_argument("--max-tokens", type=int, default=800)
    ap.add_argument("--disable-thinking", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--condition", choices=[
        "all",
        "anchored-flip",
        "anchored-stable",
        "dynamic-flip",
        "dynamic-stable",
        "anchored-removed",
        "dynamic-removed",
    ], default="all")
    ap.add_argument("--domains", default="all")
    ap.add_argument("--data", default=str(DATA / "temporal_referent.jsonl"))
    ap.add_argument("--output")
    args = ap.parse_args()

    key = os.environ.get("LLM_API_KEY")
    base = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")

    tasks = load_tasks(args.split, args.paraphrase, args.limit, args.condition, args.domains, args.data)
    client = ChatClient(
        args.model,
        base,
        key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False if args.disable_thinking else None,
    )
    RUNS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = args.model.replace("/", "_").replace(":", "_")
    path = Path(args.output) if args.output else RUNS / f"{stamp}_{safe_model}_{args.mode}_{args.split}_{args.paraphrase}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for i, task in enumerate(tasks, 1):
            started = time.time()
            attempts_before = client.request_attempts
            retries_before = client.retry_events
            try:
                if args.mode == "direct":
                    result = run_direct(client, task, args.temperature)
                elif args.mode == "state_overwrite_once":
                    result = run_state_overwrite_once(client, task, args.temperature)
                elif args.mode == "full_history_once":
                    result = run_full_history_once(client, task, args.temperature)
                elif args.mode == "generic_plan_then_act":
                    result = run_generic_plan_then_act(client, task, args.temperature)
                elif args.mode == "generic_structured_ledger_then_act":
                    result = run_generic_structured_ledger_then_act(
                        client, task, args.temperature
                    )
                elif args.mode == "generic_reference_mode_ledger_then_act":
                    result = run_generic_structured_ledger_then_act(
                        client, task, args.temperature, reference_mode_field=True
                    )
                elif args.mode == "generic_validity_gated_ledger_then_act":
                    result = run_generic_structured_ledger_then_act(
                        client, task, args.temperature, validity_gate=True
                    )
                elif args.mode == "ledger":
                    result = run_ledger(client, task, args.temperature)
                elif args.mode == "ledger_safe":
                    result = run_ledger(client, task, args.temperature, safe=True)
                elif args.mode == "natural_memory":
                    result = run_natural_memory(client, task, args.temperature)
                elif args.mode == "compressed_memory":
                    result = run_compressed_memory(client, task, args.temperature)
                elif args.mode == "summary_controller":
                    result = run_summary_controller(client, task, args.temperature)
                elif args.mode == "lossy_summary_controller":
                    result = run_summary_controller(client, task, args.temperature, lossy=True)
                elif args.mode == "compile_then_act":
                    result = run_compile_then_act(client, task, args.temperature)
                elif args.mode == "schema_compile_then_act":
                    result = run_schema_compile_then_act(client, task, args.temperature)
                elif args.mode == "factorized_schema_compile_then_act":
                    result = run_factorized_schema_compile_then_act(
                        client, task, args.temperature
                    )
                elif args.mode == "factorized_hybrid_compile_then_act":
                    result = run_factorized_schema_compile_then_act(
                        client, task, args.temperature, hybrid_gate=True
                    )
                else:
                    result = run_interactive(
                        client,
                        task,
                        args.temperature,
                        compiler=args.mode == "compiler",
                        state_overwrite=args.mode == "state_overwrite",
                    )
                status = "api_error" if has_internal_api_error(result) else "ok"
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                result, status = {"error": str(exc), "success": False}, "api_error"
            row = {
                "run_timestamp": stamp,
                "model": args.model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "enable_thinking": False if args.disable_thinking else None,
                "status": status,
                "latency_s": round(time.time() - started, 3),
                "api_request_attempts": client.request_attempts - attempts_before,
                "api_retries": client.retry_events - retries_before,
                "task": task,
                "result": result,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{i}/{len(tasks)}] {task['id']}: {status} success={result.get('success')} target={result.get('predicted_target')}")
    print(path)


if __name__ == "__main__":
    main()
