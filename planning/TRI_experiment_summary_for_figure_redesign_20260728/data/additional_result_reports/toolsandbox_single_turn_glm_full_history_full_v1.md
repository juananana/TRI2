# ToolSandbox Single-Turn 2x2 Results

Rows: 96; tasks: 96; duplicate keys: 0.

| Model | Controller | Mode | Transition | N | API/protocol errors | Correct binding | Opportunities | Mechanism errors | Conditional rate (95% cluster CI) | Wrong writes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | full_history | preserve | flip | 24 | 2 | 20 | 20 | 0 | 0.0% [0.0, 0.0] | 1 |
| Pro/zai-org/GLM-5.1 | full_history | preserve | stable | 24 | 2 | 20 | 20 | 0 | 0.0% [0.0, 0.0] | 1 |
| Pro/zai-org/GLM-5.1 | full_history | reevaluate | flip | 24 | 0 | 16 | 16 | 0 | 0.0% [0.0, 0.0] | 8 |
| Pro/zai-org/GLM-5.1 | full_history | reevaluate | stable | 24 | 0 | 17 | 17 | 0 | 0.0% [0.0, 0.0] | 3 |

Mechanism errors are unauthorized rebinding in Preserve/Flip and premature locking in Reevaluate/Flip. The denominator includes only trajectories with an observed, correctly timed, correct binding and a completed refresh. Stable cells are negative controls. API and protocol errors are not counted as TRI evidence.
