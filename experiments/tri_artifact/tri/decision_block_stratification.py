from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


HISTORY = "history_only"
VISIBLE = "decision_visible"
MATCHED_CONDITIONS = (HISTORY, VISIBLE)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_target(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.lower() in {"invalid", "invalid_bound_entity", "unavailable", "missing", "reject"}:
        return "INVALID_BOUND_ENTITY"
    return text


def normalize_action(value: object) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split()).casefold()
    return text or None


def _last_request_payload(component: dict[str, Any]) -> dict[str, Any]:
    attempts = component.get("attempts") or []
    if not attempts:
        raise ValueError("component has no recorded request attempt")
    request = attempts[-1].get("request") or {}
    messages = request.get("messages") or []
    if len(messages) < 2:
        raise ValueError("recorded request lacks a user payload")
    value = json.loads(messages[-1]["content"])
    if not isinstance(value, dict):
        raise ValueError("recorded user payload is not an object")
    return value


def validate_complete_matched_rows(rows: list[dict[str, Any]], expected: int) -> None:
    if len(rows) != expected:
        raise ValueError(f"expected {expected} matched rows, found {len(rows)}")
    task_ids = [str(row.get("task", {}).get("id")) for row in rows]
    if len(set(task_ids)) != len(task_ids):
        raise ValueError("matched run contains duplicate task IDs")
    for row in rows:
        if not row.get("complete") or row.get("logical_calls_completed") != 3:
            raise ValueError("matched run contains an incomplete task")
        if (row.get("compiler") or {}).get("parsed") is None:
            raise ValueError("matched run contains an unparsed compiler output")
        actors = row.get("actors") or {}
        if set(actors) != set(MATCHED_CONDITIONS):
            raise ValueError("matched run does not contain both actor conditions")
        if any((actors[condition] or {}).get("parsed") is None for condition in MATCHED_CONDITIONS):
            raise ValueError("matched run contains an unparsed actor output")
        for component in [row["compiler"], actors[HISTORY], actors[VISIBLE]]:
            _last_request_payload(component)


def _target_correct(row: dict[str, Any], condition: str) -> bool:
    return normalize_target((row.get("outcomes") or {}).get(condition)) == normalize_target(
        row["task"].get("correct_target")
    )


def _e2e_correct(row: dict[str, Any], condition: str) -> bool:
    actor = (row.get("actors") or {}).get(condition) or {}
    parsed = actor.get("parsed") or {}
    return _target_correct(row, condition) and normalize_action(parsed.get("action")) == normalize_action(
        row["task"].get("action")
    )


def _paired_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def measure(condition: str, predicate: Any) -> dict[str, Any]:
        numerator = sum(bool(predicate(row, condition)) for row in rows)
        return {
            "numerator": numerator,
            "denominator": len(rows),
            "rate": numerator / len(rows) if rows else None,
        }

    def discordance(predicate: Any) -> dict[str, int]:
        history = [bool(predicate(row, HISTORY)) for row in rows]
        visible = [bool(predicate(row, VISIBLE)) for row in rows]
        return {
            "visible_repairs": sum(not left and right for left, right in zip(history, visible)),
            "visible_harms": sum(left and not right for left, right in zip(history, visible)),
            "both_correct": sum(left and right for left, right in zip(history, visible)),
            "both_wrong": sum(not left and not right for left, right in zip(history, visible)),
        }

    return {
        "rows": len(rows),
        "exact_target": {
            HISTORY: measure(HISTORY, _target_correct),
            VISIBLE: measure(VISIBLE, _target_correct),
            "paired_discordance": discordance(_target_correct),
        },
        "action_and_target_e2e": {
            HISTORY: measure(HISTORY, _e2e_correct),
            VISIBLE: measure(VISIBLE, _e2e_correct),
            "paired_discordance": discordance(_e2e_correct),
        },
    }


def authored_stratification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    compiler_mode_correct = lambda row: (
        ((row.get("compiler") or {}).get("parsed") or {}).get("reference_mode")
        == row["task"].get("reference_mode_gold")
    )
    preserve = [row for row in rows if row["task"].get("reference_mode_gold") == "preserve"]
    compiler_bound_correct = lambda row: normalize_target(
        (((row.get("compiler") or {}).get("parsed") or {}).get("bound_target_id"))
    ) == normalize_target(row["task"].get("pre_refresh_target"))
    return {
        "all_rows": _paired_summary(rows),
        "by_compiler_mode_correctness": {
            "correct": _paired_summary([row for row in rows if compiler_mode_correct(row)]),
            "wrong": _paired_summary([row for row in rows if not compiler_mode_correct(row)]),
        },
        "preserve_by_compiler_bound_id_correctness": {
            "correct": _paired_summary([row for row in preserve if compiler_bound_correct(row)]),
            "wrong": _paired_summary([row for row in preserve if not compiler_bound_correct(row)]),
        },
    }


