# TRI-v2 Model Report

Rows: 320

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | 160 | 100.0 | [97.7, 100.0] | 100.0 | 0.0 |
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 71.9 | [64.5, 78.3] | 71.9 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | anchored | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | dynamic | 80 | 100.0 | 100.0 | 0.0 |
| GLM-5.1 | generic_structured_ledger_then_act | anchored | 80 | 56.2 | 56.2 | 0.0 |
| GLM-5.1 | generic_structured_ledger_then_act | dynamic | 80 | 87.5 | 87.5 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| GLM-5.1 | generic_structured_ledger_then_act | invalid_but_processed | 10 |
| GLM-5.1 | generic_structured_ledger_then_act | temporal_rebinding | 10 |
| GLM-5.1 | generic_structured_ledger_then_act | unnecessary_invalidation | 25 |
