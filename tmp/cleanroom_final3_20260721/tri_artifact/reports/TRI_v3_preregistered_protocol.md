# TRI-v3 Pre-Registered Evaluation Protocol

Frozen on 2026-07-17 before any model call on the TRI-v3 datasets.

## Research Questions

1. Does lifecycle-gated control outperform a call-matched generic structured ledger that
   stores entity identity, entity state, selector, and action preconditions but omits
   reference mode and invalidity policy?
2. Does the result persist across independent language-template clusters?
3. Does it transfer to unseen domains, entity fields, IDs, selectors, and action schemas?
4. How do target errors translate into database writes, blocked invalid attempts, and
   unnecessary rejections?

## Frozen Datasets

- `data/temporal_referent_v3_language_clusters.jsonl`
  - 160 tasks;
  - 20 independent template clusters;
  - 8 domains per cluster;
  - 40 tasks per style, with update types balanced within style.
- `data/temporal_referent_v3_unseen_domains.jsonl`
  - 80 tasks;
  - four unseen domains: project management, expense approval, inventory, and cloud deployment;
  - new IDs, fields, selectors, actions, and action preconditions;
  - 20 independent template clusters.

Frozen SHA-256 hashes after grammar validation and before API execution:

- language clusters: `bea0b48c5092e64fd3860069a5a81f09982940ca0b964b297d2e8a8f7f5970d6`;
- unseen domains: `6a42f556d6cb176575070475855549b85c08b063c8b0b75b0ee40663770aca61`;
- balanced smoke: `1c307e2d9de34a62e2412c61685f775b0e035481674f63ae863d1a72b919b0aa`;
- model runner: `f36bbd7252b2a728736227daef9d21a325265c801f44dfc5f925420a761ef8af`.

## Controllers

Primary comparison:

- `generic_structured_ledger_then_act`
- `factorized_hybrid_compile_then_act` (Lifecycle-Gated Controller)

Secondary comparisons, budget permitting:

- `generic_plan_then_act`
- `compile_then_act`
- `state_overwrite_once`

All two-stage methods use two LLM calls except preserved lifecycle targets resolved by the
deterministic gate, for which the second actor call is skipped.

## Models and Inference

- Qwen3.5-122B-A10B is run first.
- GLM-5.1 is run only after Qwen smoke tests pass and the primary comparison is informative.
- Temperature 0, thinking disabled, maximum output tokens 1200.
- API retries are logged; API errors are excluded from model-behavior interpretation and
  retried by task ID rather than triggering full reruns.

## Run Gates

1. Balanced smoke subset: 20 tasks, crossing four styles and five update types.
2. Proceed to full Qwen only with at most one API/parse failure per controller.
3. Proceed to GLM only if Qwen results expose a real controller difference or a scientifically
   useful negative result.
4. Do not modify controller prompts after inspecting any TRI-v3 model output.

## Primary Metrics and Statistics

- safe target resolution;
- wrong-target attempt rate;
- wrong-entity database write rate;
- invalid-target attempt rate;
- unnecessary rejection rate;
- final database state success;
- task accuracy and template-level macro accuracy;
- 10,000-sample cluster bootstrap confidence intervals, resampling whole template clusters.

The pre-specified primary statistical contrast is Lifecycle-Gated Controller minus Generic
Structured Ledger on the 20-cluster language set. Task-level McNemar tests are secondary.

## Interpretation Limits

- The language-cluster set improves template independence but reuses the original eight domain
  schemas and transition generator.
- The unseen-domain set tests schema transfer but remains synthetic.
- SQLite replay measures real mutation consequences of model-selected IDs, not an external
  benchmark or unconstrained end-to-end agent.
- No claim of universal agent reliability will be made from these evaluations.
