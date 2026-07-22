# TRI 定性轨迹案例（中文说明）

> 本报告由脚本直接从冻结的原始 JSONL 输出生成。中文是便于阅读的解释，
> 英文原指令、模型原始工具调用、ID 和来源路径保持不变。案例是在完整运行后
> 为解释而选取的，能够证明相应行为确实发生，但不能用于估计自然发生率。

## 案例一：v7 / SQLite 中的条件 TRI 错写

- 任务、模型和控制器：`tri-v7-core-reminders-s1-explicit_anchor-name_collision` / `Qwen/Qwen3.5-122B-A10B` / `generic_structured_ledger_then_act`。
- 英文原指令：`Choose the earliest incomplete reminder from the present view. Reload reminder_service; the action target remains that chosen reminder. Now postpone it.`
- 中文含义：从当前视图选择最早的未完成提醒；刷新后，操作对象仍应是刚才选中的提醒，然后推迟它。
- 初始 winner 和 ledger 已记录 ID：`REM-1A`；刷新后的新 winner：`REM-1B`。
- Generic 最终原始回答：`{"action":"process","target_id":"REM-1B"}`
- 实际结果：Generic 写入 `REM-1B`，SQLite 标记为 `wrong_entity_write`；授权目标和 CTA 输出均为 `REM-1A`。
- 旧目标刷新后仍存在且可执行：`True` / `True`。
- 来源：`runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl`, `runs/v7_qwen_compile_then_act_full.jsonl`, `runs/v7_core_sqlite_replay.jsonl`。

## 案例二：ToolSandbox-compatible 环境中的条件 TRI 错写

- 场景和模型：`ts2-newest-created-preserve-flip` / `Pro/zai-org/GLM-5.1`。
- 英文原指令：`Before synchronizing, check which entry is the newest-created editable reminder. Once synchronization finishes, move that reminder one day later. If the entry disappeared or is read-only, stop instead of switching entries.`
- 中文含义：同步前先找到最新创建且可编辑的提醒；同步完成后移动刚才那个提醒一天。如果它消失或只读，应停止，不能换成其他提醒。
- 初始绑定和授权目标：`REM-A`；刷新后 Generic 实际写入：`REM-B`。
- Generic 最终原始工具调用：`{"tool":"postpone_reminder","arguments":{"reminder_id":"REM-B","seconds":86400}}`
- 对照结果：Lifecycle 写入正确目标 `REM-A`。
- 结论：这是实际执行的 wrong-entity write，但任务是自定义的 ToolSandbox-compatible intervention，并非官方 ToolSandbox 分数；案例也是事后选取的。
- 来源：`data/toolsandbox_tri_matched_heldout_v1.jsonl`, `runs/toolsandbox_tri_matched_glm_heldout_v1.jsonl`。

## 案例三：AppWorld 中存在机会但没有发生 TRI

- 场景和模型：`appworld-todoist-p1-preserve-flip` / `Pro/zai-org/GLM-5.1`。
- 英文原指令：`Find the incomplete Todoist task due earliest in the list as it is now. Synchronize Todoist, then postpone the task you found by one day.`
- 中文含义：从当前 Todoist 列表找到截止日期最早的未完成任务；同步后，把刚才找到的任务推迟一天。
- 初始 winner：`6334`；刷新后 winner：`6336`。
- 模型最终原始工具调用：`{"tool":"postpone_task","arguments":{"task_id":"6334"}}`
- 实际结果：模型仍写入原绑定目标 `6334`，因此 conditional TRI 为 `False`。
- 结论：changed-winner 机会并不必然造成错误，这是防止选择性展示正例的重要负例。
- 来源：`runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl`。

## 案例四：发生了错写，但不属于 TRI

- 场景和模型：`appworld-simple-note-p1-preserve-flip` / `Qwen/Qwen3.5-122B-A10B`。
- 英文原指令：`Find the alphabetically first note tagged tri-experiment in Simple Note as the notes are now. Synchronize Simple Note, then append 'reviewed' to the note you found.`
- 中文含义：从当前 Simple Note 中找到按字母排序最靠前的指定标签笔记；同步后，在刚才找到的笔记中追加 `reviewed`。
- 正确初始目标：`3084`；刷新后 winner：`3086`。
- 模型最终原始工具调用：`{"tool":"append_to_note","arguments":{"note_id":"3086"}}`
- 实际结果：模型先同步，之后才绑定并写入 `3086`；初始绑定正确 / 绑定时机正确为 `False` / `False`。
- 结论：这是 pre-binding / tool-order error，不进入 conditional TRI 分母。
- 来源：`runs/appworld_tri_simple_note_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl`。

## 应如何使用这些案例

这些案例能够支持三点：模型确实生成了相应目标或工具调用；执行器确实修改了对应实体；严格分母能够区分 TRI、正确保持和绑定前错误。它们不能证明 TRI 在真实流量中普遍存在，也不能替代独立人员编写指令的低干预确认实验。
