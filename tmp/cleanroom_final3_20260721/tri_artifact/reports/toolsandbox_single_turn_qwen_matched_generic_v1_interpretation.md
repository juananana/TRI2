# Qwen Matched Generic Structured Ledger Interpretation

Run file:
`runs/toolsandbox_tri_single_turn_Qwen_Qwen3.5-122B-A10B_matched_generic_state_observed_full_v1.jsonl`

- Frozen tasks completed: 96/96.
- API or parser errors: 0.
- Correct immutable compiler bindings: 64/96.
- TRI opportunities: 64/96.
- Preserve/Flip unauthorized rebindings: 0/14.
- Reevaluate/Flip premature locks: 0/19.
- Wrong-entity writes: 5/96.
- Wrong writes satisfying the TRI opportunity condition: 0/64.

All five wrong writes are initial compiler-grounding errors. In the Preserve/Flip candidate, the
compiler selected `REM-C` instead of the correct initial `REM-A`; the other errors likewise have
compiled IDs that do not match the gold binding. The immutable generic ledger therefore does not
produce a post-binding referent transition in this external inventory, despite producing adjacent
initial-selector errors.

This result should not be merged with the original 24-task ToolSandbox pilot, which used a
different scenario inventory and lacked the new auditable binding denominator. It is also not
evidence that TRI cannot occur in the paper's controlled ledger; it limits the external claim to
the tested ToolSandbox-based Reminder extension and tested model/controller configuration.
