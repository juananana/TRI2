# TRI-v7 Dialogue-Aware Mutation Verifier Protocol

**Status:** planned/unverified, post-primary, with zero API calls made. This document freezes a
possible information-matched controller evaluation; it is not a result, is not manuscript
evidence, and does not authorize an API run by itself.

**Frozen:** 2026-07-22, before any verifier prompt, smoke, or full-run output is inspected.

## Why A New Condition Is Needed

The completed `full_history_once` condition receives the instruction, `S0`, and `S1`, then emits
a target in one late call. It has no observed, separately scored initial binding and does not
validate a proposed mutation at the mutation boundary. It is therefore an information-rich,
one-shot decision baseline, but not a dialogue-aware mutation-time verifier. Its unconditional
anchored substitution rate must remain reported as unconditional.

This planned condition asks a narrower question: after an agent has actually selected an ID and
later proposed a write, can a dialogue-aware model use the complete pre-refresh and refreshed
history to authorize, replace, or reject that proposal? The comparison cannot establish that CTA,
a pre-refresh field, or any serialization is uniquely necessary.

## Frozen Inventory And Trace Construction

- Inventory: `data/temporal_referent_v7_core_replication.jsonl`.
- SHA-256: `2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891`.
- Exactly 240 rows in 40 complete state clusters: 120 Preserve (`anchored`) and 120 Reevaluate
  (`dynamic`), with 80 each of Flip, Stable, and name-collision updates.
- No row may be selected, rewritten, dropped, or duplicated after this freeze.

For each row, the harness constructs this non-gold execution trace:

1. A **binder** receives the user instruction, `S0`, action schema, and action preconditions; it
   emits `observed_initial_id` or `INVALID_BOUND_ENTITY` before refresh.
2. The harness supplies `S1` after refresh. A **proposer** receives the full ordinary dialogue
   trace and produces an entity-directed mutation proposal, including `proposed_target_id`.
3. The **dialogue-aware mutation verifier** receives the complete instruction, `S0`, the
   binder's observed initial ID, `S1`, the proposed target, action schema, and preconditions. It
   authorizes the proposal, replaces it with an allowed target, or rejects it.
4. A deterministic executor applies only the verifier output and records final state and action
   validity.

`correct_target`, `pre_refresh_target`, `post_refresh_target`, `binding`, and all scorer-only
metadata are unavailable to binder, proposer, verifier, and executor prompts. The verifier may
use the observed ID, but never a hidden gold ID. A malformed, absent, or non-actionable observed
ID is retained as a failed trajectory rather than repaired with the scorer value.

## Frozen Condition And Interface

The condition is a controller, not a passive classifier: Reevaluate can require replacement of a
proposal. It uses the same model family for binder, proposer, and verifier within a cell, with
fresh calls and no hidden inter-call state beyond the listed trace fields. The implementation
must record all three raw responses separately.

The verifier system prompt must be frozen verbatim in versioned source before any call. It must
not contain `TRI`, `authorization`, `Preserve`, `Reevaluate`, `CTA`, `reference mode`, any task
ID, or example entity ID. Its only command is to decide whether the proposed entity-directed
action is justified by the original request and observed dialogue, accounting for the refresh and
action preconditions. The user payload is a JSON object with exactly these fields:

```text
original_instruction
initial_state_before_refresh
observed_initial_id
refreshed_state
proposed_action: {name, target_id, arguments}
action_schema
action_preconditions
```

The required JSON-only output schema is:

```text
{ "decision": "allow" | "replace" | "reject",
  "target_id": "stable ID" | "INVALID_BOUND_ENTITY",
  "reason_code": "preserve" | "reevaluate" | "invalid" | "ambiguous" }
```

`allow` requires that `target_id` equal the proposal target; `replace` requires an action-valid
stable ID; `reject` requires `INVALID_BOUND_ENTITY`. Schema violations, unknown IDs, incompatible
decision/target pairs, and transport failures produce no write and count in intention-to-treat.

## Frozen Metrics And Denominators

All 240 attempted rows form the ITT denominator. Report final authorized-target accuracy,
initial-binding accuracy, proposal accuracy, verifier allow/replace/reject counts, invalid
attempts, API/parse failures, rejection, wrong-entity writes, and final-state utility separately.

The strict conditional TRI denominator is evaluated only when all of the following are observable:

1. the binder selected the correct initial entity before refresh;
2. refresh completed before the proposal and verifier call;
3. the old entity survives and is action-valid;
4. the refreshed winner is distinct for Flip rows; and
5. an entity-directed proposal was attempted.

Within that denominator, report Preserve substitution to the refreshed winner, Reevaluate
premature retention of the old target, Stable errors, and executed wrong writes. Pair success
requires both matched Preserve/Reevaluate members of the same `(state_cluster_id, update)` pair
to be finally correct. Resample the 40 state clusters for descriptive 95% intervals. Do not
rename binding, selector, proposal, tool-order, or parser failures as TRI.

## Frozen Execution Settings And Stopping Rules

If a separately approved activation occurs, use the same model endpoints, temperature zero,
thinking setting, request timeout, output cap, retry policy, and API-key handling across all three
calls and comparator conditions. Pin those exact values, the prompt hashes, inventory hash,
software revision, and random seed in an activation record before the first request.

Before model calls, the implementation must pass every zero-API check below. Then run one
preselected four-row transport/parse smoke containing a matched Flip pair and a matched Stable
pair. Do not inspect smoke accuracy to alter prompts, schemas, or decision rules. Stop without a
full run on any prompt-field leak, scorer-field leak, duplicate/missing task ID, executor
invariant failure, systematic parser failure, or more than one API/parse failure in a cell. If the
smoke passes, run the frozen inventory exactly once; retain all attempted rows and all raw JSONL.

No result may be reported as primary, independent, naturalistic, externally confirmed, or evidence
of real-traffic prevalence. A positive result would only describe this post-primary controller on
the frozen controlled inventory; a null would not overturn the primary diagnosis because it tests
a stronger, history-rich controller.

## Required Zero-API Validation Before Any Activation

Implement a new harness and deterministic tests before any API request:

1. **Inventory audit:** verify hash, 240 unique IDs, 40 complete six-row clusters, the stated
   factor counts, and matched-pair membership.
2. **Trace-source audit:** assert that model-facing trace objects contain no scorer-only field;
   assert `observed_initial_id` comes from the binder output and `proposed_target_id` from the
   proposer output, never task gold metadata.
3. **Schema and executor audit:** exhaustively test valid `allow`, `replace`, and `reject` paths;
   reject unknown IDs, stale action-invalid IDs, inconsistent decision/target pairs, and malformed
   JSON without performing a write.
4. **Causal-order audit:** use deterministic stubs to verify that binding precedes refresh,
   refresh precedes proposal and verification, and only the verifier-approved target reaches the
   mutation executor.
5. **Scoring audit:** construct fixture rows for correct binding plus Preserve substitution,
   Reevaluate premature lock, Stable error, initial-binding error, tool-order error, rejection,
   and parser failure. Verify they are counted in distinct categories and that only eligible rows
   enter the strict conditional denominator.
6. **Paired-report audit:** verify cluster bootstrap input and pair success fail closed on missing
   or duplicate pair members; verify all ITT rows remain in the report.

The minimal code additions, if activated, are a dedicated
`tri/v7_dialogue_aware_verifier.py` trace runner, a report builder, and focused unit tests. They
must not modify or overwrite existing v7 run files or reports.
