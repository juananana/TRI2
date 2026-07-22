# Binding Drift Author-Adaptation Full v7 Report

This is a post-primary author adaptation on TRI tasks, not an official Binding Drift result.

| Method | Overall | Preserve | Reevaluate | Pair success | Flip | Stable | Name collision | Other visible | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| entity_lock_analogue | 160/240 | 120/120 | 40/120 | 40/120 | 40/80 | 80/80 | 40/80 | 0 | 0 |
| glm_self_reverify_author_adaptation | 155/240 | 39/120 | 116/120 | 38/120 | 40/80 | 77/80 | 38/80 | 3 | 0 |
| exact_cta_frozen | 226/240 | 110/120 | 116/120 | 106/120 | 70/80 | 80/80 | 76/80 | 0 | 0 |
| handcrafted_rule_v2_post_hoc | 220/240 | 110/120 | 110/120 | 100/120 | 70/80 | 80/80 | 70/80 | 0 | 0 |

## Frozen interpretation gate

- Outcome: `complementary_policy_result`.
- CTA minus reverify: 29.6 points; cluster-bootstrap 95% CI [26.2, 32.5].

## Post-run information audit

The frozen gate describes the observed output pattern but is not a fair CTA performance
comparison. The adapted verifier receives the instruction and refreshed state, but
neither the initial state nor the resolved pre-refresh ID. Unlike Binding Drift's
uniquely identifying step-1 referent, a TRI ranking selector cannot recover its former
winner from the refreshed state after a changed-winner transition. We therefore retain
this result as an interface audit; the matched full-history and Generic-ledger conditions
are the information-matched baselines.

## Mechanism errors

| Method | Preserve substitutions | Reevaluate premature locks |
|---|---:|---:|
| entity_lock_analogue | 0 | 80 |
| glm_self_reverify_author_adaptation | 80 | 2 |
| exact_cta_frozen | 10 | 4 |
| handcrafted_rule_v2_post_hoc | 10 | 10 |

## Run audit

- Rows: 240
- Requests/retries: 240/0
- Tokens: 89354
- Total recorded latency: 342.0 seconds

This disclosed interface difference and the use of TRI tasks prevent interpreting the
result as an official reproduction, an information-matched CTA comparison, or evidence
about Binding Drift's original initial-misbinding benchmark.
