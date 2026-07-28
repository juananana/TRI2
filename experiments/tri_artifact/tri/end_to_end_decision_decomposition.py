from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from tri.run_models import normalize_target


RUN_VERSION = "TRI-end-to-end-decision-decomposition-v1"
REPORT_VERSION = "TRI-end-to-end-decision-decomposition-report-v1"
RECORD_FORMAT_VERSION = "TRI-end-to-end-decision-decomposition-record-v2"
EVIDENCE_STATUS = "post-primary"
TASK_FILE_SHA256 = "5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c"
BOOTSTRAP_SEED = 20260728
BOOTSTRAP_SAMPLES = 10_000
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
}
ENDPOINT = "https://api.siliconflow.cn/v1"
RUN_SETTINGS = {
    "temperature": 0.0,
    "max_tokens": 500,
    "timeout_seconds": 180,
    "max_retries": 2,
    "retry_backoff_seconds": 2.0,
    "thinking_parameter": "disabled",
}
ACTOR_CONDITIONS = (
    "history_only",
    "mode_only",
    "mode_plus_id",
    "mode_plus_id_selector",
    "full_follow",
)
CONTRASTS = (
    ("history_only", "mode_only"),
    ("mode_only", "mode_plus_id"),
    ("mode_plus_id", "mode_plus_id_selector"),
    ("mode_plus_id_selector", "full_follow"),
    ("history_only", "full_follow"),
)
CONTRAST_METRICS = ("changed_pairacc", "e2e", "preserve_conditional_substitution")

COMPILER_SYSTEM_PROMPT = (
    "Compile target-resolution timing directly from the instruction and S0. Use "
    "reference_mode=\"preserve\" when the instruction selects or identifies the action target "
    "before refresh and later refers to that entity. Use reference_mode=\"reevaluate\" when "
    "refresh occurs before target selection. For preserve, resolve the selector in S0 and return "
    "that concrete ID as bound_target_id. For reevaluate, return null as bound_target_id. Restate "
    "the selector without changing its meaning or timing. Return one JSON object only with exactly "
    "these keys: reference_mode, bound_target_id, selector."
)
ACTOR_SYSTEM_PROMPT = (
    "Choose the entity ID for the requested action from the instruction and supplied states. Some "
    "payloads include a partial compiler_fragment as additional context. Only a separately supplied "
    "follow_instruction explicitly directs you to follow that fragment. Return one JSON object only "
    "with exactly these keys: action, target_id."
)
FOLLOW_INSTRUCTION = (
    "Follow the complete compiler_fragment when deciding whether to preserve its bound target or "
    "reevaluate its selector."
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def prompt_hashes() -> dict[str, str]:
    return {
        "compiler_system": sha256_text(COMPILER_SYSTEM_PROMPT),
        "actor_system": sha256_text(ACTOR_SYSTEM_PROMPT),
        "follow_instruction": sha256_text(FOLLOW_INSTRUCTION),
    }


def settings_hash() -> str:
    return sha256_text(canonical_json({"endpoint": ENDPOINT, "api_settings": RUN_SETTINGS}))


def run_implementation_provenance(root: Path) -> dict[str, Any]:
    source_paths = {
        "runner": root / "scripts" / "run_end_to_end_decision_decomposition.py",
        "core": root / "tri" / "end_to_end_decision_decomposition.py",
    }
    return {
        "record_format_version": RECORD_FORMAT_VERSION,
        "source_sha256": {
            name: sha256_path(path) for name, path in sorted(source_paths.items())
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
    }


def report_implementation_provenance(root: Path) -> dict[str, Any]:
    return {
        "reporter_sha256": sha256_path(
            root / "scripts" / "report_end_to_end_decision_decomposition.py"
        ),
        "core_sha256": sha256_path(root / "tri" / "end_to_end_decision_decomposition.py"),
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
    }


def model_id_hash(model: str) -> str:
    return sha256_text(model)


def task_hash(task: dict[str, Any]) -> str:
    return sha256_text(canonical_json(task))


def load_frozen_tasks(path: Path) -> list[dict[str, Any]]:
    observed = sha256_path(path)
    if observed != TASK_FILE_SHA256:
        raise ValueError(f"task hash mismatch: expected {TASK_FILE_SHA256}, observed {observed}")
    tasks = load_jsonl(path)
    if len(tasks) != 80 or len({task.get("id") for task in tasks}) != 80:
        raise ValueError("frozen inventory must contain 80 unique rows")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        grouped[str(task.get("state_cluster_id"))].append(task)
    if len(grouped) != 40:
        raise ValueError("frozen inventory must contain 40 state-cluster pairs")
    for cluster_id, pair in grouped.items():
        modes = Counter(task.get("reference_mode_gold") for task in pair)
        if len(pair) != 2 or modes != Counter({"preserve": 1, "reevaluate": 1}):
            raise ValueError(f"invalid matched pair: {cluster_id}")
        if any(task.get("pre_refresh_target") == task.get("post_refresh_target") for task in pair):
            raise ValueError(f"pair is not changed-winner: {cluster_id}")
    return tasks


def build_compiler_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "s0_state": task["initial_state"],
        "selector": task["selector"],
        "action": task["action"],
        "action_schema": task["action_schema"],
    }


def build_actor_base_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "s0_state": task["initial_state"],
        "s1_state": task["refreshed_state"],
        "selector": task["selector"],
        "action": task["action"],
        "action_schema": task["action_schema"],
    }


