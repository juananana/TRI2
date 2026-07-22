"""Report temperature-zero repeat stability on the frozen v7 subset."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from .v2_model_report import is_api_failure
from .v7_core_report import core_drift, core_opportunity, initial_correct, stable_error, success


RUNS = {
    "Qwen3.5": {
        "generic": [
            "v7_qwen_generic_structured_ledger_then_act_full.jsonl",
            "v7_repeat_qwen_generic_r2_v1.jsonl",
            "v7_repeat_qwen_generic_r3_v1.jsonl",
        ],
        "cta": [
            "v7_qwen_compile_then_act_full.jsonl",
            "v7_repeat_qwen_cta_r2_v1.jsonl",
            "v7_repeat_qwen_cta_r3_v1.jsonl",
        ],
    },
    "GLM-5.1": {
        "generic": [
            "v7_glm_generic_structured_ledger_then_act_full.jsonl",
            "v7_repeat_glm_generic_r2_v1.jsonl",
            "v7_repeat_glm_generic_r3_v1.jsonl",
        ],
        "cta": [
            "v7_glm_compile_then_act_full.jsonl",
            "v7_repeat_glm_cta_r2_v1.jsonl",
            "v7_repeat_glm_cta_r3_v1.jsonl",
        ],
    },
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def index_rows(rows: list[dict]) -> dict[str, dict]:
    indexed = {row["task"]["id"]: row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("Duplicate task IDs")
    return indexed


def load_repeat(path: Path, expected_ids: set[str]) -> dict[str, dict]:
    indexed = index_rows(load_jsonl(path))
    if expected_ids <= set(indexed):
        indexed = {task_id: indexed[task_id] for task_id in expected_ids}
    if set(indexed) != expected_ids:
        missing = sorted(expected_ids - set(indexed))
        extra = sorted(set(indexed) - expected_ids)
        raise ValueError(f"Repeat mismatch for {path}: missing={missing}, extra={extra}")
    return indexed


def summarize(indexed: dict[str, dict], repeat: int, file: str) -> dict:
    rows = [indexed[task_id] for task_id in sorted(indexed)]
    core = [row for row in rows if core_opportunity(row)]
    stable = [
        row for row in rows
        if row["task"]["binding"] == "anchored" and row["task"]["update"] == "stable"
    ]
    usage = [
        item for row in rows for item in row.get("api_usage", []) if isinstance(item, dict)
    ]
    token_usage_captured = bool(usage)
    return {
        "repeat": repeat,
        "file": file,
        "n": len(rows),
        "correct": sum(success(row) for row in rows),
        "accuracy": sum(success(row) for row in rows) / len(rows),
        "anchored_initial_correct": sum(
            row["task"]["binding"] == "anchored" and initial_correct(row) for row in rows
        ),
        "anchored_n": sum(row["task"]["binding"] == "anchored" for row in rows),
        "core_opportunities": len(core),
        "core_drifts": sum(core_drift(row) for row in core),
        "stable_n": len(stable),
        "stable_errors": sum(stable_error(row) for row in stable),
        "api_errors": sum(is_api_failure(row) for row in rows),
        "parse_or_internal_errors": sum(
            bool(row.get("result", {}).get("errors")) and not is_api_failure(row) for row in rows
        ),
        "request_attempts": sum(int(row.get("api_request_attempts", 0)) for row in rows),
        "retries": sum(int(row.get("api_retries", 0)) for row in rows),
        "token_usage_captured": token_usage_captured,
        "total_tokens": sum(int(item.get("total_tokens", 0)) for item in usage) if usage else None,
        "latency_seconds": sum(float(row.get("latency_s", 0.0)) for row in rows),
    }


def agreement(repeats: list[dict[str, dict]]) -> dict:
    task_ids = sorted(repeats[0])
    target_vectors = {
        task_id: [repeat[task_id].get("result", {}).get("predicted_target") for repeat in repeats]
        for task_id in task_ids
    }
    pairwise = []
    for left, right in combinations(range(len(repeats)), 2):
        matches = sum(
            targets[left] == targets[right] for targets in target_vectors.values()
        )
        pairwise.append({
            "repeats": [left + 1, right + 1],
            "matches": matches,
            "n": len(task_ids),
            "agreement": matches / len(task_ids),
        })
    unanimous = sum(len(set(targets)) == 1 for targets in target_vectors.values())
    return {
        "unanimous_targets": unanimous,
        "n": len(task_ids),
        "unanimity": unanimous / len(task_ids),
        "pairwise": pairwise,
    }


def build_report(run_dir: Path, manifest_path: Path) -> dict:
    manifest = load_jsonl(manifest_path)
    expected_ids = {task["id"] for task in manifest}
    if len(expected_ids) != 40:
        raise ValueError(f"Expected 40 frozen task IDs, found {len(expected_ids)}")

    models = []
    for model, controllers in RUNS.items():
        controller_reports = {}
        loaded = {}
        for controller, files in controllers.items():
            repeats = [load_repeat(run_dir / file, expected_ids) for file in files]
            loaded[controller] = repeats
            summaries = [
                summarize(indexed, repeat, files[repeat - 1])
                for repeat, indexed in enumerate(repeats, 1)
            ]
            controller_reports[controller] = {
                "runs": summaries,
                "accuracy_range": [
                    min(row["accuracy"] for row in summaries),
                    max(row["accuracy"] for row in summaries),
                ],
                "target_agreement": agreement(repeats),
            }

        paired = []
        for repeat in range(3):
            generic = loaded["generic"][repeat]
            cta = loaded["cta"][repeat]
            delta = sum(
                int(success(cta[task_id])) - int(success(generic[task_id]))
                for task_id in expected_ids
            ) / len(expected_ids)
            paired.append({"repeat": repeat + 1, "cta_minus_generic": delta})
        models.append({"model": model, "controllers": controller_reports, "paired": paired})

    any_reversal = any(
        row["cta_minus_generic"] <= 0 for model in models for row in model["paired"]
    )
    any_cta_drift = any(
        run["core_drifts"] > 0
        for model in models for run in model["controllers"]["cta"]["runs"]
    )
    wide_variation = any(
        controller["accuracy_range"][1] - controller["accuracy_range"][0] > 0.100000001
        for model in models for controller in model["controllers"].values()
    )
    low_unanimity = any(
        controller["target_agreement"]["unanimity"] < 0.90
        for model in models for controller in model["controllers"].values()
    )
    if any_reversal or any_cta_drift:
        decision = "unstable"
    elif wide_variation or low_unanimity:
        decision = "mixed"
    else:
        decision = "stable"
    new_runs = [
        run
        for model in models
        for controller in model["controllers"].values()
        for run in controller["runs"]
        if run["repeat"] in {2, 3}
    ]
    return {
        "manifest": f"data/{manifest_path.name}",
        "expected_tasks": len(expected_ids),
        "models": models,
        "decision": decision,
        "decision_flags": {
            "any_nonpositive_cta_delta": any_reversal,
            "any_cta_conditional_drift": any_cta_drift,
            "accuracy_range_over_10_points": wide_variation,
            "target_unanimity_below_90_percent": low_unanimity,
        },
        "new_call_totals": {
            "task_controller_executions": sum(run["n"] for run in new_runs),
            "request_attempts": sum(run["request_attempts"] for run in new_runs),
            "retries": sum(run["retries"] for run in new_runs),
            "total_tokens": sum(run["total_tokens"] or 0 for run in new_runs),
            "latency_seconds": sum(run["latency_seconds"] for run in new_runs),
        },
    }


def markdown(report: dict) -> str:
    lines = [
        "# TRI-v7 Temperature-Zero Repeat Stability",
        "",
        f"Frozen decision: **{report['decision'].upper()}**.",
        "",
        "Repeat 1 is the matching subset of the original 240-task run. Repeats 2 and 3 are new",
        "complete calls. All denominators retain API and parse failures under intention-to-treat.",
        "",
        "| Model | Controller | Repeat | Accuracy | Initial anchored | Conditional TRI | Stable errors | API / parse | Requests / retries | Tokens | Latency s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model in report["models"]:
        for controller, payload in model["controllers"].items():
            for run in payload["runs"]:
                tokens = "NA" if run["total_tokens"] is None else str(run["total_tokens"])
                lines.append(
                    f"| {model['model']} | {controller} | {run['repeat']} | "
                    f"{run['correct']}/{run['n']} ({100 * run['accuracy']:.1f}%) | "
                    f"{run['anchored_initial_correct']}/{run['anchored_n']} | "
                    f"{run['core_drifts']}/{run['core_opportunities']} | "
                    f"{run['stable_errors']}/{run['stable_n']} | "
                    f"{run['api_errors']} / {run['parse_or_internal_errors']} | "
                    f"{run['request_attempts']} / {run['retries']} | {tokens} | "
                    f"{run['latency_seconds']:.1f} |"
                )
    lines.extend([
        "",
        "| Model | CTA-Generic r1 | r2 | r3 | Generic target unanimity | CTA target unanimity |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for model in report["models"]:
        deltas = [100 * row["cta_minus_generic"] for row in model["paired"]]
        generic = model["controllers"]["generic"]["target_agreement"]
        cta = model["controllers"]["cta"]["target_agreement"]
        lines.append(
            f"| {model['model']} | {deltas[0]:+.1f} | {deltas[1]:+.1f} | {deltas[2]:+.1f} | "
            f"{generic['unanimous_targets']}/{generic['n']} ({100 * generic['unanimity']:.1f}%) | "
            f"{cta['unanimous_targets']}/{cta['n']} ({100 * cta['unanimity']:.1f}%) |"
        )
    flags = report["decision_flags"]
    totals = report["new_call_totals"]
    lines.extend([
        "",
        "New repeat-2/3 calls: "
        f"{totals['task_controller_executions']} task-controller executions, "
        f"{totals['request_attempts']} requests, {totals['retries']} retries, "
        f"{totals['total_tokens']} tokens, and {totals['latency_seconds']:.1f} client seconds.",
        "Historical repeat-1 token usage was not captured and is shown as NA.",
        "",
        "Decision flags:",
        "",
        f"- Any nonpositive CTA delta: `{flags['any_nonpositive_cta_delta']}`.",
        f"- Any CTA conditional drift: `{flags['any_cta_conditional_drift']}`.",
        f"- Accuracy range over 10 points: `{flags['accuracy_range_over_10_points']}`.",
        f"- Target unanimity below 90%: `{flags['target_unanimity_below_90_percent']}`.",
        "",
        "A MIXED decision means the method direction is preserved but endpoint-level target outputs",
        "are not deterministic enough to call the runs fully stable. It is not a reversal of the",
        "controlled effect and does not establish natural-world prevalence.",
    ])
    return "\n".join(lines) + "\n"
