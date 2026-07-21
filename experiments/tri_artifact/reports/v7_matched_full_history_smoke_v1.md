# V7 Matched Full-History Baseline Report

Full-history runs do not expose a separately scored pre-refresh binding. Anchored
substitution is therefore unconditional and must not be called conditional TRI.

| Model | Controller | n | Accuracy | Anchored | Dynamic | Anchored changed substitution | Dynamic old target | Stable errors | API / parse | Requests |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | interactive | 16 | 56.2% | 40.0% | 83.3% | 6/6 | 0/4 | 0/4 | 0 / 0 | 32 |
| Qwen3.5 | full_history_once | 16 | 75.0% | 60.0% | 100.0% | 4/6 | 0/4 | 0/4 | 0 / 0 | 16 |
| GLM-5.1 | interactive | 16 | 75.0% | 60.0% | 100.0% | 4/6 | 0/4 | 0/4 | 0 / 0 | 32 |
| GLM-5.1 | full_history_once | 16 | 87.5% | 80.0% | 100.0% | 2/6 | 0/4 | 0/4 | 0 / 0 | 16 |
| DeepSeek | interactive | 16 | 68.8% | 60.0% | 83.3% | 4/6 | 0/4 | 0/4 | 0 / 0 | 32 |
| DeepSeek | full_history_once | 16 | 75.0% | 70.0% | 83.3% | 3/6 | 0/4 | 0/4 | 0 / 0 | 16 |

| Model | A | B | n | Delta B-A | State-cluster 95% CI |
|---|---|---|---:|---:|---:|
| Qwen3.5 | interactive | full_history_once | 16 | 18.8 | [0.0, 37.5] |
| GLM-5.1 | interactive | full_history_once | 16 | 12.5 | [0.0, 31.2] |
| DeepSeek | interactive | full_history_once | 16 | 6.2 | [0.0, 18.8] |
