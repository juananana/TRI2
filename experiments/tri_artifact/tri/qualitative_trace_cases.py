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


def strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        return "\n".join(lines[1:-1]).strip()
    return stripped


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
    toolsandbox_manifest_path = root / "data/toolsandbox_tri_matched_heldout_v1.jsonl"
    ts_task = one(
        toolsandbox_manifest_path,
        lambda row: row["scenario_id"] == TOOLSANDBOX_ID,
    )
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
            "generic_actor_response": generic["result"]["raw_outputs"][-1],
            "authorized_target": task["correct_target"],
            "sqlite_action_status": replay["action_status"],
            "sqlite_acted_ids": replay["acted_ids"],
            "cta_final_target": cta["result"]["predicted_target"],
            "cta_actor_response": cta["result"]["raw_outputs"][-1],
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
            "instruction": ts_task["instruction"],
            "initial_binding": ts_generic["compiled_state"]["selected_entity_id"],
            "authorized_target": ts_generic["expected_target_id"],
            "generic_written_target": ts_generic["written_target_ids"],
            "generic_actor_response": strip_markdown_fence(
                ts_generic["raw_outputs"][-2]["content"]
            ),
            "lifecycle_written_target": ts_lifecycle["written_target_ids"],
            "lifecycle_actor_response": strip_markdown_fence(
                ts_lifecycle["raw_outputs"][-2]["content"]
            ),
            "generic_trace": compact_trace(ts_generic["tool_trace"]),
            "sources": [
                str(toolsandbox_manifest_path.relative_to(root)),
                str(toolsandbox_path.relative_to(root)),
            ],
        },
        "appworld_correct_opportunity": {
            "status": "custom AppWorld-backed case; not a leaderboard result",
            "scenario_id": APPWORLD_CORRECT_ID,
            "model": correct["model"],
            "instruction": correct["instruction"],
            "initial_target": correct["initial_target_id"],
            "refreshed_target": correct["refreshed_target_id"],
            "bound_target": correct["bound_target_id"],
            "written_target": correct["written_target_id"],
            "model_action": correct["raw_outputs"][-2],
            "conditional_tri": False,
            "trace": compact_trace(correct["trace"]),
            "source": str(appworld_glm.relative_to(root)),
        },
        "appworld_prebinding_error": {
            "status": "wrong write outside conditional TRI denominator",
            "scenario_id": APPWORLD_PREBIND_ID,
            "model": prebinding["model"],
            "instruction": prebinding["instruction"],
            "initial_target": prebinding["initial_target_id"],
            "refreshed_target": prebinding["refreshed_target_id"],
            "late_bound_target": prebinding["bound_target_id"],
            "written_target": prebinding["written_target_id"],
            "model_action": prebinding["raw_outputs"][-2],
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
        f"- User instruction: `{v7['instruction']}`",
        f"- Generic final response: `{v7['generic_actor_response']}`",
        f"- Old present/action-valid: `{v7['old_present']}` / `{v7['old_action_valid']}`.",
        f"- Sources: {', '.join(f'`{path}`' for path in v7['sources'])}.",
        "",
        "## ToolSandbox-compatible positive intervention",
        "",
        f"- `{ts['scenario_id']}`, `{ts['model']}`: initial/authorized `{ts['initial_binding']}`, Generic writes `{ts['generic_written_target'][0]}`, Lifecycle writes `{ts['lifecycle_written_target'][0]}`.",
        f"- User instruction: `{ts['instruction']}`",
        f"- Generic final action: `{ts['generic_actor_response']}`",
        f"- Status: {ts['status']}. Sources: {', '.join(f'`{path}`' for path in ts['sources'])}.",
        "",
        "## External opportunity without violation",
        "",
        f"- `{correct['scenario_id']}`, `{correct['model']}`: winner changes `{correct['initial_target']}` to `{correct['refreshed_target']}`, but binding and write remain `{correct['written_target']}`.",
        f"- User instruction: `{correct['instruction']}`",
        f"- Final action: `{correct['model_action']}`",
        f"- Status: {correct['status']}. Source: `{correct['source']}`.",
        "",
        "## Wrong write outside the conditional TRI denominator",
        "",
        f"- `{prebind['scenario_id']}`, `{prebind['model']}` refreshes before recording a binding, then binds/writes `{prebind['written_target']}` instead of initial `{prebind['initial_target']}`.",
        f"- User instruction: `{prebind['instruction']}`",
        f"- Final action: `{prebind['model_action']}`",
        f"- Initial binding correct / binding timing correct: `{prebind['initial_binding_correct']}` / `{prebind['binding_timing_correct']}`. This is a pre-binding/tool-order error, not conditional TRI.",
        f"- Source: `{prebind['source']}`.",
        "",
    ])


