from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from tri.end_to_end_decision_decomposition import (
    canonical_json,
    exact_paired_p,
    load_jsonl,
    sha256_path,
    sha256_text,
)
from tri.run_models import normalize_target


RUN_VERSION = "TRI-end-to-end-decision-decomposition-v2"
REPORT_VERSION = "TRI-end-to-end-decision-decomposition-report-v2"
RECORD_FORMAT_VERSION = "TRI-end-to-end-decision-decomposition-record-v1"
EVIDENCE_STATUS = "planned post-primary; frozen before calls"
TASK_FILE_SHA256 = "5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c"
BOOTSTRAP_SEED = 20260729
BOOTSTRAP_SAMPLES = 10_000
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
    "deepseek": "deepseek-ai/DeepSeek-V4-Pro",
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
    "placebo",
    "selector_only",
    "id_control",
    "mode_only",
    "mode_plus_id",
    "mode_plus_id_selector",
    "full_follow",
)
COMPILER_DEPENDENT = frozenset(ACTOR_CONDITIONS) - {"history_only", "placebo"}
CONTRASTS = (
    ("history_only", "placebo"),
    ("history_only", "selector_only"),
    ("history_only", "id_control"),
    ("history_only", "mode_only"),
    ("mode_only", "mode_plus_id"),
    ("mode_plus_id", "mode_plus_id_selector"),
    ("mode_plus_id_selector", "full_follow"),
    ("placebo", "full_follow"),
)
METRICS = ("changed_pairacc", "e2e", "preserve_conditional_substitution")

COMPILER_SYSTEM_PROMPT = (
    "Compile target-resolution timing directly from the instruction and S0. Return the S0 winner "
    "of the supplied selector as pre_refresh_candidate_id on every row. Use reference_mode=\"preserve\" "
    "when the instruction commits before refresh and reference_mode=\"reevaluate\" when selection is "
    "deferred until after refresh. For preserve, bound_target_id must equal pre_refresh_candidate_id; "
    "for reevaluate, bound_target_id must be null. Restate the selector without changing its meaning "
    "or timing. Return one JSON object only with exactly these keys: reference_mode, "
    "pre_refresh_candidate_id, bound_target_id, selector."
)
ACTOR_SYSTEM_PROMPT = (
    "Choose the entity ID for the requested action from the instruction and supplied states. Some "
    "payloads contain structured context or a compiler_fragment. Treat it as additional context unless "
    "a separate follow_instruction explicitly directs you to follow it. Return one JSON object only "
    "with exactly these keys: action, target_id."
)
FOLLOW_INSTRUCTION = (
    "Follow the complete compiler_fragment when deciding whether to preserve its bound target or "
    "reevaluate its selector."
)


def prompt_hashes() -> dict[str, str]:
    return {
        "compiler_system": sha256_text(COMPILER_SYSTEM_PROMPT),
        "actor_system": sha256_text(ACTOR_SYSTEM_PROMPT),
        "follow_instruction": sha256_text(FOLLOW_INSTRUCTION),
    }


def settings_hash() -> str:
    return sha256_text(canonical_json({"endpoint": ENDPOINT, "api_settings": RUN_SETTINGS}))


def load_frozen_tasks(path: Path) -> list[dict[str, Any]]:
    observed = sha256_path(path)
    if observed != TASK_FILE_SHA256:
        raise ValueError(f"task hash mismatch: expected {TASK_FILE_SHA256}, observed {observed}")
    tasks = load_jsonl(path)
    if len(tasks) != 80 or len({task.get("id") for task in tasks}) != 80:
        raise ValueError("frozen inventory must contain 80 unique rows")
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        pairs[str(task.get("state_cluster_id"))].append(task)
    if len(pairs) != 40:
        raise ValueError("frozen inventory must contain 40 pairs")
    for pair_id, pair in pairs.items():
        if len(pair) != 2 or Counter(row.get("reference_mode_gold") for row in pair) != {
            "preserve": 1,
            "reevaluate": 1,
        }:
            raise ValueError(f"invalid pair: {pair_id}")
        if any(row.get("pre_refresh_target") == row.get("post_refresh_target") for row in pair):
            raise ValueError(f"pair is not changed-winner: {pair_id}")
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


def placebo_fragment(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "requested_action": task["action"],
        "tool_schema": task["action_schema"],
        "state_record_counts": {
            "s0": len(task["initial_state"]),
            "s1": len(task["refreshed_state"]),
        },
    }


