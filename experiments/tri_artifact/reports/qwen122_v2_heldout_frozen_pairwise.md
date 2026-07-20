# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 state_overwrite_once | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 60.6 | 95.0 | 34.4 | 8 | 63 | 0/0 | 1.027e-11 |
| Qwen3.5 full_history_once | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 60.6 | 95.0 | 34.4 | 8 | 63 | 0/0 | 1.027e-11 |
| Qwen3.5 generic_plan_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 78.1 | 95.0 | 16.9 | 8 | 35 | 0/0 | 4.193e-05 |
| Qwen3.5 compile_then_act | Qwen3.5 factorized_hybrid_compile_then_act | 160 | 96.2 | 95.0 | -1.3 | 8 | 6 | 0/0 | 0.7905 |
