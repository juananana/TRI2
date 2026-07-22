from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from tri.event_graph_controller import execute_selector
from tri.reference_lifecycle import INVALID


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"

RUNS = {
    "Qwen": {
        "v7": {
            "Generic": "v7_qwen_generic_structured_ledger_then_act_full.jsonl",
            "Exact CTA": "v7_qwen_compile_then_act_full.jsonl",
            "Lifecycle-Gated": "v7_qwen_factorized_hybrid_compile_then_act_full.jsonl",
        },
        "v6": {
            "Exact CTA": "v6_qwen_exact_cta_full.jsonl",
            "Scalar Lifecycle": "v6_qwen_scalar_lifecycle_full.jsonl",
            "Role-Indexed Lifecycle": "v6_qwen_role_indexed_full.jsonl",
        },
        "upgrade": "method_upgrade_closed_loop_qwen_v1.jsonl",
    },
    "GLM": {
        "v7": {
            "Generic": "v7_glm_generic_structured_ledger_then_act_full.jsonl",
            "Exact CTA": "v7_glm_compile_then_act_full.jsonl",
            "Lifecycle-Gated": "v7_glm_factorized_hybrid_compile_then_act_full.jsonl",
        },
        "v6": {
            "Exact CTA": "v6_glm_exact_cta_full.jsonl",
            "Scalar Lifecycle": "v6_glm_scalar_lifecycle_full.jsonl",
            "Role-Indexed Lifecycle": "v6_glm_role_indexed_full.jsonl",
        },
        "upgrade": "method_upgrade_closed_loop_glm_v1.jsonl",
    },
}


def load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def valid(task: dict[str, Any], target: str | None) -> bool:
    final = task.get("final_state", task["refreshed_state"])
    entity = next((row for row in final if row.get("id") == target), None)
    conditions = task.get("action_schema", {}).get("preconditions", {})
    return entity is not None and all(entity.get(key) == value for key, value in conditions.items())


def consequence(task: dict[str, Any], predicted: str | None) -> dict[str, bool]:
    correct = task["correct_target"]
    return {
        "success": predicted == correct,
        "wrong_valid_target": bool(predicted not in {None, INVALID, correct} and valid(task, predicted)),
        "false_block": bool(predicted == INVALID and correct != INVALID),
        "invalid_attempt": bool(predicted not in {None, INVALID} and not valid(task, predicted)),
    }


def normalize_existing(model: str, method: str, source: str, row: dict[str, Any]) -> dict[str, Any]:
    task = row["task"]
    result = row["result"]
    outcome = consequence(task, result.get("predicted_target"))
    outcome["success"] = bool(result.get("final_state_success", result.get("success", False)))
    return {
        "model": model, "method": method, "source": source, "task": task,
        "predicted_target": result.get("predicted_target"),
        "errors": result.get("errors", []),
        "requests": row.get("api_request_attempts", 0),
        "prompt_tokens": 0, "completion_tokens": 0,
        **outcome,
    }


