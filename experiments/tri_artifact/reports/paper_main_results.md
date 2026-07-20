## Overall

| Model | Mode | Binding | Update | n | Accuracy | Drift |
|---|---|---|---|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | compile_then_act | anchored | flip | 13 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | anchored | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | anchored | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | dynamic | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | dynamic | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | anchored | flip | 2 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | anchored | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | dynamic | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | dynamic | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | anchored | flip | 15 | 6.7 | 86.7 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | dynamic | flip | 15 | 100.0 | 0.0 |
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
| Pro/zai-org/GLM-5.1 | ledger | p0 | anchored | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | p0 | anchored | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | p0 | dynamic | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | ledger | p0 | dynamic | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | p0 | anchored | flip | 2 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | p0 | anchored | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | p0 | dynamic | flip | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite | p0 | dynamic | stable | 2 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p0 | anchored | flip | 3 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p0 | dynamic | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p1 | anchored | flip | 3 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p1 | dynamic | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p2 | anchored | flip | 3 | 33.3 | 33.3 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p2 | dynamic | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p3 | anchored | flip | 3 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p3 | dynamic | flip | 3 | 100.0 | 0.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p4 | anchored | flip | 3 | 0.0 | 100.0 |
| Pro/zai-org/GLM-5.1 | state_overwrite_once | p4 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | anchored | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | ledger | p0 | dynamic | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | anchored | flip | 3 | 0.0 | 100.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | anchored | stable | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | dynamic | flip | 3 | 100.0 | 0.0 |
| Qwen/Qwen3.5-397B-A17B | state_overwrite | p0 | dynamic | stable | 3 | 100.0 | 0.0 |
