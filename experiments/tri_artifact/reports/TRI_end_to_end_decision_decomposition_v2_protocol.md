# TRI End-to-End Decision Decomposition v2 Protocol

**Evidence status:** planned post-primary experiment, frozen before model calls.

**Protocol version:** `TRI-end-to-end-decision-decomposition-v2`.

## Question and claim boundary

This experiment separates timing information from repeated values, structured presentation, and
an explicit follow directive. It estimates interface-level causal contrasts on one frozen authored
inventory. It does not identify an internal model mechanism, a uniquely necessary field, natural
prevalence, or open-language transfer.

No model call may begin until this protocol, the inventory hash, prompts, parser, contrasts,
failure policy, runner, reporter, and tests are frozen. Negative, null, mixed, and harmful results
remain in intention-to-treat (ITT) reporting.

## Frozen inventory and models

- Inventory: `data/call_matched_authorization_ablation_v1.jsonl`.
- SHA-256: `5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c`.
- Scope: 80 rows forming 40 changed-winner Preserve/Reevaluate pairs.
- Models: `Qwen/Qwen3.5-122B-A10B`, `Pro/zai-org/GLM-5.1`, and
  `deepseek-ai/DeepSeek-V4-Pro`.
- Temperature 0; thinking disabled; maximum completion 500 tokens.
- Retry only HTTP 429, HTTP 5xx, network, connection, and timeout errors, at most two retries.

## Shared compiler

The compiler sees only the instruction, raw S0, selector, action, and action schema. It returns:

- `reference_mode` (`preserve` or `reevaluate`);
- `pre_refresh_candidate_id`, a non-null model-produced S0 selector winner for every row;
- `bound_target_id`, equal to the candidate for Preserve and null for Reevaluate; and
- a selector restatement.

No actor receives a resolver-produced initial ID, gold mode, gold target, or derived answer. A
compiler failure does not prevent History-only or Placebo from running; compiler-dependent cells
are recorded as upstream ITT failures.

## Eight matched actor cells

All actors receive byte-identical base payloads: instruction, raw S0/S1, selector, action, and
action schema. They share one compiler call per task and differ only by the following addition:

| Cell | Addition |
|---|---|
| `history_only` | none |
| `placebo` | structured repetition of action, schema, and state counts; no target-resolution information |
| `selector_only` | compiler selector restatement only |
| `id_control` | neutral model-produced `pre_refresh_candidate_id` on every row |
| `mode_only` | `reference_mode` only |
| `mode_plus_id` | `reference_mode` and `bound_target_id` |
| `mode_plus_id_selector` | complete timing fields, no follow directive |
| `full_follow` | complete timing fields plus an explicit directive to follow them |

An original `bound_target_id`-only cell is excluded because null on Reevaluate rows reveals mode.
The neutral ID control tests ID repetition without that leak. Actor order rotates by task index
modulo eight; each cell occupies each ordinal position exactly ten times over 80 rows.

Each task plans nine logical calls (one compiler and eight actors): 720 per model and 2,160 over
the three-model full matrix. Provider-reported prompt, completion, total, cache-hit, and cache-miss
tokens are retained and summarized by cell; exact token equality is not assumed.

## Frozen endpoints and contrasts

Primary endpoints are changed PairAcc and row E2E over all 40 pairs/80 rows. Preserve conditional
substitution is restricted to Preserve rows where the compiler mode and candidate/bound ID are
correct and the old target survives action-valid while the winner changes. API, parse, schema,
upstream, and missing-output failures are incorrect under ITT.

Frozen right-minus-left contrasts are:

1. Placebo - History-only;
2. Selector-only - History-only;
3. ID-control - History-only;
4. Mode-only - History-only;
5. Mode+ID - Mode-only;
6. Mode+ID+selector - Mode+ID;
7. Full-follow - Mode+ID+selector; and
8. Full-follow - Placebo.

For each cell and contrast report PairAcc, E2E, conditional substitution, repairs, harms,
API/parse/upstream failures, calls, retries, wall time where available, and token usage.

## Inference and promotion gate

- Cluster bootstrap unit: `state_cluster_id`; 10,000 percentile replicates; seed `20260729`.
- Two-sided paired `state_cluster_id` sign-flip tests are auxiliary.
- Holm correction applies within each model across the fixed 24 contrast-endpoint tests; an
  unavailable endpoint enters the family with adjustment value one rather than shrinking it.
- No pooled model significance test and no accuracy-based stopping rule.

A field-level contrast may enter the main claim only when its PairAcc 95% interval is strictly
positive in at least two of three models and no model has a strictly negative interval. The
composite timing-interface claim uses Full-follow minus Placebo under the same rule. Otherwise the
result remains model-specific or package-level. These rules do not promote architecture necessity,
internal mechanisms, open-language transfer, or prevalence.

## Required artifacts

Retain raw JSONL, every credential-free request and response, usage records, task/prompt/protocol/
implementation hashes, crash-safe resume provenance, a machine-readable report, Markdown report,
claim-promotion report, and tests for all invariants above. Credentials must never be recorded.
