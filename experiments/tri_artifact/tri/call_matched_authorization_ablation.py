from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from tri.run_models import normalize_target


RUN_VERSION = "TRI-call-matched-authorization-ablation-v2"
EVIDENCE_STATUS = "post-primary"
SOURCE_SHA256 = "2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891"
TASK_FILE_SHA256 = "5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c"
BOOTSTRAP_SEED = 20260725
BOOTSTRAP_SAMPLES = 10_000
ACTOR_CONDITIONS = ("history_only", "decision_visible")
OUTCOME_CONDITIONS = ACTOR_CONDITIONS + ("decision_enforced",)
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
}

COMPILER_SYSTEM_PROMPT = (
    "Compile the instruction's target-resolution timing. Use reference_mode=\"preserve\" when the "
    "instruction selects or identifies the action target before refresh and later refers to that "
    "entity. Use reference_mode=\"reevaluate\" when refresh happens before target selection. For "
    "preserve, return the concrete initial selected ID as bound_target_id. For reevaluate, return "
    "null as bound_target_id. Copy the task's selector meaning without changing its timing. Return "
    "one JSON object only with exactly these keys: reference_mode, bound_target_id, selector."
)
ACTOR_SYSTEM_PROMPT = (
    "Choose the entity ID for the requested action. Use the instruction and supplied states exactly. "
    "The initial_selected_id is the entity selected by the stated selector in S0. S1 is the state "
    "after refresh. If a compiler_decision field is present, follow that decision when resolving "
    "whether the initial entity is preserved or the selector is reevaluated. Return one JSON object "
    "only with exactly these keys: action, target_id."
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return ("\n".join(canonical_json(row) for row in rows) + "\n").encode("utf-8")


def _s0_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "app": row["app"],
        "entity_type": row["entity"],
        "records": row["initial_state"],
    }


def build_tasks(source: Path, verify_source_hash: bool = True) -> list[dict[str, Any]]:
    if verify_source_hash and sha256_path(source) != SOURCE_SHA256:
        raise ValueError(f"source inventory hash mismatch: {source}")
    selected = [row for row in load_jsonl(source) if row.get("update") == "flip"]
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_cluster[str(row["state_cluster_id"])].append(row)
    if len(by_cluster) != 40:
        raise ValueError(f"expected 40 flip state clusters, found {len(by_cluster)}")

    tasks: list[dict[str, Any]] = []
    for cluster_id in sorted(by_cluster):
        source_pair = by_cluster[cluster_id]
        counts = {
            binding: sum(row.get("binding") == binding for row in source_pair)
            for binding in ("anchored", "dynamic")
        }
        if len(source_pair) != 2 or counts != {"anchored": 1, "dynamic": 1}:
            raise ValueError(f"cluster {cluster_id} is not one anchored/dynamic flip pair: {counts}")
        for binding in ("anchored", "dynamic"):
            source_row = next(row for row in source_pair if row["binding"] == binding)
            if source_row["pre_refresh_target"] == source_row["post_refresh_target"]:
                raise ValueError(f"cluster {cluster_id} is not a changed-winner flip")
            mode = "preserve" if binding == "anchored" else "reevaluate"
            expected_gold = (
                source_row["pre_refresh_target"]
                if mode == "preserve"
                else source_row["post_refresh_target"]
            )
            if source_row["correct_target"] != expected_gold:
                raise ValueError(f"source gold conflicts with mode in {source_row['id']}")
            task = dict(source_row)
            task.update({
                "id": f"tri-call-matched-{source_row['id']}",
                "source_task_id": source_row["id"],
                "inventory_version": "call-matched-authorization-ablation-v1",
                "pair_id": cluster_id,
                "reference_mode_gold": mode,
                "initial_selected_id": source_row["pre_refresh_target"],
                "s0_summary": _s0_summary(source_row),
            })
            tasks.append(task)
    return tasks


def build_compiler_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "s0_summary": task["s0_summary"],
        "initial_selected_id": task["initial_selected_id"],
        "selector": task["selector"],
        "action": task["action"],
        "action_schema": task["action_schema"],
        "refresh_notice": "State S1 is observed after refresh and before the action.",
    }


