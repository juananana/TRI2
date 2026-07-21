from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


INVALID_TARGET = "INVALID_BOUND_ENTITY"
ALLOWED_INPUTS = ("instruction", "initial_state", "refreshed_state", "action_schema")
FORBIDDEN_INPUTS = (
    "binding",
    "style",
    "phenomenon",
    "update",
    "selector",
    "pre_refresh_target",
    "post_refresh_target",
    "correct_target",
    "new_leader",
    "bound_entity_present_after_refresh",
    "bound_entity_actionable_after_refresh",
)

REFRESH_PATTERNS = (
    r"\brefresh(?:ed|es|ing)?\b",
    r"\breload(?:ed|s|ing)?\b",
    r"\bsynchroni[sz](?:e|ed|es|ing|ation)\b",
    r"\bsync(?:ed|s|ing)?\b",
    r"\bupdate(?:d|s|ing)?\b",
    r"\bpost-refresh\b",
)
SELECTION_PATTERNS = (
    r"\bselect(?:ed|s|ing)?\b",
    r"\b(?:choose|chooses|choosing|chosen)\b",
    r"\bpick(?:ed|s|ing)?\b",
    r"\bfind|finds|finding|found\b",
    r"\bidentify|identifies|identified|identifying\b",
    r"\blocate|locates|located|locating\b",
    r"\bdetermine|determines|determined|determining\b",
    r"\bdecide|decides|decided|deciding\b",
    r"\bmark|marks|marked|marking\b",
    r"\bwhich\b",
    r"\bwork(?:ing)?\s+out\b",
)
CHECK_TARGET_CUES = (
    "earliest",
    "soonest",
    "highest",
    "largest",
    "cheapest",
    "default",
    "most",
    "lowest",
    "oldest",
    "latest",
)
MINIMUM_CUES = (
    "earliest",
    "soonest",
    "cheapest",
    "lowest",
    "least",
    "minimum",
)
MAXIMUM_CUES = (
    "highest",
    "largest",
    "most",
    "latest",
    "recently",
    "delayed",
    "oldest",
    "maximum",
    "greatest",
    "top",
)
IGNORED_SELECTOR_FIELDS = {"id", "display", "owner"}


def _first_match(text: str, patterns: tuple[str, ...]) -> int | None:
    starts = [match.start() for pattern in patterns if (match := re.search(pattern, text))]
    return min(starts) if starts else None


def infer_reference_mode(instruction: str) -> tuple[str | None, str | None]:
    text = " ".join(instruction.lower().split())
    refresh_at = _first_match(text, REFRESH_PATTERNS)
    selection_at = _first_match(text, SELECTION_PATTERNS)

    for match in re.finditer(r"\bcheck(?:ed|s|ing)?\b", text):
        window = text[match.start() : match.start() + 100]
        if any(re.search(rf"\b{re.escape(cue)}\b", window) for cue in CHECK_TARGET_CUES):
            selection_at = min(selection_at, match.start()) if selection_at is not None else match.start()

    if refresh_at is None:
        return None, "missing_refresh_event"
    if selection_at is None:
        return None, "missing_selection_event"
    if refresh_at == selection_at:
        return None, "tied_events"
    return ("preserve", None) if selection_at < refresh_at else ("reevaluate", None)


def _satisfies(row: dict[str, Any], preconditions: dict[str, Any]) -> bool:
    return all(row.get(key) == value for key, value in preconditions.items())


def _direction(instruction: str) -> tuple[str | None, str | None]:
    text = instruction.lower()
    minimum = any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in MINIMUM_CUES)
    maximum = any(re.search(rf"\b{re.escape(cue)}\b", text) for cue in MAXIMUM_CUES)
    if minimum == maximum:
        return None, "ambiguous_ranking_direction"
    return ("minimum", None) if minimum else ("maximum", None)


def resolve_selector(
    instruction: str,
    state: list[dict[str, Any]],
    action_schema: dict[str, Any],
) -> tuple[str | None, str | None]:
    preconditions = dict(action_schema.get("preconditions", {}))
    eligible = [row for row in state if _satisfies(row, preconditions)]
    if not eligible:
        return None, "no_actionable_entity"

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
    direction, error = _direction(instruction)
    if error:
        return None, error
    key = numeric_fields[0]
    best_value = min(row[key] for row in eligible) if direction == "minimum" else max(
        row[key] for row in eligible
    )
    winners = [row for row in eligible if row[key] == best_value]
    if len(winners) != 1:
        return None, "tied_selector_winners"
    return winners[0]["id"], None