def normalize_upgrade(model: str, row: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    task = tasks[row["task_id"]]
    usage = [record for record in row.get("usage", [])]
    source = "v7" if row["smoke_source"] == "v7_core_replication" else "v6"
    return {
        "model": model,
        "method": "M1 Event Graph" if row["method"] == "event_graph" else "M2 Executable Selector",
        "source": source,
        "task": task,
        "predicted_target": row.get("predicted_target"),
        "errors": row.get("errors", []),
        "requests": row.get("request_attempts", 0),
        "prompt_tokens": sum(record.get("prompt_tokens", 0) for record in usage),
        "completion_tokens": sum(record.get("completion_tokens", 0) for record in usage),
        "schema_valid": row.get("schema_valid"),
        "mode_correct": row.get("mode_correct"),
        "selector_initial_correct": row.get("selector_initial_correct"),
        "selector_final_correct": row.get("selector_final_correct"),
        "success": row.get("success", False),
        "wrong_valid_target": row.get("wrong_write", False),
        "false_block": row.get("false_block", False),
        "invalid_attempt": row.get("invalid_attempt", False),
    }


def deterministic(tasks: list[dict[str, Any]], method: str) -> list[dict[str, Any]]:
    rows = []
    for task in tasks:
        if method == "Always-Lock":
            predicted = task["pre_refresh_target"]
            if not valid(task, predicted):
                predicted = INVALID
        else:
            predicted = task["post_refresh_target"]
        rows.append({
            "model": "Deterministic", "method": method,
            "source": "v7" if task["smoke_source"] == "v7_core_replication" else "v6",
            "task": task, "predicted_target": predicted, "errors": [], "requests": 0,
            "prompt_tokens": 0, "completion_tokens": 0, **consequence(task, predicted),
        })
    return rows


def collect() -> list[dict[str, Any]]:
    manifest = load(MANIFEST)
    tasks = {task["id"]: task for task in manifest}
    wanted = set(tasks)
    rows: list[dict[str, Any]] = []
    for model, config in RUNS.items():
        for source in ("v7", "v6"):
            for method, filename in config[source].items():
                for row in load(ROOT / "runs" / filename):
                    if row["task"]["id"] in wanted:
                        rows.append(normalize_existing(model, method, source, row))
        for row in load(ROOT / "runs" / config["upgrade"]):
            rows.append(normalize_upgrade(model, row, tasks))
    rows.extend(deterministic(manifest, "Always-Lock"))
    rows.extend(deterministic(manifest, "Always-Reevaluate"))
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["source"], row["model"], row["method"])].append(row)
    output = []
    for (source, model, method), group in sorted(groups.items()):
        schema = [row["schema_valid"] for row in group if "schema_valid" in row]
        modes = [row["mode_correct"] for row in group if "mode_correct" in row]
        selectors = [
            row["selector_initial_correct"] and row["selector_final_correct"]
            for row in group if row.get("selector_initial_correct") is not None
        ]
        output.append({
            "source": source, "model": model, "method": method, "n": len(group),
            "correct": sum(row["success"] for row in group),
            "schema_correct": sum(value is True for value in schema), "schema_n": len(schema),
            "mode_correct": sum(value is True for value in modes), "mode_n": len(modes),
            "selector_correct": sum(value is True for value in selectors), "selector_n": len(selectors),
            "wrong_valid_targets": sum(row["wrong_valid_target"] for row in group),
            "false_blocks": sum(row["false_block"] for row in group),
            "invalid_attempts": sum(row["invalid_attempt"] for row in group),
            "tasks_with_errors": sum(bool(row["errors"]) for row in group),
            "requests": sum(row["requests"] for row in group),
            "prompt_tokens": sum(row["prompt_tokens"] for row in group),
            "completion_tokens": sum(row["completion_tokens"] for row in group),
        })
    return output


