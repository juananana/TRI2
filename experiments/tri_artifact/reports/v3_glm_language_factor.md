# TRI-v2 Factor Report

## Explicit vs Implicit

| Model | Mode | Phenomenon | Binding | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | explicit | anchored | 40 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | explicit | dynamic | 40 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | implicit | anchored | 40 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | implicit | dynamic | 40 | 100.0 |
| GLM-5.1 | generic_structured_ledger_then_act | explicit | anchored | 40 | 70.0 |
| GLM-5.1 | generic_structured_ledger_then_act | explicit | dynamic | 40 | 92.5 |
| GLM-5.1 | generic_structured_ledger_then_act | implicit | anchored | 40 | 42.5 |
| GLM-5.1 | generic_structured_ledger_then_act | implicit | dynamic | 40 | 82.5 |

## Validity Gap for Anchored Cases

| Model | Mode | Bound status | Update | n | Acc. |
|---|---|---|---|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | bound_invalid | invalidate | 16 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | bound_invalid | remove | 16 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | bound_valid | flip | 16 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | bound_valid | name_collision | 16 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | bound_valid | stable | 16 | 100.0 |
| GLM-5.1 | generic_structured_ledger_then_act | bound_invalid | invalidate | 16 | 87.5 |
| GLM-5.1 | generic_structured_ledger_then_act | bound_invalid | remove | 16 | 50.0 |
| GLM-5.1 | generic_structured_ledger_then_act | bound_valid | flip | 16 | 18.8 |
| GLM-5.1 | generic_structured_ledger_then_act | bound_valid | name_collision | 16 | 25.0 |
| GLM-5.1 | generic_structured_ledger_then_act | bound_valid | stable | 16 | 100.0 |

## Domain Macro Accuracy

| Model | Mode | Binding | Domains | Macro Acc. | Min | Max |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | anchored | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | dynamic | 8 | 100.0 | 100.0 | 100.0 |
| GLM-5.1 | generic_structured_ledger_then_act | anchored | 8 | 56.2 | 40.0 | 70.0 |
| GLM-5.1 | generic_structured_ledger_then_act | dynamic | 8 | 87.5 | 70.0 | 100.0 |
