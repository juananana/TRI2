# TRI Call/Information-Matched Authorization Ablation Protocol

**Evidence status:** post-primary ablation. This amended protocol is frozen before the corrected
model run. The initial four-task transport smoke is invalid infrastructure output and is excluded
from all results.

**Freeze date:** 2026-07-25. Before the corrected run, zero-API review removed a gold-label
dependency from the enforcement definition; the rule below depends only on the compiler output.
An initial smoke using the provider default returned empty `content` with the completion cap
exhausted by reasoning on all four compiler calls. The corrected transport explicitly sends
`enable_thinking=false`; this changes no task, prompt, condition, metric, denominator, or stopping
rule. The four failed rows are retained as infrastructure provenance, not evidence.

**Corrected run version:** `TRI-call-matched-authorization-ablation-v2`. Corrected raw files use
the `_v2.jsonl` suffix; the failed `_v1.jsonl` smoke remains unchanged.

## Question

Does exposing a compiler's frozen referent-transition decision to an otherwise matched actor
reduce changed-pair failures and Preserve substitutions? A third, deterministic outcome asks what
would happen if a narrow Preserve decision were enforced after the decision-visible actor call.
The experiment controls logical call count and actor-visible task information across the two actor
conditions. It does not isolate every effect of compiler prompting, textual decision
representation, or deterministic enforcement, and the enforced outcome is not a complete causal
estimate of a runtime architecture.

The frozen `initial_selected_id` is supplied equally to the compiler and both actor conditions.
This is an observable-binding intervention: it isolates post-binding resolution timing and does
not measure whether a model can ground the initial selector. No condition receives the final gold
target or the gold reference mode.

## Frozen inventory and automatic selection

- Source: `data/temporal_referent_v7_core_replication.jsonl`
- Source SHA-256: `2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891`
- Selection rule: parse every source row; retain every row whose `update` is exactly `flip`;
  require exactly 40 distinct `state_cluster_id` values and exactly one `anchored` and one
  `dynamic` row in each cluster. Map `anchored` to Preserve and `dynamic` to Reevaluate. Sort by
  `state_cluster_id`, then Preserve before Reevaluate. No task, domain, template, or example may
  be selected or excluded manually.
- Frozen output: `data/call_matched_authorization_ablation_v1.jsonl` (80 rows). The builder records
  the source and output hashes in its stdout. The output hash is inserted in the freeze manifest
  below after zero-API construction and before any API call; this metadata insertion does not
  change the design.

### Freeze manifest

- Task-file SHA-256: `5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c`
- Rows: 80
- State clusters: 40
- Pairing: one Preserve/Reevaluate pair per state cluster

## Conditions and call matching

For each model and task, the runner makes exactly three logical calls when no call fails:

1. One shared compiler call. It returns JSON fields `reference_mode`, `bound_target_id`, and
   `selector`. Allowed modes are `preserve` and `reevaluate`.
2. One History-only actor call.
3. One Decision-visible actor call.

The two actors receive the same system prompt and the same task payload: original instruction,
deterministic S0 summary, initial selected ID, refreshed S1 state, selector text, action, and action
schema. The only condition difference is that Decision-visible also receives the exact parsed
compiler decision block from call 1. History-only receives no placeholder or alternative decision
text. Actor calls are issued in deterministic alternating order by task index (History-only first
for even task indices, Decision-visible first for odd indices) to avoid perfect confounding with
call order. The compiler output is stored once and referenced by both conditions.

The deterministic Decision-enforced outcome reuses the Decision-visible actor prediction and adds
no model call. When the compiler output is `preserve`, its final target is the compiled
`bound_target_id`; when the compiler output is `reevaluate` or unavailable, its final target is the
Decision-visible actor target. The executor never receives the gold reference mode. Enforcement
can therefore repair or harm an outcome when the compiler is right or wrong. The report records
both directions and actor disagreement.

## Frozen prompts

### Compiler system prompt

```text
Compile the instruction's target-resolution timing. Use reference_mode="preserve" when the
instruction selects or identifies the action target before refresh and later refers to that
entity. Use reference_mode="reevaluate" when refresh happens before target selection. For
preserve, return the concrete initial selected ID as bound_target_id. For reevaluate, return null
as bound_target_id. Copy the task's selector meaning without changing its timing. Return one JSON
object only with exactly these keys: reference_mode, bound_target_id, selector.
```

Compiler user payload fields: `instruction`, `s0_summary`, `initial_selected_id`, `selector`,
`action`, `action_schema`, and `refresh_notice` (fixed to `State S1 is observed after refresh and
before the action.`).

