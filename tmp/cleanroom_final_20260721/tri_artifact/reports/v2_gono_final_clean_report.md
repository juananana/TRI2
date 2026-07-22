# TRI-v2 Model Report

Rows: 800

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 160 | 89.4 | [83.6, 93.3] | 89.4 | 0.0 |
| GLM-5.1 | full_history_once | 160 | 76.2 | [69.1, 82.2] | 76.2 | 0.0 |
| GLM-5.1 | generic_plan_then_act | 160 | 78.1 | [71.1, 83.8] | 78.1 | 0.0 |
| GLM-5.1 | schema_compile_then_act | 160 | 95.0 | [90.4, 97.4] | 95.0 | 0.0 |
| GLM-5.1 | state_overwrite_once | 160 | 60.6 | [52.9, 67.9] | 60.6 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | anchored | 80 | 78.8 | 78.8 | 0.0 |
| GLM-5.1 | compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | full_history_once | anchored | 80 | 52.5 | 52.5 | 0.0 |
| GLM-5.1 | full_history_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | generic_plan_then_act | anchored | 80 | 56.2 | 56.2 | 0.0 |
| GLM-5.1 | generic_plan_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | schema_compile_then_act | anchored | 80 | 90.0 | 90.0 | 0.0 |
| GLM-5.1 | schema_compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | state_overwrite_once | anchored | 80 | 21.2 | 21.2 | 0.0 |
| GLM-5.1 | state_overwrite_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| GLM-5.1 | compile_then_act | invalid_but_processed | 17 |
| GLM-5.1 | full_history_once | invalid_but_processed | 23 |
| GLM-5.1 | full_history_once | temporal_rebinding | 15 |
| GLM-5.1 | generic_plan_then_act | invalid_but_processed | 19 |
| GLM-5.1 | generic_plan_then_act | temporal_rebinding | 16 |
| GLM-5.1 | schema_compile_then_act | invalid_but_processed | 8 |
| GLM-5.1 | state_overwrite_once | invalid_but_processed | 32 |
| GLM-5.1 | state_overwrite_once | temporal_rebinding | 31 |