def interface_redundancy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checks = defaultdict(int)
    for row in rows:
        task = row["task"]
        compiler = ((row.get("compiler") or {}).get("parsed") or {})
        compiler_request = _last_request_payload(row["compiler"])
        history_request = _last_request_payload(row["actors"][HISTORY])
        visible_request = _last_request_payload(row["actors"][VISIBLE])
        task_initial = normalize_target(task.get("initial_selected_id"))
        checks["compiler_selector_equals_base_selector"] += (
            compiler.get("selector") == task.get("selector")
        )
        checks["task_initial_id_equals_pre_refresh_target"] += (
            task_initial == normalize_target(task.get("pre_refresh_target"))
        )
        checks["compiler_request_initial_id_equals_task"] += (
            normalize_target(compiler_request.get("initial_selected_id")) == task_initial
        )
        checks["history_request_initial_id_equals_task"] += (
            normalize_target(history_request.get("initial_selected_id")) == task_initial
        )
        checks["visible_request_initial_id_equals_task"] += (
            normalize_target(visible_request.get("initial_selected_id")) == task_initial
        )
        checks["actor_request_initial_ids_equal_each_other"] += (
            normalize_target(history_request.get("initial_selected_id"))
            == normalize_target(visible_request.get("initial_selected_id"))
        )
    return {
        name: {
            "numerator": count,
            "denominator": len(rows),
            "rate": count / len(rows) if rows else None,
        }
        for name, count in sorted(checks.items())
    }


def _v7_initial_binding(row: dict[str, Any], controller: str) -> str | None:
    ledger = (row.get("result") or {}).get("compiled_ledger") or {}
    field = "selected_entity_id" if controller == "Generic" else "bound_target_id"
    return normalize_target(ledger.get(field))


def _v7_success(row: dict[str, Any]) -> bool:
    return normalize_target((row.get("result") or {}).get("predicted_target")) == normalize_target(
        row["task"].get("correct_target")
    )


