# TRI-v2 Model Report

Rows: 960

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 160 | 89.4 | [83.6, 93.3] | 89.4 | 0.0 |
| GLM-5.1 | state_overwrite_once | 160 | 61.3 | [53.5, 68.5] | 61.3 | 0.0 |
| MiniMax | compile_then_act | 160 | 0.0 | [0.0, 2.3] | NA | 100.0 |
| MiniMax | state_overwrite_once | 160 | 0.0 | [0.0, 2.3] | NA | 100.0 |
| Qwen3.5 | compile_then_act | 160 | 53.8 | [46.0, 61.3] | 79.6 | 32.5 |
| Qwen3.5 | state_overwrite_once | 160 | 60.0 | [52.3, 67.3] | 60.0 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | anchored | 80 | 78.8 | 78.8 | 0.0 |
| GLM-5.1 | compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | state_overwrite_once | anchored | 80 | 22.5 | 22.5 | 0.0 |
| GLM-5.1 | state_overwrite_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| MiniMax | compile_then_act | anchored | 80 | 0.0 | NA | 100.0 |
| MiniMax | compile_then_act | dynamic | 80 | 0.0 | NA | 100.0 |
| MiniMax | state_overwrite_once | anchored | 80 | 0.0 | NA | 100.0 |
| MiniMax | state_overwrite_once | dynamic | 80 | 0.0 | NA | 100.0 |
| Qwen3.5 | compile_then_act | anchored | 80 | 40.0 | 59.3 | 32.5 |
| Qwen3.5 | compile_then_act | dynamic | 80 | 67.5 | 100.0 | 32.5 |
| Qwen3.5 | state_overwrite_once | anchored | 80 | 20.0 | 20.0 | 0.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 80 | 100.0 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| GLM-5.1 | compile_then_act | invalid_but_processed | 16 |
| GLM-5.1 | compile_then_act | temporal_rebinding | 1 |
| GLM-5.1 | state_overwrite_once | invalid_but_processed | 31 |
| GLM-5.1 | state_overwrite_once | temporal_rebinding | 31 |
| MiniMax | compile_then_act | api_error | 160 |
| MiniMax | state_overwrite_once | api_error | 160 |
| Qwen3.5 | compile_then_act | api_error | 52 |
| Qwen3.5 | compile_then_act | invalid_but_processed | 14 |
| Qwen3.5 | compile_then_act | temporal_rebinding | 8 |
| Qwen3.5 | state_overwrite_once | invalid_but_processed | 32 |
| Qwen3.5 | state_overwrite_once | temporal_rebinding | 32 |