def decision_fragment(condition: str, compiler: dict[str, Any]) -> dict[str, Any] | None:
    if condition not in ACTOR_CONDITIONS:
        raise ValueError(f"unknown actor condition: {condition}")
    if condition == "history_only":
        return None
    fields = {
        "mode_only": ("reference_mode",),
        "mode_plus_id": ("reference_mode", "bound_target_id"),
        "mode_plus_id_selector": ("reference_mode", "bound_target_id", "selector"),
        "full_follow": ("reference_mode", "bound_target_id", "selector"),
    }[condition]
    return {field: compiler[field] for field in fields}


def build_actor_payload(
    task: dict[str, Any], compiler: dict[str, Any] | None, condition: str
) -> dict[str, Any]:
    payload = build_actor_base_payload(task)
    if condition != "history_only":
        if compiler is None:
            raise ValueError(f"{condition} requires a parsed compiler output")
        payload["compiler_fragment"] = decision_fragment(condition, compiler)
    if condition == "full_follow":
        payload["follow_instruction"] = FOLLOW_INSTRUCTION
    return payload


def actor_base_payload_hash(task: dict[str, Any]) -> str:
    return sha256_text(canonical_json(build_actor_base_payload(task)))


def actor_order(task_index: int) -> tuple[str, ...]:
    offset = task_index % len(ACTOR_CONDITIONS)
    return ACTOR_CONDITIONS[offset:] + ACTOR_CONDITIONS[:offset]


