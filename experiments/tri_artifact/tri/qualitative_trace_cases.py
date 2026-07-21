from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
V7_TASK_ID = "tri-v7-core-reminders-s1-explicit_anchor-name_collision"
TOOLSANDBOX_ID = "ts2-newest-created-preserve-flip"
APPWORLD_CORRECT_ID = "appworld-todoist-p1-preserve-flip"
APPWORLD_PREBIND_ID = "appworld-simple-note-p1-preserve-flip"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def one(path: Path, predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    rows = [row for row in load_jsonl(path) if predicate(row)]
    if len(rows) != 1:
        raise ValueError(f"expected one matching row in {path}, found {len(rows)}")
    return rows[0]


def compact_trace(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for step in trace:
        item: dict[str, Any] = {"tool": step.get("tool"), "status": step.get("status")}
        if "arguments" in step:
            item["arguments"] = step["arguments"]
        if "result_ids" in step:
            item["result_ids"] = step["result_ids"]
        if "transition" in step:
            item["transition"] = step["transition"]
        result = step.get("result")
        if isinstance(result, dict):
            item["result"] = {
                key: result.get(key)
                for key in ("target", "mutated", "status")
                if key in result
            }
        compact.append({key: value for key, value in item.items() if value is not None})
    return compact


def build_report(root: Path = ROOT) -> dict[str, Any]:
    generic_path = root / "runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl"
    cta_path = root / "runs/v7_qwen_compile_then_act_full.jsonl"
    replay_path = root / "runs/v7_core_sqlite_replay.jsonl"
    generic = one(generic_path, lambda row: row["task"]["id"] == V7_TASK_ID)
    cta = one(cta_path, lambda row: row["task"]["id"] == V7_TASK_ID)
    replay = one(
        replay_path,
        lambda row: row["task_id"] == V7_TASK_ID
        and row["model"] == generic["model"]
        and row["mode"] == generic["result"]["mode"],
    )
    task = generic["task"]
    ledger = generic["result"]["compiled_ledger"]
    assert task["binding"] == "anchored"
    assert task["update"] in {"flip", "name_collision"}
    assert ledger["selected_entity_id"] == task["pre_refresh_target"]
    assert task["bound_entity_present_after_refresh"]
    assert task["bound_entity_actionable_after_refresh"]
    assert generic["result"]["predicted_target"] == task["post_refresh_target"]
    assert replay["action_status"] == "wrong_entity_write"
    assert replay["acted_ids"] == [task["post_refresh_target"]]
    assert cta["result"]["success"] and cta["result"]["predicted_target"] == task["correct_target"]
    assert generic["status"] == cta["status"] == "ok"
    assert not generic["result"]["errors"] and not cta["result"]["errors"]

    toolsandbox_path = root / "runs/toolsandbox_tri_matched_glm_heldout_v1.jsonl"
    ts_generic = one(
        toolsandbox_path,
        lambda row: row["scenario_id"] == TOOLSANDBOX_ID
        and row["controller"] == "matched_generic",
    )
    ts_lifecycle = one(
        toolsandbox_path,
        lambda row: row["scenario_id"] == TOOLSANDBOX_ID
        and row["controller"] == "matched_lifecycle",
    )
    assert ts_generic["compiled_state"]["selected_entity_id"] == ts_generic["expected_target_id"]
    assert ts_generic["wrong_entity_write"] and not ts_generic["errors"]
    assert ts_lifecycle["written_target_ids"] == [ts_lifecycle["expected_target_id"]]
    assert not ts_lifecycle["wrong_entity_write"] and not ts_lifecycle["errors"]

    appworld_glm = root / "runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl"
    appworld_qwen = root / "runs/appworld_tri_simple_note_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl"
    correct = one(appworld_glm, lambda row: row["scenario_id"] == APPWORLD_CORRECT_ID)
    prebinding = one(appworld_qwen, lambda row: row["scenario_id"] == APPWORLD_PREBIND_ID)
    assert correct["initial_binding_correct"] and correct["binding_timing_correct"]
    assert correct["initial_target_id"] != correct["refreshed_target_id"]
    assert correct["written_target_id"] == correct["initial_target_id"]
    assert not correct["wrong_entity_write"]
    assert not prebinding["initial_binding_correct"] and not prebinding["binding_timing_correct"]
    assert prebinding["wrong_entity_write"] and not prebinding["errors"]

    return {
        "v7_sqlite_conditional_tri": {
            "task_id": V7_TASK_ID,
            "model": generic["model"],
            "controller": generic["result"]["mode"],
            "instruction": task["instruction"],
            "update": task["update"],
            "initial_winner": task["pre_refresh_target"],
            "refreshed_winner": task["post_refresh_target"],
            "old_present": task["bound_entity_present_after_refresh"],
            "old_action_valid": task["bound_entity_actionable_after_refresh"],
            "ledger_selected_id": ledger["selected_entity_id"],
            "generic_final_target": generic["result"]["predicted_target"],
            "authorized_target": task["correct_target"],
            "sqlite_action_status": replay["action_status"],
            "sqlite_acted_ids": replay["acted_ids"],
            "cta_final_target": cta["result"]["predicted_target"],
            "trace": compact_trace(replay["trace"]),
            "sources": [
                str(generic_path.relative_to(root)),
                str(cta_path.relative_to(root)),
                str(replay_path.relative_to(root)),
            ],
        },
        "toolsandbox_compatible_positive": {
            "status": "post-hoc selected custom benchmark-compatible intervention; not an official ToolSandbox result",
            "scenario_id": TOOLSANDBOX_ID,
            "model": ts_generic["model"],
            "initial_binding": ts_generic["compiled_state"]["selected_entity_id"],
            "authorized_target": ts_generic["expected_target_id"],
            "generic_written_target": ts_generic["written_target_ids"],
            "lifecycle_written_target": ts_lifecycle["written_target_ids"],
            "generic_trace": compact_trace(ts_generic["tool_trace"]),
            "source": str(toolsandbox_path.relative_to(root)),
        },
        "appworld_correct_opportunity": {
            "status": "custom AppWorld-backed case; not a leaderboard result",
            "scenario_id": APPWORLD_CORRECT_ID,
            "model": correct["model"],
            "initial_target": correct["initial_target_id"],
            "refreshed_target": correct["refreshed_target_id"],
            "bound_target": correct["bound_target_id"],
            "written_target": correct["written_target_id"],
            "conditional_tri": False,
            "trace": compact_trace(correct["trace"]),
            "source": str(appworld_glm.relative_to(root)),
        },
        "appworld_prebinding_error": {
            "status": "wrong write outside conditional TRI denominator",
            "scenario_id": APPWORLD_PREBIND_ID,
            "model": prebinding["model"],
            "initial_target": prebinding["initial_target_id"],
            "refreshed_target": prebinding["refreshed_target_id"],
            "late_bound_target": prebinding["bound_target_id"],
            "written_target": prebinding["written_target_id"],
            "initial_binding_correct": prebinding["initial_binding_correct"],
            "binding_timing_correct": prebinding["binding_timing_correct"],
            "conditional_tri": False,
            "trace": compact_trace(prebinding["trace"]),
            "source": str(appworld_qwen.relative_to(root)),
        },
    }


def markdown(report: dict[str, Any]) -> str:
    v7 = report["v7_sqlite_conditional_tri"]
    ts = report["toolsandbox_compatible_positive"]
    correct = report["appworld_correct_opportunity"]
    prebind = report["appworld_prebinding_error"]
    return "\n".join([
        "# Qualitative Trace Cases",
        "",
        "## Frozen v7/SQLite conditional TRI",
        "",
        f"- Task/model/controller: `{v7['task_id']}` / `{v7['model']}` / `{v7['controller']}`",
        f"- Initial winner and ledger ID: `{v7['initial_winner']}`; refreshed winner: `{v7['refreshed_winner']}`.",
        f"- Generic targets and writes `{v7['generic_final_target']}` (`{v7['sqlite_action_status']}`); authorized and CTA target `{v7['authorized_target']}`.",
        f"- Old present/action-valid: `{v7['old_present']}` / `{v7['old_action_valid']}`.",
        f"- Sources: {', '.join(f'`{path}`' for path in v7['sources'])}.",
        "",
        "## ToolSandbox-compatible positive intervention",
        "",
        f"- `{ts['scenario_id']}`, `{ts['model']}`: initial/authorized `{ts['initial_binding']}`, Generic writes `{ts['generic_written_target'][0]}`, Lifecycle writes `{ts['lifecycle_written_target'][0]}`.",
        f"- Status: {ts['status']}. Source: `{ts['source']}`.",
        "",
        "## External opportunity without violation",
        "",
        f"- `{correct['scenario_id']}`, `{correct['model']}`: winner changes `{correct['initial_target']}` to `{correct['refreshed_target']}`, but binding and write remain `{correct['written_target']}`.",
        f"- Status: {correct['status']}. Source: `{correct['source']}`.",
        "",
        "## Wrong write outside the conditional TRI denominator",
        "",
        f"- `{prebind['scenario_id']}`, `{prebind['model']}` refreshes before recording a binding, then binds/writes `{prebind['written_target']}` instead of initial `{prebind['initial_target']}`.",
        f"- Initial binding correct / binding timing correct: `{prebind['initial_binding_correct']}` / `{prebind['binding_timing_correct']}`. This is a pre-binding/tool-order error, not conditional TRI.",
        f"- Source: `{prebind['source']}`.",
        "",
    ])
