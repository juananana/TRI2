# TRI Convention-Told Natural-History Control

Status: **planned/unverified**. This protocol is frozen before any condition-specific smoke or
full call. It addresses a representation alternative on an existing authored inventory; it does
not repair the unavailable independent-human holdout or establish open-language validity.

## Question

Does an explicit natural-language convention improve selective re-resolution when both conditions
receive the same natural history and neither receives a structured ID record, parsed reference
mode, compiler decision, or deterministic gate?

The contrast separates a general discourse convention from the existing composite
Decision-visible block. It does not test whether a particular field is necessary.

## Frozen inventory

Use the existing 80-row/40-pair Flip inventory:

- `data/call_matched_authorization_ablation_v1.jsonl`;
- SHA-256 `5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c`;
- 40 state clusters, each with one Preserve and one Reevaluate row;
- Qwen3.5-122B-A10B and GLM-5.1;
- temperature 0, thinking disabled, 1,200 output-token cap.

Gold remains the authored frozen task gold. No claim may call this human-majority or
open-language evidence.

## Equal-call conditions

Each condition makes exactly one final actor call per task. Both receive byte-identical user
payloads containing only:

- `original_instruction`;
- `initial_state_before_refresh`;
- `current_refreshed_state`;
- `action_schema`;
- `question: Which target_id should be processed now?`.

Neither payload contains `initial_selected_id`, `bound_target_id`, `reference_mode`, design
metadata, pre/post winner IDs, gold, or a compiler output.

### Plain-history

System prompt:

> You are an agent controller deciding the final target after an environment refresh. You receive
> the original user instruction, the initial state observed before refresh, and the refreshed
> state. Use the user instruction and states to choose the final target. Return JSON only:
> `{"action":"process","target_id":"..."}` or
> `{"action":"invalid","target_id":"INVALID_BOUND_ENTITY"}`.

### Convention-told

The system prompt is identical except that it adds this frozen convention before the output
instruction:

> If the user selected or referred to a specific entity before the refresh, keep that entity as
> long as the requested action remains valid. If the user explicitly postponed selection until
> after the refresh, recompute the selector on the refreshed state.

The earlier `full_history_once` baseline motivated this wording but is not reused as an outcome in
the new contrast. Both conditions must be rerun under this protocol. Condition order alternates by
task index, preventing a perfect condition--time confound.

## Execution gate

1. Zero-API validation: exact inventory census, prompt diff, forbidden-field scan, output parser,
   and PairAcc denominator.
2. Smoke: the frozen first eight pairs, 16 rows per condition and model (64 calls total).
3. Continue only if every cell has all 16 rows, at most one API/parse failure, no forbidden field,
   and no systematic output-format failure. Accuracy direction is not a gate.
4. Full: all 80 rows per condition and model; retain every attempted row under ITT.

## Estimands

Primary:

- Convention-told minus Plain-history changed-winner PairAcc, separately by model, with 10,000
  state-cluster bootstrap samples and seed 20260728.

Secondary:

- Preserve and Reevaluate marginal accuracy;
- exact-target E2E;
- refreshed-winner choice on Preserve rows and old-target choice on Reevaluate rows;
- Stable is unavailable in this Flip-only inventory and must not be inferred;
- API, parse, schema, rejection, requests, retries, latency, and tokens.

Because neither condition exposes a separately scored pre-refresh binding, its refreshed-winner
rate is unconditional and must not be called conditional TRI.

## Interpretation

- A positive PairAcc effect shows that a general natural-language convention helps on this
  authored inventory without a structured ID record.
- A null or model-dependent effect leaves the representation question unresolved.
- Even a strong effect would narrow the implementation claim: it would support the normative unit
  test and discourse convention, not the necessity of CTA or typed state.
- No result from this experiment repairs native prevalence, independent human gold, or
  open-language generalization.