def build_actor_payload(task: dict[str, Any], decision: dict[str, Any] | None) -> dict[str, Any]:
    payload = {
        "instruction": task["instruction"],
        "s0_summary": task["s0_summary"],
        "initial_selected_id": task["initial_selected_id"],
        "s1_state": task["refreshed_state"],
        "selector": task["selector"],
        "action": task["action"],
        "action_schema": task["action_schema"],
    }
    if decision is not None:
        payload["compiler_decision"] = decision
    return payload


def actor_base_payload_hash(task: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(build_actor_payload(task, None)).encode("utf-8"))


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
    if value["reference_mode"] not in {"preserve", "reevaluate"}:
        raise ValueError("schema_error: invalid reference_mode")
    selector = value["selector"]
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("schema_error: selector must be a nonempty string")
    target = normalize_target(value["bound_target_id"])
    if value["reference_mode"] == "reevaluate" and target is not None:
        raise ValueError("schema_error: reevaluate bound_target_id must be null")
    if value["reference_mode"] == "preserve" and target is None:
        raise ValueError("schema_error: preserve bound_target_id must be non-null")
    return {
        "reference_mode": value["reference_mode"],
        "bound_target_id": target,
        "selector": selector.strip(),
    }


def parse_actor_output(text: str) -> dict[str, Any]:
    value = _strict_object(text)
    required = {"action", "target_id"}
    if set(value) != required:
        raise ValueError(f"schema_error: actor keys must be exactly {sorted(required)}")
    if not isinstance(value["action"], str) or not value["action"].strip():
        raise ValueError("schema_error: action must be a nonempty string")
    target = normalize_target(value["target_id"])
    if target is None:
        raise ValueError("schema_error: target_id must be non-null")
    return {"action": value["action"].strip(), "target_id": target}


def decision_enforced_target(
    compiler: dict[str, Any] | None,
    visible_target: str | None,
) -> str | None:
    if compiler and compiler.get("reference_mode") == "preserve":
        return normalize_target(compiler.get("bound_target_id"))
    return normalize_target(visible_target)


def validate_run_row(row: dict[str, Any], require_complete: bool = False) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("run provenance is missing or incorrect")
    task = row.get("task")
    if not isinstance(task, dict) or task.get("reference_mode_gold") not in {"preserve", "reevaluate"}:
        raise ValueError("invalid task payload")
    if row.get("logical_calls_planned") != 3:
        raise ValueError("each task must plan exactly three logical calls")
    decision_id = row.get("compiler_decision_id")
    actors = row.get("actors", {})
    if set(actors) != set(ACTOR_CONDITIONS):
        raise ValueError("both matched actor conditions must be recorded")
    if any(actors[name].get("compiler_decision_id") != decision_id for name in ACTOR_CONDITIONS):
        raise ValueError("actor conditions do not reference one shared compiler decision")
    base_hash = row.get("actor_base_payload_sha256")
    if base_hash is not None and base_hash != actor_base_payload_hash(task):
        raise ValueError("actor base payload hash mismatch")
    outcomes = row.get("outcomes", {})
    if set(outcomes) != set(OUTCOME_CONDITIONS):
        raise ValueError("all three outcomes must be present")
    compiler = row.get("compiler", {}).get("parsed")
    expected = decision_enforced_target(
        compiler, outcomes.get("decision_visible")
    )
    if outcomes.get("decision_enforced") != expected:
        raise ValueError("decision-enforced target was not derived from the visible actor outcome")
    compiler_parsed = row.get("compiler", {}).get("parsed")
    recorded_payloads: dict[str, dict[str, Any]] = {}
    for name in ACTOR_CONDITIONS:
        attempts = actors[name].get("attempts", [])
        if attempts and attempts[-1].get("request"):
            messages = attempts[-1]["request"].get("messages", [])
            if len(messages) != 2:
                raise ValueError("actor attempt does not contain the frozen two-message prompt")
            recorded_payloads[name] = json.loads(messages[1]["content"])
    if set(recorded_payloads) == set(ACTOR_CONDITIONS):
        history_payload = recorded_payloads["history_only"]
        visible_payload = dict(recorded_payloads["decision_visible"])
        visible_decision = visible_payload.pop("compiler_decision", None)
        if history_payload != visible_payload:
            raise ValueError("matched actor payloads differ beyond compiler_decision")
        if visible_decision != compiler_parsed:
            raise ValueError("decision-visible actor did not receive the shared parsed compiler decision")
        if history_payload != build_actor_payload(task, None):
            raise ValueError("actor payload differs from the frozen task payload")
    if require_complete:
        if not row.get("complete") or row.get("logical_calls_completed") != 3:
            raise ValueError("health-smoke row is incomplete")
        if compiler is None or any(actors[name].get("parsed") is None for name in ACTOR_CONDITIONS):
            raise ValueError("health-smoke row contains an API, parse, or schema failure")


