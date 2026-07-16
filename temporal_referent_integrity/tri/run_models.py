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
    def __init__(self, model: str, base_url: str, api_key: str, timeout: int = 180):
        self.model = model
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 800,
        }
        payload = json.dumps(body).encode()
        req = urllib.request.Request(
            self.url,
            data=payload,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json.load(resp)
        return result["choices"][0]["message"]["content"]


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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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
        errors.append(str(exc))
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=[
        "interactive",
        "direct",
        "compiler",
        "state_overwrite",
        "state_overwrite_once",
        "ledger",
        "ledger_safe",
        "natural_memory",
        "compressed_memory",
        "summary_controller",
        "lossy_summary_controller",
        "compile_then_act",
    ], required=True)
    ap.add_argument("--split", choices=["all", "dev", "heldout"], default="dev")
    ap.add_argument("--paraphrase", choices=["all", "p0", "p1", "p2", "p3", "p4"], default="p0")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=45)
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
    client = ChatClient(args.model, base, key, timeout=args.timeout)
    RUNS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = args.model.replace("/", "_").replace(":", "_")
    path = Path(args.output) if args.output else RUNS / f"{stamp}_{safe_model}_{args.mode}_{args.split}_{args.paraphrase}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for i, task in enumerate(tasks, 1):
            started = time.time()
            try:
                if args.mode == "direct":
                    result = run_direct(client, task, args.temperature)
                elif args.mode == "state_overwrite_once":
                    result = run_state_overwrite_once(client, task, args.temperature)
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
                else:
                    result = run_interactive(
                        client,
                        task,
                        args.temperature,
                        compiler=args.mode == "compiler",
                        state_overwrite=args.mode == "state_overwrite",
                    )
                status = "ok"
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                result, status = {"error": str(exc), "success": False}, "api_error"
            row = {
                "run_timestamp": stamp,
                "model": args.model,
                "temperature": args.temperature,
                "status": status,
                "latency_s": round(time.time() - started, 3),
                "task": task,
                "result": result,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{i}/{len(tasks)}] {task['id']}: {status} success={result.get('success')} target={result.get('predicted_target')}")
    print(path)


if __name__ == "__main__":
    main()
