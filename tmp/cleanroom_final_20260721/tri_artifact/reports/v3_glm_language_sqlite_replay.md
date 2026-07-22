# TRI SQLite Write-Consequence Replay

Episodes: 320

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | 160 | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 160 | 71.9 | 73.1 | 12.5 | 11.2 | 0.0 | 15.6 | 18 | 0 |
