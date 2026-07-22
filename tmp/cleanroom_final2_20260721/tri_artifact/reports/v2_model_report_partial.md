# TRI-v2 Model Report

Rows: 510

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. | 95% CI | API err. |
|---|---|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 160 | 89.4 | [83.6, 93.3] | 0.0 |
| GLM-5.1 | state_overwrite_once | 160 | 61.3 | [53.5, 68.5] | 0.0 |
| Qwen3.5 | compile_then_act | 30 | 66.7 | [48.8, 80.8] | 0.0 |
| Qwen3.5 | state_overwrite_once | 160 | 60.0 | [52.3, 67.3] | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. | API err. |
|---|---|---|---:|---:|---:|
| GLM-5.1 | compile_then_act | anchored | 80 | 78.8 | 0.0 |
| GLM-5.1 | compile_then_act | dynamic | 80 | 100.0 | 0.0 |
| GLM-5.1 | state_overwrite_once | anchored | 80 | 22.5 | 0.0 |
| GLM-5.1 | state_overwrite_once | dynamic | 80 | 100.0 | 0.0 |
| Qwen3.5 | compile_then_act | anchored | 20 | 50.0 | 0.0 |
| Qwen3.5 | compile_then_act | dynamic | 10 | 100.0 | 0.0 |
| Qwen3.5 | state_overwrite_once | anchored | 80 | 20.0 | 0.0 |
| Qwen3.5 | state_overwrite_once | dynamic | 80 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| GLM-5.1 | compile_then_act | invalid_but_processed | 16 |
| GLM-5.1 | compile_then_act | temporal_rebinding | 1 |
| GLM-5.1 | state_overwrite_once | invalid_but_processed | 31 |
| GLM-5.1 | state_overwrite_once | temporal_rebinding | 31 |
| Qwen3.5 | compile_then_act | invalid_but_processed | 6 |
| Qwen3.5 | compile_then_act | other | 1 |
| Qwen3.5 | compile_then_act | temporal_rebinding | 3 |
| Qwen3.5 | state_overwrite_once | invalid_but_processed | 32 |
| Qwen3.5 | state_overwrite_once | temporal_rebinding | 32 |
