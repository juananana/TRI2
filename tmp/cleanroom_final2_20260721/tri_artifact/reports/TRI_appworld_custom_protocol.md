# TRI AppWorld Custom Case-Study Protocol

**Status:** frozen before model calls.

## Scope

The study uses AppWorld `0.1.3.post1` and official train task world `82e2fac_1` as a
database/API substrate. The downloaded package passed AppWorld's end-to-end verification
on all 147 train/dev tasks. The TRI instructions, synchronization operator, binding
instrumentation, and evaluator are custom. Results must not be called an AppWorld
leaderboard score or an unmodified AppWorld benchmark result.

## Frozen MVP

- App: Todoist.
- Selector: earliest-due incomplete task.
- 2 reference modes: Preserve and Reevaluate.
- 2 transitions: Stable and Flip.
- 2 natural instruction paraphrases.
- Total: 8 task instances, grouped into one selector cluster.

The initial controlled records are A (due 2023-05-20) and C (due 2023-05-22). Sync adds
B. In Stable, B is due 2023-05-25 and A remains the winner. In Flip, B is due 2023-05-19
and becomes the winner. A remains present, incomplete, and editable in every cell.

## Trajectory and Gold

1. The Agent reads one natural instruction.
2. It autonomously calls AppWorld-backed `search_tasks`.
3. It calls the sidecar `record_binding(task_id)` exactly once, making initial binding
   observable rather than inferred after the fact.
4. It calls `sync_tasks`, which adds B through AppWorld's native Todoist API.
5. It calls `postpone_task(task_id)`, which delegates to native `update_task`.
6. The evaluator compares stable task IDs and the post-sync/final database snapshots.

Preserve gold is A in Stable and Flip. Reevaluate gold is A in Stable and B in Flip.
No LLM judge is used. The primary metrics are initial binding correctness, conditional
TRI error, Stable error, wrong-entity write, premature lock, and collateral modification.

## Interpretation

This is a small external case study, not a prevalence estimate. A positive conditional
error shows that TRI can produce a wrong record mutation in an AppWorld-backed trajectory.
A null result bounds the phenomenon for the tested model/controller and does not erase the
controlled TRI-v3/v7 result. Because all eight tasks share one selector cluster, confidence
intervals over task rows would be misleading and are not reported as independent-sample CIs.