def compiler_fragment(condition: str, compiler: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "selector_only": ("selector",),
        "id_control": ("pre_refresh_candidate_id",),
        "mode_only": ("reference_mode",),
        "mode_plus_id": ("reference_mode", "bound_target_id"),
        "mode_plus_id_selector": ("reference_mode", "bound_target_id", "selector"),
        "full_follow": ("reference_mode", "bound_target_id", "selector"),
    }
    if condition not in fields:
        raise ValueError(f"condition has no compiler fragment: {condition}")
    return {field: compiler[field] for field in fields[condition]}


def build_actor_payload(
    task: dict[str, Any], compiler: dict[str, Any] | None, condition: str
) -> dict[str, Any]:
    if condition not in ACTOR_CONDITIONS:
        raise ValueError(f"unknown actor condition: {condition}")
    payload = build_actor_base_payload(task)
    if condition == "placebo":
        payload["context_summary"] = placebo_fragment(task)
    elif condition in COMPILER_DEPENDENT:
        if compiler is None:
            raise ValueError(f"{condition} requires compiler output")
        payload["compiler_fragment"] = compiler_fragment(condition, compiler)
    if condition == "full_follow":
        payload["follow_instruction"] = FOLLOW_INSTRUCTION
    return payload


def actor_order(task_index: int) -> tuple[str, ...]:
    offset = task_index % len(ACTOR_CONDITIONS)
    return ACTOR_CONDITIONS[offset:] + ACTOR_CONDITIONS[:offset]


def parse_compiler_output(text: str) -> dict[str, Any]:
    from tri.end_to_end_decision_decomposition import _strict_object

    value = _strict_object(text)
    required = {
        "reference_mode",
        "pre_refresh_candidate_id",
        "bound_target_id",
        "selector",
    }
    if set(value) != required:
        raise ValueError(f"schema_error: compiler keys must be exactly {sorted(required)}")
    mode = value["reference_mode"]
    if mode not in {"preserve", "reevaluate"}:
        raise ValueError("schema_error: invalid reference_mode")
    candidate = normalize_target(value["pre_refresh_candidate_id"])
    bound = normalize_target(value["bound_target_id"])
    selector = value["selector"]
    if candidate is None:
        raise ValueError("schema_error: pre_refresh_candidate_id must be non-null")
    if mode == "preserve" and bound != candidate:
        raise ValueError("schema_error: preserve bound_target_id must equal candidate")
    if mode == "reevaluate" and bound is not None:
        raise ValueError("schema_error: reevaluate bound_target_id must be null")
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("schema_error: selector must be nonempty")
    return {
        "reference_mode": mode,
        "pre_refresh_candidate_id": candidate,
        "bound_target_id": bound,
        "selector": selector.strip(),
    }


def parse_actor_output(text: str) -> dict[str, Any]:
    from tri.end_to_end_decision_decomposition import parse_actor_output as parse_v1

    return parse_v1(text)


def validate_run_row(row: dict[str, Any]) -> None:
    if row.get("run_version") != RUN_VERSION:
        raise ValueError("run version mismatch")
    task = row.get("task", {})
    if row.get("task_sha256") != sha256_text(canonical_json(task)):
        raise ValueError("task hash mismatch")
    if row.get("task_file_sha256") != TASK_FILE_SHA256:
        raise ValueError("task inventory mismatch")
    if row.get("prompt_sha256") != prompt_hashes() or row.get("settings_sha256") != settings_hash():
        raise ValueError("prompt or settings hash mismatch")
    if row.get("logical_calls_planned") != 9:
        raise ValueError("each row must plan one compiler and eight actors")
    if tuple(row.get("actor_order", ())) != actor_order(int(row.get("task_index", -1))):
        raise ValueError("actor rotation mismatch")
    actors = row.get("actors", {})
    if set(actors) != set(ACTOR_CONDITIONS) or set(row.get("outcomes", {})) != set(ACTOR_CONDITIONS):
        raise ValueError("all eight actor cells are required")
    compiler = (row.get("compiler") or {}).get("parsed")
    for condition in ACTOR_CONDITIONS:
        component = actors[condition]
        parsed = component.get("parsed") or {}
        if normalize_target(parsed.get("target_id")) != normalize_target(row["outcomes"][condition]):
            raise ValueError(f"outcome mismatch for {condition}")
        attempts = component.get("attempts", [])
        if not attempts:
            if condition in COMPILER_DEPENDENT and compiler is None:
                continue
            raise ValueError(f"unexpected missing attempt for {condition}")
        request = attempts[-1].get("request", {})
        messages = request.get("messages", [])
        if len(messages) != 2 or messages[0] != {"role": "system", "content": ACTOR_SYSTEM_PROMPT}:
            raise ValueError(f"actor prompt mismatch for {condition}")
        payload = json.loads(messages[1]["content"])
        if payload != build_actor_payload(task, compiler, condition):
            raise ValueError(f"actor payload mismatch for {condition}")


