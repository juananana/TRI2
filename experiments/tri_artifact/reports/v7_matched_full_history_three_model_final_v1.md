# V7 Matched Full-History Baseline Report

Full-history runs do not expose a separately scored pre-refresh binding. Anchored
substitution is therefore unconditional and must not be called conditional TRI.

| Model | Controller | n | Accuracy | Anchored | Dynamic | Anchored changed substitution | Dynamic old target | Stable errors | API / parse | Requests / retries | Tokens | Latency s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | interactive | 240 | 63.3% | 33.3% | 93.3% | 77/80 | 0/80 | 3/40 | 0 / 0 | 480 / 0 | 247388 | 267.1 |
| Qwen3.5 | full_history_once | 240 | 69.6% | 51.7% | 87.5% | 56/80 | 8/80 | 0/40 | 0 / 0 | 269 / 29 | 149632 | 288.9 |
| GLM-5.1 | interactive | 240 | 67.1% | 36.7% | 97.5% | 74/80 | 0/80 | 2/40 | 0 / 0 | 480 / 0 | 236396 | 602.5 |
| GLM-5.1 | full_history_once | 240 | 80.8% | 66.7% | 95.0% | 38/80 | 2/80 | 2/40 | 0 / 0 | 240 / 0 | 143366 | 316.6 |
| DeepSeek | interactive | 240 | 68.8% | 41.7% | 95.8% | 68/80 | 0/80 | 2/40 | 0 / 0 | 480 / 0 | 246348 | 1194.2 |
| DeepSeek | full_history_once | 240 | 75.8% | 63.3% | 88.3% | 42/80 | 5/80 | 1/40 | 0 / 0 | 240 / 0 | 150801 | 732.9 |

| Model | A | B | n | A wrong / B right | A right / B wrong | Delta B-A | State-cluster 95% CI | Missing A/B |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | interactive | full_history_once | 240 | 27 | 12 | 6.2 | [2.1, 10.4] | 0/0 |
| Qwen3.5 | interactive | compile_then_act | 240 | 73 | 55 | 7.5 | [0.0, 15.0] | 0/0 |
| Qwen3.5 | full_history_once | compile_then_act | 240 | 58 | 55 | 1.2 | [-6.7, 9.2] | 0/0 |
| GLM-5.1 | interactive | full_history_once | 240 | 41 | 8 | 13.8 | [9.2, 18.3] | 0/0 |
| GLM-5.1 | interactive | compile_then_act | 240 | 69 | 4 | 27.1 | [23.8, 30.0] | 0/0 |
| GLM-5.1 | full_history_once | compile_then_act | 240 | 36 | 4 | 13.3 | [8.8, 17.9] | 0/0 |
| DeepSeek | interactive | full_history_once | 240 | 30 | 13 | 7.1 | [1.2, 12.5] | 0/0 |
| DeepSeek | interactive | compile_then_act | 240 | 68 | 14 | 22.5 | [14.6, 29.2] | 0/0 |
| DeepSeek | full_history_once | compile_then_act | 240 | 48 | 11 | 15.4 | [9.2, 21.7] | 0/0 |
