# TRI End-to-End Decision Decomposition Protocol

**Evidence status:** post-primary experiment frozen before model calls.

**Freeze date:** 2026-07-28 (Asia/Shanghai).

**Run version:** `TRI-end-to-end-decision-decomposition-v1`.

## Question and scope

The existing matched-call study exposes a composite compiler block. This experiment asks which
ordered serialization increment is associated with actor performance when the compiler must infer
the timing decision and any Preserve binding directly from the instruction and raw S0.

The five actor cells form an additive ladder. The fields are logically dependent: a bound ID and
selector are interpreted in light of the mode, and the follow directive refers to the complete
block. The experiment therefore estimates the frozen ordered increments below. It does not
identify orthogonal causal effects, every field interaction, or a unique internal mechanism.

No actor receives a resolver-produced `initial_selected_id`, gold mode, gold target, or derived
answer. One compiler output is shared by all five actor cells for a model-task.

## Frozen inventory

- File: `data/call_matched_authorization_ablation_v1.jsonl`
- SHA-256: `5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c`
- Rows per model: 80
- Matched changed-winner pairs per model: 40
- Required structure: one Preserve and one Reevaluate row per `state_cluster_id`
- Selection: all rows in file order; no task-level exclusion

The runner verifies the file hash, row count, unique IDs, pair count, opposite modes, and changed
winner before a dry run, smoke, or full run.

## Models and calls

- Qwen: `Qwen/Qwen3.5-122B-A10B`
- GLM: `Pro/zai-org/GLM-5.1`
- Endpoint: `https://api.siliconflow.cn/v1`
- Credential source: runtime `LLM_API_KEY` only
- Temperature: 0
- Maximum completion tokens: 500
- Timeout: 180 seconds per HTTP attempt
- Retries: two after the initial attempt, only for HTTP 429, HTTP 5xx, network, timeout, or
  connection errors
- Retry backoff: 2 seconds, then 4 seconds
- Provider reasoning parameter: `enable_thinking=false`

Each model-task plans six logical calls: one compiler and five actors. A full run therefore plans
480 calls per model and 960 across Qwen and GLM. Every HTTP attempt, retry, raw successful content,
parse result, usage record, task hash, model-ID hash, protocol hash, and prompt hash is retained.
Credentials are never recorded.

The endpoint and API-settings manifest is hashed as one canonical JSON object. Every row records
that settings hash, the exact runner and analysis-module source hashes, a record-format version,
the Python implementation/version, and a credential-free run-session identifier. These fields
are transport provenance; they do not alter the frozen prompts, task projection, retry policy, or
estimands. Validation also reconstructs the request and checks the recorded model, message roles,
literal system prompt, temperature, token limit, and reasoning switch rather than trusting the
hash manifest alone.

## Shared compiler

The compiler sees only `instruction`, raw `s0_state`, `selector`, `action`, and `action_schema`.
It returns exactly `reference_mode`, `bound_target_id`, and `selector`. Preserve requires a
non-null S0 ID; Reevaluate requires a null bound ID.

### Compiler system prompt

```text
Compile target-resolution timing directly from the instruction and S0. Use
reference_mode="preserve" when the instruction selects or identifies the action target before
refresh and later refers to that entity. Use reference_mode="reevaluate" when refresh occurs
before target selection. For preserve, resolve the selector in S0 and return that concrete ID as
bound_target_id. For reevaluate, return null as bound_target_id. Restate the selector without
changing its meaning or timing. Return one JSON object only with exactly these keys:
reference_mode, bound_target_id, selector.
```

Compiler-system SHA-256:
`b0d7d568bc8955dd8d5b788f26e76aebf4fa95223a7832919c4c4de9f6ba3e3c`.

## Matched actor ladder

All actors receive the same system prompt and base payload: `instruction`, raw `s0_state`, raw
`s1_state`, `selector`, `action`, and `action_schema`. They differ only as follows:

| Cell | Compiler fragment | Explicit follow directive |
|---|---|---|
| H / `history_only` | none | none |
| M / `mode_only` | `reference_mode` | none |
| MI / `mode_plus_id` | `reference_mode`, `bound_target_id` | none |
| MIS / `mode_plus_id_selector` | `reference_mode`, `bound_target_id`, `selector` | none |
| MISF / `full_follow` | `reference_mode`, `bound_target_id`, `selector` | yes |

There are no placeholders in omitted cells. Actor order is rotated by `task_index mod 5`, so every
cell occupies every ordinal position equally often over 80 rows.

### Actor system prompt

```text
Choose the entity ID for the requested action from the instruction and supplied states. Some
payloads include a partial compiler_fragment as additional context. Only a separately supplied
follow_instruction explicitly directs you to follow that fragment. Return one JSON object only
with exactly these keys: action, target_id.
```

Actor-system SHA-256:
`9926e5acb1459fd436f816f2a0eb3102f605e754adbcc2022cfd829fe42fb927`.

### MISF follow instruction