def _strict_object(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ValueError("schema_error: response content must be a string")
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"json_parse_error: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("schema_error: top-level value must be an object")
    return value


def parse_compiler_output(text: str) -> dict[str, Any]:
    value = _strict_object(text)
    required = {"reference_mode", "bound_target_id", "selector"}
    if set(value) != required:
        raise ValueError(f"schema_error: compiler keys must be exactly {sorted(required)}")
    mode = value["reference_mode"]
    if mode not in {"preserve", "reevaluate"}:
        raise ValueError("schema_error: invalid reference_mode")
    selector = value["selector"]
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("schema_error: selector must be a nonempty string")
    bound_id = normalize_target(value["bound_target_id"])
    if mode == "preserve" and bound_id is None:
        raise ValueError("schema_error: preserve bound_target_id must be non-null")
    if mode == "reevaluate" and bound_id is not None:
        raise ValueError("schema_error: reevaluate bound_target_id must be null")
    return {"reference_mode": mode, "bound_target_id": bound_id, "selector": selector.strip()}


def parse_actor_output(text: str) -> dict[str, Any]:
    value = _strict_object(text)
    if set(value) != {"action", "target_id"}:
        raise ValueError("schema_error: actor keys must be exactly action and target_id")
    if not isinstance(value["action"], str) or not value["action"].strip():
        raise ValueError("schema_error: action must be a nonempty string")
    target = normalize_target(value["target_id"])
    if target is None:
        raise ValueError("schema_error: target_id must be non-null")
    return {"action": value["action"].strip(), "target_id": target}


def _recorded_payload(
    component: dict[str, Any], expected_system_prompt: str, model: str
) -> dict[str, Any] | None:
    attempts = component.get("attempts", [])
    if not attempts:
        return None
    if len(attempts) > RUN_SETTINGS["max_retries"] + 1:
        raise ValueError("recorded component exceeds the frozen retry limit")
    payloads = []
    for attempt in attempts:
        request = attempt.get("request")
        if not isinstance(request, dict) or set(request) != {
            "model", "messages", "temperature", "max_tokens", "enable_thinking"
        }:
            raise ValueError("recorded request body does not match the frozen transport schema")
        if (
            request.get("model") != model
            or request.get("temperature") != RUN_SETTINGS["temperature"]
            or request.get("max_tokens") != RUN_SETTINGS["max_tokens"]
            or request.get("enable_thinking") is not False
        ):
            raise ValueError("recorded request body differs from the frozen transport settings")
        messages = request.get("messages", [])
        if len(messages) != 2:
            raise ValueError("recorded request must contain the frozen two-message prompt")
        if messages[0] != {"role": "system", "content": expected_system_prompt}:
            raise ValueError("recorded system prompt differs from the frozen prompt")
        if set(messages[1]) != {"role", "content"} or messages[1].get("role") != "user":
            raise ValueError("recorded user message differs from the frozen message schema")
        payloads.append(json.loads(messages[1]["content"]))
    if any(payload != payloads[0] for payload in payloads[1:]):
        raise ValueError("retry request payload differs within one logical call")
    return payloads[0]


def validate_run_row(
    row: dict[str, Any],
    require_complete: bool = False,
    expected_protocol_sha256: str | None = None,
    expected_implementation: dict[str, Any] | None = None,
) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("run provenance is missing or incorrect")
    task = row.get("task")
    if not isinstance(task, dict) or row.get("task_sha256") != task_hash(task):
        raise ValueError("task payload or task hash is invalid")
    model = str(row.get("model"))
    if row.get("model_id_sha256") != model_id_hash(model):
        raise ValueError("model ID hash mismatch")
    if row.get("prompt_sha256") != prompt_hashes():
        raise ValueError("prompt hash manifest mismatch")
    if row.get("endpoint") != ENDPOINT or row.get("api_settings") != RUN_SETTINGS:
        raise ValueError("endpoint or API settings differ from the frozen protocol")
    if row.get("settings_sha256") != settings_hash():
        raise ValueError("settings hash mismatch")
    if row.get("task_file_sha256") != TASK_FILE_SHA256:
        raise ValueError("task-file hash differs from the frozen inventory")
    if expected_protocol_sha256 is not None and row.get("protocol_sha256") != expected_protocol_sha256:
        raise ValueError("protocol hash mismatch")
    implementation = row.get("implementation_provenance")
    if not isinstance(implementation, dict):
        raise ValueError("implementation provenance is missing")
    if implementation.get("record_format_version") != RECORD_FORMAT_VERSION:
        raise ValueError("record format version mismatch")
    source_hashes = implementation.get("source_sha256")
    if not isinstance(source_hashes, dict) or set(source_hashes) != {"core", "runner"}:
        raise ValueError("implementation source hashes are incomplete")
    if any(not isinstance(value, str) or len(value) != 64 for value in source_hashes.values()):
        raise ValueError("implementation source hash is malformed")
    if expected_implementation is not None:
        if source_hashes != expected_implementation.get("source_sha256"):
            raise ValueError("run implementation differs from the current frozen implementation")
        if implementation.get("record_format_version") != expected_implementation.get(
            "record_format_version"
        ):
            raise ValueError("run implementation record format mismatch")
    recording_session = row.get("recording_session")
    if (
        not isinstance(recording_session, dict)
        or not isinstance(recording_session.get("run_session_id"), str)
        or not recording_session["run_session_id"]
        or not isinstance(recording_session.get("resumed_after_rows"), int)
        or not 0 <= recording_session["resumed_after_rows"] <= int(row.get("task_index", -1))
    ):
        raise ValueError("recording-session provenance is invalid")
    if row.get("logical_calls_planned") != 6:
        raise ValueError("each task must plan one compiler and five actor calls")

    compiler_component = row.get("compiler", {})
    compiler = compiler_component.get("parsed")
    compiler_id = row.get("compiler_output_id")
    actors = row.get("actors", {})
    if set(actors) != set(ACTOR_CONDITIONS) or set(row.get("outcomes", {})) != set(ACTOR_CONDITIONS):
        raise ValueError("all five actor conditions and outcomes must be recorded")
    if any(actors[name].get("compiler_output_id") != compiler_id for name in ACTOR_CONDITIONS):
        raise ValueError("actors do not reference one shared compiler output")
    if row.get("actor_base_payload_sha256") != actor_base_payload_hash(task):
        raise ValueError("actor base payload hash mismatch")
    if row.get("actor_order") != list(actor_order(int(row.get("task_index", -1)))):
        raise ValueError("actor order does not follow the frozen rotation")

    compiler_payload = _recorded_payload(compiler_component, COMPILER_SYSTEM_PROMPT, model)
    if compiler_payload is not None and compiler_payload != build_compiler_payload(task):
        raise ValueError("compiler payload differs from the frozen projection")
    for condition in ACTOR_CONDITIONS:
        payload = _recorded_payload(actors[condition], ACTOR_SYSTEM_PROMPT, model)
        parsed_target = normalize_target((actors[condition].get("parsed") or {}).get("target_id"))
        if normalize_target(row["outcomes"].get(condition)) != parsed_target:
            raise ValueError(f"recorded outcome does not match parsed actor target for {condition}")
        if payload is None:
            continue
        if condition != "history_only" and compiler is None:
            raise ValueError("dependent actor attempted without a parsed compiler output")
        if payload != build_actor_payload(task, compiler, condition):
            raise ValueError(f"actor payload mismatch for {condition}")
        prohibited = {"initial_selected_id", "pre_refresh_target", "correct_target", "reference_mode_gold"}
        if prohibited.intersection(payload):
            raise ValueError("actor payload exposes a resolver or gold field")

    components = [compiler_component, *(actors[name] for name in ACTOR_CONDITIONS)]
    logical_attempted = sum(bool(component.get("attempts")) for component in components)
    logical_completed = sum(
        bool(component.get("attempts"))
        and component["attempts"][-1].get("status") == "success"
        for component in components
    )
    complete = all(component.get("parsed") is not None for component in components)
    if (
        row.get("logical_calls_attempted") != logical_attempted
        or row.get("logical_calls_completed") != logical_completed
        or row.get("complete") is not complete
    ):
        raise ValueError("logical-call accounting or row completeness is inconsistent")

    if require_complete:
        if not row.get("complete") or row.get("logical_calls_completed") != 6:
            raise ValueError("health-smoke row is incomplete")
        if any(component.get("parsed") is None for component in components):
            raise ValueError("health-smoke row contains an API, parse, or schema failure")


def validate_run_inventory(
    rows: list[dict[str, Any]],
    model: str,
    tasks: list[dict[str, Any]],
    run_scope: str,
    expected_protocol_sha256: str,
    expected_implementation: dict[str, Any],
    require_exact: bool,
    require_complete: bool = False,
) -> None:
    if run_scope not in {"smoke", "full"}:
        raise ValueError("run scope must be smoke or full")
    expected = tasks[:4] if run_scope == "smoke" else tasks
    if require_exact and len(rows) != len(expected):
        raise ValueError(
            f"{run_scope} must contain exactly {len(expected)} frozen rows; observed {len(rows)}"
        )
    if len(rows) > len(expected):
        raise ValueError(f"{run_scope} contains more rows than the frozen inventory")
    observed_ids = [row.get("task", {}).get("id") for row in rows]
    expected_ids = [task["id"] for task in expected[: len(rows)]]
    if observed_ids != expected_ids or len(set(observed_ids)) != len(observed_ids):
        raise ValueError(f"{run_scope} rows must be the exact frozen inventory prefix in order")
    for index, (row, task) in enumerate(zip(rows, expected)):
        if row.get("model") != model or row.get("run_scope") != run_scope:
            raise ValueError("model or run scope does not match the requested run")
        if row.get("task_index") != index or row.get("task") != task:
            raise ValueError("task index or payload differs from the frozen inventory")
        validate_run_row(
            row,
            require_complete=require_complete,
            expected_protocol_sha256=expected_protocol_sha256,
            expected_implementation=expected_implementation,
        )


def validate_health_smoke(
    rows: list[dict[str, Any]],
    model: str,
    tasks: list[dict[str, Any]],
    expected_protocol_sha256: str,
    expected_implementation: dict[str, Any],
) -> None:
    validate_run_inventory(
        rows,
        model,
        tasks,
        "smoke",
        expected_protocol_sha256,
        expected_implementation,
        require_exact=True,
        require_complete=True,
    )


def _pairs(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["task"]["state_cluster_id"]].append(row)
    return [grouped[name] for name in sorted(grouped)]


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bootstrap(
    pairs: list[list[dict[str, Any]]],
    statistic: Callable[[list[list[dict[str, Any]]]], float | None],
    seed: int,
    samples: int,
) -> list[float | None]:
    if not pairs:
        return [None, None]
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        value = statistic(sample)
        if value is not None:
            values.append(value)
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _target(row: dict[str, Any], condition: str) -> str | None:
    return normalize_target(row.get("outcomes", {}).get(condition))


def _correct(row: dict[str, Any], condition: str) -> bool:
    parsed = row.get("actors", {}).get(condition, {}).get("parsed") or {}
    action = parsed.get("action")
    action_correct = (
        isinstance(action, str)
        and action.strip().casefold() == str(row["task"]["action"]).strip().casefold()
    )
    return action_correct and _target(row, condition) == row["task"]["correct_target"]


def _compiler_mode_correct(row: dict[str, Any]) -> bool:
    compiler = row.get("compiler", {}).get("parsed") or {}
    return compiler.get("reference_mode") == row["task"]["reference_mode_gold"]


def _compiler_preserve_id_correct(row: dict[str, Any]) -> bool:
    compiler = row.get("compiler", {}).get("parsed") or {}
    return (
        row["task"]["reference_mode_gold"] == "preserve"
        and compiler.get("reference_mode") == "preserve"
        and normalize_target(compiler.get("bound_target_id")) == row["task"]["pre_refresh_target"]
    )


def _substitution_eligible(row: dict[str, Any]) -> bool:
    task = row["task"]
    return (
        _compiler_preserve_id_correct(row)
        and bool(task.get("bound_entity_present_after_refresh"))
        and bool(task.get("bound_entity_actionable_after_refresh"))
        and task.get("pre_refresh_target") != task.get("post_refresh_target")
    )


def _row_measure(
    pairs: list[list[dict[str, Any]]],
    numerator: Callable[[dict[str, Any]], bool],
    eligible: Callable[[dict[str, Any]], bool] | None,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    rows = [row for pair in pairs for row in pair]
    use = [row for row in rows if eligible is None or eligible(row)]

    def statistic(sample_pairs: list[list[dict[str, Any]]]) -> float | None:
        sample_rows = [row for pair in sample_pairs for row in pair]
        sample_use = [row for row in sample_rows if eligible is None or eligible(row)]
        if not sample_use:
            return None
        return sum(numerator(row) for row in sample_use) / len(sample_use)

    count = sum(numerator(row) for row in use)
    return {
        "numerator": count,
        "denominator": len(use),
        "rate": count / len(use) if use else None,
        "ci95_pair_cluster": _bootstrap(pairs, statistic, seed, samples),
    }


def _pairacc_measure(
    pairs: list[list[dict[str, Any]]], condition: str, seed: int, samples: int
) -> dict[str, Any]:
    def valid(pair: list[dict[str, Any]]) -> bool:
        return len(pair) == 2 and {
            row["task"]["reference_mode_gold"] for row in pair
        } == {"preserve", "reevaluate"}

    use = [pair for pair in pairs if valid(pair)]
    pair_correct = lambda pair: all(_correct(row, condition) for row in pair)

    def statistic(sample_pairs: list[list[dict[str, Any]]]) -> float | None:
        sample_use = [pair for pair in sample_pairs if valid(pair)]
        return (
            sum(pair_correct(pair) for pair in sample_use) / len(sample_use)
            if sample_use
            else None
        )

    count = sum(pair_correct(pair) for pair in use)
    return {
        "numerator": count,
        "denominator": len(use),
        "rate": count / len(use) if use else None,
        "ci95_pair_cluster": _bootstrap(pairs, statistic, seed, samples),
    }


def _binary_units(
    pairs: list[list[dict[str, Any]]], condition: str, metric: str
) -> list[bool]:
    if metric == "changed_pairacc":
        return [all(_correct(row, condition) for row in pair) for pair in pairs]
    rows = [row for pair in pairs for row in pair]
    if metric == "e2e":
        return [_correct(row, condition) for row in rows]
    if metric == "preserve_conditional_substitution":
        return [
            _target(row, condition) == row["task"]["post_refresh_target"]
            for row in rows
            if _substitution_eligible(row)
        ]
    raise ValueError(f"unknown metric: {metric}")


def _metric_rate(pairs: list[list[dict[str, Any]]], condition: str, metric: str) -> float | None:
    units = _binary_units(pairs, condition, metric)
    return sum(units) / len(units) if units else None


def exact_paired_p(left_only: int, right_only: int) -> float | None:
    discordant = left_only + right_only
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, index) for index in range(min(left_only, right_only) + 1))
    return min(1.0, 2.0 * tail / (2**discordant))


