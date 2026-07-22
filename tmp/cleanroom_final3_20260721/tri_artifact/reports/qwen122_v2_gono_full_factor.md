# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | compile_then_act | explicit | anchored | 40 | 90.0 |
| Qwen3.5 | compile_then_act | explicit | dynamic | 40 | 100.0 |
| Qwen3.5 | compile_then_act | implicit | anchored | 40 | 85.0 |
| Qwen3.5 | compile_then_act | implicit | dynamic | 40 | 100.0 |
| Qwen3.5 | full_history_once | explicit | anchored | 40 | 40.0 |
| Qwen3.5 | full_history_once | explicit | dynamic | 40 | 100.0 |
| Qwen3.5 | full_history_once | implicit | anchored | 40 | 20.0 |
| Qwen3.5 | full_history_once | implicit | dynamic | 40 | 100.0 |
| Qwen3.5 | generic_plan_then_act | explicit | anchored | 40 | 67.5 |
| Qwen3.5 | generic_plan_then_act | explicit | dynamic | 40 | 97.5 |
| Qwen3.5 | generic_plan_then_act | implicit | anchored | 40 | 25.0 |
| Qwen3.5 | generic_plan_then_act | implicit | dynamic | 40 | 100.0 |
| Qwen3.5 | schema_compile_then_act | explicit | anchored | 40 | 95.0 |
| Qwen3.5 | schema_compile_then_act | explicit | dynamic | 40 | 82.5 |
| Qwen3.5 | schema_compile_then_act | implicit | anchored | 40 | 77.5 |
| Qwen3.5 | schema_compile_then_act | implicit | dynamic | 40 | 100.0 |
| Qwen3.5 | state_overwrite_once | explicit | anchored | 40 | 22.5 |
| Qwen3.5 | state_overwrite_once | explicit | dynamic | 40 | 100.0 |
| Qwen3.5 | state_overwrite_once | implicit | anchored | 40 | 20.0 |
| Qwen3.5 | state_overwrite_once | implicit | dynamic | 40 | 100.0 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | compile_then_act | bound_invalid | invalidate | 16 | 56.2 |
| Qwen3.5 | compile_then_act | bound_invalid | remove | 16 | 93.8 |
| Qwen3.5 | compile_then_act | bound_valid | flip | 16 | 93.8 |
| Qwen3.5 | compile_then_act | bound_valid | name_collision | 16 | 93.8 |
| Qwen3.5 | compile_then_act | bound_valid | stable | 16 | 100.0 |
| Qwen3.5 | full_history_once | bound_invalid | invalidate | 16 | 0.0 |
| Qwen3.5 | full_history_once | bound_invalid | remove | 16 | 6.2 |
| Qwen3.5 | full_history_once | bound_valid | flip | 16 | 18.8 |
| Qwen3.5 | full_history_once | bound_valid | name_collision | 16 | 25.0 |
| Qwen3.5 | full_history_once | bound_valid | stable | 16 | 100.0 |
| Qwen3.5 | generic_plan_then_act | bound_invalid | invalidate | 16 | 25.0 |
| Qwen3.5 | generic_plan_then_act | bound_invalid | remove | 16 | 56.2 |
| Qwen3.5 | generic_plan_then_act | bound_valid | flip | 16 | 25.0 |
| Qwen3.5 | generic_plan_then_act | bound_valid | name_collision | 16 | 25.0 |
| Qwen3.5 | generic_plan_then_act | bound_valid | stable | 16 | 100.0 |
| Qwen3.5 | schema_compile_then_act | bound_invalid | invalidate | 16 | 93.8 |
| Qwen3.5 | schema_compile_then_act | bound_invalid | remove | 16 | 93.8 |
| Qwen3.5 | schema_compile_then_act | bound_valid | flip | 16 | 62.5 |
| Qwen3.5 | schema_compile_then_act | bound_valid | name_collision | 16 | 81.2 |
| Qwen3.5 | schema_compile_then_act | bound_valid | stable | 16 | 100.0 |
| Qwen3.5 | state_overwrite_once | bound_invalid | invalidate | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_invalid | remove | 16 | 6.2 |
| Qwen3.5 | state_overwrite_once | bound_valid | flip | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_valid | name_collision | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_valid | stable | 16 | 100.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | anchored | 8 | 87.5 | 60.0 | 100.0 |
| Qwen3.5 | compile_then_act | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| Qwen3.5 | full_history_once | anchored | 8 | 30.0 | 20.0 | 40.0 |
| Qwen3.5 | full_history_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| Qwen3.5 | generic_plan_then_act | anchored | 8 | 46.2 | 30.0 | 60.0 |
| Qwen3.5 | generic_plan_then_act | dynamic | 8 | 98.8 | 90.0 | 100.0 |
| Qwen3.5 | schema_compile_then_act | anchored | 8 | 86.2 | 60.0 | 100.0 |
| Qwen3.5 | schema_compile_then_act | dynamic | 8 | 91.2 | 80.0 | 100.0 |
| Qwen3.5 | state_overwrite_once | anchored | 8 | 21.3 | 20.0 | 30.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
