# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 state_overwrite_once | Qwen3.5 factorized_schema_compile_then_act | 160 | 60.6 | 98.1 | 37.5 | 0 | 60 | 0/0 | 1.735e-18 |
| Qwen3.5 full_history_once | Qwen3.5 factorized_schema_compile_then_act | 160 | 65.0 | 98.1 | 33.1 | 0 | 53 | 0/0 | 2.22e-16 |
| Qwen3.5 generic_plan_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 72.5 | 98.1 | 25.6 | 0 | 41 | 0/0 | 9.095e-13 |
| Qwen3.5 compile_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 93.8 | 98.1 | 4.4 | 3 | 10 | 0/0 | 0.09229 |
| Qwen3.5 schema_compile_then_act | Qwen3.5 factorized_schema_compile_then_act | 160 | 88.8 | 98.1 | 9.4 | 3 | 18 | 0/0 | 0.00149 |
