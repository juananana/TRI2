# TRI External Review Rounds (2026-07-22)

## Status

This is an internal decision record, not empirical evidence and not a submission file.
The external reviewer received the anonymous main-paper LaTeX as pasted text. PDF upload was not
available, and the supplement was not provided in these two review passes.

## Round 1

- Verdict: Weak Reject; overall AAAI competitiveness 4/10; confidence 4/5.
- Main structural risks: narrow novelty beyond Binding Drift, synthetic-only importance, and weak
  evidence of natural incidence.
- Fixable issues: imprecise Binding Drift distinction, ambiguous controller names in Table 1,
  conflation of full-v7 deterministic SQLite replay with the separate 40-task model-facing SQLite
  experiment, over-formal presentation of the mode-blind observation, and missing version map.
- Requested but not adopted: two large main-text controller/denominator tables. The supplement
  already contains the detailed audits, and moving both tables would displace primary evidence
  from the seven-page main text.

## Implemented Revision

1. Explicitly credited Binding Drift with the shared correct-binding-then-replacement phenomenon.
   TRI now claims only the authorized deferred-resolution variable and its symmetric diagnostic.
2. Renamed the Table 1 column to `Lifecycle-Gated E2E` and standardized result references.
3. Distinguished deterministic in-memory replay of frozen v7 outputs from the separate 40-task
   model-facing SQLite experiment, including in the abstract.
4. Demoted the proposition to an elementary identifiability observation. The reproducibility
   checklist no longer classifies the paper as making a theoretical contribution.
5. Added a one-line v3/v4/v7 protocol map and retained the CTA/Lifecycle/Lifecycle-Gated split.
6. Clarified that the two-refresh negative result uses the frozen v5 scalar Lifecycle controller.

## Round 2

The reviewer marked items 1-4 resolved and the version/controller item partial. It requested only:

- exact controller names for remaining `Gated`/`lifecycle` shorthand;
- `deterministic in-memory` at the abstract's first replay mention.

Both wording changes were implemented. The reviewer then specified that no remaining
existing-evidence P0/P1 was likely to materially improve the submission. The residual acceptance
risk is structural: reviewers may consider TRI a narrow synthetic extension of Binding Drift with
limited demonstrated natural incidence. Changing that judgment requires new external evidence,
not another wording loop.

## Stop Decision

Stop iterative external review for the current revision. Do not reopen R-SSA, method search,
independent-human collection, or unplanned API experiments. Continue only submission hygiene:
claim-to-artifact audit, anonymous packaging, final PDF/checklist validation, and corrections of
newly discovered factual or reproducibility defects.
