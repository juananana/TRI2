from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from typing import Any, Callable

from tri.call_matched_authorization_ablation import (
    COMPILER_SYSTEM_PROMPT,
    build_actor_payload,
    build_compiler_payload,
    canonical_json,
    sha256_bytes,
)
from tri.deterministic_discourse_rule_v2 import predict_task_v2
from tri.independent_language_holdout import validate_model_tasks
from tri.revision_matched_audit import parse_actor_exact, parse_compiler_exact
from tri.v3_sqlite_replay import SQLiteWriteEnvironment


RUN_VERSION = "TRI-independent-language-holdout-model-v1"
REPORT_VERSION = "TRI-independent-language-holdout-model-report-v1"
EVIDENCE_STATUS = "post-primary; protocol and implementations frozen before own calls"
BOOTSTRAP_SEED = 20260728
BOOTSTRAP_SAMPLES = 10_000
WRONG_WRITE_MARGIN = 0.05
MODEL_IDS = {
    "qwen": "Qwen/Qwen3.5-122B-A10B",
    "glm": "Pro/zai-org/GLM-5.1",
    "deepseek": "deepseek-ai/DeepSeek-V4-Pro",
}
ACTOR_CONDITIONS = ("history_only", "decision_visible", "timing_reminder", "cta")
MATCHED_CONDITIONS = ("history_only", "decision_visible")

ACTOR_SYSTEM_PROMPT = (
    "Choose the exact entity ID for the requested action from the supplied states. Follow the "
    "writer's instruction. initial_selected_id is the selector winner in S0 and s1_state is observed "
    "after synchronization. If compiler_decision is present, use it to decide whether to preserve "
    "the initial entity or evaluate the selector in S1. Return one JSON object only with exactly "
    "these keys: action, target_id. Copy target_id exactly from a serialized state ID or use CLARIFY."
)
TIMING_REMINDER_SYSTEM_PROMPT = (
    "Choose the exact entity ID for the requested action from the supplied states. Before choosing, "
    "use the instruction's event order: an entity identified before synchronization remains that "
    "entity afterward, while a selection deliberately placed after synchronization is evaluated in "
    "the resulting state. Return one JSON object only with exactly these keys: action, target_id. "
    "Copy target_id exactly from a serialized state ID or use CLARIFY."
)
CTA_SYSTEM_PROMPT = (
    "Act from the supplied pre-synchronization compiled_plan. A preserve plan carries its concrete "
    "bound_target_id through synchronization; a reevaluate plan resolves its selector in s1_state. "
    "Return one JSON object only with exactly these keys: action, target_id. Copy target_id exactly "
    "from a serialized state ID or use CLARIFY."
)


def actor_base_payload(task: dict[str, Any]) -> dict[str, Any]:
    return build_actor_payload(task, None)


def actor_payload(task: dict[str, Any], condition: str, decision: dict[str, Any]) -> dict[str, Any]:
    payload = actor_base_payload(task)
    if condition == "decision_visible":
        payload["compiler_decision"] = decision
    elif condition == "cta":
        payload["compiled_plan"] = decision
    elif condition not in {"history_only", "timing_reminder"}:
        raise ValueError(f"unknown actor condition: {condition}")
    return payload


def actor_prompt(condition: str) -> str:
    if condition in MATCHED_CONDITIONS:
        return ACTOR_SYSTEM_PROMPT
    if condition == "timing_reminder":
        return TIMING_REMINDER_SYSTEM_PROMPT
    if condition == "cta":
        return CTA_SYSTEM_PROMPT
    raise ValueError(f"unknown actor condition: {condition}")


def parse_actor(text: str, task: dict[str, Any]) -> dict[str, Any]:
    try:
        return parse_actor_exact(text, task)
    except ValueError:
        stripped = text.strip()
        if stripped.startswith("{" ) and stripped.endswith("}"):
            value = json.loads(stripped)
            if set(value) == {"action", "target_id"} and value["target_id"] == "CLARIFY":
                return {"action": str(value["action"]), "target_id": "CLARIFY"}
        raise


