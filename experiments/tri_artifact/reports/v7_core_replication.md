# TRI-v7 Core Replication Report

Intervals resample the 40 state-instance clusters.

| Model | Controller | n | Accuracy | Correct initial anchored | Core drift | Stable errors | API / parse errors |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | 240 | 47.5% | 107/120 | 43/72 [46.5, 72.4] | 4/40 | 0 / 0 |
| Qwen3.5 | compile_then_act | 240 | 70.8% | 103/120 | 0/71 [0.0, 0.0] | 6/40 | 0 / 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 240 | 71.2% | 95/120 | 0/64 [0.0, 0.0] | 9/40 | 0 / 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 240 | 70.0% | 120/120 | 38/80 [35.0, 61.3] | 2/40 | 0 / 0 |
| GLM-5.1 | compile_then_act | 240 | 94.2% | 104/120 | 0/70 [0.0, 0.0] | 0/40 | 0 / 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 240 | 97.1% | 119/120 | 0/79 [0.0, 0.0] | 0/40 | 0 / 0 |

| Model | A | B | n | Delta B-A | State-cluster 95% CI |
|---|---|---|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | compile_then_act | 240 | 23.3 | [16.2, 30.4] |
| Qwen3.5 | generic_structured_ledger_then_act | factorized_hybrid_compile_then_act | 240 | 23.8 | [16.2, 31.2] |
| GLM-5.1 | generic_structured_ledger_then_act | compile_then_act | 240 | 24.2 | [19.6, 28.7] |
| GLM-5.1 | generic_structured_ledger_then_act | factorized_hybrid_compile_then_act | 240 | 27.1 | [22.1, 32.1] |

| Model | Controller | Reference mode | Anchored | Dynamic |
|---|---|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | NA | 38.3% | 56.7% |
| Qwen3.5 | compile_then_act | 94.6% | 86.7% | 55.0% |
| Qwen3.5 | factorized_hybrid_compile_then_act | 92.9% | 79.2% | 63.3% |
| GLM-5.1 | generic_structured_ledger_then_act | NA | 45.0% | 95.0% |
| GLM-5.1 | compile_then_act | 93.3% | 91.7% | 96.7% |
| GLM-5.1 | factorized_hybrid_compile_then_act | 100.0% | 99.2% | 95.0% |
