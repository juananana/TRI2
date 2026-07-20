# AppWorld TRI Custom Case-Study Results

## Scope

This result uses AppWorld's Todoist database and native create/show/update APIs, but the
eight TRI tasks, mid-trajectory synchronization, binding instrumentation, and evaluator
are custom. It is not an AppWorld TGC/SGC or leaderboard result. All tasks share one
selector cluster, so row-level confidence intervals are intentionally omitted.

## Results

| Model/controller | Rows | Strict success | Correct final write | Auditable binding | Conditional TRI | Wrong writes | Stable errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 / full-history | 8 | 8/8 | 8/8 | 8/8 | 0/8 | 0 | 0 |
| Qwen/Qwen3.5-122B-A10B / full-history | 8 | 6/8 | 8/8 | 6/8 | 0/6 | 0 | 0 |
| Combined | 16 | 14/16 | 16/16 | 14/16 | 0/14 | 0 | 0 |

The primary Preserve/Flip slice contains 0/3 unauthorized rebindings after a correct, correctly timed binding.

## Error Attribution

Qwen's two strict failures are not TRI failures. On one Preserve instruction template,
it searched A but synchronized before calling the required sidecar binding tool. Its
first write attempt was rejected; it then recorded A, retried, and modified A. Thus all
16 trajectories ultimately wrote the authorized ID, while 14/16 satisfy the complete
trajectory protocol. There are no API or parse-error rows.

## Interpretation

This is negative external evidence against a universal failure claim. It shows that the
TRI distinction can be instantiated and deterministically audited in a richer public
application database, but it does not independently demonstrate a positive TRI failure
for ordinary full-history agents. The controlled TRI-v3/v7 experiments remain the positive
mechanism diagnosis; this study narrows its external-validity boundary.
