# Revision Matched Audits Protocol

**Frozen:** 2026-07-26, before any model call on these inventories.  
**Evidence status:** post-primary; protocol frozen before own calls.  
**Claim scope:** decision visibility under matched actor payloads. This is not a retrospective
primary analysis, a component-necessity estimate, an open-language proof, a native benchmark
score, or a prevalence estimate.

**Pre-call amendment:** the initial preflight manifest was retained before any model call. The
final v1 parser adds exact invalid-target handling for the 32 Reject rows and records wrong-write,
human-actionable, and paired-difference estimands. The task bytes are unchanged. The builder
refuses this amendment once any revision smoke or full raw output exists.

## Inventories

1. **Full diagnostic:** all 160 rows of the frozen Matched Timing Diagnostic. The primary
   endpoints are changed-winner PairAcc and 128-row actionable-core accuracy. The 32
   author-specified Reject rows are secondary and reported separately.
2. **Human rewrite:** all 50 previously frozen volunteer rewrites. All-row ITT accuracy is
   primary for this addendum. Human-majority sensitivity uses the already collected 48
   determinate rewrite majorities; the seven complete opposite-mode pairs are a small-sample
   sensitivity analysis.
3. **Source grounded:** 30 changed-winner pairs selected without model outcomes: all ten
   STATE-Bench clusters, all ten AgentDojo clusters, and ten ToolSandbox cluster/paraphrase
   pairs selected by sorted paraphrase-major round-robin order. These are source-grounded
   controlled interventions, not native benchmark tasks.

The build script validates shared pair states, selectors, actions, schemas, transitions, distinct
winners, surviving/action-valid old targets, opposite golds, exact IDs, row counts, and source
balance. It records task, source, protocol, parser, and frozen Rule* hashes in a manifest.

## Conditions

Each task has one compiler call and two actor calls. `history_only` and `decision_visible` receive
byte-identical base payloads; the latter alone receives the shared parsed compiler decision.
Actor order alternates by task index. Both actors return `INVALID_BOUND_ENTITY` rather than
substituting another entity when a preserved target is absent or violates the supplied action
preconditions. `decision_enforced` is a zero-call deterministic transform of the visible actor
output; its Preserve branch applies the same serialized action-precondition check. It is not a
third actor condition.

The compiler emits exactly `reference_mode`, `bound_target_id`, and `selector`. Actors emit exactly
`action` and `target_id`. Targets must exactly match a serialized state ID or
`INVALID_BOUND_ENTITY`; fuzzy or prefix matching is forbidden.

## Models and Calls

Qwen3.5-122B-A10B and GLM-5.1 run all three audits. DeepSeek-V4-Pro runs only the source-grounded
replication. Temperature is zero, thinking is disabled, output limit is 500 tokens, timeout is
180 seconds, and at most two transport retries are allowed. A four-row health smoke must complete
all three logical calls before a full run. Full raw outputs are immutable and never overwritten.

## Estimands and Failure Accounting

- ITT exact target accuracy on all rows and the actionable core;
- changed-winner and complete-pair PairAcc;
- conditional Preserve substitution after correct compiler mode and exact initial ID;
- Reevaluate premature lock;
- human-majority sensitivity on determinate rewrite items;
- source-specific PairAcc for STATE-Bench, AgentDojo, and ToolSandbox;
- deterministic enforcement repairs and harms;
- API, transport, parse, schema, and incomplete-task counts.

Intervals use 10,000 pair/workflow-cluster bootstrap replicates with seed 20260726. McNemar tests,
if reported, are secondary. Negative, null, mixed, and failed outcomes remain in the report and
submission artifact.

## Interpretation

The full diagnostic isolates decision visibility under equal calls but remains authored and
post-primary. Human rewrites change language but retain authored task semantics. Source-grounded
contrasts use external schemas and states but add controlled timing instructions and transitions.
None establishes natural prevalence, systematic benchmark undercoverage, or independent
open-language construct validity.
