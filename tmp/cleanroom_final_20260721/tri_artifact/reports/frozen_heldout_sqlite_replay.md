# TRI SQLite Write-Consequence Replay

Episodes: 1600

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 160 | 97.5 | 100.0 | 2.5 | 0.0 | 2.5 | 0.0 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 160 | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| GLM-5.1 | full_history_once | 160 | 70.6 | 80.6 | 29.4 | 19.4 | 1.9 | 0.0 | 31 | 0 |
| GLM-5.1 | generic_plan_then_act | 160 | 80.6 | 84.4 | 18.1 | 14.4 | 1.2 | 1.2 | 23 | 0 |
| GLM-5.1 | state_overwrite_once | 160 | 60.0 | 60.0 | 40.0 | 40.0 | 0.0 | 0.0 | 64 | 0 |
| Qwen3.5 | compile_then_act | 160 | 96.2 | 99.4 | 3.1 | 0.0 | 3.1 | 0.6 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 95.0 | 95.0 | 2.5 | 2.5 | 0.0 | 2.5 | 4 | 0 |
| Qwen3.5 | full_history_once | 160 | 60.6 | 60.6 | 39.4 | 39.4 | 0.0 | 0.0 | 63 | 0 |
| Qwen3.5 | generic_plan_then_act | 160 | 78.1 | 79.4 | 18.8 | 17.5 | 0.0 | 3.1 | 28 | 0 |
| Qwen3.5 | state_overwrite_once | 160 | 60.6 | 60.6 | 39.4 | 39.4 | 0.0 | 0.0 | 63 | 0 |
