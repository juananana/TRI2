# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | full_history_once | explicit | anchored | 40 | 82.5 |
| GLM-5.1 | full_history_once | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | full_history_once | implicit | anchored | 40 | 22.5 |
| GLM-5.1 | full_history_once | implicit | dynamic | 40 | 100.0 |
| GLM-5.1 | generic_plan_then_act | explicit | anchored | 40 | 92.5 |
| GLM-5.1 | generic_plan_then_act | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | generic_plan_then_act | implicit | anchored | 40 | 20.0 |
| GLM-5.1 | generic_plan_then_act | implicit | dynamic | 40 | 100.0 |
| GLM-5.1 | schema_compile_then_act | explicit | anchored | 40 | 100.0 |
| GLM-5.1 | schema_compile_then_act | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | schema_compile_then_act | implicit | anchored | 40 | 80.0 |
| GLM-5.1 | schema_compile_then_act | implicit | dynamic | 40 | 100.0 |
| GLM-5.1 | state_overwrite_once | explicit | anchored | 40 | 22.5 |
| GLM-5.1 | state_overwrite_once | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | state_overwrite_once | implicit | anchored | 40 | 20.0 |
| GLM-5.1 | state_overwrite_once | implicit | dynamic | 40 | 100.0 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | full_history_once | bound_invalid | invalidate | 16 | 6.2 |
| GLM-5.1 | full_history_once | bound_invalid | remove | 16 | 50.0 |
| GLM-5.1 | full_history_once | bound_valid | flip | 16 | 56.2 |
| GLM-5.1 | full_history_once | bound_valid | name_collision | 16 | 50.0 |
| GLM-5.1 | full_history_once | bound_valid | stable | 16 | 100.0 |
| GLM-5.1 | generic_plan_then_act | bound_invalid | invalidate | 16 | 37.5 |
| GLM-5.1 | generic_plan_then_act | bound_invalid | remove | 16 | 43.8 |
| GLM-5.1 | generic_plan_then_act | bound_valid | flip | 16 | 50.0 |
| GLM-5.1 | generic_plan_then_act | bound_valid | name_collision | 16 | 50.0 |
| GLM-5.1 | generic_plan_then_act | bound_valid | stable | 16 | 100.0 |
| GLM-5.1 | schema_compile_then_act | bound_invalid | invalidate | 16 | 75.0 |
| GLM-5.1 | schema_compile_then_act | bound_invalid | remove | 16 | 75.0 |
| GLM-5.1 | schema_compile_then_act | bound_valid | flip | 16 | 100.0 |
| GLM-5.1 | schema_compile_then_act | bound_valid | name_collision | 16 | 100.0 |
| GLM-5.1 | schema_compile_then_act | bound_valid | stable | 16 | 100.0 |
| GLM-5.1 | state_overwrite_once | bound_invalid | invalidate | 16 | 0.0 |
| GLM-5.1 | state_overwrite_once | bound_invalid | remove | 16 | 0.0 |
| GLM-5.1 | state_overwrite_once | bound_valid | flip | 16 | 6.2 |
| GLM-5.1 | state_overwrite_once | bound_valid | name_collision | 16 | 0.0 |
| GLM-5.1 | state_overwrite_once | bound_valid | stable | 16 | 100.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | full_history_once | anchored | 8 | 52.5 | 50.0 | 70.0 |
| GLM-5.1 | full_history_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | generic_plan_then_act | anchored | 8 | 56.2 | 50.0 | 60.0 |
| GLM-5.1 | generic_plan_then_act | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | schema_compile_then_act | anchored | 8 | 90.0 | 80.0 | 100.0 |
| GLM-5.1 | schema_compile_then_act | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | state_overwrite_once | anchored | 8 | 21.3 | 20.0 | 30.0 |
| GLM-5.1 | state_overwrite_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
