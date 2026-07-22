from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .deterministic_discourse_rule import (
    ALLOWED_INPUTS,
    CHECK_TARGET_CUES,
    FORBIDDEN_INPUTS,
    IGNORED_SELECTOR_FIELDS,
    INVALID_TARGET,
    MAXIMUM_CUES,
    MINIMUM_CUES,
    REFRESH_PATTERNS,
    SELECTION_PATTERNS,
    _first_match,
    _satisfies,
    analyze_dataset,
    markdown,
)


V2_SELECTION_PATTERNS = SELECTION_PATTERNS + (
    r"\brecord(?:ed|s|ing)?\b",
    r"\b(?:resolve|resolves|resolved|resolving)\b",
    r"\blook(?:ed|s|ing)?\s+(?:over|through)\b",
    r"\b(?:note|notes|noted|noting)\b",
    r"\b(?:inspect|inspects|inspected|inspecting)\b",
    r"\b(?:settle|settles|settled|settling)\b",
    r"\bshow(?:s|ed|ing)?\s+me\b",
    r"\b(?:refind|refinds|refinding|refound)\b",
)
V2_MAXIMUM_CUES = MAXIMUM_CUES + ("longest",)


def infer_reference_mode_v2(instruction: str) -> tuple[str | None, str | None]:
    text = " ".join(instruction.lower().split())
    refresh_at = _first_match(text, REFRESH_PATTERNS)
    selection_at = _first_match(text, V2_SELECTION_PATTERNS)
    if refresh_at is None:
        return None, "missing_refresh_event"
    if selection_at is None:
        return None, "missing_selection_event"
    if refresh_at == selection_at:
        return None, "tied_events"
    return ("preserve", None) if selection_at < refresh_at else ("reevaluate", None)


def _direction_v2(instruction: str) -> tuple[str | None, str | None]:
    text = instruction.lower()
    minimum = any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in MINIMUM_CUES)
    maximum = any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in V2_MAXIMUM_CUES)
    if minimum == maximum:
        return None, "ambiguous_ranking_direction"
    return ("minimum", None) if minimum else ("maximum", None)


def resolve_selector_v2(
    instruction: str,
    state: list[dict[str, Any]],
    action_schema: dict[str, Any],
) -> tuple[str | None, str | None]:
    preconditions = dict(action_schema.get("preconditions", {}))
    eligible = [row for row in state if _satisfies(row, preconditions)]
    if not eligible:
        return None, "no_actionable_entity"
    if len(eligible) == 1:
        return eligible[0]["id"], None

    common_keys = set.intersection(*(set(row) for row in eligible))
    selector_keys = common_keys.difference(preconditions).difference(IGNORED_SELECTOR_FIELDS)
    boolean_fields = [
        key
        for key in sorted(selector_keys)
        if all(isinstance(row[key], bool) for row in eligible)
        and sum(bool(row[key]) for row in eligible) == 1
    ]
    if len(boolean_fields) == 1:
        key = boolean_fields[0]
        return next(row["id"] for row in eligible if row[key]), None

    numeric_fields = [
        key
        for key in sorted(selector_keys)
        if all(isinstance(row[key], (int, float)) and not isinstance(row[key], bool) for row in eligible)
        and len({row[key] for row in eligible}) > 1
    ]
    if len(numeric_fields) != 1:
        return None, f"ambiguous_numeric_selector:{','.join(numeric_fields)}"
    direction, error = _direction_v2(instruction)
    if error:
        return None, error
    key = numeric_fields[0]
    best = min(row[key] for row in eligible) if direction == "minimum" else max(
        row[key] for row in eligible
    )
    winners = [row for row in eligible if row[key] == best]
    return (winners[0]["id"], None) if len(winners) == 1 else (None, "tied_selector_winners")


def predict_task_v2(task: dict[str, Any]) -> dict[str, Any]:
    safe = {key: task[key] for key in ALLOWED_INPUTS}
    mode, error = infer_reference_mode_v2(safe["instruction"])
    if error:
        return {"reference_mode": None, "predicted_target": None, "error": error}
    source = safe["initial_state"] if mode == "preserve" else safe["refreshed_state"]
    target, error = resolve_selector_v2(safe["instruction"], source, safe["action_schema"])
    if error:
        return {"reference_mode": mode, "predicted_target": None, "error": error}
    if mode == "preserve":
        refreshed = next((row for row in safe["refreshed_state"] if row.get("id") == target), None)
        preconditions = dict(safe["action_schema"].get("preconditions", {}))
        if refreshed is None or not _satisfies(refreshed, preconditions):
            target = INVALID_TARGET
    return {"reference_mode": mode, "predicted_target": target, "error": None}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    specs = (
        ("v3", root / "data/temporal_referent_v3_language_clusters.jsonl", {"Qwen3.5": root / "runs/v3_exact_predecessor_qwen_full.jsonl", "GLM-5.1": root / "runs/v3_exact_predecessor_glm_full.jsonl"}),
        ("human_rewrite", root / "data/temporal_referent_human_rewrites_v1.jsonl", {"Qwen3.5": root / "runs/20260718T233608Z_Qwen_Qwen3.5-122B-A10B_compile_then_act_human_rewrites_v1.jsonl", "GLM-5.1": root / "runs/20260718T234334Z_Pro_zai-org_GLM-5.1_compile_then_act_human_rewrites_v1.jsonl"}),
        ("v7", root / "data/temporal_referent_v7_core_replication.jsonl", {"Qwen3.5": root / "runs/v7_qwen_compile_then_act_full.jsonl", "GLM-5.1": root / "runs/v7_glm_compile_then_act_full.jsonl", "DeepSeek": root / "runs/v7_deepseek_compile_then_act_full_v1.jsonl"}),
    )
    datasets: list[dict[str, Any]] = []
    for name, data, cta in specs:
        block, rows = analyze_dataset(name, data, cta, 20260721, predictor=predict_task_v2)
        datasets.append(block)
        (root / f"runs/deterministic_discourse_rule_v2_{name}.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
        )
    report = {
        "protocol": "reports/TRI_deterministic_discourse_rule_v2_protocol.md",
        "status": "post_hoc_strengthened_upper_baseline",
        "allowed_inputs": list(ALLOWED_INPUTS),
        "forbidden_inputs": list(FORBIDDEN_INPUTS),
        "bootstrap_samples": 10_000,
        "seed": 20260721,
        "datasets": datasets,
    }
    (root / "reports/deterministic_discourse_rule_v2.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (root / "reports/deterministic_discourse_rule_v2.md").write_text(
        markdown(report).replace("# Deterministic", "# Strengthened Handcrafted Deterministic", 1),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
