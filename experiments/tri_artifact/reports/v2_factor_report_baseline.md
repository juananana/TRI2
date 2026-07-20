# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | compile_then_act | explicit | anchored | 40 | 80.0 |
| GLM-5.1 | compile_then_act | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | compile_then_act | implicit | anchored | 40 | 77.5 |
| GLM-5.1 | compile_then_act | implicit | dynamic | 40 | 100.0 |
| GLM-5.1 | state_overwrite_once | explicit | anchored | 40 | 22.5 |
| GLM-5.1 | state_overwrite_once | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | state_overwrite_once | implicit | anchored | 40 | 22.5 |
| GLM-5.1 | state_overwrite_once | implicit | dynamic | 40 | 100.0 |
| MiniMax | compile_then_act | explicit | anchored | 40 | 0.0 |
| MiniMax | compile_then_act | explicit | dynamic | 40 | 0.0 |
| MiniMax | compile_then_act | implicit | anchored | 40 | 0.0 |
| MiniMax | compile_then_act | implicit | dynamic | 40 | 0.0 |
| MiniMax | state_overwrite_once | explicit | anchored | 40 | 0.0 |
| MiniMax | state_overwrite_once | explicit | dynamic | 40 | 0.0 |
| MiniMax | state_overwrite_once | implicit | anchored | 40 | 0.0 |
| MiniMax | state_overwrite_once | implicit | dynamic | 40 | 0.0 |
| Qwen3.5 | compile_then_act | explicit | anchored | 40 | 60.0 |
| Qwen3.5 | compile_then_act | explicit | dynamic | 40 | 72.5 |
| Qwen3.5 | compile_then_act | implicit | anchored | 40 | 20.0 |
| Qwen3.5 | compile_then_act | implicit | dynamic | 40 | 62.5 |
| Qwen3.5 | state_overwrite_once | explicit | anchored | 40 | 20.0 |
| Qwen3.5 | state_overwrite_once | explicit | dynamic | 40 | 100.0 |
| Qwen3.5 | state_overwrite_once | implicit | anchored | 40 | 20.0 |
| Qwen3.5 | state_overwrite_once | implicit | dynamic | 40 | 100.0 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | compile_then_act | bound_invalid | invalidate | 16 | 0.0 |
| GLM-5.1 | compile_then_act | bound_invalid | remove | 16 | 100.0 |
| GLM-5.1 | compile_then_act | bound_valid | flip | 16 | 93.8 |
| GLM-5.1 | compile_then_act | bound_valid | name_collision | 16 | 100.0 |
| GLM-5.1 | compile_then_act | bound_valid | stable | 16 | 100.0 |
| GLM-5.1 | state_overwrite_once | bound_invalid | invalidate | 16 | 0.0 |
| GLM-5.1 | state_overwrite_once | bound_invalid | remove | 16 | 6.2 |
| GLM-5.1 | state_overwrite_once | bound_valid | flip | 16 | 6.2 |
| GLM-5.1 | state_overwrite_once | bound_valid | name_collision | 16 | 0.0 |
| GLM-5.1 | state_overwrite_once | bound_valid | stable | 16 | 100.0 |
| MiniMax | compile_then_act | bound_invalid | invalidate | 16 | 0.0 |
| MiniMax | compile_then_act | bound_invalid | remove | 16 | 0.0 |
| MiniMax | compile_then_act | bound_valid | flip | 16 | 0.0 |
| MiniMax | compile_then_act | bound_valid | name_collision | 16 | 0.0 |
| MiniMax | compile_then_act | bound_valid | stable | 16 | 0.0 |
| MiniMax | state_overwrite_once | bound_invalid | invalidate | 16 | 0.0 |
| MiniMax | state_overwrite_once | bound_invalid | remove | 16 | 0.0 |
| MiniMax | state_overwrite_once | bound_valid | flip | 16 | 0.0 |
| MiniMax | state_overwrite_once | bound_valid | name_collision | 16 | 0.0 |
| MiniMax | state_overwrite_once | bound_valid | stable | 16 | 0.0 |
| Qwen3.5 | compile_then_act | bound_invalid | invalidate | 16 | 0.0 |
| Qwen3.5 | compile_then_act | bound_invalid | remove | 16 | 50.0 |
| Qwen3.5 | compile_then_act | bound_valid | flip | 16 | 43.8 |
| Qwen3.5 | compile_then_act | bound_valid | name_collision | 16 | 43.8 |
| Qwen3.5 | compile_then_act | bound_valid | stable | 16 | 62.5 |
| Qwen3.5 | state_overwrite_once | bound_invalid | invalidate | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_invalid | remove | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_valid | flip | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_valid | name_collision | 16 | 0.0 |
| Qwen3.5 | state_overwrite_once | bound_valid | stable | 16 | 100.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | anchored | 8 | 78.8 | 70.0 | 80.0 |
| GLM-5.1 | compile_then_act | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | state_overwrite_once | anchored | 8 | 22.5 | 20.0 | 40.0 |
| GLM-5.1 | state_overwrite_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| MiniMax | compile_then_act | anchored | 8 | 0.0 | 0.0 | 0.0 |
| MiniMax | compile_then_act | dynamic | 8 | 0.0 | 0.0 | 0.0 |
| MiniMax | state_overwrite_once | anchored | 8 | 0.0 | 0.0 | 0.0 |
| MiniMax | state_overwrite_once | dynamic | 8 | 0.0 | 0.0 | 0.0 |
| Qwen3.5 | compile_then_act | anchored | 8 | 40.0 | 0.0 | 70.0 |
| Qwen3.5 | compile_then_act | dynamic | 8 | 67.5 | 0.0 | 100.0 |
| Qwen3.5 | state_overwrite_once | anchored | 8 | 20.0 | 20.0 | 20.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 8 | 100.0 | 100.0 | 100.0 |
