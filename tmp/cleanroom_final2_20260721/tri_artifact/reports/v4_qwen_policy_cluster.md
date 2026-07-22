# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 40 | 10 | 52.5 | 52.5 | [37.5, 65.0] | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | 40 | 10 | 85.0 | 85.0 | [75.0, 95.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| Qwen3.5 generic_structured_ledger_then_act | Qwen3.5 guarded_lifecycle_then_act | 40 | 10 | 32.5 | [15.0, 52.5] |
