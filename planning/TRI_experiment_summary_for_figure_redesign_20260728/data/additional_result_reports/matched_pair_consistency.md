# Matched-Pair Consistency Audit

PairAcc is the fraction of complete dataset-matched Preserve/Reevaluate pairs for which both task outcomes are correct. Pairs hold S0, S1, selector, action, schema, and update fixed. Preserve and Reevaluate marginal accuracy are also reported to expose one-sided policies. Missing outputs and API/parse/protocol failures are incorrect under ITT.

explicit_anchor is paired with implicit_dynamic; implicit_anchor is paired with explicit_dynamic when both occur. Stable is a control slice; changed-winner core contains flip and name_collision; remove/invalidate form a separate policy slice.

| Dataset | Model | Controller | All pairs | Changed PairAcc | Changed Preserve | Changed Reevaluate | Stable | Invalidity policy | Missing | API/status | Parse/protocol |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v3 | Qwen3.5 | Generic | 23/80 (28.8%) | 3/32 (9.4%) | 3/32 (9.4%) | 32/32 (100.0%) | 16/16 (100.0%) | 4/32 (12.5%) | 0 | 0 | 0 |
| v3 | GLM-5.1 | Generic | 38/80 (47.5%) | 7/32 (21.9%) | 7/32 (21.9%) | 29/32 (90.6%) | 16/16 (100.0%) | 15/32 (46.9%) | 0 | 0 | 0 |
| v3 | Qwen3.5 | CTA | 72/80 (90.0%) | 30/32 (93.8%) | 31/32 (96.9%) | 31/32 (96.9%) | 16/16 (100.0%) | 26/32 (81.2%) | 0 | 0 | 0 |
| v3 | GLM-5.1 | CTA | 74/80 (92.5%) | 31/32 (96.9%) | 31/32 (96.9%) | 32/32 (100.0%) | 16/16 (100.0%) | 27/32 (84.4%) | 0 | 0 | 0 |
| v3 | Qwen3.5 | Lifecycle-free | 75/80 (93.8%) | 30/32 (93.8%) | 30/32 (93.8%) | 32/32 (100.0%) | 16/16 (100.0%) | 29/32 (90.6%) | 0 | 0 | 0 |
| v3 | GLM-5.1 | Lifecycle-free | 77/80 (96.2%) | 29/32 (90.6%) | 29/32 (90.6%) | 32/32 (100.0%) | 16/16 (100.0%) | 32/32 (100.0%) | 0 | 0 | 0 |
| v3 | Qwen3.5 | Lifecycle-gated | 77/80 (96.2%) | 32/32 (100.0%) | 32/32 (100.0%) | 32/32 (100.0%) | 16/16 (100.0%) | 29/32 (90.6%) | 0 | 0 | 0 |
| v3 | GLM-5.1 | Lifecycle-gated | 80/80 (100.0%) | 32/32 (100.0%) | 32/32 (100.0%) | 32/32 (100.0%) | 16/16 (100.0%) | 32/32 (100.0%) | 0 | 0 | 0 |
| v7 | Qwen3.5 | Generic | 34/120 (28.3%) | 7/80 (8.8%) | 10/80 (12.5%) | 41/80 (51.2%) | 27/40 (67.5%) | NA | 0 | 0 | 0 |
| v7 | GLM-5.1 | Generic | 51/120 (42.5%) | 15/80 (18.8%) | 16/80 (20.0%) | 76/80 (95.0%) | 36/40 (90.0%) | NA | 0 | 0 | 0 |
| v7 | DeepSeek-V4-Pro | Generic | 57/120 (47.5%) | 17/80 (21.2%) | 17/80 (21.2%) | 80/80 (100.0%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |
| v7 | Qwen3.5 | CTA | 59/120 (49.2%) | 31/80 (38.8%) | 70/80 (87.5%) | 35/80 (43.8%) | 28/40 (70.0%) | NA | 0 | 0 | 0 |
| v7 | GLM-5.1 | CTA | 106/120 (88.3%) | 66/80 (82.5%) | 70/80 (87.5%) | 76/80 (95.0%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |
| v7 | DeepSeek-V4-Pro | CTA | 103/120 (85.8%) | 64/80 (80.0%) | 70/80 (87.5%) | 70/80 (87.5%) | 39/40 (97.5%) | NA | 0 | 0 | 0 |
| v7 | Qwen3.5 | Lifecycle-gated | 67/120 (55.8%) | 40/80 (50.0%) | 64/80 (80.0%) | 46/80 (57.5%) | 27/40 (67.5%) | NA | 0 | 0 | 0 |
| v7 | GLM-5.1 | Lifecycle-gated | 113/120 (94.2%) | 73/80 (91.2%) | 79/80 (98.8%) | 74/80 (92.5%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |
| v3 | model-independent | Always-Lock+validity | 16/80 (20.0%) | 0/32 (0.0%) | 32/32 (100.0%) | 0/32 (0.0%) | 16/16 (100.0%) | 0/32 (0.0%) | 0 | 0 | 0 |
| v3 | model-independent | Always-Reevaluate | 16/80 (20.0%) | 0/32 (0.0%) | 0/32 (0.0%) | 32/32 (100.0%) | 16/16 (100.0%) | 0/32 (0.0%) | 0 | 0 | 0 |
| v3 | model-independent | Rule v2 (post-hoc) | 68/80 (85.0%) | 28/32 (87.5%) | 30/32 (93.8%) | 30/32 (93.8%) | 16/16 (100.0%) | 24/32 (75.0%) | 0 | 0 | 0 |
| v7 | model-independent | Always-Lock+validity | 40/120 (33.3%) | 0/80 (0.0%) | 80/80 (100.0%) | 0/80 (0.0%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |
| v7 | model-independent | Always-Reevaluate | 40/120 (33.3%) | 0/80 (0.0%) | 0/80 (0.0%) | 80/80 (100.0%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |
| v7 | model-independent | Rule v2 (post-hoc) | 100/120 (83.3%) | 60/80 (75.0%) | 70/80 (87.5%) | 70/80 (87.5%) | 40/40 (100.0%) | NA | 0 | 0 | 0 |

v7 Lifecycle-gated outputs exist for Qwen and GLM, but not DeepSeek; no value is imputed.