def predict(
    instruction: str,
    initial_state: list[dict[str, Any]],
    refreshed_state: list[dict[str, Any]],
    action_schema: dict[str, Any],
) -> dict[str, Any]:
    mode, mode_error = infer_reference_mode(instruction)
    if mode_error:
        return {"reference_mode": None, "predicted_target": None, "error": mode_error}

    source_state = initial_state if mode == "preserve" else refreshed_state
    target, selector_error = resolve_selector(instruction, source_state, action_schema)
    if selector_error:
        return {"reference_mode": mode, "predicted_target": None, "error": selector_error}

    if mode == "preserve":
        refreshed = next((row for row in refreshed_state if row.get("id") == target), None)
        preconditions = dict(action_schema.get("preconditions", {}))
        if refreshed is None or not _satisfies(refreshed, preconditions):
            target = INVALID_TARGET
    return {"reference_mode": mode, "predicted_target": target, "error": None}


def predict_task(task: dict[str, Any]) -> dict[str, Any]:
    safe = {key: task[key] for key in ALLOWED_INPUTS}
    return predict(**safe)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _expected_mode(task: dict[str, Any]) -> str:
    return "preserve" if task["binding"] == "anchored" else "reevaluate"


def _cluster_id(task: dict[str, Any], dataset: str) -> str:
    if dataset == "v7":
        return str(task["state_cluster_id"])
    return str(task.get("template_id") or task.get("paraphrase"))


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _bootstrap(
    clusters: dict[str, list[Any]], statistic: Callable[[list[Any]], float], seed: int
) -> tuple[float, float]:
    names = sorted(clusters)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(10_000):
        sample: list[Any] = []
        for _ in names:
            sample.extend(clusters[rng.choice(names)])
        values.append(statistic(sample))
    return _percentile(values, 0.025), _percentile(values, 0.975)


def _load_cta(path: Path) -> dict[str, dict[str, Any]]:
    return {row["task"]["id"]: row for row in _load_jsonl(path)}


