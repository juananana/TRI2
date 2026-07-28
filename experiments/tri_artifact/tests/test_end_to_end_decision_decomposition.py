from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from tri.end_to_end_decision_decomposition import (
    ACTOR_CONDITIONS,
    ACTOR_SYSTEM_PROMPT,
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    COMPILER_SYSTEM_PROMPT,
    EVIDENCE_STATUS,
    ENDPOINT,
    MODEL_IDS,
    RUN_SETTINGS,
    RUN_VERSION,
    TASK_FILE_SHA256,
    actor_base_payload_hash,
    actor_order,
    apply_holm,
    build_actor_base_payload,
    build_actor_payload,
    build_compiler_payload,
    build_report,
    decision_fragment,
    exact_paired_p,
    load_frozen_tasks,
    model_id_hash,
    parse_actor_output,
    parse_compiler_output,
    prompt_hashes,
    run_implementation_provenance,
    settings_hash,
    sha256_path,
    task_hash,
    validate_health_smoke,
    validate_run_inventory,
    validate_run_row,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_end_to_end_decision_decomposition_protocol.md"
MODEL = MODEL_IDS["qwen"]


def _attempt(payload: dict, system_prompt: str, raw: str = "{}") -> list[dict]:
    return [{
        "status": "success",
        "request": {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
            "temperature": RUN_SETTINGS["temperature"],
            "max_tokens": RUN_SETTINGS["max_tokens"],
            "enable_thinking": False,
        },
        "raw_content": raw,
    }]


def _component(
    parsed: dict | None,
    payload: dict | None,
    system_prompt: str,
    error_kind: str | None = None,
) -> dict:
    return {
        "parsed": parsed,
        "error": None if parsed is not None else "synthetic failure",
        "error_kind": error_kind,
        "attempts": [] if payload is None else _attempt(payload, system_prompt),
        "usage": {},
    }


def _gold_compiler(task: dict) -> dict:
    preserve = task["reference_mode_gold"] == "preserve"
    return {
        "reference_mode": task["reference_mode_gold"],
        "bound_target_id": task["pre_refresh_target"] if preserve else None,
        "selector": task["selector"],
    }


def _row(task: dict, task_index: int, targets: dict[str, str | None]) -> dict:
    compiler_parsed = _gold_compiler(task)
    compiler = _component(
        compiler_parsed, build_compiler_payload(task), COMPILER_SYSTEM_PROMPT
    )
    compiler_id = f"compiler-{task['id']}"
    actors = {}
    for condition in ACTOR_CONDITIONS:
        target = targets[condition]
        parsed = None if target is None else {"action": task["action"], "target_id": target}
        component = _component(
            parsed,
            build_actor_payload(task, compiler_parsed, condition),
            ACTOR_SYSTEM_PROMPT,
            "parse_or_schema" if target is None else None,
        )
        component["compiler_output_id"] = compiler_id
        actors[condition] = component
    components = [compiler, *(actors[name] for name in ACTOR_CONDITIONS)]
    row = {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "run_scope": "full",
        "model": MODEL,
        "model_id_sha256": model_id_hash(MODEL),
        "endpoint": ENDPOINT,
        "api_settings": RUN_SETTINGS,
        "settings_sha256": settings_hash(),
        "task_file_sha256": TASK_FILE_SHA256,
        "protocol_sha256": sha256_path(PROTOCOL),
        "prompt_sha256": prompt_hashes(),
        "implementation_provenance": run_implementation_provenance(ROOT),
        "recording_session": {
            "run_session_id": "synthetic-session",
            "resumed_after_rows": 0,
        },
        "task": task,
        "task_sha256": task_hash(task),
        "task_index": task_index,
        "actor_order": list(actor_order(task_index)),
        "actor_base_payload_sha256": actor_base_payload_hash(task),
        "compiler_output_id": compiler_id,
        "compiler": compiler,
        "actors": actors,
        "outcomes": targets,
        "logical_calls_planned": 6,
        "logical_calls_attempted": 6,
        "logical_calls_completed": 6,
        "complete": all(component["parsed"] is not None for component in components),
    }
    return row


def test_frozen_inventory_hash_and_pair_structure() -> None:
    tasks = load_frozen_tasks(TASKS)
    assert sha256_path(TASKS) == TASK_FILE_SHA256
    assert len(tasks) == 80
    assert len({task["state_cluster_id"] for task in tasks}) == 40
    assert Counter(task["reference_mode_gold"] for task in tasks) == {
        "preserve": 40,
        "reevaluate": 40,
    }


def test_actor_base_has_raw_states_but_no_resolver_or_gold_fields() -> None:
    task = load_frozen_tasks(TASKS)[0]
    compiler = _gold_compiler(task)
    base = build_actor_base_payload(task)
    assert set(base) == {
        "instruction", "s0_state", "s1_state", "selector", "action", "action_schema"
    }
    assert "initial_selected_id" not in base
    assert "pre_refresh_target" not in base
    assert "correct_target" not in base
    assert build_compiler_payload(task).keys() == {
        "instruction", "s0_state", "selector", "action", "action_schema"
    }

    payloads = {
        condition: build_actor_payload(task, compiler, condition)
        for condition in ACTOR_CONDITIONS
    }
    assert "compiler_fragment" not in payloads["history_only"]
    assert "follow_instruction" not in payloads["history_only"]
    assert set(payloads["mode_only"]["compiler_fragment"]) == {"reference_mode"}
    assert set(payloads["mode_plus_id"]["compiler_fragment"]) == {
        "reference_mode", "bound_target_id"
    }
    assert set(payloads["mode_plus_id_selector"]["compiler_fragment"]) == {
        "reference_mode", "bound_target_id", "selector"
    }
    assert "follow_instruction" not in payloads["mode_plus_id_selector"]
    assert "follow_instruction" in payloads["full_follow"]
    assert decision_fragment("full_follow", compiler) == payloads["full_follow"]["compiler_fragment"]


def test_actor_rotation_balances_every_position_over_80_rows() -> None:
    orders = [actor_order(index) for index in range(80)]
    for position in range(5):
        assert Counter(order[position] for order in orders) == {
            condition: 16 for condition in ACTOR_CONDITIONS
        }


def test_parsers_are_strict_and_accept_fenced_json() -> None:
    assert parse_compiler_output(
        '```json\n{"reference_mode":"preserve","bound_target_id":"ALT-1A",'
        '"selector":"highest-severity open alert"}\n```'
    )["bound_target_id"] == "ALT-1A"
    assert parse_actor_output('{"action":"acknowledge","target_id":"ALT-1A"}')["target_id"] == "ALT-1A"
    with pytest.raises(ValueError):
        parse_compiler_output(
            '{"reference_mode":"reevaluate","bound_target_id":"ALT-1A","selector":"x"}'
        )
    with pytest.raises(ValueError):
        parse_actor_output('{"target_id":"ALT-1A"}')


def test_transport_disables_reasoning_and_smoke_plans_24_calls() -> None:
    from scripts.run_end_to_end_decision_decomposition import build_request_body, dry_run_plan

    body = build_request_body(MODEL, [], 0.0, 500)
    assert body["enable_thinking"] is False
    plan = dry_run_plan(load_frozen_tasks(TASKS), MODEL, "smoke", Path("smoke.jsonl"))
    assert plan["rows"] == 4
    assert plan["total_logical_calls"] == 24
    assert plan["actor_base_payloads_identical"] is True
    assert plan["settings_sha256"] == settings_hash()
    assert set(plan["implementation_provenance"]["source_sha256"]) == {"core", "runner"}


def test_validator_checks_shared_compiler_and_exact_ladder() -> None:
    task = load_frozen_tasks(TASKS)[0]
    targets = {condition: task["correct_target"] for condition in ACTOR_CONDITIONS}
    row = _row(task, 0, targets)
    validate_run_row(row, require_complete=True)

    bad = json.loads(json.dumps(row))
    bad["actors"]["mode_only"]["compiler_output_id"] = "different"
    with pytest.raises(ValueError):
        validate_run_row(bad)

    bad = json.loads(json.dumps(row))
    messages = bad["actors"]["history_only"]["attempts"][-1]["request"]["messages"]
    payload = json.loads(messages[1]["content"])
    payload["initial_selected_id"] = task["pre_refresh_target"]
    messages[1]["content"] = json.dumps(payload)
    with pytest.raises(ValueError):
        validate_run_row(bad)

    bad = json.loads(json.dumps(row))
    bad["compiler"]["attempts"][-1]["request"]["messages"][0]["content"] = "drifted"
    with pytest.raises(ValueError, match="system prompt"):
        validate_run_row(bad)


def test_report_has_itt_metrics_adjacent_contrasts_and_conditional_substitution() -> None:
    tasks = load_frozen_tasks(TASKS)[:4]
    rows = []
    for index, task in enumerate(tasks):
        gold = task["correct_target"]
        if task["reference_mode_gold"] == "preserve":
            history = task["post_refresh_target"]
            targets = {
                "history_only": history,
                "mode_only": history,
                "mode_plus_id": gold,
                "mode_plus_id_selector": gold,
                "full_follow": gold,
            }
        else:
            targets = {condition: gold for condition in ACTOR_CONDITIONS}
        rows.append(_row(task, index, targets))

    report = build_report(rows, seed=BOOTSTRAP_SEED, samples=200)
    model = report["models"][0]
    assert BOOTSTRAP_SAMPLES == 10_000
    assert model["compiler"]["mode_accuracy"]["numerator"] == 4
    assert model["compiler"]["preserve_bound_id_accuracy"]["numerator"] == 2
    assert model["metrics"]["history_only"]["e2e"]["denominator"] == 4
    assert model["metrics"]["history_only"]["changed_pairacc"]["numerator"] == 0
    assert model["metrics"]["mode_plus_id"]["changed_pairacc"]["numerator"] == 2
    assert model["metrics"]["history_only"]["preserve_conditional_substitution"]["numerator"] == 2
    assert model["metrics"]["mode_plus_id"]["preserve_conditional_substitution"]["numerator"] == 0

    lookup = {
        (item["left"], item["right"], item["metric"]): item
        for item in model["paired_contrasts"]
    }
    increment = lookup[("mode_only", "mode_plus_id", "changed_pairacc")]
    assert increment["difference_right_minus_left"] == 1.0
    assert increment["discordance"]["right_only"] == 2
    assert increment["exact_p_holm"] is not None


def test_parse_failure_remains_in_itt_and_failure_accounting() -> None:
    tasks = load_frozen_tasks(TASKS)[:2]
    rows = []
    for index, task in enumerate(tasks):
        targets = {condition: task["correct_target"] for condition in ACTOR_CONDITIONS}
        rows.append(_row(task, index, targets))
    failed = rows[1]
    failed["actors"]["full_follow"]["parsed"] = None
    failed["actors"]["full_follow"]["error"] = "json_parse_error"
    failed["actors"]["full_follow"]["error_kind"] = "parse_or_schema"
    failed["outcomes"]["full_follow"] = None
    failed["complete"] = False

    report = build_report(rows, seed=BOOTSTRAP_SEED, samples=50)
    model = report["models"][0]
    assert model["metrics"]["full_follow"]["e2e"]["denominator"] == 2
    assert model["metrics"]["full_follow"]["e2e"]["numerator"] == 1
    assert model["metrics"]["full_follow"]["changed_pairacc"]["denominator"] == 1
    assert model["metrics"]["full_follow"]["changed_pairacc"]["numerator"] == 0
    assert model["failure_and_attempt_accounting"]["full_follow"]["parse_or_schema_failures"] == 1


def test_e2e_requires_both_requested_action_and_target() -> None:
    tasks = load_frozen_tasks(TASKS)[:2]
    rows = [
        _row(task, index, {condition: task["correct_target"] for condition in ACTOR_CONDITIONS})
        for index, task in enumerate(tasks)
    ]
    rows[0]["actors"]["history_only"]["parsed"]["action"] = "different_action"
    report = build_report(rows, seed=BOOTSTRAP_SEED, samples=50)
    history = report["models"][0]["metrics"]["history_only"]
    assert history["e2e"]["numerator"] == 1
    assert history["changed_pairacc"]["numerator"] == 0


def test_exact_discordance_and_holm_are_deterministic() -> None:
    assert exact_paired_p(0, 3) == pytest.approx(0.25)
    items = [
        {"exact_p_unadjusted": 0.01, "exact_p_holm": None},
        {"exact_p_unadjusted": 0.04, "exact_p_holm": None},
        {"exact_p_unadjusted": 0.03, "exact_p_holm": None},
    ]
    apply_holm(items)
    assert [item["exact_p_holm"] for item in items] == pytest.approx([0.03, 0.06, 0.06])


def test_smoke_requires_all_six_calls_to_parse() -> None:
    tasks = load_frozen_tasks(TASKS)
    rows = [
        _row(task, index, {condition: task["correct_target"] for condition in ACTOR_CONDITIONS})
        for index, task in enumerate(tasks[:4])
    ]
    for row in rows:
        row["run_scope"] = "smoke"
    validate_health_smoke(
        rows,
        MODEL,
        tasks,
        sha256_path(PROTOCOL),
        run_implementation_provenance(ROOT),
    )
    rows[0]["actors"]["mode_only"]["parsed"] = None
    rows[0]["outcomes"]["mode_only"] = None
    rows[0]["complete"] = False
    with pytest.raises(ValueError):
        validate_health_smoke(
            rows,
            MODEL,
            tasks,
            sha256_path(PROTOCOL),
            run_implementation_provenance(ROOT),
        )


def test_strict_inventory_rejects_nonprefix_and_settings_drift() -> None:
    tasks = load_frozen_tasks(TASKS)
    rows = [
        _row(task, index, {condition: task["correct_target"] for condition in ACTOR_CONDITIONS})
        for index, task in enumerate(tasks[:4])
    ]
    for row in rows:
        row["run_scope"] = "smoke"
    validate_run_inventory(
        rows,
        MODEL,
        tasks,
        "smoke",
        sha256_path(PROTOCOL),
        run_implementation_provenance(ROOT),
        require_exact=True,
        require_complete=True,
    )
    nonprefix = json.loads(json.dumps(rows))
    nonprefix[1]["task"] = tasks[2]
    nonprefix[1]["task_sha256"] = task_hash(tasks[2])
    with pytest.raises(ValueError, match="exact frozen inventory prefix"):
        validate_run_inventory(
            nonprefix,
            MODEL,
            tasks,
            "smoke",
            sha256_path(PROTOCOL),
            run_implementation_provenance(ROOT),
            require_exact=True,
        )
    drift = json.loads(json.dumps(rows))
    drift[0]["api_settings"]["max_tokens"] = 501
    with pytest.raises(ValueError, match="API settings"):
        validate_run_inventory(
            drift,
            MODEL,
            tasks,
            "smoke",
            sha256_path(PROTOCOL),
            run_implementation_provenance(ROOT),
            require_exact=True,
        )


def test_resume_repairs_only_torn_tail_and_retains_completed_rows(tmp_path: Path) -> None:
    from scripts.run_end_to_end_decision_decomposition import load_and_repair_resume_file

    tasks = load_frozen_tasks(TASKS)
    rows = [
        _row(task, index, {condition: task["correct_target"] for condition in ACTOR_CONDITIONS})
        for index, task in enumerate(tasks[:2])
    ]
    for row in rows:
        row["run_scope"] = "smoke"
    path = tmp_path / "resume.jsonl"
    complete = "".join(json.dumps(row) + "\n" for row in rows).encode("utf-8")
    path.write_bytes(complete + b'{"task":"torn')
    with path.open("a+b") as handle:
        loaded, recovery = load_and_repair_resume_file(handle)
    assert loaded == rows
    assert recovery == {"action": "discarded_torn_tail", "bytes_discarded": 13}
    assert path.read_bytes() == complete


def test_claim_promotion_summary_is_machine_readable_and_bounded() -> None:
    tasks = load_frozen_tasks(TASKS)[:4]
    rows = [
        _row(task, index, {condition: task["correct_target"] for condition in ACTOR_CONDITIONS})
        for index, task in enumerate(tasks)
    ]
    summary = build_report(rows, seed=BOOTSTRAP_SEED, samples=50)["claim_promotion"]
    assert summary["composite_effect"]["promotion_status"] == (
        "not_eligible_for_bounded_composite_claim"
    )
    assert summary["prohibited_promotions"]["open_language_transfer"] == "not_evaluated"


def test_protocol_freezes_current_hashes_and_scope() -> None:
    text = PROTOCOL.read_text(encoding="utf-8")
    assert TASK_FILE_SHA256 in text
    assert prompt_hashes()["compiler_system"] in text
    assert prompt_hashes()["actor_system"] in text
    assert "960" in text
    assert "logically dependent" in text
    assert "orthogonal causal effects" in text
