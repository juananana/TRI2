from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

from tri.run_models import normalize_target


RUN_VERSION = "TRI-convention-told-natural-history-v1"
REPORT_VERSION = "TRI-convention-told-natural-history-report-v1"
EVIDENCE_STATUS = "post-primary replication/audit"
TASK_FILE_SHA256 = "5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c"
BOOTSTRAP_SEED = 20260728
BOOTSTRAP_SAMPLES = 10_000
CONDITIONS = ("plain_history", "convention_told")
PAYLOAD_KEYS = {
    "original_instruction",
    "initial_state_before_refresh",
    "current_refreshed_state",
    "action_schema",
    "question",
}
FORBIDDEN_KEY_PARTS = (
    "gold",
    "initial_selected_id",
    "bound_target_id",
    "reference_mode",
    "compiler",
    "pre_refresh_target",
    "post_refresh_target",
    "correct_target",
    "pair_id",
    "selector",
    "binding",
    "phenomenon",
    "template",
    "paraphrase",
)

PLAIN_SYSTEM_PROMPT = (
    "You are an agent controller deciding the final target after an environment refresh. You "
    "receive the original user instruction, the initial state observed before refresh, and the "
    "refreshed state. Use the user instruction and states to choose the final target. Return JSON "
    "only: {\"action\":\"process\",\"target_id\":\"...\"} or "
    "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)
CONVENTION_TEXT = (
    "If the user selected or referred to a specific entity before the refresh, keep that entity "
    "as long as the requested action remains valid. If the user explicitly postponed selection "
    "until after the refresh, recompute the selector on the refreshed state."
)
CONVENTION_SYSTEM_PROMPT = (
    "You are an agent controller deciding the final target after an environment refresh. You "
    "receive the original user instruction, the initial state observed before refresh, and the "
    "refreshed state. Use the user instruction and states to choose the final target. "
    + CONVENTION_TEXT
    + " Return JSON only: {\"action\":\"process\",\"target_id\":\"...\"} or "
    "{\"action\":\"invalid\",\"target_id\":\"INVALID_BOUND_ENTITY\"}."
)
SYSTEM_PROMPTS = {
    "plain_history": PLAIN_SYSTEM_PROMPT,
    "convention_told": CONVENTION_SYSTEM_PROMPT,
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_inventory(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    if len(tasks) != 80:
        raise ValueError(f"expected 80 frozen rows, found {len(tasks)}")
    if len({task.get("id") for task in tasks}) != 80:
        raise ValueError("task IDs must be unique")
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        if task.get("update") != "flip":
            raise ValueError("Convention inventory must contain changed-winner Flip rows only")
        if task.get("reference_mode_gold") not in {"preserve", "reevaluate"}:
            raise ValueError("invalid reference_mode_gold")
        if task.get("pre_refresh_target") == task.get("post_refresh_target"):
            raise ValueError("changed-winner row has the same pre/post target")
        expected = (
            task["pre_refresh_target"]
            if task["reference_mode_gold"] == "preserve"
            else task["post_refresh_target"]
        )
        if task.get("correct_target") != expected:
            raise ValueError("task gold conflicts with frozen timing mode")
        pairs[str(task.get("pair_id"))].append(task)
    if len(pairs) != 40:
        raise ValueError(f"expected 40 pairs, found {len(pairs)}")
    for pair_id, pair in pairs.items():
        if len(pair) != 2 or {row["reference_mode_gold"] for row in pair} != {
            "preserve",
            "reevaluate",
        }:
            raise ValueError(f"pair {pair_id} is not one Preserve/Reevaluate pair")
        if pair[0]["initial_state"] != pair[1]["initial_state"]:
            raise ValueError(f"pair {pair_id} has unmatched initial states")
        if pair[0]["refreshed_state"] != pair[1]["refreshed_state"]:
            raise ValueError(f"pair {pair_id} has unmatched refreshed states")
        if pair[0]["correct_target"] == pair[1]["correct_target"]:
            raise ValueError(f"pair {pair_id} does not have opposite gold targets")
    return {"rows": len(tasks), "pairs": len(pairs)}


def load_frozen_inventory(path: Path) -> list[dict[str, Any]]:
    if sha256_path(path) != TASK_FILE_SHA256:
        raise ValueError("Convention inventory hash does not match the frozen protocol")
    tasks = load_jsonl(path)
    validate_inventory(tasks)
    return tasks


def build_payload(task: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "original_instruction": task["instruction"],
        "initial_state_before_refresh": task["initial_state"],
        "current_refreshed_state": task["refreshed_state"],
        "action_schema": task["action_schema"],
        "question": "Which target_id should be processed now?",
    }
    validate_payload(payload)
    return payload


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_payload(payload: dict[str, Any]) -> None:
    if set(payload) != PAYLOAD_KEYS:
        raise ValueError(f"payload keys must be exactly {sorted(PAYLOAD_KEYS)}")
    lowered_keys = [key.lower() for key in _walk_keys(payload)]
    leaked = sorted(
        forbidden for forbidden in FORBIDDEN_KEY_PARTS if any(forbidden in key for key in lowered_keys)
    )
    if leaked:
        raise ValueError(f"forbidden payload fields: {leaked}")


def payload_sha256(task: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(build_payload(task)).encode("utf-8"))


def _strict_object(text: str) -> dict[str, Any]:
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


def parse_output(text: str) -> dict[str, Any]:
    value = _strict_object(text)
    if set(value) != {"action", "target_id"}:
        raise ValueError("schema_error: keys must be exactly action and target_id")
    action = value["action"]
    if action not in {"process", "invalid"}:
        raise ValueError("schema_error: action must be process or invalid")
    target = normalize_target(value["target_id"])
    if target is None:
        raise ValueError("schema_error: target_id must be non-null")
    if action == "invalid" and target != "INVALID_BOUND_ENTITY":
        raise ValueError("schema_error: invalid action requires INVALID_BOUND_ENTITY")
    return {"action": action, "target_id": target}


def _component_error_kind(component: dict[str, Any]) -> str | None:
    if component.get("error_kind"):
        return str(component["error_kind"])
    return None


def validate_run_row(row: dict[str, Any]) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("invalid run provenance")
    task = row.get("task")
    if not isinstance(task, dict):
        raise ValueError("missing frozen task")
    if row.get("logical_calls_planned") != 2:
        raise ValueError("each row must plan two logical calls")
    if set(row.get("conditions", {})) != set(CONDITIONS):
        raise ValueError("both convention conditions must be recorded")
    if set(row.get("outcomes", {})) != set(CONDITIONS):
        raise ValueError("both convention outcomes must be recorded")
    expected_hash = payload_sha256(task)
    if row.get("user_payload_sha256") != expected_hash:
        raise ValueError("user payload hash mismatch")
    recorded_payloads: dict[str, dict[str, Any]] = {}
    for condition in CONDITIONS:
        component = row["conditions"][condition]
        attempts = component.get("attempts", [])
        if attempts and attempts[-1].get("request"):
            messages = attempts[-1]["request"].get("messages", [])
            if len(messages) != 2:
                raise ValueError("attempt does not contain the frozen two-message prompt")
            if messages[0] != {"role": "system", "content": SYSTEM_PROMPTS[condition]}:
                raise ValueError("system prompt differs from the frozen condition prompt")
            payload = json.loads(messages[1]["content"])
            validate_payload(payload)
            if payload != build_payload(task):
                raise ValueError("recorded payload differs from the frozen task payload")
            recorded_payloads[condition] = payload
        parsed = component.get("parsed")
        target = None if parsed is None else normalize_target(parsed.get("target_id"))
        if row["outcomes"].get(condition) != target:
            raise ValueError("outcome does not match parsed target")
    if set(recorded_payloads) == set(CONDITIONS):
        if canonical_json(recorded_payloads[CONDITIONS[0]]) != canonical_json(
            recorded_payloads[CONDITIONS[1]]
        ):
            raise ValueError("condition user payloads are not byte-matched")


def validate_smoke(rows: list[dict[str, Any]], tasks: list[dict[str, Any]], model: str) -> None:
    expected = [task["id"] for task in tasks[:16]]
    observed = [row.get("task", {}).get("id") for row in rows]
    if len(rows) != 16 or observed != expected:
        raise ValueError("smoke must contain the first eight complete pairs (16 rows)")
    if any(row.get("model") != model for row in rows):
        raise ValueError("smoke model mismatch")
    failures = {condition: 0 for condition in CONDITIONS}
    for row in rows:
        validate_run_row(row)
        for condition in CONDITIONS:
            if row["conditions"][condition].get("parsed") is None:
                failures[condition] += 1
    if any(count > 1 for count in failures.values()):
        raise ValueError(f"smoke exceeds the frozen failure gate: {failures}")


def validate_resume_prefix(
    rows: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    model: str,
    run_scope: str,
    task_hash: str,
    protocol_hash: str,
    addendum_hash: str,
) -> None:
    if len(rows) >= len(tasks):
        raise ValueError("resume output is already complete or too long")
    if [row.get("task", {}).get("id") for row in rows] != [task["id"] for task in tasks[: len(rows)]]:
        raise ValueError("resume output is not the exact ordered frozen prefix")
    for index, row in enumerate(rows):
        validate_run_row(row)
        if row.get("task_index") != index:
            raise ValueError("resume task index mismatch")
        if row.get("model") != model or row.get("run_scope") != run_scope:
            raise ValueError("resume model or run scope mismatch")
        if (
            row.get("task_file_sha256") != task_hash
            or row.get("protocol_sha256") != protocol_hash
            or row.get("addendum_sha256") != addendum_hash
        ):
            raise ValueError("resume freeze hash mismatch")


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
    clusters: dict[str, list[dict[str, Any]]],
    statistic: Callable[[list[dict[str, Any]]], float | None],
    seed: int,
    samples: int,
) -> list[float | None]:
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        sample = [row for _ in names for row in clusters[rng.choice(names)]]
        value = statistic(sample)
        if value is not None:
            values.append(value)
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _target(row: dict[str, Any], condition: str) -> str | None:
    return normalize_target(row.get("outcomes", {}).get(condition))


def _correct(row: dict[str, Any], condition: str) -> bool:
    return _target(row, condition) == row["task"]["correct_target"]


def _rate_metric(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    numerator: Callable[[dict[str, Any]], bool],
    eligible: Callable[[dict[str, Any]], bool],
    seed: int,
    samples: int,
) -> dict[str, Any]:
    use = [row for row in rows if eligible(row)]
    count = sum(numerator(row) for row in use)

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        sample_use = [row for row in sample if eligible(row)]
        return None if not sample_use else sum(numerator(row) for row in sample_use) / len(sample_use)

    return {
        "numerator": count,
        "denominator": len(use),
        "rate": None if not use else count / len(use),
        "ci95_state_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _pair_rate(rows: list[dict[str, Any]], condition: str) -> float | None:
    if not rows:
        return None
    if len(rows) % 2:
        raise ValueError("paired statistic received an odd number of rows")
    pairs = [rows[index : index + 2] for index in range(0, len(rows), 2)]
    return sum(
        len(pair) == 2
        and {row["task"]["reference_mode_gold"] for row in pair} == {"preserve", "reevaluate"}
        and all(_correct(row, condition) for row in pair)
        for pair in pairs
    ) / len(pairs)


def _pair_metric(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    condition: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    rate = _pair_rate(rows, condition)
    numerator = round((rate or 0) * len(clusters))
    return {
        "numerator": numerator,
        "denominator": len(clusters),
        "rate": rate,
        "ci95_state_cluster": _bootstrap(
            clusters, lambda sample: _pair_rate(sample, condition), seed, samples
        ),
    }


def _difference(
    rows: list[dict[str, Any]],
    clusters: dict[str, list[dict[str, Any]]],
    metric: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    def rate(sample: list[dict[str, Any]], condition: str) -> float | None:
        if metric == "changed_pairacc":
            return _pair_rate(sample, condition)
        if not sample:
            return None
        return sum(_correct(row, condition) for row in sample) / len(sample)

    left = rate(rows, "plain_history")
    right = rate(rows, "convention_told")
    estimate = None if left is None or right is None else right - left

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        sample_left = rate(sample, "plain_history")
        sample_right = rate(sample, "convention_told")
        return None if sample_left is None or sample_right is None else sample_right - sample_left

    return {
        "left": "plain_history",
        "right": "convention_told",
        "metric": metric,
        "difference_right_minus_left": estimate,
        "ci95_state_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _model_report(rows: list[dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    if len(rows) != len({row["task"]["id"] for row in rows}):
        raise ValueError("duplicate task rows for one model")
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        validate_run_row(row)
        clusters[row["task"]["pair_id"]].append(row)
    metrics: dict[str, Any] = {}
    for condition in CONDITIONS:
        metrics[condition] = {
            "changed_pairacc": _pair_metric(rows, clusters, condition, seed, samples),
            "e2e": _rate_metric(rows, clusters, lambda row, c=condition: _correct(row, c), lambda _: True, seed, samples),
            "preserve_accuracy": _rate_metric(
                rows,
                clusters,
                lambda row, c=condition: _correct(row, c),
                lambda row: row["task"]["reference_mode_gold"] == "preserve",
                seed,
                samples,
            ),
            "reevaluate_accuracy": _rate_metric(
                rows,
                clusters,
                lambda row, c=condition: _correct(row, c),
                lambda row: row["task"]["reference_mode_gold"] == "reevaluate",
                seed,
                samples,
            ),
            "preserve_refreshed_winner_error": _rate_metric(
                rows,
                clusters,
                lambda row, c=condition: _target(row, c) == row["task"]["post_refresh_target"],
                lambda row: row["task"]["reference_mode_gold"] == "preserve",
                seed,
                samples,
            ),
            "reevaluate_old_target_error": _rate_metric(
                rows,
                clusters,
                lambda row, c=condition: _target(row, c) == row["task"]["pre_refresh_target"],
                lambda row: row["task"]["reference_mode_gold"] == "reevaluate",
                seed,
                samples,
            ),
        }
    components = [row["conditions"][condition] for row in rows for condition in CONDITIONS]
    attempts = [attempt for component in components for attempt in component.get("attempts", [])]
    usages = [component.get("usage") or {} for component in components]
    return {
        "model": rows[0]["model"],
        "rows": len(rows),
        "state_clusters": len(clusters),
        "metrics": metrics,
        "paired_differences": [
            _difference(rows, clusters, metric, seed, samples)
            for metric in ("changed_pairacc", "e2e")
        ],
        "failures": {
            "api": sum(_component_error_kind(component) == "api" for component in components),
            "parse_or_schema": sum(
                _component_error_kind(component) == "parse_or_schema" for component in components
            ),
            "incomplete_tasks": sum(not row.get("complete") for row in rows),
        },
        "calls": {
            "logical_planned": sum(row.get("logical_calls_planned", 0) for row in rows),
            "logical_completed": sum(row.get("logical_calls_completed", 0) for row in rows),
            "http_attempts": len(attempts),
            "retries": sum(max(0, len(component.get("attempts", [])) - 1) for component in components),
            "prompt_tokens": sum(int(usage.get("prompt_tokens", 0) or 0) for usage in usages),
            "completion_tokens": sum(int(usage.get("completion_tokens", 0) or 0) for usage in usages),
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
    return {
        "report_version": REPORT_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "estimand": "Convention-told minus Plain-history changed PairAcc, separately by model",
        "bootstrap": {"unit": "state_cluster_id", "samples": samples, "seed": seed},
        "models": [_model_report(by_model[model], seed, samples) for model in sorted(by_model)],
        "boundaries": [
            "Authored frozen gold; not independent-human or open-language evidence.",
            "No structured ID, reference-mode record, compiler decision, or separately scored initial binding.",
            "Refreshed-winner and old-target errors are unconditional and are not called conditional TRI.",
        ],
    }


def _pct(metric: dict[str, Any]) -> str:
    if metric["rate"] is None:
        return f"NA ({metric['numerator']}/{metric['denominator']})"
    lo, hi = metric["ci95_state_cluster"]
    interval = "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
    return f"{100 * metric['rate']:.1f}% ({metric['numerator']}/{metric['denominator']}), {interval}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Convention-Told Natural-History Control",
        "",
        "Evidence status: **post-primary replication/audit**.",
        "",
        report["estimand"] + ".",
        "",
        f"Bootstrap: {report['bootstrap']['samples']:,} state-cluster draws; seed {report['bootstrap']['seed']}.",
        "",
    ]
    for model in report["models"]:
        lines.extend([
            f"## {model['model']}",
            "",
            f"Rows: {model['rows']}; changed pairs: {model['state_clusters']}.",
            "",
            "| Condition | Changed PairAcc | E2E | Preserve | Reevaluate |",
            "|---|---:|---:|---:|---:|",
        ])
        for condition in CONDITIONS:
            metrics = model["metrics"][condition]
            lines.append(
                f"| {condition} | {_pct(metrics['changed_pairacc'])} | {_pct(metrics['e2e'])} | "
                f"{_pct(metrics['preserve_accuracy'])} | {_pct(metrics['reevaluate_accuracy'])} |"
            )
        lines.extend(["", "| Contrast | Estimate | 95% CI |", "|---|---:|---:|"])
        for contrast in model["paired_differences"]:
            estimate = contrast["difference_right_minus_left"]
            lo, hi = contrast["ci95_state_cluster"]
            estimate_text = "NA" if estimate is None else f"{100 * estimate:.1f} pp"
            interval = "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
            lines.append(f"| Convention - Plain {contrast['metric']} | {estimate_text} | {interval} |")
        lines.extend([
            "",
            f"Failures: {model['failures']['api']} API; {model['failures']['parse_or_schema']} parse/schema; "
            f"{model['failures']['incomplete_tasks']} incomplete task rows.",
            f"Calls: {model['calls']['logical_completed']}/{model['calls']['logical_planned']} logical; "
            f"{model['calls']['http_attempts']} HTTP attempts; {model['calls']['retries']} retries.",
            "",
        ])
    lines.extend(["## Boundaries", ""] + [f"- {item}" for item in report["boundaries"]] + [""])
    return "\n".join(lines)