def analyze_dataset(
    name: str,
    data_path: Path,
    cta_paths: dict[str, Path],
    seed: int,
    predictor: Callable[[dict[str, Any]], dict[str, Any]] = predict_task,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    artifact_root = data_path.parents[1]
    tasks = _load_jsonl(data_path)
    predictions: list[dict[str, Any]] = []
    for task in tasks:
        result = predictor(task)
        predictions.append({"task": task, "result": result})

    def summarize(group: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(group)
        return {
            "n": n,
            "correct": sum(row["result"]["predicted_target"] == row["task"]["correct_target"] for row in group),
            "mode_correct": sum(row["result"]["reference_mode"] == _expected_mode(row["task"]) for row in group),
            "unresolved": sum(row["result"]["predicted_target"] is None for row in group),
        }

    actionable = [row for row in predictions if row["task"]["correct_target"] != INVALID_TARGET]
    reject = [row for row in predictions if row["task"]["correct_target"] == INVALID_TARGET]
    report: dict[str, Any] = {
        "dataset": name,
        "data_path": data_path.relative_to(artifact_root).as_posix(),
        "overall": summarize(predictions),
        "actionable_core": summarize(actionable),
        "reject_policy": summarize(reject),
        "by_binding": {
            binding: summarize([row for row in predictions if row["task"]["binding"] == binding])
            for binding in ("anchored", "dynamic")
        },
        "errors": dict(sorted({
            error: sum(row["result"]["error"] == error for row in predictions)
            for error in {row["result"]["error"] for row in predictions if row["result"]["error"]}
        }.items())),
        "cta_comparisons": {},
    }

    rule_by_id = {row["task"]["id"]: row for row in predictions}
    for model, path in cta_paths.items():
        cta = _load_cta(path)
        common = sorted(set(rule_by_id) & set(cta))
        clusters: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
        for task_id in common:
            pair = (rule_by_id[task_id], cta[task_id])
            clusters[_cluster_id(pair[0]["task"], name)].append(pair)

        def delta(sample: list[tuple[dict[str, Any], dict[str, Any]]]) -> float:
            return sum(
                int(cta_row["result"]["predicted_target"] == cta_row["task"]["correct_target"])
                - int(rule_row["result"]["predicted_target"] == rule_row["task"]["correct_target"])
                for rule_row, cta_row in sample
            ) / len(sample)

        pairs = [pair for group in clusters.values() for pair in group]
        lo, hi = _bootstrap(clusters, delta, seed)
        report["cta_comparisons"][model] = {
            "path": path.relative_to(artifact_root).as_posix(),
            "n": len(pairs),
            "n_clusters": len(clusters),
            "rule_accuracy": sum(
                rule["result"]["predicted_target"] == rule["task"]["correct_target"]
                for rule, _ in pairs
            ) / len(pairs),
            "cta_accuracy": sum(
                cta_row["result"]["predicted_target"] == cta_row["task"]["correct_target"]
                for _, cta_row in pairs
            ) / len(pairs),
            "cta_minus_rule": delta(pairs),
            "cluster_ci95": [lo, hi],
        }
    return report, predictions


def _rate(block: dict[str, Any], key: str = "correct") -> str:
    if not block["n"]:
        return "NA"
    return f"{block[key]}/{block['n']} ({100 * block[key] / block['n']:.1f}%)"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Deterministic Discourse-Rule Baseline",
        "",
        "The controller reads only instruction, initial/refreshed state, and action schema. "
        "Gold and generator metadata are used only by the evaluator after prediction.",
        "",
        "| Dataset | n | E2E | Mode | Actionable core | Reject policy | Unresolved |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for block in report["datasets"]:
        overall = block["overall"]
        lines.append(
            f"| {block['dataset']} | {overall['n']} | {_rate(overall)} | "
            f"{_rate(overall, 'mode_correct')} | {_rate(block['actionable_core'])} | "
            f"{_rate(block['reject_policy'])} | {overall['unresolved']} |"
        )
    lines.extend(["", "## CTA comparisons", "", "| Dataset | Model | Rule | CTA | CTA - Rule | Cluster 95% CI |", "|---|---|---:|---:|---:|---:|"])
    for block in report["datasets"]:
        for model, comparison in block["cta_comparisons"].items():
            lo, hi = comparison["cluster_ci95"]
            lines.append(
                f"| {block['dataset']} | {model} | {100 * comparison['rule_accuracy']:.1f} | "
                f"{100 * comparison['cta_accuracy']:.1f} | {100 * comparison['cta_minus_rule']:+.1f} | "
                f"[{100 * lo:+.1f}, {100 * hi:+.1f}] |"
            )
    lines.extend(["", "## Unresolved cases", ""])
    for block in report["datasets"]:
        lines.append(f"- {block['dataset']}: {block['errors'] or 'none'}")
    lines.extend(["", "The frozen interpretation thresholds are defined in `reports/TRI_deterministic_discourse_rule_protocol.md`.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--seed", type=int, default=20260721)
    args = parser.parse_args()
    root = args.root
    specs = (
        (
            "v3",
            root / "data/temporal_referent_v3_language_clusters.jsonl",
            {"Qwen3.5": root / "runs/v3_exact_predecessor_qwen_full.jsonl", "GLM-5.1": root / "runs/v3_exact_predecessor_glm_full.jsonl"},
        ),
        (
            "human_rewrite",
            root / "data/temporal_referent_human_rewrites_v1.jsonl",
            {
                "Qwen3.5": root / "runs/20260718T233608Z_Qwen_Qwen3.5-122B-A10B_compile_then_act_human_rewrites_v1.jsonl",
                "GLM-5.1": root / "runs/20260718T234334Z_Pro_zai-org_GLM-5.1_compile_then_act_human_rewrites_v1.jsonl",
            },
        ),
        (
            "v7",
            root / "data/temporal_referent_v7_core_replication.jsonl",
            {
                "Qwen3.5": root / "runs/v7_qwen_compile_then_act_full.jsonl",
                "GLM-5.1": root / "runs/v7_glm_compile_then_act_full.jsonl",
                "DeepSeek": root / "runs/v7_deepseek_compile_then_act_full_v1.jsonl",
            },
        ),
    )
    datasets: list[dict[str, Any]] = []
    for name, data, cta in specs:
        block, rows = analyze_dataset(name, data, cta, args.seed)
        datasets.append(block)
        run_path = root / f"runs/deterministic_discourse_rule_{name}.jsonl"
        run_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    report = {
        "protocol": "reports/TRI_deterministic_discourse_rule_protocol.md",
        "allowed_inputs": list(ALLOWED_INPUTS),
        "forbidden_inputs": list(FORBIDDEN_INPUTS),
        "bootstrap_samples": 10_000,
        "seed": args.seed,
        "datasets": datasets,
    }
    json_path = root / "reports/deterministic_discourse_rule_v1.json"
    md_path = root / "reports/deterministic_discourse_rule_v1.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
