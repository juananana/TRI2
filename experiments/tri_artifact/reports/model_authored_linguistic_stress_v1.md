# Model-Authored Linguistic Stress Test

**Evidence status:** post-primary model-authored linguistic stress test.

This result is scoped to a frozen model-authored linguistic distribution. It is not
independent human, naturally occurring workflow, benchmark-prevalence, or primary evidence.

## Inventory and model-assisted validity

The ITT inventory contains 48 rows, 24 opposite-gold pairs, and 24 workflow schemas. Generation succeeded for 48/48 rows. Both model judges accepted 11/48 rows forming 0/24 complete pairs.

| Judge | Accepted | Status counts |
|---|---:|---|
| qwen | 25/48 | `{"ok": 48}` |
| glm | 33/48 | `{"ok": 48}` |

## Controller results

| Model / controller | ITT row acc. | ITT PairAcc | Dual-valid row acc. | Dual-valid PairAcc | Preserve substitution | Failures |
|---|---:|---:|---:|---:|---:|---:|
| qwen_generic | 0/48 (0.0%) | 0/24 (0.0%) | 0/11 (0.0%) | 0/0 (NA) | 0/0 (NA) | 0 |
| qwen_cta | 0/48 (0.0%) | 0/24 (0.0%) | 0/11 (0.0%) | 0/0 (NA) | 0/0 (NA) | 0 |
| glm_generic | 0/48 (0.0%) | 0/24 (0.0%) | 0/11 (0.0%) | 0/0 (NA) | 0/0 (NA) | 0 |
| glm_cta | 0/48 (0.0%) | 0/24 (0.0%) | 0/11 (0.0%) | 0/0 (NA) | 0/0 (NA) | 0 |
| Rule* (post-hoc) | 15/48 (31.2%) | 5/24 (20.8%) | 2/11 (18.2%) | 0/0 (NA) | NA | 28 |

## Paired comparisons

| Model | CTA - Generic PairAcc | 95% cluster interval | Dual-valid difference | 95% interval | Row discordance G-only / CTA-only |
|---|---:|---:|---:|---:|---:|
| qwen | 0.0% | [0.0%, 0.0%] | NA | [NA, NA] | 0 / 0 |
| glm | 0.0% | [0.0%, 0.0%] | NA | [NA, NA] | 0 / 0 |

## Interpretation boundary

The all-generated ITT result remains primary for this post-primary addendum; the dual-judge subset is a model-assisted sensitivity analysis. Rule* is retained as the strongest post-hoc baseline. Zero observed failures in any cell would not establish zero risk or natural prevalence.
