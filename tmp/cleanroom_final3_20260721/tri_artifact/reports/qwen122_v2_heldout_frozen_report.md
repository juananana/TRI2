# TRI-v2 Model Report

Rows: 800

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | 160 | 96.2 | [92.1, 98.3] | 96.2 | 0.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 95.0 | [90.4, 97.4] | 95.0 | 0.0 |
| Qwen3.5 | full_history_once | 160 | 60.6 | [52.9, 67.9] | 60.6 | 0.0 |
| Qwen3.5 | generic_plan_then_act | 160 | 78.1 | [71.1, 83.8] | 78.1 | 0.0 |
| Qwen3.5 | state_overwrite_once | 160 | 60.6 | [52.9, 67.9] | 60.6 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | anchored | 80 | 92.5 | 92.5 | 0.0 |
| Qwen3.5 | compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 80 | 90.0 | 90.0 | 0.0 |
| Qwen3.5 | full_history_once | anchored | 80 | 21.2 | 21.2 | 0.0 |
| Qwen3.5 | full_history_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | generic_plan_then_act | anchored | 80 | 58.8 | 58.8 | 0.0 |
| Qwen3.5 | generic_plan_then_act | dynamic | 80 | 97.5 | 97.5 | 0.0 |
| Qwen3.5 | state_overwrite_once | anchored | 80 | 21.2 | 21.2 | 0.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | compile_then_act | invalid_but_processed | 5 |
| Qwen3.5 | compile_then_act | unnecessary_invalidation | 1 |
| Qwen3.5 | factorized_hybrid_compile_then_act | premature_binding | 4 |
| Qwen3.5 | factorized_hybrid_compile_then_act | unnecessary_invalidation | 4 |
| Qwen3.5 | full_history_once | invalid_but_processed | 31 |
| Qwen3.5 | full_history_once | temporal_rebinding | 32 |
| Qwen3.5 | generic_plan_then_act | invalid_but_processed | 9 |
| Qwen3.5 | generic_plan_then_act | temporal_rebinding | 21 |
| Qwen3.5 | generic_plan_then_act | unnecessary_invalidation | 5 |
| Qwen3.5 | state_overwrite_once | invalid_but_processed | 31 |
| Qwen3.5 | state_overwrite_once | temporal_rebinding | 32 |
