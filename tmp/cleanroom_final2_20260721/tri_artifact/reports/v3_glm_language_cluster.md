# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 20 | 71.9 | 71.9 | [61.9, 81.9] | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 160 | 20 | 100.0 | 100.0 | [100.0, 100.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| GLM-5.1 generic_structured_ledger_then_act | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 20 | 28.1 | [18.1, 38.1] |
