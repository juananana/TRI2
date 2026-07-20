# TRI-v2 Paired Significance Report

Accuracy counts API failures as incorrect. McNemar uses discordant task outcomes.

| A | B | n | Acc. A | Acc. B | Delta B-A | A-only | B-only | API A/B | Exact p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 state_overwrite_once | GLM-5.1 compile_then_act | 160 | 61.3 | 89.4 | 28.1 | 0 | 45 | 0/0 | 5.684e-14 |
| Qwen3.5 state_overwrite_once | Qwen3.5 compile_then_act | 160 | 60.0 | 53.8 | -6.2 | 32 | 22 | 0/52 | 0.2203 |
