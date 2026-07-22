# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 state_overwrite_once | Qwen3.5 schema_compile_then_act | 160 | 60.6 | 88.8 | 28.1 | 7 | 52 | 0/0 | 1.359e-09 |
| Qwen3.5 full_history_once | Qwen3.5 schema_compile_then_act | 160 | 65.0 | 88.8 | 23.7 | 8 | 46 | 0/0 | 1.384e-07 |
| Qwen3.5 generic_plan_then_act | Qwen3.5 schema_compile_then_act | 160 | 72.5 | 88.8 | 16.2 | 7 | 33 | 0/0 | 4.228e-05 |
| Qwen3.5 compile_then_act | Qwen3.5 schema_compile_then_act | 160 | 93.8 | 88.8 | -5.0 | 15 | 7 | 0/0 | 0.1338 |
