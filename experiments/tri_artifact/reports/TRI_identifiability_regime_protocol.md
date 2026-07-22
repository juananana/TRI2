# Evaluation-Regime Identifiability Audit

**Status:** post-primary, zero-API reanalysis of frozen v3/v7 outputs. This report must not be
described as a preregistered confirmatory experiment.

## Question

Can an evaluation protocol distinguish selective Preserve/Reevaluate authorization from an
unconditional policy, and can it separate initial-binding error from post-binding substitution?

## Regimes

- `aggregate_e2e`: all complete task rows;
- `preserve_only`: anchored rows, including stable and changed-winner updates;
- `reevaluate_only`: dynamic rows, including stable and changed-winner updates;
- `stable_only`: unchanged selector-winner updates;
- `changed_winner_only`: anchored, action-valid rows with a distinct refreshed winner;
- `changed PairAcc`: both members of each matched Preserve/Reevaluate pair are correct;
- `conditional substitution`: among changed-winner rows with a correct observable initial binding, the
  model selects the refreshed winner.

The last denominator uses the controller's observable compiled ID (`selected_entity_id` for the
Generic ledger and `bound_target_id` for CTA/Lifecycle). Failed, missing, and malformed rows are
incorrect under intention-to-treat scoring. Deterministic Always-Lock and Always-Reevaluate are
policy extremes, not model baselines.

## Interpretation rule

If aggregate or one-sided scores rate a controller highly while changed PairAcc is low and
conditional substitution is high, the evaluation regime is non-identifying for selective re-resolution.
The analysis does not establish that natural public benchmarks make this error on strict TRI cases;
the separate public audits found almost no such opportunities.
