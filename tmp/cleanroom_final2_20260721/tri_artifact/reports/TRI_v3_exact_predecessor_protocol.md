# TRI-v3 Exact Historical Compile-Then-Act Protocol

Frozen on 2026-07-17 before any API call for this v3 condition.

## Question

Does the exact `compile_then_act` controller used in the earlier TRI experiments already solve
the frozen 160-task TRI-v3 primary set? This is a reviewer-requested predecessor audit. It is
not a new prompt variant and must not be modified after inspecting smoke or full outputs.

## Controller and Fairness Boundary

The experiment calls `run_compile_then_act` in `tri/run_models.py` without changing either
prompt. Before refresh, its compiler receives the instruction, initial state, and the fact that
a refresh will precede action. It emits `binding_time`, `selector`, `bound_target_id`, and a
free-form reason. After refresh, its actor receives that ledger and the refreshed state.

The predecessor and Lifecycle-free both use two model calls, the same pre-refresh compilation
boundary, temperature zero, disabled thinking, and a 1,200-token output cap. They are not a
strict representation-only match: the historical actor does not receive the action schema and
its preserve rule rejects only a missing entity, not a present but action-invalid entity. The
comparison therefore tests historical-method coverage, not the isolated necessity of every
lifecycle field.

## Frozen Inputs

- Primary data: `data/temporal_referent_v3_language_clusters.jsonl`
- Primary data SHA-256: `bea0b48c5092e64fd3860069a5a81f09982940ca0b964b297d2e8a8f7f5970d6`
- Runner SHA-256: `a71a68dc2f07579485833a2a361c50071430fa209f5654a9687402bfb2284afb`
- Historical controller: `run_compile_then_act`
- Models: `Qwen/Qwen3.5-122B-A10B` and `Pro/zai-org/GLM-5.1`

The historical controller was already listed as a secondary comparison in
`reports/TRI_v3_preregistered_protocol.md` before the original v3 model calls.

## Run Gate

Run the first four frozen tasks only as an API/parse health check for each model. Expand to all
160 tasks if there is at most one API or parse failure. Do not inspect task accuracy to change
the prompt, parameters, data, or interpretation rules. The health-check rows are not combined
with the full run.

## Metrics and Pre-Specified Comparisons

Report intention-to-treat exact-target accuracy overall and by binding mode, update type,
explicitness, and template cluster. Report API failures separately. Use 10,000 resamples of the
20 complete template clusters with seed 20260717. Pair the exact predecessor separately against
the matched untyped pre-refresh plan and Lifecycle-free for each model.

## Interpretation Rules

- If the exact predecessor matches Lifecycle-free and the paired cluster interval includes zero,
  position the contribution as pre-refresh referential compilation and executable semantics;
  do not claim that the full lifecycle tuple is empirically necessary.
- If it is weaker mainly on present-but-invalid Preserve cases, attribute the difference to
  post-binding action validity and invalidity policy, not to generic benefits of typed state.
- If it is weaker on Flip or Name-collision cases, inspect compilation and actor traces before
  attributing the failure to binding-time semantics.
- API and parse failures remain failures in intention-to-treat accuracy and are also disclosed.
- No prompt or task changes are permitted after any output is observed.
