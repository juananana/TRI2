# TRI SQLite Write-Consequence Replay

Episodes: 160

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | 80 | 82.5 | 82.5 | 1.2 | 0.0 | 1.2 | 16.2 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | 80 | 46.2 | 46.2 | 22.5 | 22.5 | 0.0 | 31.2 | 18 | 0 |
