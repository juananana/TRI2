## Overall

| Model | Mode | Binding | Update | n | Accuracy | Drift |
|---|---|---|---|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | compile_then_act | anchored | flip | 13 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | anchored | flip | 33 | 3.0 | 97.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | dynamic | flip | 21 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | anchored | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | dynamic | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | anchored | flip | 3 | 0.0 | 100.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | dynamic | stable | 3 | 100.0 | 0.0 |

## By Paraphrase

| Model | Mode | Para | Binding | Update | n | Accuracy | Drift |
|---|---|---|---|---|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | compile_then_act | p0 | anchored | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | compile_then_act | p1 | anchored | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | compile_then_act | p2 | anchored | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | compile_then_act | p3 | anchored | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | compile_then_act | p4 | anchored | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p0 | anchored | flip | 7 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p0 | dynamic | flip | 4 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p1 | anchored | flip | 7 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p1 | dynamic | flip | 5 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p2 | anchored | flip | 5 | 20.0 | 80.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p2 | dynamic | flip | 5 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p3 | anchored | flip | 7 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p3 | dynamic | flip | 4 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p4 | anchored | flip | 7 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p4 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | anchored | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | dynamic | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | anchored | flip | 3 | 0.0 | 100.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | dynamic | stable | 3 | 100.0 | 0.0 |
