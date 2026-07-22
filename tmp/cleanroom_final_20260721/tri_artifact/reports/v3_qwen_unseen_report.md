# TRI-v2 Model Report

Rows: 160

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | 80 | 82.5 | [72.7, 89.3] | 82.5 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | 80 | 46.2 | [35.7, 57.1] | 46.2 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 40 | 70.0 | 70.0 | 0.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 40 | 95.0 | 95.0 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 40 | 27.5 | 27.5 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 40 | 65.0 | 65.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | other | 1 |
| Qwen3.5 | factorized_hybrid_compile_then_act | unnecessary_invalidation | 13 |
| Qwen3.5 | generic_structured_ledger_then_act | invalid_but_processed | 9 |
| Qwen3.5 | generic_structured_ledger_then_act | temporal_rebinding | 9 |
| Qwen3.5 | generic_structured_ledger_then_act | unnecessary_invalidation | 25 |
