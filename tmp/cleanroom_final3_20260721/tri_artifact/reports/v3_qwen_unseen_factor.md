# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | explicit | anchored | 20 | 70.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | explicit | dynamic | 20 | 95.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | implicit | anchored | 20 | 70.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | implicit | dynamic | 20 | 95.0 |
| Qwen3.5 | generic_structured_ledger_then_act | explicit | anchored | 20 | 35.0 |
| Qwen3.5 | generic_structured_ledger_then_act | explicit | dynamic | 20 | 70.0 |
| Qwen3.5 | generic_structured_ledger_then_act | implicit | anchored | 20 | 20.0 |
| Qwen3.5 | generic_structured_ledger_then_act | implicit | dynamic | 20 | 60.0 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_invalid | invalidate | 8 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_invalid | remove | 8 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | flip | 8 | 50.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | name_collision | 8 | 50.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | bound_valid | stable | 8 | 50.0 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_invalid | invalidate | 8 | 25.0 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_invalid | remove | 8 | 62.5 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | flip | 8 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | name_collision | 8 | 0.0 |
| Qwen3.5 | generic_structured_ledger_then_act | bound_valid | stable | 8 | 50.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 4 | 70.0 | 40.0 | 100.0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 4 | 95.0 | 90.0 | 100.0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 4 | 27.5 | 20.0 | 30.0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 4 | 65.0 | 30.0 | 100.0 |