def freeze_prompt_hash() -> str:
    return sha256_bytes(
        canonical_json(
            {
                "compiler": COMPILER_SYSTEM_PROMPT,
                "actor": ACTOR_SYSTEM_PROMPT,
                "timing_reminder": TIMING_REMINDER_SYSTEM_PROMPT,
                "cta": CTA_SYSTEM_PROMPT,
            }
        ).encode("utf-8")
    )


def offline_rule(task: dict[str, Any]) -> dict[str, Any]:
    result = predict_task_v2(task)
    return {
        "reference_mode": result["reference_mode"],
        "target_id": result["predicted_target"],
        "error": result["error"],
    }


def sqlite_consistency(task: dict[str, Any], target: str | None) -> dict[str, Any]:
    if task["correct_target"] is None:
        return {"scored": False, "target": target, "status": "unclear_writer_intent"}
    if target == "CLARIFY":
        return {"scored": True, "target": target, "status": "unnecessary_clarification", "acted_ids": []}
    env = SQLiteWriteEnvironment(task)
    try:
        env.query()
        env.refresh()
        action = env.act(target)
        return {
            "scored": True,
            "target": target,
            "status": action["status"],
            "acted_ids": env.acted_ids(),
            "state_diff_kind": "deterministic target-to-write consistency check",
        }
    finally:
        env.close()


def validate_run_row(row: dict[str, Any], require_complete: bool = False) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("run provenance is missing")
    task = row.get("task")
    if not isinstance(task, dict) or task.get("pair_id") is None:
        raise ValueError("run row has no valid task")
    if set(row.get("actors", {})) != set(ACTOR_CONDITIONS):
        raise ValueError("run row lacks a frozen actor condition")
    if row.get("logical_calls_planned") != 5:
        raise ValueError("each row must plan one compiler and four actor calls")
    compiler = row.get("compiler", {}).get("parsed")
    if compiler is not None:
        expected_base = actor_base_payload(task)
        history_attempts = row["actors"]["history_only"].get("attempts", [])
        visible_attempts = row["actors"]["decision_visible"].get("attempts", [])
        if history_attempts and visible_attempts:
            history = json.loads(history_attempts[-1]["request"]["messages"][1]["content"])
            visible = json.loads(visible_attempts[-1]["request"]["messages"][1]["content"])
            decision = visible.pop("compiler_decision", None)
            if history != visible or history != expected_base or decision != compiler:
                raise ValueError("matched actor payloads differ beyond compiler_decision")
    if row.get("rule_star") != offline_rule(task):
        raise ValueError("recorded Rule* output differs from the frozen implementation")
    expected_sqlite = {
        condition: sqlite_consistency(task, row["outcomes"].get(condition))
        for condition in ACTOR_CONDITIONS
    }
    if row.get("sqlite_consistency") != expected_sqlite:
        raise ValueError("SQLite consistency result differs from actor targets")
    if require_complete:
        if not row.get("complete") or row.get("logical_calls_completed") != 5:
            raise ValueError("health smoke contains an incomplete row")


def pairacc(rows: list[dict[str, Any]], condition: str, clear_only: bool = True) -> tuple[int, int]:
    by_pair = defaultdict(list)
    for row in rows:
        task = row["task"]
        if clear_only and not task["clear_complete_pair"]:
            continue
        by_pair[task["pair_id"]].append(row)
    eligible = [members for members in by_pair.values() if len(members) == 2]
    correct = sum(
        all(member["outcomes"].get(condition) == member["task"]["correct_target"] for member in members)
        for members in eligible
    )
    return correct, len(eligible)


