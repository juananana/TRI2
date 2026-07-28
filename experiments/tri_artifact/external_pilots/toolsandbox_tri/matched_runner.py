from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tri.run_models import ChatClient, format_exception, parse_json

from .agent_runner import COMMON_SYSTEM, Controller, _dispatch
from .environment import active_scenario, observe_state_binding
from .evaluation import score_runtime
from .scenarios import Scenario, build_pilot_scenarios, load_scenarios


NAVIGATOR_SYSTEM = COMMON_SYSTEM + """
Before a controller state has been compiled, choose only the next tool required by the user's
stated order. Return JSON only: {"tool":"...","arguments":{}}. After a controller state is
provided, use it and the tool history to complete the task. The controller state is persistent
and cannot be rewritten by the actor. Return JSON only: {"tool":"...","arguments":{}}.
"""

COMPILER_SYSTEM = {
    "generic": """Compile a generic structured task record after the agent's first reminder
search. Record the selected entity ID and snapshot, selector, action, and action preconditions.
Do not use specialized temporal-reference fields such as reference_mode, bound_target_id,
binding_time, or invalidity_policy. Return JSON only:
{"task_goal":"...","selected_entity_id":"...","selected_entity_snapshot":{},
"selector":"...","action":"postpone","action_preconditions":{"editable":true}}.""",
    "untyped": """Write a concise free-form plan after the agent's first reminder search.
The plan must say which tools and reminder should be used later, but must not use a typed schema
or the field names reference_mode, bound_target_id, binding_time, or invalidity_policy.
Return JSON only: {"plan":"..."}.""",
    "lifecycle": """Compile a factorized reference lifecycle record after the agent's first
reminder search. Infer preserve when the instruction establishes a reminder before sync and then
refers back to it; infer reevaluate when sync precedes finding or selecting the target. For
preserve, store the concrete selected reminder ID. A selector establishes identity but does not
authorize changing it after sync. If the preserved object becomes absent or non-editable and the
instruction does not authorize fallback, use reject. Return JSON only:
{"reference_mode":"preserve|reevaluate","selector":"...",
"bound_target_id":"ID or null","invalidity_policy":"reject"}.""",
}

ACTOR_SYSTEM = {
    "generic": """Use the generic record, instruction, and tool history with ordinary reasoning.
The record does not itself specify temporal authorization. Its selected entity has already been
logged for evaluation, so do not call record_binding. Complete the task by choosing one tool per
turn. Return JSON only: {"tool":"...","arguments":{}}.""",
    "untyped": """Follow the free-form plan, instruction, and tool history. Complete the task by
choosing one tool per turn. Return JSON only: {"tool":"...","arguments":{}}.""",
    "lifecycle": """Execute from the lifecycle record. For preserve, never reapply the selector
to replace bound_target_id after sync. You may search again only to check whether that ID remains
present and editable. If it is absent or non-editable under reject, finish without mutation. For
reevaluate, use the synchronized selector result. Complete the task by choosing one tool per turn.
Return JSON only: {"tool":"...","arguments":{}}.""",
}


