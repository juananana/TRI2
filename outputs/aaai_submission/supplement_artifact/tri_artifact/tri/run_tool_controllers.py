from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from tri.run_models import (
    ChatClient,
    drifted_to_new_leader,
    is_success,
    load_tasks,
    normalize_target,
    parse_json,
)
from tri.tool_env import TOOL_SCHEMAS, ToolEnvironment


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def first_refresh_call(client: ChatClient, task: dict, observation: dict, temperature: float) -> tuple[str, dict]:
    system = (
        "You are a tool-using agent operating in a stateful environment. "
        "The user instruction says a refresh must happen before the final action. "
        "Return JSON only: {\"tool\":\"refresh\",\"arguments\":{}}."
    )
    prompt = {
        "instruction": task["instruction"],
        "observation": observation,
        "available_tools": TOOL_SCHEMAS,
    }
    text = client.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
    ], temperature)
    return text, parse_json(text)


def final_act_from_payload(client: ChatClient, system: str, payload: dict, temperature: float) -> tuple[str, str | None]:
    text = client.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ], temperature)
    obj = parse_json(text)
    target = obj.get("target_id")
    if target is None and isinstance(obj.get("arguments"), dict):
        target = obj["arguments"].get("target_id")
    return text, normalize_target(target)


def run_tool_latest_state(client: ChatClient, task: dict, temperature: float) -> dict:
    env = ToolEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    try:
        initial = env.observe()
        first_text, first = first_refresh_call(client, task, initial, temperature)
        raw.append(first_text)
        if first.get("tool") != "refresh":
            errors.append("first tool call was not refresh")
        refreshed = env.refresh()
        system = (
            "You are the next step of an agent controller after a tool refresh. "
            "The controller state has been overwritten by the latest tool observation: "
            "you receive only the original instruction, the latest observation, and tool schemas. "
            "Choose the final process target. Return JSON only: "
            "{\"tool\":\"process\",\"target_id\":\"...\"} or "
            "{\"tool\":\"process\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
        )
        payload = {
            "original_instruction": task["instruction"],
            "latest_observation": refreshed,
            "available_tools": TOOL_SCHEMAS,
        }
        text, target = final_act_from_payload(client, system, payload, temperature)
        raw.append(text)
        tool_result = env.process(target)
    except Exception as exc:
        errors.append(str(exc))
        target = None
        tool_result = None
    return result_payload("tool_latest_state", task, env, target, raw, errors, tool_result)


def run_tool_full_history(client: ChatClient, task: dict, temperature: float) -> dict:
    env = ToolEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    try:
        initial = env.observe()
        first_text, first = first_refresh_call(client, task, initial, temperature)
        raw.append(first_text)
        if first.get("tool") != "refresh":
            errors.append("first tool call was not refresh")
        refreshed = env.refresh()
        system = (
            "You are a tool-using agent with the full transcript. Follow the user's temporal "
            "instruction exactly. If the target was selected before refresh, preserve that "
            "entity identity. If the target is to be selected after refresh, use the refreshed "
            "observation. Return JSON only: {\"tool\":\"process\",\"target_id\":\"...\"}."
        )
        payload = {
            "instruction": task["instruction"],
            "initial_observation": initial,
            "assistant_tool_call": first,
            "refresh_result": refreshed,
            "available_tools": TOOL_SCHEMAS,
        }
        text, target = final_act_from_payload(client, system, payload, temperature)
        raw.append(text)
        tool_result = env.process(target)
    except Exception as exc:
        errors.append(str(exc))
        target = None
        tool_result = None
    return result_payload("tool_full_history", task, env, target, raw, errors, tool_result)


def run_tool_lossy_summary(client: ChatClient, task: dict, temperature: float) -> dict:
    env = ToolEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    try:
        initial = env.observe()
        first_text, first = first_refresh_call(client, task, initial, temperature)
        raw.append(first_text)
        if first.get("tool") != "refresh":
            errors.append("first tool call was not refresh")
        refreshed = env.refresh()
        transcript = {
            "instruction": task["instruction"],
            "initial_observation": initial,
            "assistant_tool_call": first,
            "refresh_result": refreshed,
        }
        summary_text = client.chat([
            {
                "role": "system",
                "content": (
                    "You are the controller's bounded memory module. Summarize the tool "
                    "transcript for the next step in at most 18 words. Do NOT include entity "
                    "IDs, exact names, or exact numeric values. Do not use JSON."
                ),
            },
            {"role": "user", "content": json.dumps(transcript, ensure_ascii=False)},
        ], temperature)
        raw.append(summary_text)
        system = (
            "You are the next controller step. You receive only a bounded memory summary, "
            "the latest tool observation, and tool schemas. Choose the final process target. "
            "Return JSON only: {\"tool\":\"process\",\"target_id\":\"...\"}."
        )
        payload = {
            "controller_memory": summary_text,
            "latest_observation": refreshed,
            "available_tools": TOOL_SCHEMAS,
        }
        text, target = final_act_from_payload(client, system, payload, temperature)
        raw.append(text)
        tool_result = env.process(target)
    except Exception as exc:
        errors.append(str(exc))
        target = None
        tool_result = None
    return result_payload("tool_lossy_summary", task, env, target, raw, errors, tool_result)