### Shared actor system prompt

```text
Choose the entity ID for the requested action. Use the instruction and supplied states exactly.
The initial_selected_id is the entity selected by the stated selector in S0. S1 is the state after
refresh. If a compiler_decision field is present, follow that decision when resolving whether the
initial entity is preserved or the selector is reevaluated. Return one JSON object only with
exactly these keys: action, target_id.
```

Both actor payloads contain `instruction`, `s0_summary`, `initial_selected_id`, `s1_state`,
`selector`, `action`, and `action_schema`. Decision-visible alone adds `compiler_decision`.

## Models and API settings

- Endpoint: `https://api.siliconflow.cn/v1`
- Models:
  - Qwen: `Qwen/Qwen3.5-122B-A10B`
  - GLM: `Pro/zai-org/GLM-5.1`
- Credential source: runtime environment variable `LLM_API_KEY` only. The runner must exit before
  network access when the variable is absent or blank. Keys are never written to tasks, runs,
  reports, prompts, or error messages.
- Temperature: 0
- Maximum completion tokens: 500 per logical call
- Timeout: 180 seconds per HTTP attempt
- Retries: at most 2 retries after the initial attempt (3 HTTP attempts total), only for HTTP 429,
  HTTP 5xx, URL/network errors, timeouts, and connection errors
- Retry backoff: 2 seconds, then 4 seconds
- Thinking parameter: explicitly disabled (`enable_thinking=false`) for both models. This is a
  provider transport repair after the invalid empty-content smoke; it is fixed for all corrected
  health and full runs.
- Parsing: one top-level JSON object; fenced JSON is accepted; required keys and allowed values are
  schema checked. Target IDs use the existing `normalize_target` convention.
- Raw retention: the run JSONL records every HTTP attempt, including request messages without the
  credential, timestamps, status/error, raw successful content, response usage, and parse result.

## Zero-API validation, health smoke, and stopping rule

The builder, dry-run, report fixtures, and tests run without a credential or network access.
Dry-run must show 80 tasks, 40 complete pairs, one compiler plus two actor calls per task, identical
base actor payloads, and one shared compiler decision identifier.

Before a full model run, run the automatically selected first two sorted state clusters (four
tasks) for that model. Full execution is allowed only when all four tasks complete all three
logical calls, all 12 calls return valid JSON, every compiler decision is shared by the two actor
conditions, and the output passes the same structural validator used by the report. Any API,
schema, or parse failure stops the smoke or full run after the current task and blocks the full run
for that model. Remaining rows are retained as explicitly unattempted; failures are not silently
repaired or excluded.
There is no accuracy threshold in the smoke gate.

## Estimands

All failures remain in intention-to-treat (ITT) denominators and count as incorrect.

### Primary

1. **Changed PairAcc**, separately for History-only, Decision-visible, and Decision-enforced: the
   proportion of 40 state clusters for which both Preserve and Reevaluate final targets equal
   their gold targets. Report paired condition differences.
2. **Preserve conditional substitution**, separately by outcome: among Preserve rows where the
   shared compiler returns mode `preserve` and the correct `pre_refresh_target` as
   `bound_target_id`, the proportion whose final target equals the distinct
   `post_refresh_target`. Report numerator and denominator. This conditional estimand is shown
   alongside, not in place of, ITT PairAcc.

### Secondary

- Row-level E2E accuracy (ITT) by condition and reference mode.
- Compiler mode accuracy; Preserve binding accuracy; joint mode-and-binding accuracy.
- History-only versus Decision-visible shadow actor target disagreement.
- Decision enforcement repairs (`visible` wrong, `enforced` correct) and harms (`visible` correct,
  `enforced` wrong), plus other changed outcomes.
- API failure, parse/schema failure, and incomplete-task counts in ITT denominators.
- Logical calls, HTTP attempts, retries, and token usage by model and condition.

## Inference and reporting

- Evidence label in every report: `post-primary`.
- Resampling unit: `state_cluster_id`; the Preserve/Reevaluate pair and all three outcomes remain
  together.
- Bootstrap: 10,000 replicates with seed `20260725`.
- Report percentile 95% intervals for each metric and paired differences. No global multiplicity
  correction is applied; secondary intervals are descriptive.
- Results are reported for each model and pooled only as a clearly labeled descriptive summary.
- Negative, null, mixed, API-failure, and enforcement-harm results are retained.

## Permitted deviations

Only infrastructure repair that does not alter inventory, prompts, model identifiers, endpoint,
API settings, conditions, metrics, seed, or stopping rule is permitted. Any other change creates a
new protocol/version and the present run remains reported as designed.
