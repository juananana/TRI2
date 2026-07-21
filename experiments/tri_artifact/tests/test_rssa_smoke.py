from __future__ import annotations

import json
from pathlib import Path

import pytest

from tri.referential_ssa import compile_oracle_rssa, rssa_program_to_dict
from tri.rssa_smoke import (
    ACTOR_SYSTEM,
    COMPILER_SYSTEM,
    FORBIDDEN_REQUEST_FIELDS,
    GROUNDER_SYSTEM,
    actor_payload,
    compiler_payload,
    grounder_payload,
    request_field_leaks,
    run_rssa_task,
    strict_json_object,
)


DATA = Path(__file__).resolve().parents[1] / "data"


def _tasks() -> list[dict]:
    return [
        json.loads(line)
        for line in (DATA / "temporal_referent_method_upgrade_smoke_v1.jsonl")
        .read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class FakeClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.request_attempts = 0
        self.usage_records: list[dict] = []
        self.messages: list[list[dict]] = []

    def chat(self, messages: list[dict], temperature: float) -> str:
        self.request_attempts += 1
        self.usage_records.append({"prompt_tokens": 1, "completion_tokens": 1})
        self.messages.append(messages)
        return self.responses.pop(0)


def test_strict_json_rejects_wrappers_duplicates_and_constants() -> None:
    assert strict_json_object('{"a":1}') == {"a": 1}
    for bad in ('```json\n{"a":1}\n```', 'prose {"a":1}', '{"a":1,"a":2}', '{"a":NaN}'):
        with pytest.raises(ValueError):
            strict_json_object(bad)


def test_runner_prompts_match_frozen_protocol_byte_for_byte() -> None:
    protocol = (
        Path(__file__).resolve().parents[1] / "reports/TRI_rssa_20task_protocol.md"
    ).read_text(encoding="utf-8")

    def block_after(marker: str) -> str:
        tail = protocol.split(marker, 1)[1]
        return tail.split("```text\n", 1)[1].split("\n```", 1)[0]

    assert COMPILER_SYSTEM == block_after("## Frozen compiler prompt")
    assert GROUNDER_SYSTEM == block_after("Frozen grounder prompt:")
    assert ACTOR_SYSTEM == block_after("Frozen actor prompt:")


def test_all_request_payloads_exclude_benchmark_private_fields() -> None:
    for task in _tasks():
        program = compile_oracle_rssa(task)
        grounded = {binding.name: task["pre_refresh_target"] for binding in program.bindings}
        payloads = [compiler_payload(task), actor_payload(task, program, grounded)]
        payloads.extend(grounder_payload(task, binding) for binding in program.bindings)
        for payload in payloads:
            assert request_field_leaks(payload) == []
            assert not (set(payload) & FORBIDDEN_REQUEST_FIELDS)


def test_fake_anchored_run_isolates_free_and_enforced_execution() -> None:
    task = next(
        row for row in _tasks()
        if row["binding"] == "anchored"
        and row["pre_refresh_target"] != row["post_refresh_target"]
        and row["correct_target"] != "INVALID_BOUND_ENTITY"
    )
    program = compile_oracle_rssa(task)
    compiler = FakeClient([json.dumps(rssa_program_to_dict(program))])
    grounder = FakeClient([json.dumps({"target_id": task["pre_refresh_target"]})])
    actor = FakeClient([json.dumps({"target_id": task["post_refresh_target"]})])
    result = run_rssa_task(compiler, grounder, actor, task)
    assert result["pipeline_complete"]
    assert result["free"]["target"] == task["post_refresh_target"]
    assert result["free"]["wrong_write"]
    assert result["enforced"]["target"] == task["pre_refresh_target"]
    assert result["enforced"]["success"]
    assert result["actor_handle_disagreement"]
    for client in (compiler, grounder, actor):
        for messages in client.messages:
            payload = json.loads(messages[1]["content"])
            assert request_field_leaks(payload) == []


def test_fake_multirefresh_run_grounds_each_role_in_its_epoch() -> None:
    task = next(row for row in _tasks() if row["binding"] == "dynamic" and "final_state" in row)
    program = compile_oracle_rssa(task)
    compiler = FakeClient([json.dumps(rssa_program_to_dict(program))])
    grounder = FakeClient([
        json.dumps({"target_id": task["pre_refresh_target"]}),
        json.dumps({"target_id": task["post_refresh_target"]}),
    ])
    actor = FakeClient([json.dumps({"target_id": task["post_refresh_target"]})])
    result = run_rssa_task(compiler, grounder, actor, task)
    assert result["binding_inventory_correct"]
    assert result["role_correct"]
    assert result["grounding_complete"]
    assert result["enforced"]["success"]
    assert len(grounder.messages) == 2
    states = [json.loads(messages[1]["content"])["world_epoch_state"] for messages in grounder.messages]
    assert states == [task["intermediate_state"], task["final_state"]]


def test_compiler_failure_is_retained_as_itt_failure() -> None:
    task = _tasks()[0]
    result = run_rssa_task(FakeClient(["not json"]), FakeClient([]), FakeClient([]), task)
    assert not result["schema_valid"]
    assert not result["pipeline_complete"]
    assert not result["free"]["success"]
    assert not result["enforced"]["success"]
    assert result["request_attempts"] == {"compiler": 1, "grounder": 0, "actor": 0}
    assert result["errors"]
