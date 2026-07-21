# Qualitative Trace Cases

## Frozen v7/SQLite conditional TRI

- Task/model/controller: `tri-v7-core-reminders-s1-explicit_anchor-name_collision` / `Qwen/Qwen3.5-122B-A10B` / `generic_structured_ledger_then_act`
- Initial winner and ledger ID: `REM-1A`; refreshed winner: `REM-1B`.
- Generic targets and writes `REM-1B` (`wrong_entity_write`); authorized and CTA target `REM-1A`.
- Old present/action-valid: `True` / `True`.
- Sources: `runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl`, `runs/v7_qwen_compile_then_act_full.jsonl`, `runs/v7_core_sqlite_replay.jsonl`.

## ToolSandbox-compatible positive intervention

- `ts2-newest-created-preserve-flip`, `Pro/zai-org/GLM-5.1`: initial/authorized `REM-A`, Generic writes `REM-B`, Lifecycle writes `REM-A`.
- Status: post-hoc selected custom benchmark-compatible intervention; not an official ToolSandbox result. Source: `runs/toolsandbox_tri_matched_glm_heldout_v1.jsonl`.

## External opportunity without violation

- `appworld-todoist-p1-preserve-flip`, `Pro/zai-org/GLM-5.1`: winner changes `6334` to `6336`, but binding and write remain `6334`.
- Status: custom AppWorld-backed case; not a leaderboard result. Source: `runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl`.

## Wrong write outside the conditional TRI denominator

- `appworld-simple-note-p1-preserve-flip`, `Qwen/Qwen3.5-122B-A10B` refreshes before recording a binding, then binds/writes `3086` instead of initial `3084`.
- Initial binding correct / binding timing correct: `False` / `False`. This is a pre-binding/tool-order error, not conditional TRI.
- Source: `runs/appworld_tri_simple_note_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl`.
