from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from tri.deterministic_discourse_rule_v2 import predict_task_v2
from tri.run_models import normalize_target, parse_json


RUN_VERSION = "TRI-model-authored-linguistic-stress-v1"
EVIDENCE_STATUS = "post-primary model-authored linguistic stress test"
ENDPOINT = "https://api.siliconflow.cn/v1"
AUTHOR_MODEL = "deepseek-ai/DeepSeek-V4-Pro"
MODEL_IDS = {"qwen": "Qwen/Qwen3.5-122B-A10B", "glm": "Pro/zai-org/GLM-5.1"}
CONTROLLERS = ("generic", "cta")
TEMPERATURE = 0.0
MAX_TOKENS = 700
TIMEOUT = 180
MAX_RETRIES = 2
RETRY_BACKOFF = 2.0
BOOTSTRAP_SEED = 20260726
BOOTSTRAP_SAMPLES = 10_000
SEMANTIC_SPECS_SHA256 = "50407590a7c06355ec44b82beaa6334782dcb95ce5161f1a1351516f7a0c45ed"

AUTHOR_SYSTEM_PROMPT = (
    "You write realistic English requests for a tool-using assistant. Realize the supplied "
    "workflow semantics without copying stock benchmark phrasing. Produce two standalone user "
    "requests with the same selector, action, and state-update event. In preserve_instruction, "
    "the user must resolve the target before the update and later refer to that same entity. In "
    "reevaluate_instruction, the user must request the update before resolving the target. Keep "
    "both requests unambiguous, preserve the specified action, and do not mention entity IDs, "
    "TRI, binding, reference modes, gold labels, or benchmark terminology. Follow the requested "
    "linguistic style naturally. Return one JSON object only with exactly the keys "
    "preserve_instruction and reevaluate_instruction."
)

JUDGE_SYSTEM_PROMPT = (
    "Audit whether a user request faithfully realizes a supplied workflow specification. "
    "Classify target resolution as preserve only when the request resolves the action target "
    "before the state update and later refers to that entity; classify it as reevaluate only "
    "when target resolution occurs after the update. Check that the selector and requested "
    "action are unchanged and that the timing is unambiguous. Do not repair the request. Return "
    "one JSON object only with exactly these keys: classified_mode, selector_preserved, "
    "action_preserved, unambiguous, notes."
)