```text
Follow the complete compiler_fragment when deciding whether to preserve its bound target or
reevaluate its selector.
```

Follow-instruction SHA-256:
`fe800777d103c07e6def98c50c699215dc7c6e5abf0fbb2f38c06ac96dbc8772`.

## Parsing, failures, and run gate

Each response must be one JSON object. Fenced JSON is accepted. Required keys, mode values, null
rules, and normalized target IDs are schema checked. No parser repair is allowed.

The smoke uses the first four frozen rows and plans 24 logical calls per model. A full run for a
model is permitted only when all 24 smoke calls return and parse successfully and the structural
validator confirms the shared compiler, actor ladder, payload matching, and rotation.

The full run has no accuracy-based stopping rule. It writes one record for each of all 80 tasks.
An actor failure does not prevent later actor cells or later tasks from running. If the compiler
fails, History-only still runs because it has no compiler dependency; M, MI, MIS, and MISF are
recorded as upstream failures, and execution continues with the next task. API, parse, schema, and
upstream failures count as incorrect in all ITT endpoints. No failed output is retried at the
logical-call level or replaced with gold-derived content.

### Crash-safe persistence and resume

The runner holds an exclusive lock on one output JSONL, appends only the next frozen task in file
order, flushes, and calls `fsync` after every completed task row. On restart it validates every
persisted row against the current protocol, task-file, prompt, settings, implementation, model,
scope, task index, and exact frozen inventory prefix. Valid persisted rows are never called again,
including rows that retain API, parse, schema, or upstream failures under ITT. An unterminated but
valid final JSON object is completed by adding its newline. Only an invalid unterminated byte tail
may be discarded as a torn write; invalid newline-terminated records cause refusal rather than
repair. Resume then begins at the first task ID without a valid persisted row. This persistence
behavior does not introduce logical-call retries or change the no-accuracy-stopping rule.

## Estimands

### Actor outcomes

For each cell and model:

1. **Changed PairAcc (ITT):** both members of a changed Preserve/Reevaluate pair must return the
   requested action and exact gold target. All 40 pairs remain in the denominator.
2. **Row-level E2E (ITT):** exact action-and-target accuracy over all 80 rows.
3. **Preserve conditional substitution:** among Preserve rows where the shared compiler predicts
   Preserve and its `bound_target_id` equals the gold S0 winner, the old target remains present and
   action-valid, and the winner changes, count predictions equal to the S1 winner. This endpoint
   localizes post-binding substitution and does not replace ITT reporting.

### Compiler outcomes

1. Reference-mode accuracy over all 80 rows, with failures incorrect.
2. Preserve bound-ID accuracy over all 40 Preserve rows. A row is correct only when the compiler
   predicts Preserve and returns the gold S0 target ID.

### Frozen contrasts

For PairAcc, E2E, and conditional substitution, report right-minus-left differences for:

- M - H
- MI - M
- MIS - MI
- MISF - MIS
- MISF - H

The first four are the adjacent ladder increments. The last is the full composite contrast.

## Inference

- Cluster bootstrap unit: `state_cluster_id`
- Replicates: 10,000
- Seed: `20260728`
- Interval: percentile 95% interval
- Paired discordance: two-sided exact binomial test on discordant paired binary outcomes
- Discordance unit: matched pair for PairAcc; task row for E2E and conditional substitution
- Auxiliary p-value adjustment: Holm within each model across the 15 frozen contrast-endpoint
  tests

Bootstrap intervals are primary. Exact tests are auxiliary; row-level exact tests do not model
within-pair dependence. No pooled model significance test is planned.

## Interpretation declared before calls

- **Strengthen:** A reproducible full-vs-H PairAcc gain with reduced conditional substitution,
  together with interpretable adjacent increments, would strengthen the claim that executable
  timing serialization changes target selection when binding is model-produced.
- **Narrow:** Null adjacent increments, model heterogeneity, or gains confined to the explicit
  follow directive would narrow the claim to a prompt/interface effect under this inventory.
- **Overturn the stronger mechanism reading:** Low compiler mode or Preserve-ID accuracy, no
  full-vs-H improvement, or material full-cell harms would remove support for treating the
  composite decision block as an effective end-to-end mechanism in this setting. TRI's matched
  diagnostic definition would remain a separate evaluation claim.

All negative, null, mixed, failure, and harm outcomes will be retained. No prompt, task, parser,
metric, contrast, correction family, or stopping rule may be changed after the first model call.

The generated JSON report includes a machine-readable `claim_promotion` object. It can mark the
bounded composite interpretation eligible only when MISF-H improves PairAcc and reduces
conditional substitution across both frozen models. It marks an adjacent attribution promotable
only when the PairAcc increment has same-direction positive pair-cluster interval support in both
models. The summary always records that the logically dependent ladder does not identify
orthogonal field effects, a unique internal mechanism, open-language transfer, or deployment
prevalence. This encoding reports the frozen interpretation rule; it is not an additional endpoint
or a data-dependent stopping rule.