def markdown_zh(report: dict[str, Any]) -> str:
    v7 = report["v7_sqlite_conditional_tri"]
    ts = report["toolsandbox_compatible_positive"]
    correct = report["appworld_correct_opportunity"]
    prebind = report["appworld_prebinding_error"]
    return "\n".join([
        "# TRI 定性轨迹案例（中文说明）",
        "",
        "> 本报告由脚本直接从冻结的原始 JSONL 输出生成。中文是便于阅读的解释，",
        "> 英文原指令、模型原始工具调用、ID 和来源路径保持不变。案例是在完整运行后",
        "> 为解释而选取的，能够证明相应行为确实发生，但不能用于估计自然发生率。",
        "",
        "## 案例一：v7 / SQLite 中的条件 TRI 错写",
        "",
        f"- 任务、模型和控制器：`{v7['task_id']}` / `{v7['model']}` / `{v7['controller']}`。",
        f"- 英文原指令：`{v7['instruction']}`",
        "- 中文含义：从当前视图选择最早的未完成提醒；刷新后，操作对象仍应是刚才选中的提醒，然后推迟它。",
        f"- 初始 winner 和 ledger 已记录 ID：`{v7['initial_winner']}`；刷新后的新 winner：`{v7['refreshed_winner']}`。",
        f"- Generic 最终原始回答：`{v7['generic_actor_response']}`",
        f"- 实际结果：Generic 写入 `{v7['generic_final_target']}`，SQLite 标记为 `{v7['sqlite_action_status']}`；授权目标和 CTA 输出均为 `{v7['authorized_target']}`。",
        f"- 旧目标刷新后仍存在且可执行：`{v7['old_present']}` / `{v7['old_action_valid']}`。",
        f"- 来源：{', '.join(f'`{path}`' for path in v7['sources'])}。",
        "",
        "## 案例二：ToolSandbox-compatible 环境中的条件 TRI 错写",
        "",
        f"- 场景和模型：`{ts['scenario_id']}` / `{ts['model']}`。",
        f"- 英文原指令：`{ts['instruction']}`",
        "- 中文含义：同步前先找到最新创建且可编辑的提醒；同步完成后移动刚才那个提醒一天。如果它消失或只读，应停止，不能换成其他提醒。",
        f"- 初始绑定和授权目标：`{ts['initial_binding']}`；刷新后 Generic 实际写入：`{ts['generic_written_target'][0]}`。",
        f"- Generic 最终原始工具调用：`{ts['generic_actor_response']}`",
        f"- 对照结果：Lifecycle 写入正确目标 `{ts['lifecycle_written_target'][0]}`。",
        "- 结论：这是实际执行的 wrong-entity write，但任务是自定义的 ToolSandbox-compatible intervention，并非官方 ToolSandbox 分数；案例也是事后选取的。",
        f"- 来源：{', '.join(f'`{path}`' for path in ts['sources'])}。",
        "",
        "## 案例三：AppWorld 中存在机会但没有发生 TRI",
        "",
        f"- 场景和模型：`{correct['scenario_id']}` / `{correct['model']}`。",
        f"- 英文原指令：`{correct['instruction']}`",
        "- 中文含义：从当前 Todoist 列表找到截止日期最早的未完成任务；同步后，把刚才找到的任务推迟一天。",
        f"- 初始 winner：`{correct['initial_target']}`；刷新后 winner：`{correct['refreshed_target']}`。",
        f"- 模型最终原始工具调用：`{correct['model_action']}`",
        f"- 实际结果：模型仍写入原绑定目标 `{correct['written_target']}`，因此 conditional TRI 为 `{correct['conditional_tri']}`。",
        "- 结论：changed-winner 机会并不必然造成错误，这是防止选择性展示正例的重要负例。",
        f"- 来源：`{correct['source']}`。",
        "",
        "## 案例四：发生了错写，但不属于 TRI",
        "",
        f"- 场景和模型：`{prebind['scenario_id']}` / `{prebind['model']}`。",
        f"- 英文原指令：`{prebind['instruction']}`",
        "- 中文含义：从当前 Simple Note 中找到按字母排序最靠前的指定标签笔记；同步后，在刚才找到的笔记中追加 `reviewed`。",
        f"- 正确初始目标：`{prebind['initial_target']}`；刷新后 winner：`{prebind['refreshed_target']}`。",
        f"- 模型最终原始工具调用：`{prebind['model_action']}`",
        f"- 实际结果：模型先同步，之后才绑定并写入 `{prebind['written_target']}`；初始绑定正确 / 绑定时机正确为 `{prebind['initial_binding_correct']}` / `{prebind['binding_timing_correct']}`。",
        "- 结论：这是 pre-binding / tool-order error，不进入 conditional TRI 分母。",
        f"- 来源：`{prebind['source']}`。",
        "",
        "## 应如何使用这些案例",
        "",
        "这些案例能够支持三点：模型确实生成了相应目标或工具调用；执行器确实修改了对应实体；严格分母能够区分 TRI、正确保持和绑定前错误。它们不能证明 TRI 在真实流量中普遍存在，也不能替代独立人员编写指令的低干预确认实验。",
        "",
    ])
