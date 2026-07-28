# TRI SQLite Write-Consequence Replay

Episodes: 1440

| Model | Controller | n | Safe resolution | Final state | Wrong attempt | Wrong write | Invalid attempt | Unneeded reject | Collateral | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | full_history_once | 240 | 75.8 | 75.8 | 23.8 | 23.8 | 0.0 | 0.4 | 57 | 0 |
| DeepSeek | interactive | 240 | 68.8 | 68.8 | 31.2 | 31.2 | 0.0 | 0.0 | 75 | 0 |
| GLM-5.1 | full_history_once | 240 | 80.8 | 80.8 | 19.2 | 19.2 | 0.0 | 0.0 | 46 | 0 |
| GLM-5.1 | interactive | 240 | 67.1 | 67.1 | 32.9 | 32.9 | 0.0 | 0.0 | 79 | 0 |
| Qwen3.5 | full_history_once | 240 | 69.6 | 69.6 | 30.4 | 29.2 | 1.2 | 0.0 | 70 | 0 |
| Qwen3.5 | interactive | 240 | 63.3 | 63.3 | 36.7 | 36.2 | 0.4 | 0.0 | 87 | 0 |