def _paired_contrast(
    pairs: list[list[dict[str, Any]]],
    left: str,
    right: str,
    metric: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    left_units = _binary_units(pairs, left, metric)
    right_units = _binary_units(pairs, right, metric)
    if len(left_units) != len(right_units):
        raise ValueError("paired contrast has unmatched eligibility")
    left_only = sum(a and not b for a, b in zip(left_units, right_units))
    right_only = sum(b and not a for a, b in zip(left_units, right_units))
    both_correct = sum(a and b for a, b in zip(left_units, right_units))
    both_incorrect = sum(not a and not b for a, b in zip(left_units, right_units))

    def statistic(sample_pairs: list[list[dict[str, Any]]]) -> float | None:
        l_rate = _metric_rate(sample_pairs, left, metric)
        r_rate = _metric_rate(sample_pairs, right, metric)
        return None if l_rate is None or r_rate is None else r_rate - l_rate

    left_rate = _metric_rate(pairs, left, metric)
    right_rate = _metric_rate(pairs, right, metric)
    difference = None if left_rate is None or right_rate is None else right_rate - left_rate
    return {
        "left": left,
        "right": right,
        "metric": metric,
        "difference_right_minus_left": difference,
        "ci95_pair_cluster": _bootstrap(pairs, statistic, seed, samples),
        "discordance": {
            "unit": "pair" if metric == "changed_pairacc" else "task_row",
            "both_positive": both_correct,
            "left_only": left_only,
            "right_only": right_only,
            "both_negative": both_incorrect,
            "n": len(left_units),
        },
        "exact_p_unadjusted": exact_paired_p(left_only, right_only),
        "holm_family": "all_actor_contrasts_within_model",
        "exact_p_holm": None,
    }


def apply_holm(items: list[dict[str, Any]]) -> None:
    indexed = [
        (index, item["exact_p_unadjusted"])
        for index, item in enumerate(items)
        if item["exact_p_unadjusted"] is not None
    ]
    indexed.sort(key=lambda value: value[1])
    running = 0.0
    total = len(indexed)
    for rank, (index, p_value) in enumerate(indexed):
        running = max(running, min(1.0, (total - rank) * p_value))
        items[index]["exact_p_holm"] = running


def _component_summary(components: list[dict[str, Any]]) -> dict[str, Any]:
    def kind(component: dict[str, Any]) -> str:
        if component.get("parsed") is not None:
            return "parsed"
        if component.get("error_kind"):
            return str(component["error_kind"])
        return "unknown"

    attempts = [attempt for component in components for attempt in component.get("attempts", [])]
    kinds = Counter(kind(component) for component in components)
    return {
        "logical_planned": len(components),
        "logical_attempted": sum(bool(component.get("attempts")) for component in components),
        "logical_parsed": kinds["parsed"],
        "api_failures": kinds["api"],
        "parse_or_schema_failures": kinds["parse_or_schema"],
        "upstream_skips": kinds["upstream"],
        "unknown_failures": kinds["unknown"],
        "http_attempts": len(attempts),
        "http_retries": sum(max(0, len(component.get("attempts", [])) - 1) for component in components),
        "attempt_statuses": dict(sorted(Counter(str(a.get("status", "unknown")) for a in attempts).items())),
        "attempt_error_kinds": dict(sorted(Counter(
            str(a.get("error_kind", "none")) for a in attempts if a.get("status") != "success"
        ).items())),
    }


def _model_report(rows: list[dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    if len({row["task"]["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate task rows for one model")
    for row in rows:
        validate_run_row(row)
    pairs = _pairs(rows)
    preserve = lambda row: row["task"]["reference_mode_gold"] == "preserve"
    compiler = {
        "mode_accuracy": _row_measure(pairs, _compiler_mode_correct, None, seed, samples),
        "preserve_bound_id_accuracy": _row_measure(
            pairs, _compiler_preserve_id_correct, preserve, seed, samples
        ),
    }
    metrics = {
        condition: {
            "changed_pairacc": _pairacc_measure(pairs, condition, seed, samples),
            "e2e": _row_measure(
                pairs, lambda row, c=condition: _correct(row, c), None, seed, samples
            ),
            "preserve_conditional_substitution": _row_measure(
                pairs,
                lambda row, c=condition: _target(row, c) == row["task"]["post_refresh_target"],
                _substitution_eligible,
                seed,
                samples,
            ),
        }
        for condition in ACTOR_CONDITIONS
    }
    contrasts = [
        _paired_contrast(pairs, left, right, metric, seed, samples)
        for left, right in CONTRASTS
        for metric in CONTRAST_METRICS
    ]
    apply_holm(contrasts)
    components = {
        "compiler": [row["compiler"] for row in rows],
        **{condition: [row["actors"][condition] for row in rows] for condition in ACTOR_CONDITIONS},
    }
    attempts = {name: _component_summary(values) for name, values in components.items()}
    attempts["all_components"] = _component_summary(
        [component for values in components.values() for component in values]
    )
    usage = [
        component.get("usage") or {}
        for values in components.values()
        for component in values
    ]
    return {
        "model": rows[0]["model"],
        "model_id_sha256": model_id_hash(rows[0]["model"]),
        "rows": len(rows),
        "pairs": len(pairs),
        "complete_rows": sum(bool(row.get("complete")) for row in rows),
        "compiler": compiler,
        "metrics": metrics,
        "paired_contrasts": contrasts,
        "failure_and_attempt_accounting": attempts,
        "token_usage": {
            "prompt_tokens": sum(int(item.get("prompt_tokens", 0) or 0) for item in usage),
            "completion_tokens": sum(int(item.get("completion_tokens", 0) or 0) for item in usage),
        },
    }


def build_report(
    rows: list[dict[str, Any]],
    seed: int = BOOTSTRAP_SEED,
    samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot report an empty run")
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    report = {
        "report_version": REPORT_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "causal_scope": (
            "The ladder adds logically dependent serialized fields. It estimates these ordered "
            "increments under the frozen prompts, not all interactions or orthogonal field effects."
        ),
        "bootstrap": {"unit": "state_cluster_id", "samples": samples, "seed": seed},
        "auxiliary_tests": {
            "test": "two-sided exact paired discordance",
            "adjustment": "Holm within each model across 15 actor-contrast endpoint tests",
        },
        "provenance": {
            "task_file_sha256": sorted({str(row.get("task_file_sha256")) for row in rows}),
            "protocol_sha256": sorted({str(row.get("protocol_sha256")) for row in rows}),
            "prompt_sha256": prompt_hashes(),
            "run_scopes": sorted({str(row.get("run_scope")) for row in rows}),
        },
        "models": [_model_report(by_model[model], seed, samples) for model in sorted(by_model)],
    }
    report["claim_promotion"] = build_claim_promotion_summary(report)
    return report


def _contrast_lookup(model: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (item["left"], item["right"], item["metric"]): item
        for item in model["paired_contrasts"]
    }


def _ci_supports(item: dict[str, Any], direction: str) -> bool:
    lower, upper = item["ci95_pair_cluster"]
    if lower is None or upper is None:
        return False
    if direction == "positive":
        return lower > 0
    if direction == "negative":
        return upper < 0
    raise ValueError(f"unknown direction: {direction}")


def build_claim_promotion_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Encode only the interpretation gates frozen before provider calls."""
    composite_by_model: list[dict[str, Any]] = []
    adjacent: dict[str, Any] = {}
    models = report["models"]
    for model in models:
        lookup = _contrast_lookup(model)
        pairacc = lookup[("history_only", "full_follow", "changed_pairacc")]
        substitution = lookup[
            ("history_only", "full_follow", "preserve_conditional_substitution")
        ]
        pairacc_gain = pairacc["difference_right_minus_left"]
        substitution_change = substitution["difference_right_minus_left"]
        direction_gate = (
            pairacc_gain is not None
            and pairacc_gain > 0
            and substitution_change is not None
            and substitution_change < 0
        )
        composite_by_model.append({
            "model": model["model"],
            "pairacc_gain_full_minus_history": pairacc_gain,
            "pairacc_ci95_pair_cluster": pairacc["ci95_pair_cluster"],
            "conditional_substitution_change_full_minus_history": substitution_change,
            "conditional_substitution_ci95_pair_cluster": substitution["ci95_pair_cluster"],
            "direction_gate_met": direction_gate,
        })

    for left, right in CONTRASTS[:-1]:
        name = f"{right}_minus_{left}"
        per_model = []
        for model in models:
            item = _contrast_lookup(model)[(left, right, "changed_pairacc")]
            difference = item["difference_right_minus_left"]
            per_model.append({
                "model": model["model"],
                "difference": difference,
                "ci95_pair_cluster": item["ci95_pair_cluster"],
                "positive_ci_support": _ci_supports(item, "positive"),
                "negative_ci_support": _ci_supports(item, "negative"),
            })
        positive = len(per_model) == len(MODEL_IDS) and all(
            item["positive_ci_support"] for item in per_model
        )
        negative = len(per_model) == len(MODEL_IDS) and all(
            item["negative_ci_support"] for item in per_model
        )
        adjacent[name] = {
            "models": per_model,
            "cross_model_interval_status": (
                "supported_positive" if positive else "supported_negative" if negative else "not_supported"
            ),
            "adjacent_attribution_promotable": positive,
        }

    composite_gate = len(composite_by_model) == len(MODEL_IDS) and all(
        item["direction_gate_met"] for item in composite_by_model
    )
    earlier_attribution = any(
        adjacent[name]["adjacent_attribution_promotable"]
        for name in list(adjacent)[:-1]
    )
    follow_only = (
        adjacent.get("full_follow_minus_mode_plus_id_selector", {}).get(
            "adjacent_attribution_promotable", False
        )
        and not earlier_attribution
    )
    return {
        "frozen_rule": (
            "Promote only a bounded end-to-end composite decision representation effect when "
            "MISF-H improves PairAcc and reduces conditional substitution across both frozen "
            "models. Attribute an adjacent increment only with same-direction cross-model "
            "pair-cluster interval support."
        ),
        "composite_effect": {
            "models": composite_by_model,
            "cross_model_direction_gate_met": composite_gate,
            "promotion_status": (
                "eligible_for_bounded_composite_claim"
                if composite_gate
                else "not_eligible_for_bounded_composite_claim"
            ),
        },
        "adjacent_pairacc_attribution": adjacent,
        "interpretation": (
            "narrow_to_explicit_follow_or_interface_effect"
            if follow_only
            else "ordered_ladder_requires_result-specific_interpretation"
        ),
        "prohibited_promotions": {
            "orthogonal_field_effects": "not_identified_by_logically_dependent_ladder",
            "unique_internal_mechanism": "not_identified",
            "open_language_transfer": "not_evaluated",
            "deployment_prevalence": "not_evaluated",
        },
    }


def _pct(metric: dict[str, Any]) -> str:
    if metric["rate"] is None:
        return f"NA ({metric['numerator']}/{metric['denominator']})"
    lo, hi = metric["ci95_pair_cluster"]
    ci = "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
    return f"{100 * metric['rate']:.1f}% ({metric['numerator']}/{metric['denominator']}), CI {ci}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# End-to-End Decision Decomposition",
        "",
        "**Evidence status:** post-primary.",
        "",
        report["causal_scope"],
        "",
        f"Pair-cluster bootstrap: {report['bootstrap']['samples']:,} replicates, seed "
        f"{report['bootstrap']['seed']}.",
        "",
    ]
    for model in report["models"]:
        lines.extend([
            f"## {model['model']}",
            "",
            f"Rows: {model['rows']}; pairs: {model['pairs']}; complete rows: "
            f"{model['complete_rows']}. Model hash: `{model['model_id_sha256']}`.",
            "",
            f"Compiler mode accuracy: {_pct(model['compiler']['mode_accuracy'])}.",
            f"Compiler Preserve bound-ID accuracy: "
            f"{_pct(model['compiler']['preserve_bound_id_accuracy'])}.",
            "",
            "| Condition | Changed PairAcc | ITT E2E | Preserve substitution after correct compiler binding |",
            "|---|---:|---:|---:|",
        ])
        for condition in ACTOR_CONDITIONS:
            metrics = model["metrics"][condition]
            lines.append(
                f"| {condition} | {_pct(metrics['changed_pairacc'])} | {_pct(metrics['e2e'])} | "
                f"{_pct(metrics['preserve_conditional_substitution'])} |"
            )
        lines.extend([
            "",
            "| Contrast | Metric | Difference (right-left) | 95% cluster CI | Discordance L/R | Exact p | Holm p |",
            "|---|---|---:|---:|---:|---:|---:|",
        ])
        for item in model["paired_contrasts"]:
            estimate = item["difference_right_minus_left"]
            lo, hi = item["ci95_pair_cluster"]
            estimate_text = "NA" if estimate is None else f"{100 * estimate:.1f} pp"
            ci_text = "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
            discordance = item["discordance"]
            lines.append(
                f"| {item['left']} -> {item['right']} | {item['metric']} | {estimate_text} | "
                f"{ci_text} | {discordance['left_only']}/{discordance['right_only']} | "
                f"{item['exact_p_unadjusted']:.4g} | {item['exact_p_holm']:.4g} |"
            )
        lines.extend(["", "### Failure and attempt accounting", ""])
        lines.append(
            "| Component | Planned | Attempted | Parsed | API fail | Parse fail | Upstream skip | HTTP attempts | Retries |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for component, values in model["failure_and_attempt_accounting"].items():
            lines.append(
                f"| {component} | {values['logical_planned']} | {values['logical_attempted']} | "
                f"{values['logical_parsed']} | {values['api_failures']} | "
                f"{values['parse_or_schema_failures']} | {values['upstream_skips']} | "
                f"{values['http_attempts']} | {values['http_retries']} |"
            )
        lines.append("")
    lines.extend([
        "API, parse, schema, and upstream failures remain incorrect in ITT E2E and PairAcc. The "
        "conditional substitution denominator uses only Preserve rows with a correct compiler mode "
        "and S0 bound ID, a surviving action-valid old target, and a changed winner.",
        "",
    ])
    return "\n".join(lines)