def run_tool_compile_then_act(client: ChatClient, task: dict, temperature: float) -> dict:
    env = ToolEnvironment(task)
    raw: list[str] = []
    errors: list[str] = []
    ledger = None
    try:
        initial = env.observe()
        compile_text = client.chat([
            {
                "role": "system",
                "content": (
                    "Compile the user's instruction and current tool observation into a temporal "
                    "reference ledger. Decide whether the target should bind before refresh or "
                    "after refresh. If it binds before refresh, store the concrete target_id from "
                    "the observation. Return JSON only: {\"binding_time\":\"pre_refresh or "
                    "post_refresh\",\"selector\":\"...\",\"bound_target_id\":\"id or null\","
                    "\"reason\":\"...\"}."
                ),
            },
            {"role": "user", "content": json.dumps({
                "instruction": task["instruction"],
                "current_tool_observation": initial,
                "available_tools": TOOL_SCHEMAS,
                "future_tool_call": "refresh",
            }, ensure_ascii=False)},
        ], temperature)
        raw.append(compile_text)
        ledger = parse_json(compile_text)
        refreshed = env.refresh()
        system = (
            "Act using only the temporal reference ledger, the latest tool observation, "
            "and tool schemas. If binding_time is pre_refresh, process bound_target_id only "
            "if still present; otherwise return INVALID_BOUND_ENTITY. If binding_time is "
            "post_refresh, evaluate the selector on the latest observation. Return JSON only."
        )
        payload = {
            "ledger": ledger,
            "latest_observation": refreshed,
            "available_tools": TOOL_SCHEMAS,
        }
        text, target = final_act_from_payload(client, system, payload, temperature)
        raw.append(text)
        tool_result = env.process(target)
    except Exception as exc:
        errors.append(str(exc))
        target = None
        tool_result = None
    result = result_payload("tool_compile_then_act", task, env, target, raw, errors, tool_result)
    result["compiled_ledger"] = ledger
    return result


def result_payload(
    mode: str,
    task: dict,
    env: ToolEnvironment,
    target: str | None,
    raw: list[str],
    errors: list[str],
    tool_result: dict | None,
) -> dict:
    return {
        "mode": mode,
        "predicted_target": target,
        "correct_target": task["correct_target"],
        "success": is_success(target, task),
        "drift_to_new_leader": drifted_to_new_leader(target, task),
        "errors": errors,
        "raw_outputs": raw,
        "tool_result": tool_result,
        "tool_trace": env.trace,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=[
        "tool_latest_state",
        "tool_full_history",
        "tool_lossy_summary",
        "tool_compile_then_act",
    ], required=True)
    ap.add_argument("--split", choices=["all", "dev", "heldout"], default="dev")
    ap.add_argument("--paraphrase", choices=["all", "p0", "p1", "p2", "p3", "p4"], default="p0")
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
    ap.add_argument("--limit", type=int)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--output")
    args = ap.parse_args()

    key = os.environ.get("LLM_API_KEY")
    base = os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")

    tasks = load_tasks(args.split, args.paraphrase, args.limit, args.condition, args.domains)
    client = ChatClient(args.model, base, key, timeout=args.timeout)
    RUNS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_model = args.model.replace("/", "_").replace(":", "_")
    path = Path(args.output) if args.output else RUNS / f"{stamp}_{safe_model}_{args.mode}_{args.split}_{args.paraphrase}.jsonl"
    runners = {
        "tool_latest_state": run_tool_latest_state,
        "tool_full_history": run_tool_full_history,
        "tool_lossy_summary": run_tool_lossy_summary,
        "tool_compile_then_act": run_tool_compile_then_act,
    }
    with path.open("w", encoding="utf-8") as f:
        for i, task in enumerate(tasks, 1):
            started = time.time()
            try:
                result = runners[args.mode](client, task, args.temperature)
                status = "ok"
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                result, status = {"mode": args.mode, "error": str(exc), "success": False}, "api_error"
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
