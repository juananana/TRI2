# TRI-v2 Model Report

Rows: 960

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | 160 | 93.8 | [88.9, 96.6] | 93.8 | 0.0 |
| Qwen3.5 | factorized_schema_compile_then_act | 160 | 98.1 | [94.6, 99.4] | 98.1 | 0.0 |
| Qwen3.5 | full_history_once | 160 | 65.0 | [57.3, 72.0] | 65.0 | 0.0 |
| Qwen3.5 | generic_plan_then_act | 160 | 72.5 | [65.1, 78.8] | 72.5 | 0.0 |
| Qwen3.5 | schema_compile_then_act | 160 | 88.8 | [82.9, 92.8] | 88.8 | 0.0 |
| Qwen3.5 | state_overwrite_once | 160 | 60.6 | [52.9, 67.9] | 60.6 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | anchored | 80 | 87.5 | 87.5 | 0.0 |
| Qwen3.5 | compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | factorized_schema_compile_then_act | anchored | 80 | 96.2 | 96.2 | 0.0 |
| Qwen3.5 | factorized_schema_compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | full_history_once | anchored | 80 | 30.0 | 30.0 | 0.0 |
| Qwen3.5 | full_history_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | generic_plan_then_act | anchored | 80 | 46.2 | 46.2 | 0.0 |
| Qwen3.5 | generic_plan_then_act | dynamic | 80 | 98.8 | 98.8 | 0.0 |
| Qwen3.5 | schema_compile_then_act | anchored | 80 | 86.2 | 86.2 | 0.0 |
| Qwen3.5 | schema_compile_then_act | dynamic | 80 | 91.2 | 91.2 | 0.0 |
| Qwen3.5 | state_overwrite_once | anchored | 80 | 21.2 | 21.2 | 0.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | compile_then_act | invalid_but_processed | 8 |
| Qwen3.5 | compile_then_act | temporal_rebinding | 2 |
| Qwen3.5 | factorized_schema_compile_then_act | unnecessary_invalidation | 3 |
| Qwen3.5 | full_history_once | invalid_but_processed | 31 |
| Qwen3.5 | full_history_once | temporal_rebinding | 25 |
| Qwen3.5 | generic_plan_then_act | invalid_but_processed | 19 |
| Qwen3.5 | generic_plan_then_act | temporal_rebinding | 24 |
| Qwen3.5 | generic_plan_then_act | unnecessary_invalidation | 1 |
| Qwen3.5 | schema_compile_then_act | invalid_but_processed | 2 |
| Qwen3.5 | schema_compile_then_act | temporal_rebinding | 5 |
| Qwen3.5 | schema_compile_then_act | unnecessary_invalidation | 11 |
| Qwen3.5 | state_overwrite_once | invalid_but_processed | 31 |
| Qwen3.5 | state_overwrite_once | temporal_rebinding | 32 |
