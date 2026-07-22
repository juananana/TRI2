# TRI-v3 Pre-Refresh Untyped Compile-Then-Act Protocol

Frozen on 2026-07-17 before any API call for this condition. This reviewer-prompted addendum
tests the strongest remaining alternative explanation: whether any pre-refresh natural-language
action plan is sufficient, without a typed lifecycle record.

## Matched Condition

The compiler runs before refresh on the original instruction, initial state, action schema, and
the fact that refresh will precede action. It returns exactly one free-form string field,
`plan`. The prompt prohibits lifecycle field names. The actor receives only that plan, refreshed
state, and action schema, matching the Lifecycle-free actor's temporal information boundary. It
does not receive the original instruction or benchmark labels.

This condition and Lifecycle-free both use two model calls per task at temperature zero with
thinking disabled and a 1,200-token output cap. The comparison changes representation only:
free-form natural-language contract versus typed lifecycle state.

## Frozen Files

- Runner SHA-256: `3a4efeb7b83385f267d5abdd6b6820f3081e12f15c734680709d6738e1cfa610`
- Qwen smoke source: `bd67fdbeb61a432fcf66354902bd55fec29032bfde725c51194fa7280dee504d`
- Qwen full source: `ab61e7957b07a0e1b7161561ffec7a1a006cbac9e8169323fd39b1a37a512b76`
- GLM smoke source: `ae22f11c3208c853040e937464d2954f9950e99a234f45c33fa03d23074ffeee`
- GLM full source: `07a44b564932e7f5fe43a7f6d865f152970745ca093fb9eb8b878c9410236d41`

## Run Gate and Estimands

Run each 20-task balanced smoke first. Expand a model only if the smoke has at most one API or
parse failure. Do not change prompts after smoke inspection. Full evaluation uses all 160 frozen
primary tasks and reports overall, anchored, dynamic, template-macro accuracy, template-cluster
95% intervals, and paired effects against Generic-free and Lifecycle-free.

## Interpretation Rule

- If untyped planning matches Lifecycle-free within 2--3 points with a paired cluster interval
  containing zero, reposition the contribution as pre-refresh commitment compilation rather
  than necessity of the full typed tuple.
- If typed lifecycle is materially better, claim only that explicit typed state outperforms this
  matched free-form plan in the controlled scalar setting; do not claim mathematical minimality.
- Any API or parse failure remains a failure in the intention-to-treat result.
