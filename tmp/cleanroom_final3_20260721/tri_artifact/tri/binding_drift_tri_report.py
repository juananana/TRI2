"""Report the frozen Binding Drift author-adaptation TRI smoke."""

from __future__ import annotations

import json
from pathlib import Path

from tri.binding_drift_tri_adapter import entity_lock_target, file_sha256, load_predictions, score_target, summarize


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def rows_from_targets(tasks: list[dict], targets: dict[str, str | None], method: str, model: str) -> list[dict]:
    missing = {task["id"] for task in tasks}.difference(targets)
    if missing:
        raise ValueError(f"{method}/{model}: missing {sorted(missing)}")
    return [{"model": model, "method": method, "task": task, "result": score_target(task, targets[task["id"]])} for task in tasks]


def build_report(data: Path, qwen_reverify: Path, glm_reverify: Path, qwen_cta: Path, glm_cta: Path) -> dict:
    tasks = load_jsonl(data)
    if len(tasks) != 20 or len({task["id"] for task in tasks}) != 20:
        raise ValueError("Expected 20 unique frozen tasks")
    raw_adapted = {"Qwen3.5": load_jsonl(qwen_reverify), "GLM-5.1": load_jsonl(glm_reverify)}
    for model, rows in raw_adapted.items():
        if {row["task"]["id"] for row in rows} != {task["id"] for task in tasks}:
            raise ValueError(f"{model}: adapted run does not match frozen task IDs")
    qwen_targets = {row["task"]["id"]: row["result"]["predicted_target"] for row in raw_adapted["Qwen3.5"]}
    glm_targets = {row["task"]["id"]: row["result"]["predicted_target"] for row in raw_adapted["GLM-5.1"]}
    adapted = {
        "Qwen3.5": rows_from_targets(tasks, qwen_targets, "self_reverify_author_adaptation", "Qwen3.5"),
        "GLM-5.1": rows_from_targets(tasks, glm_targets, "self_reverify_author_adaptation", "GLM-5.1"),
    }
    conditions = []
    for model, self_rows, cross_targets, cta_path in (
        ("Qwen3.5", adapted["Qwen3.5"], glm_targets, qwen_cta),
        ("GLM-5.1", adapted["GLM-5.1"], qwen_targets, glm_cta),
    ):
        lock_rows = rows_from_targets(tasks, {task["id"]: entity_lock_target(task) for task in tasks}, "entity_lock_analogue", model)
        cross_rows = rows_from_targets(tasks, cross_targets, "cross_reverify_author_adaptation", model)
        cta_rows = rows_from_targets(tasks, load_predictions(cta_path), "exact_cta_frozen", model)
        for method, rows in (("entity_lock_analogue", lock_rows), ("self_reverify_author_adaptation", self_rows), ("cross_reverify_author_adaptation", cross_rows), ("exact_cta_frozen", cta_rows)):
            conditions.append({"model": model, "method": method, **summarize(rows)})
    run_audit = []
    for model, path, rows in (
        ("Qwen3.5", qwen_reverify, raw_adapted["Qwen3.5"]),
        ("GLM-5.1", glm_reverify, raw_adapted["GLM-5.1"]),
    ):
        run_audit.append({
            "model": model,
            "file": path.name,
            "sha256": file_sha256(path),
            "rows": len(rows),
            "request_attempts": sum(row.get("api_request_attempts", 0) for row in rows),
            "retries": sum(row.get("api_retries", 0) for row in rows),
            "tokens": sum(sum((usage or {}).get("total_tokens", 0) or 0 for usage in row.get("usage", [])) for row in rows),
        })
    return {"n_tasks": len(tasks), "conditions": conditions, "run_audit": run_audit}


def markdown(report: dict) -> str:
    lines = [
        "# Binding Drift Author-Adaptation Symmetric Smoke",
        "",
        "This is an author adaptation on TRI tasks, not an official Binding Drift result.",
        "",
        "| Model | Method | Overall | Preserve | Reevaluate | Preserve substitutions | Premature locks | Other visible | Clarify | Errors |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["conditions"]:
        lines.append(
            f"| {row['model']} | {row['method']} | {row['correct']}/{row['n']} | "
            f"{row['anchored']['correct']}/{row['anchored']['n']} | "
            f"{row['dynamic']['correct']}/{row['dynamic']['n']} | "
            f"{row['anchored']['drift_to_refreshed_winner']} | {row['dynamic']['premature_lock']} | {row['other_visible_target']} | "
            f"{row['clarify']} | {row['api_or_parse_errors']} |"
        )
    lines.extend(["", "## Run audit", "", "| Verifier | Rows | Requests | Retries | Tokens |", "|---|---:|---:|---:|---:|"])
    for row in report["run_audit"]:
        lines.append(f"| {row['model']} | {row['rows']} | {row['request_attempts']} | {row['retries']} | {row['tokens']} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The lock analogue is perfectly asymmetric: Preserve 10/10 and Reevaluate 0/10.",
        "- GLM re-verification always resolves the selector on the refreshed candidates: Reevaluate",
        "  10/10 and Preserve 0/10. This cleanly demonstrates that unconditional re-resolution",
        "  solves the opposite half of the paired authorization problem from locking.",
        "- Qwen re-verification selects a different visible but selector-ineligible entity on 14/20",
        "  tasks. Its 3/20 accuracy is therefore dominated by selector grounding, not interpretable",
        "  as a pure temporal-authorization preference.",
        "- Frozen CTA is 12/20 for Qwen and 17/20 for GLM. It is not perfect and is not claimed to",
        "  dominate Binding Drift's original initial-misbinding benchmark. On this smoke, it is the",
        "  only tested policy with nonzero accuracy on both Preserve and Reevaluate for each model.",
        "",
        "The official Binding Drift verifier normally receives a short `step1_referent`. TRI must",
        "retain the full temporal instruction or it deletes the authorization variable under test.",
        "This author adaptation therefore preserves the official prompt frame but is not interface-",
        "identical to the official workflow. The Qwen grounding failures expose this limitation.",
    ])
    return "\n".join(lines) + "\n"