# These specifications contain no authored instructions. They freeze workflow semantics,
# state schemas, and requested linguistic forms before the authoring model is called.
WORKFLOW_BLUEPRINTS = (
    ("warehouse", "stock bin", "open an expedited replenishment order for", "the bin with the fewest cover days", "cover_days", "minimum", "multi_sentence"),
    ("cloud_release", "deployment", "open the failure logs for", "the deployment with the highest error rate", "error_rate", "maximum", "parenthetical"),
    ("recruiting", "candidate", "schedule a screening call with", "the candidate with the highest match score", "match_score", "maximum", "context_then_request"),
    ("fleet", "vehicle", "create a maintenance work order for", "the vehicle with the highest risk score", "risk_score", "maximum", "correction"),
    ("cold_storage", "freezer", "inspect the sensor history for", "the freezer with the highest temperature", "temperature_c", "maximum", "nominalized_event"),
    ("advertising", "campaign", "pause", "the campaign with the lowest conversion rate", "conversion_rate", "minimum", "multi_sentence"),
    ("contracts", "contract", "open the renewal checklist for", "the contract with the earliest renewal day", "renewal_day", "minimum", "parenthetical"),
    ("power_grid", "meter", "dispatch an inspection for", "the meter with the highest load", "load_kw", "maximum", "context_then_request"),
    ("manufacturing", "batch", "quarantine", "the batch with the highest defect rate", "defect_rate", "maximum", "correction"),
    ("coursework", "submission", "request a revision for", "the submission with the lowest score", "score", "minimum", "nominalized_event"),
    ("hospitality", "room", "open the inspection form for", "the room with the highest cleaning priority", "cleaning_priority", "maximum", "multi_sentence"),
    ("portfolio", "holding", "open the risk note for", "the holding with the highest exposure", "exposure_pct", "maximum", "parenthetical"),
    ("agriculture", "plot", "schedule irrigation for", "the plot with the lowest moisture reading", "moisture_pct", "minimum", "context_then_request"),
    ("media_pipeline", "asset", "start a transcode for", "the asset with the largest file size", "file_mb", "maximum", "correction"),
    ("retail_promotion", "promotion", "open the review sheet for", "the promotion with the earliest expiry day", "expiry_day", "minimum", "nominalized_event"),
    ("grant_making", "grant", "open the escalation brief for", "the grant with the highest urgency score", "urgency_score", "maximum", "multi_sentence"),
    ("network_ops", "link", "open the rerouting panel for", "the link with the highest latency", "latency_ms", "maximum", "parenthetical"),
    ("restaurant", "order", "open the service check for", "the order with the longest wait", "wait_minutes", "maximum", "context_then_request"),
    ("insurance", "claim", "flag", "the claim with the highest review score", "review_score", "maximum", "correction"),
    ("construction", "inspection", "assign a follow-up for", "the inspection with the most overdue days", "overdue_days", "maximum", "nominalized_event"),
    ("library", "hold request", "notify the patron for", "the oldest hold request", "request_age_days", "maximum", "multi_sentence"),
    ("waste_routes", "container", "dispatch collection for", "the container with the highest fill level", "fill_pct", "maximum", "parenthetical"),
    ("robotics", "workcell", "open diagnostics for", "the workcell with the highest fault count", "fault_count", "maximum", "context_then_request"),
    ("water_quality", "sampling station", "open an investigation for", "the station with the highest contaminant reading", "contaminant_ppm", "maximum", "correction"),
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return ("\n".join(canonical_json(row) for row in rows) + "\n").encode("utf-8")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _state(prefix: str, field: str, direction: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    before, after = ((10, 30, 50), (40, 5, 50)) if direction == "minimum" else ((90, 70, 50), (60, 95, 50))
    ids = (f"{prefix}-A", f"{prefix}-B", f"{prefix}-C")

    def rows(values: tuple[int, int, int]) -> list[dict[str, Any]]:
        return [
            {"id": entity_id, "display": f"{prefix.title()} {index}", field: value, "status": "active", "actionable": True}
            for index, (entity_id, value) in enumerate(zip(ids, values), 1)
        ]

    return rows(before), rows(after)


def build_semantic_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for index, blueprint in enumerate(WORKFLOW_BLUEPRINTS, 1):
        domain, entity, action, selector, field, direction, style = blueprint
        prefix = f"MAS-{index:02d}"
        initial_state, refreshed_state = _state(prefix, field, direction)
        specs.append({
            "spec_id": f"model-authored-spec-{index:02d}-{domain}",
            "domain": domain,
            "app": f"{domain}_workspace",
            "entity": entity,
            "action": action,
            "selector": selector,
            "selector_field": field,
            "ranking_direction": direction,
            "linguistic_style": style,
            "state_update": "the workspace obtains a newer snapshot before the final action",
            "initial_state": initial_state,
            "refreshed_state": refreshed_state,
            "pre_refresh_target": f"{prefix}-A",
            "post_refresh_target": f"{prefix}-B",
            "action_schema": {"preconditions": {"status": "active", "actionable": True}},
        })
    validate_semantic_specs(specs)
    return specs


def validate_semantic_specs(specs: list[dict[str, Any]]) -> None:
    if len(specs) != 24 or len({row["spec_id"] for row in specs}) != 24:
        raise ValueError("semantic inventory must contain 24 unique specifications")
    if len({row["domain"] for row in specs}) != 24:
        raise ValueError("semantic inventory must contain 24 distinct workflow domains")
    for spec in specs:
        initial = {row["id"]: row for row in spec["initial_state"]}
        refreshed = {row["id"]: row for row in spec["refreshed_state"]}
        old_id, new_id = spec["pre_refresh_target"], spec["post_refresh_target"]
        if old_id == new_id or old_id not in refreshed or new_id not in refreshed:
            raise ValueError(f"{spec['spec_id']}: changed surviving targets required")
        preconditions = spec["action_schema"]["preconditions"]
        if not all(refreshed[old_id].get(k) == v for k, v in preconditions.items()):
            raise ValueError(f"{spec['spec_id']}: old target must remain actionable")
        field = spec["selector_field"]
        chooser = min if spec["ranking_direction"] == "minimum" else max
        if chooser(initial, key=lambda key: initial[key][field]) != old_id:
            raise ValueError(f"{spec['spec_id']}: initial winner mismatch")
        if chooser(refreshed, key=lambda key: refreshed[key][field]) != new_id:
            raise ValueError(f"{spec['spec_id']}: refreshed winner mismatch")


def build_author_payload(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_domain": spec["domain"],
        "entity_type": spec["entity"],
        "selector_meaning": spec["selector"],
        "requested_action": spec["action"],
        "state_update_meaning": spec["state_update"],
        "linguistic_style": spec["linguistic_style"],
        "preserve_event_order": ["resolve target", "state update", "act on that resolved target"],
        "reevaluate_event_order": ["state update", "resolve target", "act on that resolved target"],
    }


def _strict_object(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ValueError("response content must be a string")
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"json_parse_error: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("top-level response must be an object")
    return value


def parse_author_output(text: str) -> dict[str, str]:
    value = _strict_object(text)
    required = {"preserve_instruction", "reevaluate_instruction"}
    if set(value) != required:
        raise ValueError(f"author keys must be exactly {sorted(required)}")
    output: dict[str, str] = {}
    for key in sorted(required):
        instruction = value[key]
        if not isinstance(instruction, str) or len(instruction.split()) < 8:
            raise ValueError(f"{key} must be a substantive string")
        output[key] = " ".join(instruction.split())
    if output["preserve_instruction"] == output["reevaluate_instruction"]:
        raise ValueError("paired instructions must differ")
    return output


def build_tasks(specs: list[dict[str, Any]], author_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    validate_semantic_specs(specs)
    by_id = {row["spec"]["spec_id"]: row for row in author_rows}
    if len(author_rows) != 24 or len(by_id) != 24 or set(by_id) != {row["spec_id"] for row in specs}:
        raise ValueError("authoring run must contain all 24 unique specifications")
    tasks: list[dict[str, Any]] = []
    for spec in specs:
        author_row = by_id[spec["spec_id"]]
        parsed = author_row.get("parsed")
        for mode, binding in (("preserve", "anchored"), ("reevaluate", "dynamic")):
            instruction = parsed.get(f"{mode}_instruction") if isinstance(parsed, dict) else None
            correct_target = spec["pre_refresh_target"] if mode == "preserve" else spec["post_refresh_target"]
            tasks.append({
                "id": f"{spec['spec_id']}-{mode}",
                "candidate": "model-authored-linguistic-stress-v1",
                "task_type": "scalar",
                "phenomenon": "model_authored_language",
                "split": "post_primary_stress",
                "domain": spec["domain"],
                "app": spec["app"],
                "style": spec["linguistic_style"],
                "paraphrase": f"model-authored-{spec['linguistic_style']}",
                "template_id": f"model-authored-{spec['linguistic_style']}",
                "state_cluster_id": spec["spec_id"],
                "binding": binding,
                "reference_mode_gold": mode,
                "update": "flip",
                "entity": spec["entity"],
                "action": spec["action"],
                "selector": spec["selector"],
                "instruction": instruction,
                "initial_state": spec["initial_state"],
                "refreshed_state": spec["refreshed_state"],
                "pre_refresh_target": spec["pre_refresh_target"],
                "post_refresh_target": spec["post_refresh_target"],
                "correct_target": correct_target,
                "new_leader": spec["post_refresh_target"],
                "action_schema": spec["action_schema"],
                "bound_entity_present_after_refresh": True,
                "bound_entity_actionable_after_refresh": True,
                "generation_valid": instruction is not None,
                "author_model": AUTHOR_MODEL,
                "authoring_attempt_index": author_row.get("spec_index"),
                "text_variant": "model_authored",
            })
    validate_tasks(tasks)
    return tasks


def validate_tasks(tasks: list[dict[str, Any]]) -> None:
    if len(tasks) != 48 or len({row["id"] for row in tasks}) != 48:
        raise ValueError("task inventory must contain 48 unique rows")
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        pairs[task["state_cluster_id"]].append(task)
        expected = task["pre_refresh_target"] if task["reference_mode_gold"] == "preserve" else task["post_refresh_target"]
        if task["correct_target"] != expected:
            raise ValueError(f"{task['id']}: gold target mismatch")
        if task["correct_target"] == "INVALID_BOUND_ENTITY":
            raise ValueError("reject-policy rows are excluded from this stress test")
    if len(pairs) != 24:
        raise ValueError("task inventory must contain 24 pairs")
    for pair_id, pair in pairs.items():
        if {row["reference_mode_gold"] for row in pair} != {"preserve", "reevaluate"}:
            raise ValueError(f"{pair_id}: opposite-gold pair is incomplete")


def build_judge_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "instruction": task["instruction"],
        "workflow_specification": {
            "selector_meaning": task["selector"],
            "requested_action": task["action"],
            "state_update_meaning": "the workspace obtains a newer snapshot before the final action",
        },
    }


def parse_judge_output(text: str) -> dict[str, Any]:
    value = _strict_object(text)
    required = {"classified_mode", "selector_preserved", "action_preserved", "unambiguous", "notes"}
    if set(value) != required:
        raise ValueError(f"judge keys must be exactly {sorted(required)}")
    if value["classified_mode"] not in {"preserve", "reevaluate", "unclear"}:
        raise ValueError("invalid classified_mode")
    for key in ("selector_preserved", "action_preserved", "unambiguous"):
        if not isinstance(value[key], bool):
            raise ValueError(f"{key} must be boolean")
    if not isinstance(value["notes"], str):
        raise ValueError("notes must be a string")
    return value


def judge_accepts(task: dict[str, Any], row: dict[str, Any]) -> bool:
    parsed = row.get("parsed")
    return bool(
        row.get("status") == "ok"
        and parsed
        and parsed.get("classified_mode") == task["reference_mode_gold"]
        and parsed.get("selector_preserved") is True
        and parsed.get("action_preserved") is True
        and parsed.get("unambiguous") is True
    )


def extract_initial_binding(result: dict[str, Any], controller: str) -> str | None:
    ledger = result.get("compiled_ledger") or {}
    key = "selected_entity_id" if controller == "generic" else "bound_target_id"
    return normalize_target(ledger.get(key))


def run_rule(tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for task in tasks:
        output[task["id"]] = predict_task_v2(task) if task.get("generation_valid") else {
            "reference_mode": None,
            "predicted_target": None,
            "error": "authoring_failure",
        }
    return output


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def cluster_bootstrap_difference(pairs: dict[str, tuple[bool, bool]], samples: int = BOOTSTRAP_SAMPLES, seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    names = sorted(pairs)
    if not names:
        return {"difference": None, "interval": [None, None], "n_pairs": 0}
    effects = {name: float(pairs[name][1]) - float(pairs[name][0]) for name in names}
    rng = random.Random(seed)
    draws = [sum(effects[rng.choice(names)] for _ in names) / len(names) for _ in range(samples)]
    return {
        "difference": sum(effects.values()) / len(names),
        "interval": [_percentile(draws, 0.025), _percentile(draws, 0.975)],
        "n_pairs": len(names),
        "samples": samples,
        "seed": seed,
    }


def summarize_predictions(tasks: list[dict[str, Any]], predictions: dict[str, dict[str, Any]], valid_ids: set[str] | None = None) -> dict[str, Any]:
    selected = [task for task in tasks if valid_ids is None or task["id"] in valid_ids]
    correct = {task["id"]: predictions.get(task["id"], {}).get("predicted_target") == task["correct_target"] for task in selected}
    pair_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in selected:
        pair_rows[task["state_cluster_id"]].append(task)
    complete_pairs = {
        pair_id: pair for pair_id, pair in pair_rows.items()
        if len(pair) == 2 and {row["reference_mode_gold"] for row in pair} == {"preserve", "reevaluate"}
    }
    pair_correct = sum(all(correct[row["id"]] for row in pair) for pair in complete_pairs.values())
    return {
        "n_rows": len(selected),
        "correct_rows": sum(correct.values()),
        "accuracy": sum(correct.values()) / len(selected) if selected else None,
        "n_complete_pairs": len(complete_pairs),
        "correct_pairs": pair_correct,
        "pair_accuracy": pair_correct / len(complete_pairs) if complete_pairs else None,
    }


def _exact_transport_target(value: Any, task: dict[str, Any]) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in {"invalid", "invalid_bound_entity", "unavailable", "missing"}:
        return "INVALID_BOUND_ENTITY"
    state_ids = {
        str(row["id"])
        for state_name in ("initial_state", "refreshed_state")
        for row in task[state_name]
    }
    return text if text in state_ids else None


def prediction_rows_from_run(path: Path, controller: str, transport_repair: bool = False) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in load_jsonl(path):
        task_id = row["task"]["id"]
        result = row.get("result") or {}
        predicted = normalize_target(result.get("predicted_target"))
        initial_binding = extract_initial_binding(result, controller)
        actor_transport_error = None
        if transport_repair:
            try:
                raw_outputs = result.get("raw_outputs") or []
                actor = parse_json(raw_outputs[-1])
                predicted = _exact_transport_target(actor.get("target_id"), row["task"])
            except (IndexError, TypeError, ValueError) as exc:
                predicted = None
                actor_transport_error = f"{type(exc).__name__}: {exc}"
            ledger = result.get("compiled_ledger") or {}
            binding_key = "selected_entity_id" if controller == "generic" else "bound_target_id"
            initial_binding = _exact_transport_target(ledger.get(binding_key), row["task"])
        output[task_id] = {
            "predicted_target": predicted,
            "initial_binding": initial_binding,
            "status": row.get("status"),
            "errors": result.get("errors", []),
            "transport_repair": transport_repair,
            "actor_transport_error": actor_transport_error,
        }
    return output


def conditional_substitution(tasks: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, int | float | None]:
    eligible = []
    for task in tasks:
        prediction = predictions.get(task["id"], {})
        if task["reference_mode_gold"] == "preserve" and prediction.get("status") == "ok" and prediction.get("initial_binding") == task["pre_refresh_target"]:
            eligible.append((task, prediction))
    substitutions = sum(prediction.get("predicted_target") == task["post_refresh_target"] for task, prediction in eligible)
    return {"eligible": len(eligible), "substitutions": substitutions, "rate": substitutions / len(eligible) if eligible else None}


def exact_mcnemar(baseline: list[bool], treatment: list[bool]) -> dict[str, Any]:
    baseline_only = sum(a and not b for a, b in zip(baseline, treatment))
    treatment_only = sum(b and not a for a, b in zip(baseline, treatment))
    discordant = baseline_only + treatment_only
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(min(baseline_only, treatment_only) + 1))
        p_value = min(1.0, 2 * tail / (2**discordant))
    return {"baseline_only": baseline_only, "treatment_only": treatment_only, "exact_p": p_value}
