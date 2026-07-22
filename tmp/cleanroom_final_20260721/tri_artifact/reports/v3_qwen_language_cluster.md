# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 20 | 64.4 | 64.4 | [49.4, 78.8] | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 20 | 98.1 | 98.1 | [95.0, 100.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 20 | 33.8 | [18.1, 50.0] |
