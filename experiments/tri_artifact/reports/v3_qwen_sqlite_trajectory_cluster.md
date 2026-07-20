# TRI-v3 Cluster-Aware Report

Cluster bootstrap samples: 10000; seed: 20260717.

## Controllers

| Model | Controller | Tasks | Templates | Task Acc. | Template Macro | Cluster 95% CI | API err. |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | 40 | 20 | 67.5 | 67.5 | [50.0, 85.0] | 0 |
| Qwen3.5 | sqlite_lifecycle_gated | 40 | 20 | 100.0 | 100.0 | [100.0, 100.0] | 0 |

## Pre-Specified Paired Comparisons

| A | B | Tasks | Templates | Delta B-A | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| Qwen3.5 sqlite_generic_structured_ledger | Qwen3.5 sqlite_lifecycle_gated | 40 | 20 | 32.5 | [15.0, 50.0] |
