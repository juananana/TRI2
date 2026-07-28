# Model-Authored Linguistic Stress-Test Transport Repair Addendum

**Status:** post-primary scoring-transport repair, frozen after the invalid v1 aggregate report
and before complete-set reparsing. The original raw runs and
`reports/model_authored_linguistic_stress_v1.{json,md}` remain unchanged as instrumentation
provenance and are not scientific results.

## Trigger

The frozen generated inventory uses identifiers such as `MAS-01-A`. The pre-existing
`normalize_target` helper accepts the repository's usual single-hyphen IDs through the regular
expression `[A-Z]{2,5}-[A-Za-z0-9]+`. It therefore truncates every returned `MAS-01-A`-style
identifier to `MAS-01`. The first aggregate report consequently scored all four controller cells
as 0/48 even when the raw compiled ledger and actor response contained a full state identifier.

This is an identifier-grammar incompatibility introduced by the new semantic inventory. It is
not a model failure and the v1 aggregate must not be cited as a negative behavioral result.

## Frozen zero-request repair

No author, judge, or controller request is rerun. No instruction, state, gold target, prompt,
model output, or task inclusion decision changes. For each existing controller row:

1. Parse the final element of `result.raw_outputs` with the repository's existing JSON parser.
2. Read only its `target_id` field.
3. Accept the field only when it is exactly equal to one identifier in that row's initial or
   refreshed state, or exactly one of the existing invalid-target spellings.
4. Otherwise return a null target and keep the row incorrect in ITT. No substring, fuzzy,
   display-name, case-insensitive, or semantic matching is allowed.
5. For conditional-substitution eligibility, read `selected_entity_id` (Generic) or
   `bound_target_id` (CTA) from the already parsed compiled ledger and accept it only when it is
   exactly equal to an initial-state identifier. Reevaluate null bindings remain null.

The repaired report must record, per run, how many actor targets and initial bindings were
recovered, how many remained unresolved, the source raw-file hashes, and the repair source hash.
All judge outputs and the frozen post-hoc Rule* remain unchanged. The repair cannot create a
dual-judge-valid pair where the two judges did not already accept both instructions.

## Interpretation

The repaired controller estimates are labeled `post-primary transport-repaired`. Because the
repair was specified after observing the invalid all-zero aggregate, it is not primary or
confirmatory evidence. It may support only the protocol's original bounded statement about the
frozen model-authored distribution. The identifier failure and repair must be disclosed wherever
this addendum is reported.
