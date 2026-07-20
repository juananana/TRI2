# TRI-v2 Model Report

Rows: 320

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 98.1 | [94.6, 99.4] | 98.1 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 64.4 | [56.7, 71.4] | 64.4 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 80 | 100.0 | 100.0 | 0.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 80 | 96.2 | 96.2 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 80 | 33.8 | 33.8 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 80 | 95.0 | 95.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | unnecessary_invalidation | 3 |
| Qwen3.5 | generic_structured_ledger_then_act | invalid_but_processed | 24 |
| Qwen3.5 | generic_structured_ledger_then_act | temporal_rebinding | 29 |
| Qwen3.5 | generic_structured_ledger_then_act | unnecessary_invalidation | 4 |
