# Evaluation-Selection Regret Audit Protocol

Status: frozen post-primary zero-API audit before implementation and report generation.

Freeze date: 2026-07-22 (Asia/Shanghai).

## Claim and alternative

**Claim tested.** Evaluation regimes that omit the matched authorization contrast can select, or
leave score-maximal, an unconditional policy with large loss on balanced changed-winner
Preserve/Reevaluate pairs. This is a benchmark-level decision consequence of non-identifiability.

**Alternative excluded.** Stable-only or one-sided scores may be formally non-identifying yet still
select exactly the same tested policy configurations as changed PairAcc, making the distinction
irrelevant to benchmark-based policy selection in the frozen candidate sets.

## Inputs

No model calls and no new task rows are permitted. The only inputs are:

- `reports/v3_identifiability_regimes_v1.json`, SHA-256
  `f9acb0c9e7ba9028f1402dff31e7239f937e9267f73bd125653d2e9e845e67d7`;
- `reports/v7_identifiability_regimes_v1.json`, SHA-256
  `8aac36f5c4d18c3ed1d119d20886ee7c42c3ff1d584a7d2f76b34a1512e61ed4`.

The reports already count missing/API/parse failures under their frozen ITT rules.

## Candidate sets

Analyses are separated by dataset and model family. Each candidate set contains that model's
available Generic, CTA, and other reported lifecycle configuration plus the two deterministic
model-independent extremes, `Always-Lock+validity` and `Always-Reevaluate`. No cross-model ranking
is reported.

## Frozen metrics

Proxy regimes:

1. aggregate E2E accuracy;
2. Preserve-only accuracy;
3. Reevaluate-only accuracy;
4. Stable-only accuracy.

Target regime: changed-winner matched PairAcc.

For each dataset/model/proxy regime, report:

- maximum proxy score;
- every exact proxy maximizer;
- minimum and maximum PairAcc among proxy maximizers;
- best PairAcc anywhere in the same candidate set;
- worst-case selection regret = best PairAcc minus minimum PairAcc among proxy maximizers;
- optimistic selection regret = best PairAcc minus maximum PairAcc among proxy maximizers;
- whether any proxy maximizer has zero PairAcc.

Scores are exact descriptive quantities from frozen reports. No confidence interval or hypothesis
test is added because the deterministic extreme policies make the identifiability counterexample
constructive and the candidate-set analysis is not a population estimate.

## Interpretation

- **Strengthen:** Stable-only or one-sided maximizer sets contain a zero-PairAcc policy and have
  large worst-case regret in multiple model-family candidate sets.
- **Narrow:** Only one dataset or one family shows substantial regret, or aggregate scoring already
  resolves the ambiguity everywhere.
- **Overturn:** Every proxy maximizer is also changed-PairAcc-optimal in every candidate set.

The audit does not claim that benchmark users literally deploy the worst tied policy, that the
tested candidate set is exhaustive, or that PairAcc alone captures general task utility. It shows
whether a proxy score licenses a poor authorization policy among concrete tested alternatives.

## Stopping and reporting rule

Run the implementation once after unit tests validate input hashes, candidate-set construction,
maximizer enumeration, and regret arithmetic. Retain all dataset/model/proxy rows. Do not change
the metric, candidate sets, tie handling, or interpretation thresholds after report inspection.
Write machine-readable JSON and Markdown reports and add the result to
`reports/current_claim_provenance.md` as post-primary zero-API evidence.

