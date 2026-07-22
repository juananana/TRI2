# Deterministic Discourse-Rule Baseline

The controller reads only instruction, initial/refreshed state, and action schema. Gold and generator metadata are used only by the evaluator after prediction.

| Dataset | n | E2E | Mode | Actionable core | Reject policy | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| v3 | 160 | 97/160 (60.6%) | 112/160 (70.0%) | 80/128 (62.5%) | 17/32 (53.1%) | 52 |
| human_rewrite | 50 | 37/50 (74.0%) | 46/50 (92.0%) | 27/40 (67.5%) | 10/10 (100.0%) | 12 |
| v7 | 240 | 186/240 (77.5%) | 180/240 (75.0%) | 186/240 (77.5%) | NA | 44 |

## CTA comparisons

| Dataset | Model | Rule | CTA | CTA - Rule | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| v3 | Qwen3.5 | 60.6 | 95.0 | +34.4 | [+17.5, +51.2] |
| v3 | GLM-5.1 | 60.6 | 96.2 | +35.6 | [+18.8, +53.1] |
| human_rewrite | Qwen3.5 | 74.0 | 90.0 | +16.0 | [-3.7, +36.5] |
| human_rewrite | GLM-5.1 | 74.0 | 98.0 | +24.0 | [+7.4, +41.3] |
| v7 | Qwen3.5 | 77.5 | 70.8 | -6.7 | [-14.6, +1.2] |
| v7 | GLM-5.1 | 77.5 | 94.2 | +16.7 | [+12.9, +20.4] |
| v7 | DeepSeek | 77.5 | 91.2 | +13.8 | [+8.3, +18.8] |

## Unresolved cases

- v3: {'ambiguous_numeric_selector:': 20, 'missing_selection_event': 32}
- human_rewrite: {'ambiguous_numeric_selector:': 8, 'ambiguous_ranking_direction': 1, 'missing_selection_event': 3}
- v7: {'missing_selection_event': 44}

The frozen interpretation thresholds are defined in `reports/TRI_deterministic_discourse_rule_protocol.md`.
