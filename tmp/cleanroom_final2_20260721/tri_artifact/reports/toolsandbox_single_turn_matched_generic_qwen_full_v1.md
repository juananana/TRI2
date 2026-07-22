# ToolSandbox Single-Turn 2x2 Results

Rows: 96; tasks: 96; duplicate keys: 0.

| Model | Controller | Mode | Transition | N | API/protocol errors | Correct binding | Opportunities | Mechanism errors | Conditional rate (95% cluster CI) | Wrong writes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.5-122B-A10B | matched_generic_state_observed | preserve | flip | 24 | 0 | 14 | 14 | 0 | 0.0% [0.0, 0.0] | 1 |
| Qwen/Qwen3.5-122B-A10B | matched_generic_state_observed | preserve | stable | 24 | 0 | 14 | 14 | 0 | 0.0% [0.0, 0.0] | 1 |
| Qwen/Qwen3.5-122B-A10B | matched_generic_state_observed | reevaluate | flip | 24 | 0 | 19 | 19 | 0 | 0.0% [0.0, 0.0] | 2 |
| Qwen/Qwen3.5-122B-A10B | matched_generic_state_observed | reevaluate | stable | 24 | 0 | 17 | 17 | 0 | 0.0% [0.0, 0.0] | 1 |

Mechanism errors are unauthorized rebinding in Preserve/Flip and premature locking in Reevaluate/Flip. The denominator includes only trajectories with an observed, correctly timed, correct binding and a completed refresh. Stable cells are negative controls. API and protocol errors are not counted as TRI evidence.
