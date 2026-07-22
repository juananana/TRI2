# TRI-v7 Core Replication Report

Intervals resample each run's observed state-instance clusters (40 in this report).

| Model | Controller | n | Accuracy | Correct initial anchored | Core drift | Stable errors | API / parse errors |
|---|---|---:|---:|---:|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | 240 | 73.8% | 119/120 | 59/79 [62.5, 86.1] | 0/40 | 0 / 0 |
| DeepSeek | compile_then_act | 240 | 91.2% | 107/120 | 0/70 [0.0, 0.0] | 1/40 | 0 / 0 |

| Model | A | B | n | Delta B-A | State-cluster 95% CI |
|---|---|---|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | compile_then_act | 240 | 17.5 | [10.8, 23.3] |

| Model | Controller | Reference mode | Anchored | Dynamic |
|---|---|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | NA | 47.5% | 100.0% |
| DeepSeek | compile_then_act | 95.0% | 90.8% | 91.7% |