def v7_boundary(rows: list[dict[str, Any]], controller: str) -> dict[str, Any]:
    flip = [row for row in rows if row.get("task", {}).get("update") == "flip"]
    if len(flip) != 80:
        raise ValueError(f"expected 80 v7 flip rows, found {len(flip)}")
    ids = [row["task"]["id"] for row in flip]
    if len(set(ids)) != 80:
        raise ValueError("v7 flip inventory contains duplicate task IDs")
    preserve = [row for row in flip if row["task"].get("binding") == "anchored"]
    reevaluate = [row for row in flip if row["task"].get("binding") == "dynamic"]
    if len(preserve) != 40 or len(reevaluate) != 40:
        raise ValueError("v7 flip inventory is not balanced by binding mode")
    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in flip:
        pairs[str(row["task"].get("state_cluster_id"))].append(row)
    if len(pairs) != 40 or any(
        len(pair) != 2 or {row["task"].get("binding") for row in pair} != {"anchored", "dynamic"}
        for pair in pairs.values()
    ):
        raise ValueError("v7 flip inventory does not contain 40 complete opposite-mode pairs")

    def measure(items: Iterable[dict[str, Any]], predicate: Any) -> dict[str, Any]:
        selected = list(items)
        numerator = sum(bool(predicate(row)) for row in selected)
        return {
            "numerator": numerator,
            "denominator": len(selected),
            "rate": numerator / len(selected) if selected else None,
        }

    pair_numerator = sum(all(_v7_success(row) for row in pair) for pair in pairs.values())
    return {
        "preserve_initial_binding": measure(
            preserve,
            lambda row: _v7_initial_binding(row, controller)
            == normalize_target(row["task"].get("pre_refresh_target")),
        ),
        "preserve_e2e": measure(preserve, _v7_success),
        "reevaluate_e2e": measure(reevaluate, _v7_success),
        "changed_pairacc": {
            "numerator": pair_numerator,
            "denominator": len(pairs),
            "rate": pair_numerator / len(pairs),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    def fraction(metric: dict[str, Any]) -> str:
        return f"{metric['numerator']}/{metric['denominator']} ({100 * metric['rate']:.1f}%)"

    lines = [
        "# Decision-Block Stratification Audit",
        "",
        f"Evidence status: `{report['evidence_status']}`. No model calls were made.",
        "",
        "The compiler strata below are post-treatment. They are descriptive associations, not",
        "mediation estimates or causal effects of mode, bound-ID, selector restatement, or enforcement.",
        "",
        "## Authored matched-call stratification",
        "",
    ]
    for model, result in report["authored_stratification"].items():
        lines.extend([
            f"### {model}",
            "",
            "| Stratum | Rows | History exact | Visible exact | History E2E | Visible E2E | Repairs | Harms |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for label, summary in [
            ("All", result["all_rows"]),
            ("Compiler mode correct", result["by_compiler_mode_correctness"]["correct"]),
            ("Compiler mode wrong", result["by_compiler_mode_correctness"]["wrong"]),
            ("Preserve bound ID correct", result["preserve_by_compiler_bound_id_correctness"]["correct"]),
            ("Preserve bound ID wrong", result["preserve_by_compiler_bound_id_correctness"]["wrong"]),
        ]:
            exact = summary["exact_target"]
            e2e = summary["action_and_target_e2e"]
            discord = exact["paired_discordance"]
            lines.append(
                f"| {label} | {summary['rows']} | {fraction(exact[HISTORY])} | "
                f"{fraction(exact[VISIBLE])} | {fraction(e2e[HISTORY])} | "
                f"{fraction(e2e[VISIBLE])} | {discord['visible_repairs']} | {discord['visible_harms']} |"
            )
        lines.append("")

    lines.extend(["## Interface redundancy", "", "| Dataset/model | Rows | Selector exact | Task initial ID = pre-refresh | Compiler copy | History copy | Visible copy | Actor copies equal |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for key, entry in report["interface_redundancy"].items():
        checks = entry["checks"]
        lines.append(
            f"| {key} | {entry['rows']} | {fraction(checks['compiler_selector_equals_base_selector'])} | "
            f"{fraction(checks['task_initial_id_equals_pre_refresh_target'])} | "
            f"{fraction(checks['compiler_request_initial_id_equals_task'])} | "
            f"{fraction(checks['history_request_initial_id_equals_task'])} | "
            f"{fraction(checks['visible_request_initial_id_equals_task'])} | "
            f"{fraction(checks['actor_request_initial_ids_equal_each_other'])} |"
        )

    pooled = report["interface_redundancy_pooled"]
    pooled_checks = pooled["checks"]
    lines.append(
        f"| **Pooled** | **{pooled['rows']}** | "
        f"**{fraction(pooled_checks['compiler_selector_equals_base_selector'])}** | "
        f"**{fraction(pooled_checks['task_initial_id_equals_pre_refresh_target'])}** | "
        f"**{fraction(pooled_checks['compiler_request_initial_id_equals_task'])}** | "
        f"**{fraction(pooled_checks['history_request_initial_id_equals_task'])}** | "
        f"**{fraction(pooled_checks['visible_request_initial_id_equals_task'])}** | "
        f"**{fraction(pooled_checks['actor_request_initial_ids_equal_each_other'])}** |"
    )

    lines.extend([
        "",
        "Exact equality shows value redundancy in the recorded interface. It does not rule out a salience effect from restatement.",
        "",
        "## Existing v7 end-to-end boundary",
        "",
        "| Model | Controller | Preserve initial binding | Preserve E2E | Reevaluate E2E | PairAcc |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for model, controllers in report["v7_end_to_end_boundary"].items():
        for controller, result in controllers.items():
            lines.append(
                f"| {model} | {controller} | {fraction(result['preserve_initial_binding'])} | "
                f"{fraction(result['preserve_e2e'])} | {fraction(result['reevaluate_e2e'])} | "
                f"{fraction(result['changed_pairacc'])} |"
            )
    lines.extend([
        "",
        "The v7 controller table is not call- or information-matched. It bounds end-to-end grounding and execution behavior but does not decompose the matched decision block.",
        "",
        "## Input provenance",
        "",
        "| Input | Rows | SHA-256 |",
        "|---|---:|---|",
    ])
    for item in report["inputs"]:
        lines.append(f"| `{item['path']}` | {item['rows']} | `{item['sha256']}` |")
    return "\n".join(lines) + "\n"
