# TRI-v7 Core Replication Protocol

Frozen on 2026-07-20 before any model output on TRI-v7 was observed.

## Purpose

TRI-v7 is an independent controlled replication of the referential core. It increases state-
instance and schema diversity rather than duplicating the original templates. Remove and
invalidate cases are excluded because human validation showed that reject/fallback behavior is
a normative policy boundary rather than settled referential semantics.

## Frozen Design

- 240 tasks, bringing the original 160-task primary inventory plus this replication to 400;
- 10 schemas not used in TRI-v3 primary or schema transfer;
- four independently parameterized state instances per schema, yielding 40 state clusters;
- balanced `anchored`/`dynamic` reference modes (120 each);
- balanced `flip`/`stable`/`name_collision` transitions (80 each);
- balanced explicit/implicit language (120 each);
- five entities per state, including valid distractors and an invalid extreme-valued distractor;
- every pre-refresh target remains present and action-valid after refresh.

The deterministic generator, not an LLM judge, computes the selector winners and gold target.
The data and smoke hashes below are filled and frozen before API execution.

## Models and Controllers

Models:

- `Qwen/Qwen3.5-122B-A10B`;
- `Pro/zai-org/GLM-5.1` after the Qwen health gate.

Controllers:

- Generic Structured Ledger;
- exact Compile-then-act (CTA);
- Lifecycle-Gated.

Temperature is zero, thinking is disabled, and maximum output tokens are 1200. Controller prompts
are reused unchanged from TRI-v3. API attempts, retries, parse errors, compiler output, and final
target are retained per row.

## Health and Stop Rules

1. Run the frozen 12-task smoke set for all three Qwen controllers.
2. Continue only if each controller has at most one API/parse failure.
3. Do not alter prompts, schemas, states, templates, or analysis after viewing smoke/full outputs.
4. Retry transport failures by task ID; never silently delete them or regenerate the dataset.
5. Run GLM after Qwen whenever the Qwen result is interpretable, including an informative null.

## Primary Estimand

For Generic Ledger, condition on a correct initial `selected_entity_id`. A core TRI event requires:

1. an anchored flip or name-collision task;
2. the old entity remains present and action-valid;
3. the final prediction changes from the correctly bound old ID to the refreshed selector winner.

The primary phenomenon statistic is this conditional drift rate. Stable anchored tasks are the
negative control. Dynamic accuracy checks that a controller does not obtain apparent safety by
always locking old IDs.

## Statistics

- exact target accuracy and API/parse failure rate;
- conditional TRI drift count/rate;
- stable-control error rate;
- anchored and dynamic accuracy;
- paired CTA-minus-Generic and Lifecycle-minus-Generic differences;
- 10,000-sample bootstrap intervals resampling all six tasks in each of the 40 state clusters.

The state cluster, not the individual templated row, is the primary resampling unit. Language-
template-cluster intervals are a secondary sensitivity analysis.

## Falsification and Interpretation

- If conditional Generic TRI drift is below 5% for both models, the original effect is not robust
  to new states/schemas and the paper must be downgraded to a narrow benchmark observation.
- Drift above 15% for at least one model, with stable error at or below 5%, supports a
  model/controller-conditional phenomenon claim.
- A high dynamic error rate means an intervention is over-locking and cannot support selective
  authorization.
- This synthetic replication does not estimate real-traffic prevalence, even if positive.

## Frozen Hashes

- full data: `2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891`;
- smoke data: `e1cb32f694024cd22884daa1b099d23053ff7dbeaaa5b68d684afcab3b61750b`.
