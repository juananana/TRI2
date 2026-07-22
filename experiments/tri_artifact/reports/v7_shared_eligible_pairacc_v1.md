# V7 Shared-Eligible and PairAcc Uncertainty Audit

**Status:** post-primary zero-API audit of frozen outputs.

| Model | Shared eligible | Generic substitutions | CTA substitutions |
|---|---:|---:|---:|
| Qwen3.5 | 66 | 41 | 0 |
| GLM-5.1 | 70 | 30 | 0 |
| DeepSeek | 69 | 50 | 0 |

The shared denominator requires both controllers to expose the correct initial ID on the
same action-valid changed-winner task and excludes API, parse, and protocol failures.

| Model | Generic PairAcc (95% CI) | CTA PairAcc (95% CI) | CTA-Generic (95% CI) |
|---|---:|---:|---:|
| Qwen3.5 | 7/80 [2.5%, 16.2%] | 31/80 [26.2%, 51.2%] | 30.0% [16.2%, 43.8%] |
| GLM-5.1 | 15/80 [8.8%, 30.0%] | 66/80 [73.8%, 90.0%] | 63.7% [52.5%, 75.0%] |
| DeepSeek | 17/80 [11.2%, 32.5%] | 64/80 [70.0%, 88.8%] | 58.8% [43.8%, 72.5%] |

Bootstrap: 10,000 resamples of all 40 state clusters with replacement; base seed 20260722.

Shared eligibility removes controller-specific initial-binding selection only. Zero observed CTA substitutions do not establish zero population risk.
