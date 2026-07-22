# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | explicit | anchored | 40 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | explicit | dynamic | 40 | 97.5 |
| Qwen3.5 | factorized_hybrid_compile_then_act | implicit | anchored | 40 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | implicit | dynamic | 40 | 95.0 |
| Qwen3.5 | generic_structured_ledger_then_act | explicit | anchored | 40 | 45.0 |
| Qwen3.5 | generic_structured_ledger_then_act | explicit | dynamic | 40 | 97.5 |
| Qwen3.5 | generic_structured_ledger_then_act | implicit | anchored | 40 | 22.5 |
| Qwen3.5 | generic_structured_ledger_then_act | implicit | dynamic | 40 | 92.5 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_invalid | invalidate | 16 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_invalid | remove | 16 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | flip | 16 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | name_collision | 16 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | stable | 16 | 100.0 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_invalid | invalidate | 16 | 12.5 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_invalid | remove | 16 | 37.5 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | flip | 16 | 6.2 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | name_collision | 16 | 12.5 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | stable | 16 | 100.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 8 | 100.0 | 100.0 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 8 | 96.2 | 80.0 | 100.0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 8 | 33.8 | 20.0 | 50.0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 8 | 95.0 | 80.0 | 100.0 |