def validate_run_inventory(rows: list[dict[str, Any]], model: str, tasks: list[dict[str, Any]]) -> None:
    if len(rows) != len(tasks):
        raise ValueError(f"expected {len(tasks)} rows, observed {len(rows)}")
    if [row.get("task", {}).get("id") for row in rows] != [task["id"] for task in tasks]:
        raise ValueError("run rows do not match frozen task order")
    if any(row.get("model") != model for row in rows):
        raise ValueError("mixed or unexpected model")
    for row in rows:
        validate_run_row(row)


def _is_correct(row: dict[str, Any], condition: str) -> bool:
    parsed = row["actors"][condition].get("parsed") or {}
    return (
        parsed.get("action") == row["task"]["action"]
        and normalize_target(parsed.get("target_id")) == normalize_target(row["task"]["correct_target"])
    )


def _pairs(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["task"]["state_cluster_id"]].append(row)
    pairs = list(grouped.values())
    if any(len(pair) != 2 for pair in pairs):
        raise ValueError("report requires complete pairs")
    return pairs


def _substitution_units(rows: list[dict[str, Any]], condition: str) -> list[int]:
    values = []
    for row in rows:
        task = row["task"]
        compiler = row["compiler"].get("parsed") or {}
        eligible = (
            task["reference_mode_gold"] == "preserve"
            and compiler.get("reference_mode") == "preserve"
            and normalize_target(compiler.get("pre_refresh_candidate_id")) == normalize_target(task["pre_refresh_target"])
            and normalize_target(compiler.get("bound_target_id")) == normalize_target(task["pre_refresh_target"])
            and task.get("bound_entity_present_after_refresh") is True
            and task.get("bound_entity_actionable_after_refresh") is True
            and task["pre_refresh_target"] != task["post_refresh_target"]
        )
        if eligible:
            target = normalize_target((row["actors"][condition].get("parsed") or {}).get("target_id"))
            values.append(int(target == normalize_target(task["post_refresh_target"])))
    return values


def _units(rows: list[dict[str, Any]], condition: str, metric: str) -> list[int]:
    if metric == "e2e":
        return [int(_is_correct(row, condition)) for row in rows]
    if metric == "changed_pairacc":
        return [int(all(_is_correct(row, condition) for row in pair)) for pair in _pairs(rows)]
    if metric == "preserve_conditional_substitution":
        return _substitution_units(rows, condition)
    raise ValueError(metric)


def _rate(units: list[int]) -> float | None:
    return None if not units else sum(units) / len(units)


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bootstrap_difference(
    left: list[int], right: list[int], seed: int, samples: int
) -> tuple[float | None, list[float | None]]:
    if len(left) != len(right) or not left:
        return None, [None, None]
    rng = random.Random(seed)
    diffs = []
    for _ in range(samples):
        indices = [rng.randrange(len(left)) for _ in left]
        diffs.append(sum(right[i] - left[i] for i in indices) / len(indices))
    return _rate(right) - _rate(left), [_percentile(diffs, 0.025), _percentile(diffs, 0.975)]


def _token_summary(rows: list[dict[str, Any]], condition: str) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        usage = row["actors"][condition].get("usage") or {}
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            if isinstance(usage.get(key), int):
                totals[key] += usage[key]
        details = usage.get("prompt_tokens_details") or {}
        if isinstance(details.get("cached_tokens"), int):
            totals["cached_tokens"] += details["cached_tokens"]
    return dict(totals)


def _holm(items: list[dict[str, Any]]) -> None:
    valid = [(index, item["p_value"]) for index, item in enumerate(items) if item["p_value"] is not None]
    running = 0.0
    for rank, (index, p_value) in enumerate(sorted(valid, key=lambda value: value[1])):
        adjusted = min(1.0, p_value * (len(valid) - rank))
        running = max(running, adjusted)
        items[index]["p_value_holm"] = running
    for item in items:
        item.setdefault("p_value_holm", None)


