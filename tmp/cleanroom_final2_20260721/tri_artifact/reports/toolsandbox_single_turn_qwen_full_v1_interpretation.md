# Qwen Full-History Frozen 2x2 Interpretation

Run file:
`runs/toolsandbox_tri_single_turn_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl`

- Frozen tasks completed: 96/96.
- API or parser errors: 0.
- End-to-end successes: 68/96.
- Correct, timed binding opportunities: 70/96.
- Unauthorized rebinding in eligible Preserve/Flip trajectories: 0/16.
- Premature locking in eligible Reevaluate/Flip trajectories: 0/18.
- Total conditional TRI mechanism errors: 0/70.
- Wrong-entity writes: 6/96.
- Wrong-entity writes satisfying the TRI opportunity condition: 0/70.

All six wrong writes occur in the `p2` Reevaluate/Flip template, one for each selector cluster.
The model records `REM-A` after refresh even though the refreshed selector winner is `REM-B`.
They are initial target-selection/order errors, not post-binding referent transitions, and are
excluded from the TRI numerator under the frozen protocol.

This is negative evidence for TRI prevalence in the tested Qwen full-history Agent: the external
experiment does not reproduce a TRI mechanism error among 70 auditable opportunities. It does
show that semantically equivalent Reevaluate wording can induce systematic premature selection
and real wrong-entity writes. That adjacent failure mode must not be relabeled as TRI.

The result neither invalidates the controlled Generic-Ledger findings nor establishes deployment
prevalence. It narrows the claim: the phenomenon is controller- and model-dependent, and ordinary
full-history Qwen is not evidence that TRI is universal. The frozen GLM replication determines
whether this null result is model-specific.
