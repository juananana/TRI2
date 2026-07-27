# TRI Model-Authored Linguistic Stress-Test Protocol

**Evidence status:** post-primary model-authored linguistic stress test. This is neither
independent human evidence nor a primary, confirmatory, or natural-workflow experiment.

**Freeze date:** 2026-07-26, before any authoring-model request. The experiment addresses a
review-critical template-shortcut concern after the primary analyses. It cannot be relabeled as
primary/frozen evidence for the original paper claim.

## Claim and excluded explanation

The test asks whether the controlled TRI contrast and controller ordering survive instructions
written by a model that did not receive the paper's original instructions, template inventory,
Rule* cue list, model outputs, or controller failures. It probes dependence on the authors'
surface templates and ten v7 schemas.

It does not exclude dependence on model-generated prose, shared pretraining, explicit semantic
briefs, the controlled changed-winner construction, or the supplied structured states. It does
not estimate real-traffic prevalence, native benchmark coverage, human interpretation, or
performance on naturally occurring workflows.

## Frozen semantic inventory

- File: `data/model_authored_linguistic_semantics_v1.jsonl`
- SHA-256: `50407590a7c06355ec44b82beaa6334782dcb95ce5161f1a1351516f7a0c45ed`
- Inventory: 24 distinct workflow domains and 24 state schemas. Each specification has one
  numeric selector field, three action-valid entities, a unique S0 winner, and a different S1
  winner. The S0 winner remains present and action-valid after the update.
- Derived task inventory: two instructions per specification, one Preserve and one Reevaluate,
  for 48 all-actionable rows and 24 opposite-gold pairs. Gold targets follow mechanically from
  the frozen event order and states. No authoring or judge output determines gold.
- Excluded slices: Reject/fallback policy, removed targets, invalidated targets, Stable winners,
  multi-role composition, and prevalence sampling.

The deterministic builder validates all winners, action preconditions, pair membership, and gold
targets. Authoring failures remain in the 48-row intention-to-treat denominator with a null
instruction and no controller request.

## Model authoring

- Model: `deepseek-ai/DeepSeek-V4-Pro`
- Endpoint: `https://api.siliconflow.cn/v1`
- Temperature: 0; thinking disabled; maximum 700 completion tokens.
- Author prompt SHA-256: `9afe6960c6f0ecc10d171d87228be6dc2fefe392effedf41f9811c21a119c9b0`.
- Input: domain, entity type, selector meaning, action, update meaning, linguistic style, and the
  two semantic event orders. The authoring model does not receive entity IDs, original TRI
  instructions, Rule* patterns, prior outputs, controller prompts, or failures.
- Output: exactly one `preserve_instruction` and one `reevaluate_instruction` per specification.
  Any API, JSON, schema, or minimum-length failure is retained and marks both derived rows as
  authoring failures. There is no regeneration or manual editing.

Requested forms rotate across multi-sentence requests, parentheticals, context followed by a
request, corrections, and nominalized update events. These labels constrain generation; they are
not independent linguistic categories inferred after seeing outputs.

## Model-assisted validity audit

Qwen (`Qwen/Qwen3.5-122B-A10B`) and GLM (`Pro/zai-org/GLM-5.1`) independently audit all 48
generated instructions. The frozen judge prompt hash is
`d45b13c9507128e6b1c37c8e210eb416f71b480f7532c74c23921a8c2709090b`. Each judge classifies
resolution timing and checks selector fidelity, action fidelity, and ambiguity. A row enters the
dual-judge-valid sensitivity subset only when both valid responses match the deterministic mode
and mark all three checks true. A pair enters that subset only when both rows pass both judges.

Judge disagreement, API failure, and parse failure are reported. The all-generated 48-row and
24-pair ITT estimates remain primary for this addendum. The dual-judge subset is a model-assisted
sensitivity analysis, not independent annotation.

## Frozen controllers and rule

For Qwen and GLM, run the unchanged implementations in `tri/run_models.py`:

1. Generic Structured Ledger (`run_generic_structured_ledger_then_act`);
2. Historical Compile-then-act (`run_compile_then_act`, called CTA in reports).

The frozen source SHA-256 is
`f394c3c55df77d064f7dd106850b1d65ded59dc5748ba60e3eb8e673525f7932`. Both use temperature
zero, thinking disabled, and a two-call plan/compile then act sequence. The controller prompts,
parsers, and action logic may not be changed after authoring begins.

Run the already disclosed post-hoc Rule* without changing its cue list or logic. Its frozen source
SHA-256 is `34cbbd39072bd5d473768666bad684c9d5e491b830df6a6b6ebcb98abd1bbfb8`.
Rule* performance on this distribution is reported whether positive, negative, or unresolved.

## Staging, retries, and stopping

All API stages use a 180-second timeout and at most two retries after the initial request, only
for HTTP 429, HTTP 5xx, URL/network errors, timeouts, and connection errors. Backoff is two then
four seconds. Every HTTP attempt, credential-free request body, raw successful content, parse
result, usage record, and error is retained in JSONL. Credentials come only from
`SILICONFLOW_API_KEY` or `LLM_API_KEY` and are never serialized.

1. Zero API: build and validate 24 semantic specifications; run unit tests and Rule* fixtures.
2. Author smoke: first two sorted specifications. Full authoring is blocked unless both calls
   complete and parse.
3. Full authoring: all 24 specifications. Retain all rows; do not regenerate failures.
4. Freeze derived 48-row task file and record semantic, authoring, task, prompt, protocol, and
   controller hashes before judge or controller requests.
5. Judge smoke: first two pairs, separately for each judge. Full judging for that model is blocked
   unless all four rows complete and parse.
6. Controller smoke: first two pairs, separately for each model and controller. A full condition
   is blocked unless all four rows complete both logical calls without API or parse failure.
7. Full judge and controller runs continue through all rows. Any later failure remains incorrect
   in ITT; no result-triggered retries, exclusions, prompt changes, or task edits are allowed.

## Frozen estimands

Report separately for each model/controller and for Rule*:

- all-generated row accuracy and changed-winner PairAcc;
- dual-judge-valid row accuracy and PairAcc, with retained subset denominators;
- Preserve conditional substitution among rows where the controller's observable initial binding
  equals the deterministic S0 winner;
- Preserve and Reevaluate row accuracy;
- API, parse, authoring, and judge failures;
- controller call/attempt/retry counts;
- Generic-versus-CTA paired row discordances and state-cluster bootstrap differences in PairAcc.

Bootstrap complete state pairs with replacement, 10,000 draws, seed `20260726`. Intervals and
tests are descriptive; no global multiplicity correction is applied.

## Decision rule

- **Strengthen the bounded conclusion:** both evaluator families retain a positive CTA-minus-
  Generic PairAcc difference on all-generated ITT and on the dual-judge-valid subset, while
  Generic retains nonzero conditional substitution.
- **Narrow it:** effects are mixed by model, disappear on the valid subset, most generated rows
  fail fidelity checks, or Rule* remains competitive. Report the exact failure and restrict the
  conclusion to the successful model/distribution.
- **Overturn language robustness:** both evaluator families show no positive PairAcc difference,
  or the inventory cannot pass the frozen generation/validation gates. Retain the result and do
  not use this addendum as support.

Regardless of outcome, the strongest permitted statement is performance on a frozen,
model-authored linguistic distribution. The experiment cannot be cited as independent open
language, human validation, native workflow evidence, or benchmark prevalence.
