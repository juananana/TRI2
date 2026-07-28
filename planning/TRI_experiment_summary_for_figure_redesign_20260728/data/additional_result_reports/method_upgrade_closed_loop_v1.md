# TRI Method Upgrade 20-Task Closed Loop

## Scalar core (16 tasks)

| Model | Method | Accuracy | Schema | Mode | Selector | Wrong valid target | False block | Errors | Requests |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Deterministic | Always-Lock | 12/16 (75.0%) | NA | NA | NA | 4 | 0 | 0 | 0 |
| Deterministic | Always-Reevaluate | 10/16 (62.5%) | NA | NA | NA | 6 | 0 | 0 | 0 |
| GLM | Exact CTA | 16/16 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 32 |
| GLM | Generic | 11/16 (68.8%) | NA | NA | NA | 2 | 3 | 0 | 32 |
| GLM | Lifecycle-Gated | 16/16 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 22 |
| GLM | M1 Event Graph | 16/16 (100.0%) | 16/16 (100.0%) | 16/16 (100.0%) | NA | 0 | 0 | 0 | 22 |
| GLM | M2 Executable Selector | 14/16 (87.5%) | 14/16 (87.5%) | 14/16 (87.5%) | 15/16 (93.8%) | 1 | 0 | 1 | 16 |
| Qwen | Exact CTA | 11/16 (68.8%) | NA | NA | NA | 0 | 0 | 0 | 32 |
| Qwen | Generic | 9/16 (56.2%) | NA | NA | NA | 3 | 2 | 0 | 32 |
| Qwen | Lifecycle-Gated | 10/16 (62.5%) | NA | NA | NA | 1 | 0 | 0 | 22 |
| Qwen | M1 Event Graph | 7/16 (43.8%) | 12/16 (75.0%) | 10/16 (62.5%) | NA | 1 | 1 | 4 | 23 |
| Qwen | M2 Executable Selector | 11/16 (68.8%) | 11/16 (68.8%) | 10/16 (62.5%) | 11/16 (68.8%) | 0 | 0 | 5 | 16 |

## Compositional stress (4 tasks)

| Model | Method | Accuracy | Schema | Mode | Selector | Wrong valid target | False block | Errors | Requests |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Deterministic | Always-Lock | 2/4 (50.0%) | NA | NA | NA | 1 | 1 | 0 | 0 |
| Deterministic | Always-Reevaluate | 2/4 (50.0%) | NA | NA | NA | 2 | 0 | 0 | 0 |
| GLM | Exact CTA | 4/4 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 8 |
| GLM | M1 Event Graph | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | NA | 0 | 0 | 0 | 6 |
| GLM | M2 Executable Selector | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 0 | 0 | 0 | 4 |
| GLM | Role-Indexed Lifecycle | 4/4 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 6 |
| GLM | Scalar Lifecycle | 4/4 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 6 |
| Qwen | Exact CTA | 2/4 (50.0%) | NA | NA | NA | 0 | 1 | 0 | 8 |
| Qwen | M1 Event Graph | 2/4 (50.0%) | 2/4 (50.0%) | 2/4 (50.0%) | NA | 0 | 0 | 2 | 4 |
| Qwen | M2 Executable Selector | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 0 | 0 | 0 | 4 |
| Qwen | Role-Indexed Lifecycle | 4/4 (100.0%) | NA | NA | NA | 0 | 0 | 0 | 6 |
| Qwen | Scalar Lifecycle | 2/4 (50.0%) | NA | NA | NA | 1 | 1 | 0 | 4 |

## New-method combined view

| Model | Method | Accuracy | Schema | Mode | Selector | Wrong valid target | Errors | Requests | Tokens in/out |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen | M1 Event Graph | 9/20 (45.0%) | 14/20 (70.0%) | 12/20 (60.0%) | NA | 1 | 6 | 27 | 13379/5504 |
| Qwen | M2 Executable Selector | 15/20 (75.0%) | 15/20 (75.0%) | 14/20 (70.0%) | 15/20 (75.0%) | 0 | 5 | 20 | 11281/7047 |
| GLM | M1 Event Graph | 20/20 (100.0%) | 20/20 (100.0%) | 20/20 (100.0%) | NA | 0 | 0 | 28 | 13345/5140 |
| GLM | M2 Executable Selector | 18/20 (90.0%) | 18/20 (90.0%) | 18/20 (90.0%) | 19/20 (95.0%) | 1 | 1 | 20 | 10837/6472 |

## Decision

- m2_schema_at_least_95pct_both_models: False
- m2_selector_at_least_95pct_both_models: False
- m2_not_more_than_2_points_below_cta: False
- m2_effect_direction_consistent: False
- promote_m2_to_main_method: False
- recommended_main_method: Exact CTA
- recommended_compositional_extension: Role-Indexed Lifecycle

The 20-task matrix is a smoke/decision experiment, not a final powered comparison.
