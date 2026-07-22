# TRI SQLite Write-Consequence Replay

Episodes: 480

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | compile_then_act | 240 | 91.2 | 91.2 | 7.1 | 7.1 | 0.0 | 1.7 | 17 | 0 |
| DeepSeek | generic_structured_ledger_then_act | 240 | 73.8 | 73.8 | 25.0 | 25.0 | 0.0 | 1.2 | 60 | 0 |
