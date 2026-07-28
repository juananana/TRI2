# TRI Decision-Block Stratification Audit Protocol

## Status and purpose

This is a post-primary, zero-API descriptive audit of frozen model outputs. It was specified to
clarify what the existing matched-call intervention contains and where its observed gains occur.
It makes no new model calls and does not alter any frozen task, prompt, parser, or outcome.

The matched-call intervention exposes a compound compiler block containing `reference_mode`,
`bound_target_id`, and a restated `selector`. The authored analysis stratifies actor outcomes by
whether the shared compiler predicted the gold mode and, on Preserve rows, the correct bound ID.
These are post-treatment strata. They describe associations with compiler quality; they do not
identify mediation, the causal contribution of an individual field, or component necessity.

## Frozen inputs

The analysis reads complete raw JSONL records from:

- authored matched-call runs: Qwen and GLM, 160 rows per model;
- one-volunteer rewrite matched-call runs: Qwen and GLM, 50 rows per model;
- source-derived matched-call runs: Qwen, GLM, and DeepSeek, 60 rows per model;
- call-matched cross-schema runs: Qwen and GLM, 80 rows per model;
- v7 Cross-Schema Controlled Replication: Qwen and GLM outputs for Generic, historical CTA,
  and Lifecycle-Gated, restricted to the shared 40-pair changed-winner (`flip`) inventory.

The generated JSON report records the SHA-256 digest and row count of every input. All required
files must exist, and the expected complete census must be present. The script fails closed on
missing rows, duplicate task IDs, incomplete matched calls, malformed request payloads, or a
non-paired v7 flip inventory.

## Authored matched-call estimands

For History-only and Decision-visible actors, report within each compiler-mode stratum:

1. exact-target accuracy;
2. action-and-target E2E accuracy;
3. paired discordances: visible repair, visible harm, both correct, and both wrong.

On Preserve rows, repeat these summaries within strata defined by whether the compiler
`bound_target_id` equals the frozen pre-refresh target. A repair is History-only wrong and
Decision-visible correct; a harm is the reverse. The unit is a matched task row, so no unpaired
comparison is used.

Exact-target accuracy requires the parsed target ID to equal the frozen target gold. E2E accuracy
additionally requires the parsed action string to equal the frozen action after whitespace and
case normalization. API, parse, schema, and incomplete outcomes remain incorrect under ITT.

## Interface-redundancy audit

Across the complete authored, rewrite, source-derived, and cross-schema matched records, report:

- exact equality between the compiler's parsed selector and the base task selector;
- equality of task `initial_selected_id` and frozen `pre_refresh_target`;
- equality of the compiler-request, History-only-request, and Decision-visible-request copies of
  `initial_selected_id` with the task field;
- equality of the two actor-request copies with each other.

These checks establish whether the visible selector and initial-ID fields add new values in the
recorded interface. Equality does not imply that restatement has no salience effect.

## End-to-end boundary table

On the exact v7 40-pair changed-winner inventory, report for each model/controller:

- correct Preserve initial binding;
- Preserve E2E exact-target accuracy;
- Reevaluate E2E exact-target accuracy;
- changed-pair PairAcc.

For Generic, the initial binding is `compiled_ledger.selected_entity_id`; for historical CTA and
Lifecycle-Gated it is `compiled_ledger.bound_target_id`. This table is a boundary comparison among
existing end-to-end controllers. It is not call- or information-matched and must not be used as a
component causal estimate.
