# TRI SQLite Write-Consequence Replay

Episodes: 1440

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 240 | 94.2 | 94.2 | 5.8 | 5.8 | 0.0 | 0.0 | 14 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 240 | 97.1 | 97.1 | 2.9 | 2.9 | 0.0 | 0.0 | 7 | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 240 | 70.0 | 70.0 | 15.8 | 15.8 | 0.0 | 14.2 | 38 | 0 |
| Qwen3.5 | compile_then_act | 240 | 70.8 | 70.8 | 24.2 | 3.3 | 20.8 | 5.0 | 8 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 240 | 71.2 | 71.2 | 19.6 | 7.1 | 12.5 | 9.2 | 17 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | 240 | 47.5 | 47.5 | 32.1 | 18.3 | 13.8 | 20.4 | 44 | 0 |
