# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 state_overwrite_once | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 60.0 | 100.0 | 40.0 | 0 | 64 | 0/0 | 1.084e-19 |
| GLM-5.1 full_history_once | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 70.6 | 100.0 | 29.4 | 0 | 47 | 0/0 | 1.421e-14 |
| GLM-5.1 generic_plan_then_act | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 80.6 | 100.0 | 19.4 | 0 | 31 | 0/0 | 9.313e-10 |
| GLM-5.1 compile_then_act | GLM-5.1 factorized_hybrid_compile_then_act | 160 | 97.5 | 100.0 | 2.5 | 0 | 4 | 0/0 | 0.125 |
| Qwen3.5 state_overwrite_once | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 60.6 | 95.0 | 34.4 | 8 | 63 | 0/0 | 1.027e-11 |
| Qwen3.5 full_history_once | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 60.6 | 95.0 | 34.4 | 8 | 63 | 0/0 | 1.027e-11 |
| Qwen3.5 generic_plan_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 78.1 | 95.0 | 16.9 | 8 | 35 | 0/0 | 4.193e-05 |
| Qwen3.5 compile_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 96.2 | 95.0 | -1.3 | 8 | 6 | 0/0 | 0.7905 |