def build_report(rows: list[dict[str, Any]], seed: int = BOOTSTRAP_SEED, samples: int = BOOTSTRAP_SAMPLES) -> dict[str, Any]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    models = []
    for model, model_rows in sorted(by_model.items()):
        cells = {}
        for condition in ACTOR_CONDITIONS:
            metrics = {}
            for metric in METRICS:
                units = _units(model_rows, condition, metric)
                metrics[metric] = {"numerator": sum(units), "denominator": len(units), "rate": _rate(units)}
            failures = Counter(
                (row["actors"][condition].get("error_kind") or "none") for row in model_rows
            )
            cells[condition] = {"metrics": metrics, "failures": dict(failures), "tokens": _token_summary(model_rows, condition)}
        contrasts = []
        for contrast_index, (left_name, right_name) in enumerate(CONTRASTS):
            for metric_index, metric in enumerate(METRICS):
                left = _units(model_rows, left_name, metric)
                right = _units(model_rows, right_name, metric)
                difference, interval = _bootstrap_difference(
                    left, right, seed + contrast_index * 101 + metric_index, samples
                )
                left_only = sum(a == 1 and b == 0 for a, b in zip(left, right)) if len(left) == len(right) else 0
                right_only = sum(a == 0 and b == 1 for a, b in zip(left, right)) if len(left) == len(right) else 0
                contrasts.append({
                    "left": left_name,
                    "right": right_name,
                    "metric": metric,
                    "difference": difference,
                    "ci95": interval,
                    "left_only": left_only,
                    "right_only": right_only,
                    "p_value": exact_paired_p(left_only, right_only) if len(left) == len(right) else None,
                })
        _holm(contrasts)
        models.append({"model": model, "rows": len(model_rows), "cells": cells, "contrasts": contrasts})
    report = {
        "report_version": REPORT_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "bootstrap": {"seed": seed, "samples": samples, "unit": "paired binary endpoint"},
        "models": models,
    }
    report["claim_promotion"] = build_claim_promotion(report)
    return report


def build_claim_promotion(report: dict[str, Any]) -> dict[str, Any]:
    decisions = []
    for left, right in CONTRASTS:
        intervals = []
        for model in report["models"]:
            match = next(
                item for item in model["contrasts"]
                if item["left"] == left and item["right"] == right and item["metric"] == "changed_pairacc"
            )
            intervals.append({"model": model["model"], "ci95": match["ci95"]})
        positive = sum(ci["ci95"][0] is not None and ci["ci95"][0] > 0 for ci in intervals)
        negative = any(ci["ci95"][1] is not None and ci["ci95"][1] < 0 for ci in intervals)
        decisions.append({
            "contrast": f"{right}-{left}",
            "eligible_for_field_claim": positive >= 2 and not negative,
            "positive_models": positive,
            "has_significant_reverse_model": negative,
            "model_intervals": intervals,
        })
    return {
        "rule": "PairAcc CI positive in at least two of three models and negative in none",
        "decisions": decisions,
        "never_promotes": ["architecture necessity", "internal mechanism", "open-language transfer", "prevalence"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Decision Decomposition v2", "", f"Evidence status: `{report['evidence_status']}`.", ""]
    for model in report["models"]:
        lines.extend([f"## {model['model']}", "", "| Cell | PairAcc | E2E | Substitution | Prompt tokens | Completion tokens |", "|---|---:|---:|---:|---:|---:|"])
        for condition in ACTOR_CONDITIONS:
            cell = model["cells"][condition]
            values = []
            for metric in METRICS:
                item = cell["metrics"][metric]
                values.append(f"{item['numerator']}/{item['denominator']}")
            lines.append(
                f"| {condition} | {' | '.join(values)} | {cell['tokens'].get('prompt_tokens', 0)} | {cell['tokens'].get('completion_tokens', 0)} |"
            )
        lines.extend(["", "| Contrast | Metric | Difference | 95% CI | Holm p |", "|---|---|---:|---:|---:|"])
        for item in model["contrasts"]:
            diff = "NA" if item["difference"] is None else f"{100 * item['difference']:.1f} pp"
            ci = item["ci95"]
            ci_text = "NA" if ci[0] is None else f"[{100 * ci[0]:.1f}, {100 * ci[1]:.1f}]"
            p = "NA" if item["p_value_holm"] is None else f"{item['p_value_holm']:.4g}"
            lines.append(f"| {item['right']} - {item['left']} | {item['metric']} | {diff} | {ci_text} | {p} |")
        lines.append("")
    lines.extend(["## Claim gate", "", "Field and composite claims require positive PairAcc intervals in at least two models and no significant reverse-model interval. The gate cannot promote architecture, mechanism, transfer, or prevalence claims.", ""])
    return "\n".join(lines)
