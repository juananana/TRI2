# Binding Drift Author-Adaptation Symmetric Smoke

This is an author adaptation on TRI tasks, not an official Binding Drift result.

| Model | Method | Overall | Preserve | Reevaluate | Preserve substitutions | Premature locks | Other visible | Clarify | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | entity_lock_analogue | 10/20 | 10/10 | 0/10 | 0 | 10 | 0 | 0 | 0 |
| Qwen3.5 | self_reverify_author_adaptation | 3/20 | 0/10 | 3/10 | 3 | 0 | 14 | 0 | 0 |
| Qwen3.5 | cross_reverify_author_adaptation | 10/20 | 0/10 | 10/10 | 10 | 0 | 0 | 0 | 0 |
| Qwen3.5 | exact_cta_frozen | 12/20 | 8/10 | 4/10 | 0 | 2 | 5 | 1 | 0 |
| GLM-5.1 | entity_lock_analogue | 10/20 | 10/10 | 0/10 | 0 | 10 | 0 | 0 | 0 |
| GLM-5.1 | self_reverify_author_adaptation | 10/20 | 0/10 | 10/10 | 10 | 0 | 0 | 0 | 0 |
| GLM-5.1 | cross_reverify_author_adaptation | 3/20 | 0/10 | 3/10 | 3 | 0 | 14 | 0 | 0 |
| GLM-5.1 | exact_cta_frozen | 17/20 | 7/10 | 10/10 | 3 | 0 | 0 | 0 | 0 |

## Run audit

| Verifier | Rows | Requests | Retries | Tokens |
|---|---:|---:|---:|---:|
| Qwen3.5 | 20 | 20 | 0 | 8644 |
| GLM-5.1 | 20 | 20 | 0 | 7444 |

## Interpretation

- The lock analogue is perfectly asymmetric: Preserve 10/10 and Reevaluate 0/10.
- GLM re-verification always resolves the selector on the refreshed candidates: Reevaluate
  10/10 and Preserve 0/10. This cleanly demonstrates that unconditional re-resolution
  solves the opposite half of the paired authorization problem from locking.
- Qwen re-verification selects a different visible but selector-ineligible entity on 14/20
  tasks. Its 3/20 accuracy is therefore dominated by selector grounding, not interpretable
  as a pure temporal-authorization preference.
- Frozen CTA is 12/20 for Qwen and 17/20 for GLM. It is not perfect and is not claimed to
  dominate Binding Drift's original initial-misbinding benchmark. On this smoke, it is the
  only tested policy with nonzero accuracy on both Preserve and Reevaluate for each model.

The official Binding Drift verifier normally receives a short `step1_referent`. TRI must
retain the full temporal instruction or it deletes the authorization variable under test.
This author adaptation therefore preserves the official prompt frame but is not interface-
identical to the official workflow. The Qwen grounding failures expose this limitation.