def validate_health_smoke(rows: list[dict[str, Any]], model: str, tasks: list[dict[str, Any]]) -> None:
    expected = [task["id"] for task in tasks[:4]]
    observed = [row.get("task", {}).get("id") for row in rows]
    if len(rows) != 4 or observed != expected:
        raise ValueError("health smoke must contain the first four frozen tasks in order")
    if any(row.get("model") != model for row in rows):
        raise ValueError("health-smoke model does not match the requested full run")
    for row in rows:
        validate_run_row(row, require_complete=True)
        successful_attempts = sum(
            bool(component.get("attempts")) and component["attempts"][-1].get("status") == "success"
            for component in [row["compiler"], *(row["actors"][name] for name in ACTOR_CONDITIONS)]
        )
        if successful_attempts != 3:
            raise ValueError("health-smoke task does not have three successful logical calls")


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
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


def _measure(
    rows: list[dict[str, Any]],
    numerator: Callable[[dict[str, Any]], bool],
    eligible: Callable[[dict[str, Any]], bool] | None,
    clusters: dict[str, list[dict[str, Any]]],
    seed: int,
    samples: int,
) -> dict[str, Any]:
    use = [row for row in rows if eligible is None or eligible(row)]
    count = sum(numerator(row) for row in use)
    denominator = len(use)

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        sample_use = [row for row in sample if eligible is None or eligible(row)]
        if not sample_use:
            return None
        return sum(numerator(row) for row in sample_use) / len(sample_use)

    return {
        "count": count,
        "numerator": count,
        "denominator": denominator,
        "rate": count / denominator if denominator else None,
        "ci95_state_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _target(row: dict[str, Any], condition: str) -> str | None:
    return normalize_target(row.get("outcomes", {}).get(condition))


def _correct(row: dict[str, Any], condition: str) -> bool:
    return _target(row, condition) == row["task"]["correct_target"]


def _pair_measure(
    clusters: dict[str, list[dict[str, Any]]], condition: str, seed: int, samples: int
) -> dict[str, Any]:
    def pair_correct(pair: list[dict[str, Any]]) -> bool:
        modes = {row["task"]["reference_mode_gold"] for row in pair}
        return len(pair) == 2 and modes == {"preserve", "reevaluate"} and all(_correct(row, condition) for row in pair)

    count = sum(pair_correct(pair) for pair in clusters.values())

    def statistic(sample: list[dict[str, Any]]) -> float:
        pairs = [sample[index:index + 2] for index in range(0, len(sample), 2)]
        return sum(pair_correct(pair) for pair in pairs) / len(pairs)

    return {
        "count": count,
        "numerator": count,
        "denominator": len(clusters),
        "rate": count / len(clusters) if clusters else None,
        "ci95_state_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _paired_difference(
    clusters: dict[str, list[dict[str, Any]]],
    left: str,
    right: str,
    metric: str,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    def rate(rows: list[dict[str, Any]], condition: str) -> float | None:
        if metric == "e2e":
            return sum(_correct(row, condition) for row in rows) / len(rows)
        if metric == "preserve_conditional_substitution":
            eligible = [
                row
                for row in rows
                if row["task"]["reference_mode_gold"] == "preserve"
                and (row.get("compiler", {}).get("parsed") or {}).get("reference_mode")
                == "preserve"
                and normalize_target(
                    (row.get("compiler", {}).get("parsed") or {}).get("bound_target_id")
                )
                == row["task"]["pre_refresh_target"]
            ]
            if not eligible:
                return None
            return sum(
                _target(row, condition) == row["task"]["post_refresh_target"]
                for row in eligible
            ) / len(eligible)
        pairs = [rows[index:index + 2] for index in range(0, len(rows), 2)]
        if not pairs:
            return None
        return sum(
            len(pair) == 2 and all(_correct(row, condition) for row in pair)
            for pair in pairs
        ) / len(pairs)

    all_rows = [row for pair in clusters.values() for row in pair]
    left_estimate, right_estimate = rate(all_rows, left), rate(all_rows, right)
    estimate = (
        None
        if left_estimate is None or right_estimate is None
        else right_estimate - left_estimate
    )

    def statistic(sample: list[dict[str, Any]]) -> float | None:
        left_rate, right_rate = rate(sample, left), rate(sample, right)
        return None if left_rate is None or right_rate is None else right_rate - left_rate

    return {
        "left": left,
        "right": right,
        "metric": metric,
        "difference_right_minus_left": estimate,
        "ci95_state_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _error_kind(component: dict[str, Any]) -> str | None:
    kind = component.get("error_kind")
    if kind:
        return str(kind)
    error = str(component.get("error") or "")
    if error.startswith("api_") or "HTTP" in error or "network" in error or "timeout" in error:
        return "api"
    if error:
        return "parse_or_schema"
    return None


def _model_report(rows: list[dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    if len({row["task"]["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate task rows for one model")
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        validate_run_row(row)
        clusters[row["task"]["state_cluster_id"]].append(row)
    metrics: dict[str, Any] = {}
    for condition in OUTCOME_CONDITIONS:
        preserve_eligible = lambda row: (
            row["task"]["reference_mode_gold"] == "preserve"
            and (row.get("compiler", {}).get("parsed") or {}).get("reference_mode") == "preserve"
            and normalize_target((row.get("compiler", {}).get("parsed") or {}).get("bound_target_id"))
            == row["task"]["pre_refresh_target"]
        )
        metrics[condition] = {
            "changed_pairacc": _pair_measure(clusters, condition, seed, samples),
            "e2e": _measure(rows, lambda row, c=condition: _correct(row, c), None, clusters, seed, samples),
            "preserve_e2e": _measure(
                rows,
                lambda row, c=condition: _correct(row, c),
                lambda row: row["task"]["reference_mode_gold"] == "preserve",
                clusters,
                seed,
                samples,
            ),
            "reevaluate_e2e": _measure(
                rows,
                lambda row, c=condition: _correct(row, c),
                lambda row: row["task"]["reference_mode_gold"] == "reevaluate",
                clusters,
                seed,
                samples,
            ),
            "preserve_conditional_substitution": _measure(
                rows,
                lambda row, c=condition: _target(row, c) == row["task"]["post_refresh_target"],
                preserve_eligible,
                clusters,
                seed,
                samples,
            ),
        }

    mode_correct = lambda row: (
        (row.get("compiler", {}).get("parsed") or {}).get("reference_mode")
        == row["task"]["reference_mode_gold"]
    )
    binding_correct = lambda row: (
        normalize_target((row.get("compiler", {}).get("parsed") or {}).get("bound_target_id"))
        == row["task"]["pre_refresh_target"]
    )
    compiler = {
        "mode_accuracy": _measure(rows, mode_correct, None, clusters, seed, samples),
        "preserve_binding_accuracy": _measure(
            rows,
            binding_correct,
            lambda row: row["task"]["reference_mode_gold"] == "preserve",
            clusters,
            seed,
            samples,
        ),
        "joint_mode_binding_accuracy": _measure(
            rows,
            lambda row: mode_correct(row) and (
                binding_correct(row)
                if row["task"]["reference_mode_gold"] == "preserve"
                else (row.get("compiler", {}).get("parsed") or {}).get("bound_target_id") is None
            ),
            None,
            clusters,
            seed,
            samples,
        ),
    }
    visible_changed = [row for row in rows if _target(row, "decision_visible") != _target(row, "decision_enforced")]
    repair_measure = _measure(
        rows,
        lambda row: not _correct(row, "decision_visible") and _correct(row, "decision_enforced"),
        None,
        clusters,
        seed,
        samples,
    )
    harm_measure = _measure(
        rows,
        lambda row: _correct(row, "decision_visible") and not _correct(row, "decision_enforced"),
        None,
        clusters,
        seed,
        samples,
    )
    enforcement = {
        "changed": len(visible_changed),
        "repairs": repair_measure["numerator"],
        "harms": harm_measure["numerator"],
        "repair_rate": repair_measure,
        "harm_rate": harm_measure,
        "other_changed": sum(
            not _correct(row, "decision_visible")
            and not _correct(row, "decision_enforced")
            and _target(row, "decision_visible") != _target(row, "decision_enforced")
            for row in rows
        ),
    }
    actor_available = [
        row for row in rows
        if row.get("actors", {}).get("history_only", {}).get("parsed") is not None
        and row.get("actors", {}).get("decision_visible", {}).get("parsed") is not None
    ]
    shadow_measure = _measure(
        rows,
        lambda row: _target(row, "history_only") != _target(row, "decision_visible"),
        lambda row: row.get("actors", {}).get("history_only", {}).get("parsed") is not None
        and row.get("actors", {}).get("decision_visible", {}).get("parsed") is not None,
        clusters,
        seed,
        samples,
    )
    shadow = {
        "disagreements": shadow_measure["numerator"],
        "denominator_both_parsed": len(actor_available),
        "unavailable": len(rows) - len(actor_available),
        "disagreement_rate": shadow_measure,
    }
    components = [row.get("compiler", {}) for row in rows]
    components += [row.get("actors", {}).get(name, {}) for row in rows for name in ACTOR_CONDITIONS]
    failures = {
        "api": sum(_error_kind(component) == "api" for component in components),
        "parse_or_schema": sum(_error_kind(component) == "parse_or_schema" for component in components),
        "incomplete_tasks": sum(not row.get("complete") for row in rows),
    }
    attempts = [attempt for component in components for attempt in component.get("attempts", [])]
    usage = [component.get("usage") or {} for component in components]
    calls = {
        "logical_planned": sum(row.get("logical_calls_planned", 0) for row in rows),
        "logical_completed": sum(row.get("logical_calls_completed", 0) for row in rows),
        "http_attempts": len(attempts),
        "retries": sum(max(0, len(component.get("attempts", [])) - 1) for component in components),
        "prompt_tokens": sum(int(item.get("prompt_tokens", 0) or 0) for item in usage),
        "completion_tokens": sum(int(item.get("completion_tokens", 0) or 0) for item in usage),
    }
    differences = [
        _paired_difference(clusters, "history_only", "decision_visible", metric, seed, samples)
        for metric in ("changed_pairacc", "preserve_conditional_substitution", "e2e")
    ] + [
        _paired_difference(clusters, "decision_visible", "decision_enforced", metric, seed, samples)
        for metric in ("changed_pairacc", "preserve_conditional_substitution", "e2e")
    ]
    return {
        "model": rows[0]["model"],
        "rows": len(rows),
        "state_clusters": len(clusters),
        "metrics": metrics,
        "paired_differences": differences,
        "compiler": compiler,
        "shadow_actor": shadow,
        "enforcement": enforcement,
        "failures": failures,
        "calls": calls,
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
        "report_version": "TRI-call-matched-authorization-ablation-report-v2",
        "evidence_status": EVIDENCE_STATUS,
        "causal_scope": (
            "Call/information-matched actor ablation; deterministic enforcement reuses the visible "
            "actor call and is not a complete component causal estimate."
        ),
        "bootstrap": {"unit": "state_cluster_id", "samples": samples, "seed": seed},
        "models": [_model_report(by_model[model], seed, samples) for model in sorted(by_model)],
    }


def _pct(metric: dict[str, Any]) -> str:
    if metric["rate"] is None:
        return f"NA ({metric['numerator']}/{metric['denominator']})"
    lo, hi = metric["ci95_state_cluster"]
    return (
        f"{100 * metric['rate']:.1f}% ({metric['numerator']}/{metric['denominator']}), "
        f"95% CI [{100 * lo:.1f}, {100 * hi:.1f}]"
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Call/Information-Matched Authorization Ablation",
        "",
        "**Evidence status:** post-primary.",
        "",
        report["causal_scope"],
        "",
        f"State-cluster bootstrap: {report['bootstrap']['samples']:,} replicates, seed {report['bootstrap']['seed']}.",
        "",
    ]
    for model in report["models"]:
        lines.extend([
            f"## {model['model']}",
            "",
            f"Rows: {model['rows']}; state clusters: {model['state_clusters']}.",
            "",
            "| Outcome | Changed PairAcc | E2E | Preserve conditional substitution |",
            "|---|---:|---:|---:|",
        ])
        for condition in OUTCOME_CONDITIONS:
            metrics = model["metrics"][condition]
            lines.append(
                f"| {condition} | {_pct(metrics['changed_pairacc'])} | {_pct(metrics['e2e'])} | "
                f"{_pct(metrics['preserve_conditional_substitution'])} |"
            )
        lines.extend([
            "",
            f"Compiler mode accuracy: {_pct(model['compiler']['mode_accuracy'])}.",
            f"Preserve binding accuracy: {_pct(model['compiler']['preserve_binding_accuracy'])}.",
            f"Joint mode/binding accuracy: {_pct(model['compiler']['joint_mode_binding_accuracy'])}.",
            "",
            f"Shadow actor disagreement: {model['shadow_actor']['disagreements']}/"
            f"{model['shadow_actor']['denominator_both_parsed']} both-parsed tasks; "
            f"{model['shadow_actor']['unavailable']} unavailable; "
            f"cluster interval {_pct(model['shadow_actor']['disagreement_rate'])}.",
            f"Enforcement changes: {model['enforcement']['changed']}; repairs: "
            f"{model['enforcement']['repairs']}; harms: {model['enforcement']['harms']}; "
            f"other wrong-to-wrong changes: {model['enforcement']['other_changed']}.",
            f"Enforcement repair rate: {_pct(model['enforcement']['repair_rate'])}; "
            f"harm rate: {_pct(model['enforcement']['harm_rate'])}.",
            f"Failures: {model['failures']['api']} API calls; "
            f"{model['failures']['parse_or_schema']} parse/schema calls; "
            f"{model['failures']['incomplete_tasks']} incomplete tasks.",
            f"Calls: {model['calls']['logical_completed']}/{model['calls']['logical_planned']} logical; "
            f"{model['calls']['http_attempts']} HTTP attempts; {model['calls']['retries']} retries.",
            "",
            "| Paired contrast | Metric | Difference (right-left) | 95% CI |",
            "|---|---|---:|---:|",
        ])
        for item in model["paired_differences"]:
            lo, hi = item["ci95_state_cluster"]
            estimate = item["difference_right_minus_left"]
            estimate_text = "NA" if estimate is None else f"{100 * estimate:.1f} pp"
            interval_text = (
                "NA" if lo is None or hi is None else f"[{100 * lo:.1f}, {100 * hi:.1f}]"
            )
            lines.append(
                f"| {item['left']} -> {item['right']} | {item['metric']} | "
                f"{estimate_text} | {interval_text} |"
            )
        lines.append("")
    lines.extend([
        "Negative, null, mixed, API-failure, and enforcement-harm outcomes remain in this report.",
        "The conditional substitution denominator requires a correct shared Preserve compiler "
        "mode and bound ID; ITT PairAcc and E2E retain all observed task failures.",
        "",
    ])
    return "\n".join(lines)
