# TRI-v2 Model Report

Rows: 20

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 10 | 40.0 | [16.8, 68.7] | 40.0 | 0.0 |
| Qwen3.5 | guarded_lifecycle_then_act | 10 | 80.0 | [49.0, 94.3] | 80.0 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | conditional | 10 | 40.0 | 40.0 | 0.0 |
| Qwen3.5 | guarded_lifecycle_then_act | conditional | 10 | 80.0 | 80.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | generic_structured_ledger_then_act | alias_collision | 1 |
| Qwen3.5 | generic_structured_ledger_then_act | other | 1 |
| Qwen3.5 | generic_structured_ledger_then_act | unnecessary_invalidation | 4 |
| Qwen3.5 | guarded_lifecycle_then_act | alias_collision | 1 |
| Qwen3.5 | guarded_lifecycle_then_act | other | 1 |