def _compile_state(
    client: Any,
    controller: Controller,
    scenario: Scenario,
    history: list[dict[str, Any]],
    search_result: list[dict[str, Any]],
    temperature: float,
) -> tuple[Any, str]:
    payload = {
        "instruction": scenario.instruction,
        "search_result": search_result,
        "sync_already_occurred": any(item["tool"] == "sync_reminders" for item in history),
        "tool_history": history,
    }
    raw = client.chat(
        [
            {"role": "system", "content": COMPILER_SYSTEM[controller]},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature,
    )
    state = parse_json(raw)
    if controller == "generic":
        forbidden = {"reference_mode", "bound_target_id", "binding_time", "invalidity_policy"}
        required = {
            "task_goal",
            "selected_entity_id",
            "selected_entity_snapshot",
            "selector",
            "action",
            "action_preconditions",
        }
        if set(state) != required or forbidden & set(state):
            raise ValueError("generic compiler returned the wrong schema")
    elif controller == "untyped":
        if set(state) != {"plan"} or not isinstance(state["plan"], str):
            raise ValueError("untyped compiler returned the wrong schema")
        forbidden = {"reference_mode", "bound_target_id", "binding_time", "invalidity_policy"}
        if any(field in state["plan"].lower() for field in forbidden):
            raise ValueError("untyped compiler used prohibited lifecycle field names")
    else:
        required = {"reference_mode", "selector", "bound_target_id", "invalidity_policy"}
        if set(state) != required:
            raise ValueError("lifecycle compiler returned the wrong schema")
        if state["reference_mode"] not in {"preserve", "reevaluate"}:
            raise ValueError("invalid lifecycle reference_mode")
        if state["invalidity_policy"] != "reject":
            raise ValueError("invalid lifecycle invalidity_policy")
        if state["reference_mode"] == "preserve" and not state["bound_target_id"]:
            raise ValueError("preserve lifecycle state omitted bound_target_id")
    return state, raw


def run_matched_agent(
    client: Any,
    scenario: Scenario,
    controller: Controller,
    temperature: float = 0.0,
    max_actor_steps: int = 7,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": NAVIGATOR_SYSTEM},
        {"role": "user", "content": scenario.instruction},
    ]
    history: list[dict[str, Any]] = []
    raw_outputs: list[dict[str, str]] = []
    errors: list[str] = []
    state: Any = None
    finished = False
    with active_scenario(scenario) as runtime:
        for _ in range(max_actor_steps):
            system = NAVIGATOR_SYSTEM if state is None else COMMON_SYSTEM + ACTOR_SYSTEM[controller]
            payload = {
                "instruction": scenario.instruction,
                "controller_state": state,
                "tool_history": history,
                "next_step": "Choose one available tool now.",
            }
            try:
                raw = client.chat(
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                    ],
                    temperature,
                )
                raw_outputs.append({"role": "actor", "content": raw})
                obj = parse_json(raw)
                tool = str(obj.get("tool", ""))
                arguments = obj.get("arguments", {})
                if not isinstance(arguments, dict):
                    raise ValueError("tool arguments must be an object")
                observation = _dispatch(tool, arguments)
                history.append({"tool": tool, "arguments": arguments, "result": observation})
                if tool == "search_reminder" and state is None:
                    state, compiler_raw = _compile_state(
                        client,
                        controller,
                        scenario,
                        history,
                        observation,
                        temperature,
                    )
                    raw_outputs.append({"role": "compiler", "content": compiler_raw})
                    if controller == "generic":
                        observe_state_binding(str(state["selected_entity_id"]))
                if tool == "finish":
                    finished = True
                    break
            except Exception as exc:
                errors.append(format_exception(exc))
                break
        score = score_runtime(runtime)
    score.update(
        {
            "controller": (
                "matched_generic_state_observed"
                if controller == "generic"
                else f"matched_{controller}"
            ),
            "finished": finished,
            "actor_steps": sum(item["role"] == "actor" for item in raw_outputs),
            "compiler_calls": sum(item["role"] == "compiler" for item in raw_outputs),
            "compiled_state": state,
            "raw_outputs": raw_outputs,
            "errors": errors,
        }
    )
    score["success"] = bool(
        score["success"]
        and finished
        and state is not None
        and score["order_success"]
        and not errors
    )
    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--controllers", default="generic,untyped,lifecycle")
    parser.add_argument("--data")
    parser.add_argument("--output", required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-api-retries", type=int, default=1)
    parser.add_argument("--retry-backoff", type=float, default=5.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--protocol-addendum")
    args = parser.parse_args()
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise SystemExit("Set LLM_API_KEY in the environment.")
    controllers = [item.strip() for item in args.controllers.split(",") if item.strip()]
    if not controllers or any(item not in COMPILER_SYSTEM for item in controllers):
        raise SystemExit("controllers must be from generic,untyped,lifecycle")
    scenarios = load_scenarios(Path(args.data)) if args.data else build_pilot_scenarios()
    addendum_sha256 = None
    if args.protocol_addendum:
        addendum_sha256 = hashlib.sha256(Path(args.protocol_addendum).read_bytes()).hexdigest()
    client = ChatClient(
        model=args.model,
        base_url=os.environ.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1"),
        api_key=key,
        timeout=args.timeout,
        max_retries=args.max_api_retries,
        retry_backoff=args.retry_backoff,
        max_tokens=args.max_tokens,
        enable_thinking=False,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    completed: set[tuple[str, str]] = set()
    if args.resume and output.exists():
        with output.open(encoding="utf-8") as handle:
            completed = {
                (row["controller"], row["scenario_id"])
                for row in (json.loads(line) for line in handle if line.strip())
            }
    def controller_label(controller: str) -> str:
        return (
            "matched_generic_state_observed"
            if controller == "generic"
            else f"matched_{controller}"
        )

    jobs = [
        (controller, scenario)
        for controller in controllers
        for scenario in scenarios
        if (controller_label(controller), scenario.scenario_id) not in completed
    ]
    if args.limit is not None:
        jobs = jobs[: args.limit]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    started = time.time()
    passed = 0
    with output.open("a" if args.resume else "w", encoding="utf-8") as handle:
        for index, (controller, scenario) in enumerate(jobs, 1):
            row_started = time.time()
            attempts_before = client.request_attempts
            row = run_matched_agent(
                client,
                scenario,
                controller,  # type: ignore[arg-type]
                temperature=args.temperature,
            )
            row.update(
                {
                    "model": args.model,
                    "temperature": args.temperature,
                    "run_timestamp": stamp,
                    "latency_s": round(time.time() - row_started, 3),
                    "api_request_attempts": client.request_attempts - attempts_before,
                    "protocol_addendum_sha256": addendum_sha256,
                }
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            passed += int(row["success"])
            print(
                f"[{index}/{len(jobs)}] matched_{controller} {scenario.scenario_id}: "
                f"success={row['success']} wrong_write={row['wrong_entity_write']}",
                flush=True,
            )
    print(f"{passed}/{len(jobs)} successful; {client.request_attempts} API attempts")
    print(f"elapsed_s={time.time() - started:.1f}")
    print(output)


if __name__ == "__main__":
    main()
