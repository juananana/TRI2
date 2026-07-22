# GLM Full-History Frozen 2x2 Interpretation

Run file:
`runs/toolsandbox_tri_single_turn_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl`

- Frozen tasks completed: 96/96.
- End-to-end successes: 71/96.
- Correct, timed binding opportunities: 73/96.
- Unauthorized rebinding in eligible Preserve/Flip trajectories: 0/20.
- Premature locking in eligible Reevaluate/Flip trajectories: 0/16.
- Total conditional TRI mechanism errors: 0/73.
- Wrong-entity writes: 13/96.
- Wrong-entity writes satisfying the TRI opportunity condition: 0/73.
- Tool-selection errors: 4/96, all using the nonexistent name `search_reminders`.

The 13 wrong writes are excluded from the TRI numerator because their recorded binding does not
match the authorized binding. Eight are Reevaluate/Flip initial-selection errors, three are
Reevaluate/Stable selector-grounding errors, and two are Preserve alphabetic-selector grounding
errors. The repeated `p2` Reevaluate/Flip failure generalizes across selector clusters and matches
the Qwen pattern, but it is an adjacent instruction-order failure rather than post-binding
unauthorized rebinding.

Within this frozen 96-task, ordinary full-history protocol, Qwen and GLM produce zero TRI
mechanism errors in 143 auditable opportunities. This is negative evidence against a
universal-LLM framing, not a claim that every ToolSandbox-compatible controller is null. A
separate post-hoc strict audit of the earlier frozen 24-task intervention finds conditional TRI
under GLM Generic (3/6) and Qwen Lifecycle-free (2/6), while matched Stable controls are clean.
Those tasks use the same native reminder database and search/modify tools but a different custom
controller and transition protocol; see `toolsandbox_tri_pilot_conditional_audit_v1.md`.
