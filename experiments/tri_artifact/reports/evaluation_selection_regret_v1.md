# Evaluation-Selection Regret Audit

**Status:** post-primary zero-API audit over frozen identifiability reports.

A proxy-score maximizer is any candidate tied for the highest score under that regime.
Regret is measured against the best changed-winner PairAcc in the same model-family candidate set.

| Dataset/model | Proxy | Maximizers | PairAcc range | Best PairAcc | Worst regret | Optimistic regret | Zero-PairAcc maximizer? |
|---|---|---|---:|---:|---:|---:|---:|
| v3 / GLM | Aggregate E2E | GLM-Lifecycle-free | 90.6--90.6 | 96.9 | 6.2 | 6.2 | no |
| v3 / GLM | Preserve only | Always-Lock+validity | 0.0--0.0 | 96.9 | 96.9 | 96.9 | yes |
| v3 / GLM | Reevaluate only | Always-Reevaluate, GLM-CTA, GLM-Lifecycle-free | 0.0--96.9 | 96.9 | 96.9 | 0.0 | yes |
| v3 / GLM | Stable only | Always-Lock+validity, Always-Reevaluate, GLM-CTA, GLM-Generic, GLM-Lifecycle-free | 0.0--96.9 | 96.9 | 96.9 | 0.0 | yes |
| v3 / Qwen | Aggregate E2E | Qwen-Lifecycle-free | 93.8--93.8 | 93.8 | 0.0 | 0.0 | no |
| v3 / Qwen | Preserve only | Always-Lock+validity | 0.0--0.0 | 93.8 | 93.8 | 93.8 | yes |
| v3 / Qwen | Reevaluate only | Always-Reevaluate | 0.0--0.0 | 93.8 | 93.8 | 93.8 | yes |
| v3 / Qwen | Stable only | Always-Lock+validity, Always-Reevaluate, Qwen-CTA, Qwen-Generic, Qwen-Lifecycle-free | 0.0--93.8 | 93.8 | 93.8 | 0.0 | yes |
| v7 / DeepSeek | Aggregate E2E | DeepSeek-CTA | 80.0--80.0 | 80.0 | 0.0 | 0.0 | no |
| v7 / DeepSeek | Preserve only | Always-Lock+validity | 0.0--0.0 | 80.0 | 80.0 | 80.0 | yes |
| v7 / DeepSeek | Reevaluate only | Always-Reevaluate, DeepSeek-Generic | 0.0--21.2 | 80.0 | 80.0 | 58.8 | yes |
| v7 / DeepSeek | Stable only | Always-Lock+validity, Always-Reevaluate, DeepSeek-Generic | 0.0--21.2 | 80.0 | 80.0 | 58.8 | yes |
| v7 / GLM | Aggregate E2E | GLM-CTA | 82.5--82.5 | 82.5 | 0.0 | 0.0 | no |
| v7 / GLM | Preserve only | Always-Lock+validity | 0.0--0.0 | 82.5 | 82.5 | 82.5 | yes |
| v7 / GLM | Reevaluate only | Always-Reevaluate | 0.0--0.0 | 82.5 | 82.5 | 82.5 | yes |
| v7 / GLM | Stable only | Always-Lock+validity, Always-Reevaluate, GLM-CTA | 0.0--82.5 | 82.5 | 82.5 | 0.0 | yes |
| v7 / Qwen | Aggregate E2E | Qwen-CTA | 38.8--38.8 | 38.8 | 0.0 | 0.0 | no |
| v7 / Qwen | Preserve only | Always-Lock+validity | 0.0--0.0 | 38.8 | 38.8 | 38.8 | yes |
| v7 / Qwen | Reevaluate only | Always-Reevaluate | 0.0--0.0 | 38.8 | 38.8 | 38.8 | yes |
| v7 / Qwen | Stable only | Always-Lock+validity, Always-Reevaluate | 0.0--0.0 | 38.8 | 38.8 | 38.8 | yes |

Across 5 dataset/model candidate sets and 20 proxy evaluations, all 15 Stable-only or one-sided maximizer sets include a zero-PairAcc unconditional policy.
The maximum worst-case selection regret is 96.9 points.

- The candidate sets are concrete tested alternatives, not an exhaustive policy class.
- Worst-case tie handling means the proxy score licenses a poor policy; it does not claim users always choose it.
- PairAcc measures the balanced changed-winner authorization contrast, not general task utility or prevalence.
