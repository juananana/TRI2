# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 80 | 20 | 46.2 | 46.2 | [32.5, 58.8] | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 80 | 20 | 82.5 | 82.5 | [72.5, 91.2] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 80 | 20 | 36.2 | [25.0, 47.5] |
