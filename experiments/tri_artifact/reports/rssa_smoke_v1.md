# R-SSA Prospective 20-Task Smoke

Decision: **NO-GO**

| Model | Schema | Epoch | Edge | Roles | Grounding | Free | Enforced | Free source errors | Enforced source errors | False blocks F/E |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM | 0/20 (0.0%) | 0/20 (0.0%) | 0/20 (0.0%) | 0/4 | 0/20 (0.0%) | 0/20 (0.0%) | 0/20 (0.0%) | 0 | 0 | 0/0 |
| Qwen | 20/20 (100.0%) | 11/20 (55.0%) | 20/20 (100.0%) | 0/4 | 6/20 (30.0%) | 5/20 (25.0%) | 6/20 (30.0%) | 0 | 2 | 11/8 |

## Frozen gates

- `GLM_composition_roles_4_of_4`: False
- `GLM_edge_at_least_19_of_20`: False
- `GLM_enforced_within_one_of_cta`: False
- `GLM_epoch_at_least_19_of_20`: False
- `GLM_no_forbidden_fields`: True
- `GLM_not_more_false_blocks_than_free`: True
- `GLM_refresh_at_least_19_of_20`: False
- `GLM_schema_at_least_19_of_20`: False
- `Qwen_composition_roles_4_of_4`: False
- `Qwen_edge_at_least_19_of_20`: True
- `Qwen_enforced_within_one_of_cta`: False
- `Qwen_epoch_at_least_19_of_20`: False
- `Qwen_no_forbidden_fields`: True
- `Qwen_not_more_false_blocks_than_free`: True
- `Qwen_refresh_at_least_19_of_20`: False
- `Qwen_schema_at_least_19_of_20`: True
- `free_and_enforced_not_identical_both_models`: True
- `no_cross_model_cta_direction_reversal`: True
- `source_errors_improve_one_and_do_not_worsen_other`: False

Exact CTA is reused from the prior closed-loop report on the identical task IDs; it is
not rerun. This smoke is post-primary method-feasibility evidence, not a powered final
comparison. A GO permits expansion but does not automatically replace CTA in the paper.
