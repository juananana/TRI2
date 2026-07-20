# TRI-v7 Core Replication Report

Intervals resample each run's observed state-instance clusters (16 in this report).

| Model | Controller | n | Accuracy | Correct initial anchored | Core drift | Stable errors | API / parse errors |
|---|---|---:|---:|---:|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | 16 | 68.8% | 10/10 | 5/6 [50.0, 100.0] | 0/4 | 0 / 0 |
| DeepSeek | compile_then_act | 16 | 93.8% | 9/10 | 0/6 [0.0, 0.0] | 1/4 | 0 / 0 |

| Model | A | B | n | Delta B-A | State-cluster 95% CI |
|---|---|---|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | compile_then_act | 16 | 25.0 | [0.0, 50.0] |

| Model | Controller | Reference mode | Anchored | Dynamic |
|---|---|---:|---:|---:|
| DeepSeek | generic_structured_ledger_then_act | NA | 50.0% | 100.0% |
| DeepSeek | compile_then_act | 100.0% | 90.0% | 100.0% |
