# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 20 | 64.4 | 64.4 | [49.4, 78.8] | 0 |
| Qwen3.5 | generic_validity_gated_ledger_then_act | 160 | 20 | 65.0 | 65.0 | [49.4, 79.4] | 0 |
| Qwen3.5 | factorized_schema_compile_then_act | 160 | 20 | 96.9 | 96.9 | [93.8, 99.4] | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 20 | 98.1 | 98.1 | [95.0, 100.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 generic_validity_gated_ledger_then_act | 160 | 20 | 0.6 | [0.0, 1.9] |
| Qwen3.5 generic_validity_gated_ledger_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 20 | 31.9 | [17.5, 47.5] |
| Qwen3.5 factorized_schema_compile_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 20 | 1.2 | [0.0, 3.1] |
