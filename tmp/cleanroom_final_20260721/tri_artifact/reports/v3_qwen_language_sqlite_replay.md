# TRI SQLite Write-Consequence Replay

Episodes: 320

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | 160 | 98.1 | 98.1 | 0.0 | 0.0 | 0.0 | 1.9 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | 160 | 64.4 | 65.0 | 33.1 | 32.5 | 0.0 | 2.5 | 52 | 0 |
