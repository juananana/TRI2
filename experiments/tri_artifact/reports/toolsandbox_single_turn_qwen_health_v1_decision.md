# Qwen Single-Turn Health-Check Decision

Run file:
`runs/toolsandbox_tri_single_turn_Qwen_Qwen3.5-122B-A10B_full_history_health_v1.jsonl`

## Infrastructure decision

- Completed rows: 8/8.
- API or parser errors: 0/8.
- End-to-end task success: 4/8.
- Correct, timed initial binding and completed-refresh opportunities: 5/8.
- Opportunity coverage: nonzero in all four Preserve/Reevaluate x Stable/Flip cells.

The infrastructure health check therefore passes the preregistered conditions for a Qwen
full-history run. End-to-end accuracy is not itself the health gate because autonomous tool-order
and binding failures are experimental outcomes.

## Scientific interpretation

- Unauthorized rebinding among eligible Preserve/Flip opportunities: 0/1.
- Premature locking among eligible Reevaluate/Flip opportunities: 0/1.
- Wrong-entity writes: 1/8.
- Wrong-entity writes satisfying the TRI opportunity condition: 0/5.

The single wrong write occurred in a Reevaluate/Flip task where the model recorded `REM-A` after
refresh although the correct refreshed binding was `REM-B`. It is an initial target-selection
error, not a post-binding TRI error, and is excluded from the conditional mechanism numerator.

Two Preserve rows selected the correct final ID but recorded the binding only after refresh. They
are conservatively excluded from the TRI opportunity denominator. This indicates measurement
compliance sensitivity to wording and must be reported as opportunity coverage, not silently
converted into either success or failure.

Eight tasks are insufficient to estimate a mechanism rate. The health run authorizes the frozen
96-task Qwen full-history experiment; it does not support a paper-facing claim by itself.