def _percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bootstrap(
    clusters: list[list[dict[str, Any]]],
    statistic: Callable[[list[list[dict[str, Any]]]], float | None],
    seed: int,
    samples: int,
) -> list[float | None]:
    if not clusters:
        return [None, None]
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        resampled = [clusters[rng.randrange(len(clusters))] for _ in clusters]
        value = statistic(resampled)
        if value is not None:
            values.append(value)
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _clusters(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_pair[str(row["task"]["pair_id"])].append(row)
    return [by_pair[pair_id] for pair_id in sorted(by_pair)]


def _expected_target(row: dict[str, Any]) -> str | None:
    task = row["task"]
    gold = task.get("correct_target")
    if gold is not None:
        return str(gold)
    return "CLARIFY" if task.get("writer_intent") == "CLARIFY" else None


def _target_correct(row: dict[str, Any], condition: str) -> bool:
    # A missing output is never equal to a scored target under ITT.
    gold = _expected_target(row)
    return gold is not None and row.get("outcomes", {}).get(condition) == gold


def _e2e_correct(row: dict[str, Any], condition: str) -> bool:
    actor = row.get("actors", {}).get(condition, {}).get("parsed") or {}
    action = actor.get("action")
    return (
        _target_correct(row, condition)
        and isinstance(action, str)
        and action.strip().casefold() == str(row["task"].get("action", "")).strip().casefold()
    )


def _clear_pair(pair: list[dict[str, Any]]) -> bool:
    return (
        len(pair) == 2
        and all(bool(row["task"].get("clear_complete_pair")) for row in pair)
        and {row["task"].get("reference_mode_design") for row in pair}
        == {"preserve", "reevaluate"}
    )


def _pairacc_rate(clusters: list[list[dict[str, Any]]], condition: str) -> float | None:
    eligible = [pair for pair in clusters if _clear_pair(pair)]
    if not eligible:
        return None
    return sum(all(_target_correct(row, condition) for row in pair) for pair in eligible) / len(eligible)


def _old_target_is_actionable(task: dict[str, Any]) -> bool:
    old = task.get("pre_refresh_target")
    record = next((item for item in task.get("refreshed_state", []) if item.get("id") == old), None)
    if record is None:
        return False
    preconditions = task.get("action_schema", {}).get("preconditions", {})
    return all(record.get(key) == value for key, value in preconditions.items())


def _preserve_substitution_eligible(row: dict[str, Any]) -> bool:
    task = row["task"]
    return (
        task.get("reference_mode_design") == "preserve"
        and bool(task.get("actionable_core"))
        and task.get("correct_target") == task.get("pre_refresh_target")
        and task.get("initial_selected_id") == task.get("pre_refresh_target")
        and task.get("pre_refresh_target") != task.get("post_refresh_target")
        and _old_target_is_actionable(task)
    )


def _wrong_write(row: dict[str, Any], condition: str) -> bool:
    return (
        row.get("sqlite_consistency", {}).get(condition, {}).get("status")
        == "wrong_entity_write"
    )


def _row_rate(
    clusters: list[list[dict[str, Any]]],
    predicate: Callable[[dict[str, Any]], bool],
    eligible: Callable[[dict[str, Any]], bool] | None = None,
) -> float | None:
    rows = [row for pair in clusters for row in pair]
    selected = [row for row in rows if eligible is None or eligible(row)]
    return sum(predicate(row) for row in selected) / len(selected) if selected else None


def _measure(
    clusters: list[list[dict[str, Any]]],
    statistic: Callable[[list[list[dict[str, Any]]]], float | None],
    numerator: Callable[[dict[str, Any]], bool],
    eligible: Callable[[dict[str, Any]], bool] | None,
    seed: int,
    samples: int,
) -> dict[str, Any]:
    rows = [row for pair in clusters for row in pair]
    selected = [row for row in rows if eligible is None or eligible(row)]
    count = sum(numerator(row) for row in selected)
    return {
        "numerator": count,
        "denominator": len(selected),
        "rate": count / len(selected) if selected else None,
        "ci95_pair_cluster": _bootstrap(clusters, statistic, seed, samples),
    }


def _pairacc_measure(
    clusters: list[list[dict[str, Any]]], condition: str, seed: int, samples: int
) -> dict[str, Any]:
    eligible = [pair for pair in clusters if _clear_pair(pair)]
    correct = sum(all(_target_correct(row, condition) for row in pair) for pair in eligible)
    return {
        "numerator": correct,
        "denominator": len(eligible),
        "rate": correct / len(eligible) if eligible else None,
        "ci95_pair_cluster": _bootstrap(
            eligible,
            lambda sample: _pairacc_rate(sample, condition),
            seed,
            samples,
        ),
    }


def _pairacc_difference(
    clusters: list[list[dict[str, Any]]], seed: int, samples: int
) -> dict[str, Any]:
    eligible = [pair for pair in clusters if _clear_pair(pair)]

    def difference(sample: list[list[dict[str, Any]]]) -> float | None:
        history = _pairacc_rate(sample, "history_only")
        visible = _pairacc_rate(sample, "decision_visible")
        return None if history is None or visible is None else visible - history

    return {
        "left": "history_only",
        "right": "decision_visible",
        "difference_right_minus_left": difference(eligible),
        "ci95_pair_cluster": _bootstrap(eligible, difference, seed, samples),
    }


def _wrong_write_difference(clusters: list[list[dict[str, Any]]]) -> dict[str, Any]:
    actionable = lambda row: bool(row["task"].get("actionable_core"))
    history = _row_rate(
        clusters, lambda row: _wrong_write(row, "history_only"), actionable
    )
    visible = _row_rate(
        clusters, lambda row: _wrong_write(row, "decision_visible"), actionable
    )
    return {
        "left": "history_only",
        "right": "decision_visible",
        "denominator": "all actionable rows",
        "difference_right_minus_left": (
            None if history is None or visible is None else visible - history
        ),
    }


def _compiler_summary(
    clusters: list[list[dict[str, Any]]], seed: int, samples: int
) -> dict[str, Any]:
    def parsed(row: dict[str, Any]) -> dict[str, Any]:
        return row.get("compiler", {}).get("parsed") or {}

    mode_error = lambda row: (
        parsed(row).get("reference_mode") != row["task"].get("reference_mode_design")
    )
    preserve = lambda row: row["task"].get("reference_mode_design") == "preserve"
    preserve_binding_error = lambda row: not (
        parsed(row).get("reference_mode") == "preserve"
        and parsed(row).get("bound_target_id") == row["task"].get("pre_refresh_target")
    )
    input_binding_error = lambda row: (
        row["task"].get("initial_selected_id") != row["task"].get("pre_refresh_target")
    )
    compiler_missing = lambda row: row.get("compiler", {}).get("parsed") is None
    compiler_api = lambda row: row.get("compiler", {}).get("error_kind") == "api"
    compiler_parse = lambda row: (
        row.get("compiler", {}).get("error_kind") == "parse_or_schema"
    )
    metrics = {}
    for name, predicate, eligibility in (
        ("input_initial_binding_error", input_binding_error, None),
        ("compiler_any_failure", compiler_missing, None),
        ("compiler_api_error", compiler_api, None),
        ("compiler_parse_or_schema_error", compiler_parse, None),
        ("compiler_mode_error", mode_error, None),
        ("preserve_compiler_binding_error", preserve_binding_error, preserve),
    ):
        metrics[name] = _measure(
            clusters,
            lambda sample, p=predicate, e=eligibility: _row_rate(sample, p, e),
            predicate,
            eligibility,
            seed,
            samples,
        )
    return metrics


def _model_report(
    rows: list[dict[str, Any]], seed: int, samples: int
) -> dict[str, Any]:
    if len({row["task"]["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate task rows for one model")
    for row in rows:
        validate_run_row(row)
    clusters = _clusters(rows)
    actionable = lambda row: bool(row["task"].get("actionable_core"))
    metrics: dict[str, Any] = {}
    for condition in ACTOR_CONDITIONS:
        metrics[condition] = {
            "clear_pair_pairacc": _pairacc_measure(clusters, condition, seed, samples),
            "all_row_e2e": _measure(
                clusters,
                lambda sample, c=condition: _row_rate(
                    sample, lambda row: _e2e_correct(row, c)
                ),
                lambda row, c=condition: _e2e_correct(row, c),
                None,
                seed,
                samples,
            ),
            "preserve_conditional_substitution": _measure(
                clusters,
                lambda sample, c=condition: _row_rate(
                    sample,
                    lambda row: row.get("outcomes", {}).get(c)
                    == row["task"].get("post_refresh_target"),
                    _preserve_substitution_eligible,
                ),
                lambda row, c=condition: row.get("outcomes", {}).get(c)
                == row["task"].get("post_refresh_target"),
                _preserve_substitution_eligible,
                seed,
                samples,
            ),
            "deterministic_sqlite_wrong_write": _measure(
                clusters,
                lambda sample, c=condition: _row_rate(
                    sample, lambda row: _wrong_write(row, c), actionable
                ),
                lambda row, c=condition: _wrong_write(row, c),
                actionable,
                seed,
                samples,
            ),
        }
    return {
        "model": rows[0]["model"],
        "rows": len(rows),
        "pairs": len(clusters),
        "clear_complete_pairs": sum(_clear_pair(pair) for pair in clusters),
        "complete_rows": sum(bool(row.get("complete")) for row in rows),
        "compiler_and_initial_binding": _compiler_summary(clusters, seed, samples),
        "metrics": metrics,
        "primary_pairacc_contrast": _pairacc_difference(clusters, seed, samples),
        "wrong_write_rate_contrast": _wrong_write_difference(clusters),
    }


def build_claim_gate(models: list[dict[str, Any]]) -> dict[str, Any]:
    by_model = {model["model"]: model for model in models}
    expected = set(MODEL_IDS.values())
    details = []
    for model_id in sorted(expected):
        model = by_model.get(model_id)
        pairacc = model.get("primary_pairacc_contrast", {}) if model else {}
        wrong = model.get("wrong_write_rate_contrast", {}) if model else {}
        difference = pairacc.get("difference_right_minus_left")
        interval = pairacc.get("ci95_pair_cluster", [None, None])
        lower = interval[0] if len(interval) == 2 else None
        wrong_difference = wrong.get("difference_right_minus_left")
        details.append(
            {
                "model": model_id,
                "present": model is not None,
                "pairacc_difference_positive": difference is not None and difference > 0,
                "pairacc_difference": difference,
                "pairacc_ci95_pair_cluster": interval,
                "pairacc_ci_excludes_zero_positive": lower is not None and lower > 0,
                "wrong_write_rate_difference": wrong_difference,
                "wrong_write_margin_at_most_plus_5pp": (
                    wrong_difference is not None and wrong_difference <= WRONG_WRITE_MARGIN
                ),
            }
        )
    all_present = set(by_model) == expected
    all_positive = all(item["pairacc_difference_positive"] for item in details)
    supported_intervals = sum(
        item["pairacc_ci_excludes_zero_positive"] for item in details
    )
    wrong_write_gate = all(
        item["wrong_write_margin_at_most_plus_5pp"] for item in details
    )
    return {
        "gate_name": "abstract_level_open_language_intervention_transfer",
        "required_models": sorted(expected),
        "all_three_models_present": all_present,
        "all_three_pairacc_point_estimates_positive": all_positive,
        "models_with_positive_pairacc_ci_excluding_zero": supported_intervals,
        "at_least_two_positive_intervals": supported_intervals >= 2,
        "wrong_write_margin_pp": 100 * WRONG_WRITE_MARGIN,
        "wrong_write_margin_met_for_every_model": wrong_write_gate,
        "promote_claim": (
            all_present and all_positive and supported_intervals >= 2 and wrong_write_gate
        ),
        "models": details,
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
        by_model[str(row.get("model", ""))].append(row)
    models = [
        _model_report(by_model[model], seed, samples) for model in sorted(by_model)
    ]
    return {
        "report_version": REPORT_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "scoring": {
            "intention_to_treat": True,
            "failed_api_parse_schema_and_upstream_outputs": "scored as incorrect",
            "primary_endpoint": "clear-complete-pair PairAcc",
            "e2e_denominator": (
                "all attempted rows; determinate rows use writer target and indeterminate rows "
                "use the writer's CLARIFY judgment"
            ),
            "wrong_write_denominator": "all actionable rows",
            "wrong_write_source": "deterministic SQLite target-to-write replay",
        },
        "bootstrap": {"unit": "pair_id", "samples": samples, "seed": seed},
        "models": models,
        "claim_promotion": build_claim_gate(models),
    }


def _fraction(metric: dict[str, Any]) -> str:
    rate = metric.get("rate")
    if rate is None:
        return f"{metric.get('numerator', 0)}/{metric.get('denominator', 0)} (NA)"
    return f"{metric['numerator']}/{metric['denominator']} ({100 * rate:.1f}%)"


def _pp(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:+.1f}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI Independent-Language Holdout Model Report",
        "",
        "All attempted rows are retained under intention-to-treat scoring. PairAcc uses only "
        "human-clear complete pairs; SQLite wrong writes use all actionable rows.",
        "",
        f"Pair-cluster bootstrap: {report['bootstrap']['samples']:,} resamples, seed "
        f"{report['bootstrap']['seed']}.",
        "",
        "| Model | Condition | Clear-pair PairAcc | All-row E2E | Preserve substitution | SQLite wrong writes |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for model in report["models"]:
        for condition in ACTOR_CONDITIONS:
            metrics = model["metrics"][condition]
            lines.append(
                f"| {model['model']} | {condition} | "
                f"{_fraction(metrics['clear_pair_pairacc'])} | "
                f"{_fraction(metrics['all_row_e2e'])} | "
                f"{_fraction(metrics['preserve_conditional_substitution'])} | "
                f"{_fraction(metrics['deterministic_sqlite_wrong_write'])} |"
            )
    lines.extend(
        [
            "",
            "## Primary matched contrast",
            "",
            "| Model | Decision-visible - History-only PairAcc (pp) | Pair-cluster 95% CI (pp) | Wrong-write difference (pp) |",
            "|---|---:|---:|---:|",
        ]
    )
    for model in report["models"]:
        pairacc = model["primary_pairacc_contrast"]
        interval = pairacc["ci95_pair_cluster"]
        wrong = model["wrong_write_rate_contrast"]["difference_right_minus_left"]
        lines.append(
            f"| {model['model']} | {_pp(pairacc['difference_right_minus_left'])} | "
            f"[{_pp(interval[0])}, {_pp(interval[1])}] | {_pp(wrong)} |"
        )
    lines.extend(["", "## Compiler and initial-binding errors", ""])
    lines.extend(
        [
            "| Model | Input binding | Compiler failed | API | Parse/schema | Compiler mode | Preserve compiler binding |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model in report["models"]:
        metrics = model["compiler_and_initial_binding"]
        lines.append(
            f"| {model['model']} | {_fraction(metrics['input_initial_binding_error'])} | "
            f"{_fraction(metrics['compiler_any_failure'])} | "
            f"{_fraction(metrics['compiler_api_error'])} | "
            f"{_fraction(metrics['compiler_parse_or_schema_error'])} | "
            f"{_fraction(metrics['compiler_mode_error'])} | "
            f"{_fraction(metrics['preserve_compiler_binding_error'])} |"
        )
    gate = report["claim_promotion"]
    lines.extend(
        [
            "",
            "## Frozen claim-promotion gate",
            "",
            f"Promote abstract-level claim: **{'YES' if gate['promote_claim'] else 'NO'}**.",
            "",
            f"Positive PairAcc point estimates: {gate['all_three_pairacc_point_estimates_positive']}; "
            f"positive intervals excluding zero: {gate['models_with_positive_pairacc_ci_excluding_zero']}/3; "
            f"wrong-write +5 pp gate for every model: {gate['wrong_write_margin_met_for_every_model']}.",
            "",
        ]
    )
    return "\n".join(lines)
