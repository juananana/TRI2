# ToolSandbox Single-Turn 2x2 Results

Rows: 96; tasks: 96; duplicate keys: 0.

| Model | Controller | Mode | Transition | N | API/protocol errors | Correct binding | Opportunities | Mechanism errors | Conditional rate (95% cluster CI) | Wrong writes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | matched_generic_state_observed | preserve | flip | 24 | 0 | 24 | 24 | 0 | 0.0% [0.0, 0.0] | 0 |
| Pro/zai-org/GLM-5.1 | matched_generic_state_observed | preserve | stable | 24 | 0 | 24 | 24 | 0 | 0.0% [0.0, 0.0] | 0 |
| Pro/zai-org/GLM-5.1 | matched_generic_state_observed | reevaluate | flip | 24 | 0 | 19 | 19 | 0 | 0.0% [0.0, 0.0] | 4 |
| Pro/zai-org/GLM-5.1 | matched_generic_state_observed | reevaluate | stable | 24 | 0 | 20 | 20 | 0 | 0.0% [0.0, 0.0] | 0 |

Mechanism errors are unauthorized rebinding in Preserve/Flip and premature locking in Reevaluate/Flip. The denominator includes only trajectories with an observed, correctly timed, correct binding and a completed refresh. Stable cells are negative controls. API and protocol errors are not counted as TRI evidence.
