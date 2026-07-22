# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 20 | 64.4 | 64.4 | [49.4, 78.8] | 0 |
| Qwen3.5 | generic_ledger_tri_reminder_actor | 160 | 20 | 58.8 | 58.8 | [46.9, 70.0] | 0 |
| Qwen3.5 | generic_ledger_action_time_semantic_gate | 160 | 20 | 68.1 | 68.1 | [51.2, 83.8] | 0 |
| Qwen3.5 | factorized_schema_compile_then_act | 160 | 20 | 96.9 | 96.9 | [93.8, 99.4] | 0 |

## Binding Slices

| Model | Controller | Binding | Tasks | Task Acc. |
|---|---|---|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 80 | 33.8 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 80 | 95.0 |
| Qwen3.5 | generic_ledger_tri_reminder_actor | anchored | 80 | 77.5 |
| Qwen3.5 | generic_ledger_tri_reminder_actor | dynamic | 80 | 40.0 |
| Qwen3.5 | generic_ledger_action_time_semantic_gate | anchored | 80 | 37.5 |
| Qwen3.5 | generic_ledger_action_time_semantic_gate | dynamic | 80 | 98.8 |
| Qwen3.5 | factorized_schema_compile_then_act | anchored | 80 | 97.5 |
| Qwen3.5 | factorized_schema_compile_then_act | dynamic | 80 | 96.2 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI | B win / tie / A win |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 generic_ledger_tri_reminder_actor | 160 | 20 | -5.6 | [-30.0, 18.8] | 9 / 0 / 11 |
| Qwen3.5 generic_ledger_tri_reminder_actor | Qwen3.5 factorized_schema_compile_then_act | 160 | 20 | 38.1 | [27.5, 49.4] | 18 / 2 / 0 |
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 generic_ledger_action_time_semantic_gate | 160 | 20 | 3.8 | [-0.6, 8.8] | 6 / 12 / 2 |
| Qwen3.5 generic_ledger_action_time_semantic_gate | Qwen3.5 factorized_schema_compile_then_act | 160 | 20 | 28.7 | [12.5, 45.6] | 9 / 9 / 2 |
