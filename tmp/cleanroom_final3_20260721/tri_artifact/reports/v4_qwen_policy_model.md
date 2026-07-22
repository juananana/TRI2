# TRI-v2 Model Report

Rows: 80

Accuracy counts API errors as failures.

## Overall

| Model | Mode | n | Acc. all | 95% CI | Completed acc. | API err. |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 40 | 52.5 | [37.5, 67.1] | 52.5 | 0.0 |
| Qwen3.5 | guarded_lifecycle_then_act | 40 | 85.0 | [70.9, 92.9] | 85.0 | 0.0 |

## By Binding

| Model | Mode | Binding | n | Acc. all | Completed acc. | API err. |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | conditional | 40 | 52.5 | 52.5 | 0.0 |
| Qwen3.5 | guarded_lifecycle_then_act | conditional | 40 | 85.0 | 85.0 | 0.0 |

## Error Counts

| Model | Mode | Error | Count |
|---|---|---|---:|
| Qwen3.5 | generic_structured_ledger_then_act | alias_collision | 3 |
| Qwen3.5 | generic_structured_ledger_then_act | other | 3 |
| Qwen3.5 | generic_structured_ledger_then_act | unnecessary_invalidation | 13 |
| Qwen3.5 | guarded_lifecycle_then_act | alias_collision | 3 |
| Qwen3.5 | guarded_lifecycle_then_act | other | 3 |
