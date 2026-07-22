# Qualitative Trace Cases

## Frozen v7/SQLite conditional TRI

- Task/model/controller: `tri-v7-core-reminders-s1-explicit_anchor-name_collision` / `Qwen/Qwen3.5-122B-A10B` / `generic_structured_ledger_then_act`
- Initial winner and ledger ID: `REM-1A`; refreshed winner: `REM-1B`.
- Generic targets and writes `REM-1B` (`wrong_entity_write`); authorized and CTA target `REM-1A`.
- User instruction: `Choose the earliest incomplete reminder from the present view. Reload reminder_service; the action target remains that chosen reminder. Now postpone it.`
- Generic final response: `{"action":"process","target_id":"REM-1B"}`
- Old present/action-valid: `True` / `True`.
- Sources: `runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl`, `runs/v7_qwen_compile_then_act_full.jsonl`, `runs/v7_core_sqlite_replay.jsonl`.

## ToolSandbox-compatible positive intervention

- `ts2-newest-created-preserve-flip`, `Pro/zai-org/GLM-5.1`: initial/authorized `REM-A`, Generic writes `REM-B`, Lifecycle writes `REM-A`.
- User instruction: `Before synchronizing, check which entry is the newest-created editable reminder. Once synchronization finishes, move that reminder one day later. If the entry disappeared or is read-only, stop instead of switching entries.`
- Generic final action: `{"tool":"postpone_reminder","arguments":{"reminder_id":"REM-B","seconds":86400}}`
- Status: post-hoc selected custom benchmark-compatible intervention; not an official ToolSandbox result. Sources: `data/toolsandbox_tri_matched_heldout_v1.jsonl`, `runs/toolsandbox_tri_matched_glm_heldout_v1.jsonl`.

## External opportunity without violation

- `appworld-todoist-p1-preserve-flip`, `Pro/zai-org/GLM-5.1`: winner changes `6334` to `6336`, but binding and write remain `6334`.
- User instruction: `Find the incomplete Todoist task due earliest in the list as it is now. Synchronize Todoist, then postpone the task you found by one day.`
- Final action: `{"tool":"postpone_task","arguments":{"task_id":"6334"}}`
- Status: custom AppWorld-backed case; not a leaderboard result. Source: `runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl`.

## Wrong write outside the conditional TRI denominator

- `appworld-simple-note-p1-preserve-flip`, `Qwen/Qwen3.5-122B-A10B` refreshes before recording a binding, then binds/writes `3086` instead of initial `3084`.
- User instruction: `Find the alphabetically first note tagged tri-experiment in Simple Note as the notes are now. Synchronize Simple Note, then append 'reviewed' to the note you found.`
- Final action: `{"tool":"append_to_note","arguments":{"note_id":"3086"}}`
- Initial binding correct / binding timing correct: `False` / `False`. This is a pre-binding/tool-order error, not conditional TRI.
- Source: `runs/appworld_tri_simple_note_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl`.
