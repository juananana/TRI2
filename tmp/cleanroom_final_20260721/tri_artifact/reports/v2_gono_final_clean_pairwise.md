# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 state_overwrite_once | GLM-5.1 schema_compile_then_act | 160 | 60.6 | 95.0 | 34.4 | 0 | 55 | 0/0 | 5.551e-17 |
| GLM-5.1 full_history_once | GLM-5.1 schema_compile_then_act | 160 | 76.2 | 95.0 | 18.8 | 0 | 30 | 0/0 | 1.863e-09 |
| GLM-5.1 generic_plan_then_act | GLM-5.1 schema_compile_then_act | 160 | 78.1 | 95.0 | 16.9 | 0 | 27 | 0/0 | 1.49e-08 |
| GLM-5.1 compile_then_act | GLM-5.1 schema_compile_then_act | 160 | 89.4 | 95.0 | 5.6 | 3 | 12 | 0/0 | 0.03516 |
