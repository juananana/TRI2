# ToolSandbox Single-Turn 2x2 Results

Rows: 8; tasks: 8; duplicate keys: 0.

| Model | Controller | Mode | Transition | N | API/protocol errors | Correct binding | Opportunities | Mechanism errors | Conditional rate (95% cluster CI) | Wrong writes |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.5-122B-A10B | full_history | preserve | flip | 2 | 0 | 1 | 1 | 0 | 0.0% (CI unavailable) | 0 |
| Qwen/Qwen3.5-122B-A10B | full_history | preserve | stable | 2 | 0 | 1 | 1 | 0 | 0.0% (CI unavailable) | 0 |
| Qwen/Qwen3.5-122B-A10B | full_history | reevaluate | flip | 2 | 0 | 1 | 1 | 0 | 0.0% (CI unavailable) | 1 |
| Qwen/Qwen3.5-122B-A10B | full_history | reevaluate | stable | 2 | 0 | 2 | 2 | 0 | 0.0% (CI unavailable) | 0 |

Mechanism errors are unauthorized rebinding in Preserve/Flip and premature locking in Reevaluate/Flip. The denominator includes only trajectories with an observed, correctly timed, correct binding and a completed refresh. Stable cells are negative controls. API and protocol errors are not counted as TRI evidence.
