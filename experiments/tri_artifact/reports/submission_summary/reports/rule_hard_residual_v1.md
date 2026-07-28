# Rule*-Hard Residual Audit

Status: `post_hoc_residual_audit_zero_api`.

Rule*-hard rows: 20 (10 Preserve, 10 Reevaluate).
Complete residual pairs: 0.

| Model / method | Correct | Preserve | Reevaluate |
|---|---:|---:|---:|
| Qwen / History-only | 10/20 | 0/10 | 10/10 |
| Qwen / Timing-reminder | 13/20 | 4/10 | 9/10 |
| Qwen / CTA | 13/20 | 7/10 | 6/10 |
| GLM / History-only | 10/20 | 0/10 | 10/10 |
| GLM / Timing-reminder | 20/20 | 10/10 | 10/10 |
| GLM / CTA | 20/20 | 10/10 | 10/10 |
| DeepSeek / History-only | 15/20 | 5/10 | 10/10 |
| DeepSeek / Timing-reminder | 18/20 | 9/10 | 9/10 |
| DeepSeek / CTA | 16/20 | 8/10 | 8/10 |

The subset is selected after observing Rule* errors and contains no complete Preserve/Reevaluate pair; row accuracy is descriptive and PairAcc is undefined.
