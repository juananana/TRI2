# Source-Derived Matched-Call Repeat Stability

Evidence status: **post-primary replication/audit**.

Temperature-zero repeats measure endpoint repeatability on the same 30 source-derived pairs. They do not increase the independent pair count or establish native behavior.

| Model | Pass | History PairAcc | Visible PairAcc | Effect | History E2E | Visible E2E | Incomplete |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.5-122B-A10B | historical | 12/30 | 13/30 | 3.3 pp | 39/60 | 39/60 | 0 |
| Pro/zai-org/GLM-5.1 | historical | 11/30 | 20/30 | 30.0 pp | 37/60 | 48/60 | 0 |
| deepseek-ai/DeepSeek-V4-Pro | historical | 19/30 | 22/30 | 10.0 pp | 45/60 | 47/60 | 0 |
| Qwen/Qwen3.5-122B-A10B | repeat2 | 10/30 | 15/30 | 16.7 pp | 37/60 | 41/60 | 0 |
| Pro/zai-org/GLM-5.1 | repeat2 | 12/30 | 19/30 | 23.3 pp | 38/60 | 47/60 | 0 |
| deepseek-ai/DeepSeek-V4-Pro | repeat2 | 18/30 | 20/30 | 6.7 pp | 45/60 | 47/60 | 0 |
| Pro/MiniMaxAI/MiniMax-M2.5 | first-pass | 19/30 | 20/30 | 3.3 pp | 48/60 | 46/60 | 0 |

## Exact-target agreement with the historical pass

- Qwen/Qwen3.5-122B-A10B: history_only 58/60, decision_visible 56/60, decision_enforced 58/60.
- Pro/zai-org/GLM-5.1: history_only 58/60, decision_visible 59/60, decision_enforced 60/60.
- deepseek-ai/DeepSeek-V4-Pro: history_only 57/60, decision_visible 53/60, decision_enforced 56/60.
