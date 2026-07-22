# AppWorld Released-Trajectory TRI Audit

## Coverage

The downloaded AppWorld release contains 732 task instances from 244 generator families. The unmodified task format has an initial world and Agent-driven actions but no independently scheduled post-binding
external transition. Therefore the strict exogenous-refresh TRI opportunity count is **0**.

One public task family, `8ce6779` (three instances), is a natural TRI-like trace. The
Agent selects incomplete Todoist tasks assigned to the user, reassigns them, and then
must resolve `leave a comment there` to the same task IDs. Reassignment makes those IDs
fail the original assigned-to-me selector, while their discourse identity persists.

## Released Trace Audit

| Quantity | Count |
|---|---:|
| Public Agent trajectories containing the family | 42 |
| Released experiment configurations | 14 |
| Correct target-binding operations | 16 |
| Same-ID comments after reassignment | 16 |
| Post-binding target substitutions | 0 |
| Expected task targets never reassigned | 152 |
| Correct assignments lacking the required comment | 0 |
| Assignments to non-gold task IDs | 2 |
| Comments on non-gold task IDs | 3 |
| Trajectories passing every official evaluator test | 2 |

## Interpretation

This public trace establishes that post-binding reference persistence across a
selector-invalidating state mutation occurs naturally in an independent benchmark.
It does not establish TRI failure prevalence: the family has no Stable/Flip or
Preserve/Reevaluate counterpart and no concurrent external update. In these released
traces, the dominant failure is failure to bind/reassign expected tasks, not substitution of a
different task after a correct binding. The result therefore supports problem realism
while preserving the paper's model/controller-conditional failure claim.

Per-experiment aggregate counts and official evaluator outcomes are stored in
`appworld_public_trace_tri_audit.json`.