def combined_upgrade(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for model in ("Qwen", "GLM"):
        for method in ("M1 Event Graph", "M2 Executable Selector"):
            parts = [row for row in summary if row["model"] == model and row["method"] == method]
            total = {key: sum(row[key] for row in parts) for key in (
                "n", "correct", "schema_correct", "schema_n", "mode_correct", "mode_n",
                "selector_correct", "selector_n", "wrong_valid_targets", "false_blocks",
                "invalid_attempts", "tasks_with_errors", "requests", "prompt_tokens",
                "completion_tokens",
            )}
            output.append({"model": model, "method": method, **total})
    return output


def conclusions(summary: list[dict[str, Any]], combined: list[dict[str, Any]]) -> dict[str, Any]:
    m2 = {row["model"]: row for row in combined if row["method"] == "M2 Executable Selector"}
    cta = {}
    for model in ("Qwen", "GLM"):
        parts = [row for row in summary if row["model"] == model and row["method"] == "Exact CTA"]
        cta[model] = {"n": sum(row["n"] for row in parts), "correct": sum(row["correct"] for row in parts)}
    gates = {
        "m2_schema_at_least_95pct_both_models": all(
            m2[model]["schema_correct"] / m2[model]["schema_n"] >= 0.95 for model in m2
        ),
        "m2_selector_at_least_95pct_both_models": all(
            m2[model]["selector_correct"] / m2[model]["selector_n"] >= 0.95 for model in m2
        ),
        "m2_not_more_than_2_points_below_cta": all(
            m2[model]["correct"] / m2[model]["n"] >= cta[model]["correct"] / cta[model]["n"] - 0.02
            for model in m2
        ),
        "m2_effect_direction_consistent": all(
            (m2[model]["correct"] / m2[model]["n"] - cta[model]["correct"] / cta[model]["n"]) >= 0
            for model in m2
        ),
    }
    return {
        "cta": cta,
        "m2": {model: {"n": row["n"], "correct": row["correct"]} for model, row in m2.items()},
        "gates": gates,
        "promote_m2_to_main_method": all(gates.values()),
        "recommended_main_method": "M2" if all(gates.values()) else "Exact CTA",
        "recommended_compositional_extension": "Role-Indexed Lifecycle",
    }


def cell(correct: int, n: int) -> str:
    return "NA" if not n else f"{correct}/{n} ({100 * correct / n:.1f}%)"


def markdown(report: dict[str, Any]) -> str:
    lines = ["# TRI Method Upgrade 20-Task Closed Loop", ""]
    for source, title in (("v7", "Scalar core (16 tasks)"), ("v6", "Compositional stress (4 tasks)")):
        lines.extend([
            f"## {title}", "",
            "| Model | Method | Accuracy | Schema | Mode | Selector | Wrong valid target | False block | Errors | Requests |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in report["summary"]:
            if row["source"] != source:
                continue
            lines.append(
                f"| {row['model']} | {row['method']} | {cell(row['correct'], row['n'])} | "
                f"{cell(row['schema_correct'], row['schema_n'])} | {cell(row['mode_correct'], row['mode_n'])} | "
                f"{cell(row['selector_correct'], row['selector_n'])} | {row['wrong_valid_targets']} | "
                f"{row['false_blocks']} | {row['tasks_with_errors']} | {row['requests']} |"
            )
        lines.append("")
    lines.extend([
        "## New-method combined view", "",
        "| Model | Method | Accuracy | Schema | Mode | Selector | Wrong valid target | Errors | Requests | Tokens in/out |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report["combined_upgrade"]:
        lines.append(
            f"| {row['model']} | {row['method']} | {cell(row['correct'], row['n'])} | "
            f"{cell(row['schema_correct'], row['schema_n'])} | {cell(row['mode_correct'], row['mode_n'])} | "
            f"{cell(row['selector_correct'], row['selector_n'])} | {row['wrong_valid_targets']} | "
            f"{row['tasks_with_errors']} | {row['requests']} | "
            f"{row['prompt_tokens']}/{row['completion_tokens']} |"
        )
    lines.extend(["", "## Decision", ""])
    for key, value in report["conclusions"]["gates"].items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        f"- promote_m2_to_main_method: {report['conclusions']['promote_m2_to_main_method']}",
        f"- recommended_main_method: {report['conclusions']['recommended_main_method']}",
        f"- recommended_compositional_extension: {report['conclusions']['recommended_compositional_extension']}",
        "",
        "The 20-task matrix is a smoke/decision experiment, not a final powered comparison.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    rows = collect()
    summary = summarize(rows)
    combined = combined_upgrade(summary)
    report = {
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "rows": len(rows),
        "summary": summary,
        "combined_upgrade": combined,
        "conclusions": conclusions(summary, combined),
    }
    json_path = ROOT / "reports/method_upgrade_closed_loop_v1.json"
    md_path = ROOT / "reports/method_upgrade_closed_loop_v1.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
