# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 20 | 64.4 | 64.4 | [49.4, 78.8] | 0 |
| Qwen3.5 | pre_refresh_untyped_compile_then_act | 160 | 20 | 81.2 | 81.2 | [71.9, 90.0] | 0 |
| Qwen3.5 | factorized_schema_compile_then_act | 160 | 20 | 96.9 | 96.9 | [93.8, 99.4] | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 20 | 71.9 | 71.9 | [61.9, 81.9] | 0 |
| GLM-5.1 | pre_refresh_untyped_compile_then_act | 160 | 20 | 70.6 | 70.6 | [56.2, 84.4] | 0 |
| GLM-5.1 | factorized_schema_compile_then_act | 160 | 20 | 98.1 | 98.1 | [96.2, 100.0] | 0 |

## Binding Slices

| Model | Controller | Binding | Tasks | Task Acc. |
|---|---|---|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 80 | 33.8 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 80 | 95.0 |
| Qwen3.5 | pre_refresh_untyped_compile_then_act | anchored | 80 | 71.2 |
| Qwen3.5 | pre_refresh_untyped_compile_then_act | dynamic | 80 | 91.2 |
| Qwen3.5 | factorized_schema_compile_then_act | anchored | 80 | 97.5 |
| Qwen3.5 | factorized_schema_compile_then_act | dynamic | 80 | 96.2 |
| GLM-5.1 | generic_structured_ledger_then_act | anchored | 80 | 56.2 |
| GLM-5.1 | generic_structured_ledger_then_act | dynamic | 80 | 87.5 |
| GLM-5.1 | pre_refresh_untyped_compile_then_act | anchored | 80 | 42.5 |
| GLM-5.1 | pre_refresh_untyped_compile_then_act | dynamic | 80 | 98.8 |
| GLM-5.1 | factorized_schema_compile_then_act | anchored | 80 | 96.2 |
| GLM-5.1 | factorized_schema_compile_then_act | dynamic | 80 | 100.0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI | B win / tie / A win |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 pre_refresh_untyped_compile_then_act | 160 | 20 | 16.9 | [5.0, 29.4] | 12 / 4 / 4 |
| Qwen3.5 pre_refresh_untyped_compile_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 20 | 15.6 | [7.5, 25.0] | 13 / 6 / 1 |
| GLM-5.1 generic_structured_ledger_then_act | GLM-5.1 pre_refresh_untyped_compile_then_act | 160 | 20 | -1.2 | [-8.8, 6.3] | 7 / 6 / 7 |
| GLM-5.1 pre_refresh_untyped_compile_then_act | GLM-5.1 factorized_schema_compile_then_act | 160 | 20 | 27.5 | [15.0, 41.2] | 11 / 9 / 0 |
