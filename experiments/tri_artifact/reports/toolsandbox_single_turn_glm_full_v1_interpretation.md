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

Together, Qwen and GLM ordinary full-history Agents produce zero TRI mechanism errors in 143
auditable opportunities. This is negative external evidence against a universal-LLM framing. The
next discriminating experiment is the same frozen inventory under a generic rewritable state
controller: a nonzero conditional error there would locate the risk in Agent state management
rather than in every full-history model trajectory.
