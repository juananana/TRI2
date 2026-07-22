# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 20 | 71.9 | 71.9 | [61.9, 81.9] | 0 |
| GLM-5.1 | generic_validity_gated_ledger_then_act | 160 | 20 | 73.1 | 73.1 | [62.5, 83.1] | 0 |
| GLM-5.1 | factorized_schema_compile_then_act | 160 | 20 | 98.1 | 98.1 | [96.2, 100.0] | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 160 | 20 | 100.0 | 100.0 | [100.0, 100.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| GLM-5.1 generic_structured_ledger_then_act | GLM-5.1 generic_validity_gated_ledger_then_act | 160 | 20 | 1.2 | [0.0, 3.8] |
| GLM-5.1 generic_validity_gated_ledger_then_act | GLM-5.1 factorized_schema_compile_then_act | 160 | 20 | 25.0 | [15.6, 35.0] |
| GLM-5.1 factorized_schema_compile_then_act | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 20 | 1.9 | [0.0, 3.8] |
