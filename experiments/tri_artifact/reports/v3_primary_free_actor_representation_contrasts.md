# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 20 | 64.4 | 64.4 | [49.4, 78.8] | 0 |
| Qwen3.5 | factorized_schema_compile_then_act | 160 | 20 | 96.9 | 96.9 | [93.8, 99.4] | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 20 | 71.9 | 71.9 | [61.9, 81.9] | 0 |
| GLM-5.1 | factorized_schema_compile_then_act | 160 | 20 | 98.1 | 98.1 | [96.2, 100.0] | 0 |

## Binding Slices

| Model | Controller | Binding | Tasks | Task Acc. |
|---|---|---|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 80 | 33.8 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 80 | 95.0 |
| Qwen3.5 | factorized_schema_compile_then_act | anchored | 80 | 97.5 |
| Qwen3.5 | factorized_schema_compile_then_act | dynamic | 80 | 96.2 |
| GLM-5.1 | generic_structured_ledger_then_act | anchored | 80 | 56.2 |
| GLM-5.1 | generic_structured_ledger_then_act | dynamic | 80 | 87.5 |
| GLM-5.1 | factorized_schema_compile_then_act | anchored | 80 | 96.2 |
| GLM-5.1 | factorized_schema_compile_then_act | dynamic | 80 | 100.0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI | B win / tie / A win |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 20 | 32.5 | [17.5, 48.1] | 12 / 7 / 1 |
| GLM-5.1 generic_structured_ledger_then_act | GLM-5.1 factorized_schema_compile_then_act | 160 | 20 | 26.2 | [17.5, 35.6] | 16 / 4 / 0 |
