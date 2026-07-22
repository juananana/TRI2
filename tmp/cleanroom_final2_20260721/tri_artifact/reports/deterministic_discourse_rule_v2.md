# Strengthened Handcrafted Deterministic Discourse-Rule Baseline

The controller reads only instruction, initial/refreshed state, and action schema. Gold and generator metadata are used only by the evaluator after prediction.

| Dataset | n | E2E | Mode | Actionable core | Reject policy | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| v3 | 160 | 148/160 (92.5%) | 144/160 (90.0%) | 120/128 (93.8%) | 28/32 (87.5%) | 0 |
| human_rewrite | 50 | 48/50 (96.0%) | 48/50 (96.0%) | 38/40 (95.0%) | 10/10 (100.0%) | 0 |
| v7 | 240 | 220/240 (91.7%) | 210/240 (87.5%) | 220/240 (91.7%) | NA | 0 |

## CTA comparisons

| Dataset | Model | Rule | CTA | CTA - Rule | Cluster 95% CI |
|---|---|---:|---:|---:|---:|
| v3 | Qwen3.5 | 92.5 | 95.0 | +2.5 | [-7.5, +15.0] |
| v3 | GLM-5.1 | 92.5 | 96.2 | +3.8 | [-6.2, +16.2] |
| human_rewrite | Qwen3.5 | 96.0 | 90.0 | -6.0 | [-15.9, +4.3] |
| human_rewrite | GLM-5.1 | 96.0 | 98.0 | +2.0 | [-4.4, +9.1] |
| v7 | Qwen3.5 | 91.7 | 70.8 | -20.8 | [-28.7, -13.3] |
| v7 | GLM-5.1 | 91.7 | 94.2 | +2.5 | [-0.4, +5.4] |
| v7 | DeepSeek | 91.7 | 91.2 | -0.4 | [-5.0, +4.2] |

## Unresolved cases

- v3: none
- human_rewrite: none
- v7: none

The frozen interpretation thresholds are defined in `reports/TRI_deterministic_discourse_rule_protocol.md`.
