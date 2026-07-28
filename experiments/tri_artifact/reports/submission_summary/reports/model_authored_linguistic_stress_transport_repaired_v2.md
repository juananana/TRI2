# Model-Authored Linguistic Stress Test

**Evidence status:** post-primary model-authored linguistic stress test; post-primary transport-repaired.

This result is scoped to a frozen model-authored linguistic distribution. It is not
independent human, naturally occurring workflow, benchmark-prevalence, or primary evidence.
The original all-zero v1 aggregate was an identifier-normalization failure. This report
uses the frozen exact-ID, zero-request transport repair and retains the invalid report.

## Inventory and model-assisted validity

The ITT inventory contains 48 rows, 24 opposite-gold pairs, and 24 workflow schemas. Generation succeeded for 48/48 rows. Both model judges accepted 11/48 rows forming 0/24 complete pairs.

| Judge | Accepted | Status counts |
|---|---:|---|
| qwen | 25/48 | `{"ok": 48}` |
| glm | 33/48 | `{"ok": 48}` |

## Controller results

| Model / controller | ITT row acc. | ITT PairAcc | Dual-valid row acc. | Dual-valid PairAcc | Preserve substitution | Failures |
|---|---:|---:|---:|---:|---:|---:|
| qwen_generic | 24/48 (50.0%) | 0/24 (0.0%) | 1/11 (9.1%) | 0/0 (NA) | 24/24 (100.0%) | 0 |
| qwen_cta | 36/48 (75.0%) | 12/24 (50.0%) | 10/11 (90.9%) | 0/0 (NA) | 0/12 (0.0%) | 0 |
| glm_generic | 24/48 (50.0%) | 0/24 (0.0%) | 1/11 (9.1%) | 0/0 (NA) | 20/24 (83.3%) | 0 |
| glm_cta | 36/48 (75.0%) | 12/24 (50.0%) | 9/11 (81.8%) | 0/0 (NA) | 0/12 (0.0%) | 0 |
| Rule* (post-hoc) | 15/48 (31.2%) | 5/24 (20.8%) | 2/11 (18.2%) | 0/0 (NA) | NA | 28 |

## Paired comparisons

| Model | CTA - Generic PairAcc | 95% cluster interval | Dual-valid difference | 95% interval | Row discordance G-only / CTA-only |
|---|---:|---:|---:|---:|---:|
| qwen | 50.0% | [29.2%, 70.8%] | NA | [NA, NA] | 0 / 12 |
| glm | 50.0% | [29.2%, 70.8%] | NA | [NA, NA] | 0 / 12 |

## Interpretation boundary

The all-generated ITT result remains primary for this post-primary addendum; the dual-judge subset is a model-assisted sensitivity analysis. Rule* is retained as the strongest post-hoc baseline. Zero observed failures in any cell would not establish zero risk or natural prevalence.
