# TRI-v2 Model Report

Rows: 80

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | 40 | 67.5 | [52.0, 79.9] | 67.5 | 0.0 |
| Qwen3.5 | sqlite_lifecycle_gated | 40 | 100.0 | [91.2, 100.0] | 100.0 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | anchored | 20 | 35.0 | 35.0 | 0.0 |
| Qwen3.5 | sqlite_generic_structured_ledger | dynamic | 20 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | sqlite_lifecycle_gated | anchored | 20 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | sqlite_lifecycle_gated | dynamic | 20 | 100.0 | 100.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | invalid_but_processed | 5 |
| Qwen3.5 | sqlite_generic_structured_ledger | temporal_rebinding | 8 |
