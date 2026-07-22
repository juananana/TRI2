# V7 Shared-Eligible and PairAcc Uncertainty Audit

**Status:** post-primary, zero-API analysis of frozen v7 outputs. The analysis is descriptive and
must not be described as preregistered or as evidence of natural prevalence.

## Claim and alternative explanation

The audit tests whether the observed Generic-versus-CTA conditional-substitution contrast remains
when both controllers are evaluated on exactly the same eligible tasks. This excludes the narrower
alternative that the contrast is created by controller-specific initial-binding denominators. It
does not exclude prompt, controller, model, or benchmark-design effects.

## Frozen inputs

- task inventory: `data/temporal_referent_v7_core_replication.jsonl`;
- complete Generic and Exact CTA runs for Qwen3.5, GLM-5.1, and DeepSeek-V4-Pro listed in
  `reports/current_claim_provenance.md`;
- no model calls, retries, row deletion, or prompt changes.

## Shared-eligible denominator

A task is retained only when (1) it is an anchored Flip or Name-collision task with a distinct
refreshed winner, (2) the old target remains present and action-valid, (3) both controllers expose
the correct pre-refresh ID, and (4) neither row has an API, parse, or protocol failure. The
numerator is a final target equal to the distinct refreshed winner. Every attempted row remains in
the source files; this intersection is a conditional mechanism audit, not an ITT score.

## PairAcc uncertainty

Changed-winner PairAcc retains the existing 80 matched Preserve/Reevaluate pairs per controller.
We resample the 40 complete state-instance clusters with replacement 10,000 times, using seed
20260722. Percentile 95% intervals are reported for each controller's PairAcc and for the paired
CTA-minus-Generic difference. Pair members and all rows within a sampled cluster remain together.

## Interpretation and stopping rule

- A nonzero Generic count and zero CTA count on the shared denominator strengthens the claim that
  controller-specific eligibility alone does not explain the observed contrast.
- A materially attenuated or reversed shared-denominator contrast narrows the mechanism claim and
  must be reported.
- Intervals spanning zero narrow evidence for the corresponding PairAcc contrast.
- Zero observed CTA substitutions do not establish zero population risk; no row-level binomial
  upper bound is reported because state-cluster dependence is the designated sampling structure.

The analysis stops after one execution on the six frozen files. All outputs are written to JSON
and Markdown and added to claim provenance.
