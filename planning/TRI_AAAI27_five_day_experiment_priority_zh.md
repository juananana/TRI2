# TRI AAAI-27 five-day experiment priority

Status: planning record, not manuscript evidence unless a protocol is frozen before any new
collection or model/API call. Current date: 2026-07-24.

## Principle

Five days is enough for a small number of targeted repairs, but not enough for broad exploratory
experiments. A new run should be started only if it answers a likely Phase-1 objection that would
be hard to fix in rebuttal:

1. the result is only an artifact of authored templates;
2. the result is only an artifact of Generic's ledger serialization;
3. the primary gain is inflated by call asymmetry or package-level comparison;
4. reject/fallback semantics are author-defined rather than human-supported;
5. public benchmarks have no native strict opportunities, so practical relevance is unclear.

## Highest-value experiments if people/API are available

### P0: Independent-language scalar holdout

Claim tested: TRI survives instructions not written by the authors while keeping the same frozen
state transitions and automatic gold.

Alternative explanation excluded: the diagnostic is mainly exploiting author-template wording.

Minimum viable protocol:

- freeze 40 to 80 matched scalar tasks sampled across existing schemas and state clusters;
- ask at least two non-author writers to produce Preserve/Reevaluate wording without seeing gold
  labels or controller results;
- freeze all rewrites before any model run;
- run Generic, CTA, and the strengthened deterministic rule on the full frozen set;
- report exact target, PairAcc, initial binding, conditional substitution, parse/API failures, and
  writer-cluster bootstrap intervals;
- count every row under ITT and do not edit prompts after seeing smoke/full results.

High-score outcome: CTA exceeds Generic and the post-hoc rule does not close the gap on independent
language. If the rule remains competitive, the paper should say more strongly that the contribution
is diagnostic identifiability and executable timing status rather than an algorithm.

### P0: Independent human adjudication of reject/fallback

Claim tested: the invalid-target policy used in Remove/Invalidate cases matches human judgments.

Alternative explanation excluded: reject/fallback scores are mostly author policy preference.

Minimum viable protocol:

- sample all 32 current reject-policy cases plus 32 matched actionable controls;
- recruit at least three new annotators uninvolved in TRI design;
- hide condition, gold, controller names, and previous human results;
- ask for target choice among old target, refreshed winner, reject, or other/ambiguous;
- report majority-gold, unanimity, kappa/alpha, and sensitivity excluding reject rows.

High-score outcome: reject majority-gold improves clearly over the current 55%. If not, keep
reject/fallback outside the main TRI claim, as the current paper does.

### P1: Human-reviewed public-candidate recall audit

Claim tested: zero strict native opportunities in public suites is not merely a weak automatic
scanner.

Alternative explanation excluded: the paper missed obvious public-suite opportunities.

Minimum viable protocol:

- use the existing API-Bank/BFCL/ToolTalk candidate inventory;
- have two independent reviewers label strict TRI slots with a conflict adjudication rule;
- report recall boundary, disagreements, and all near-matches;
- no model behavior run is needed unless strict positives are found and automatic gold/state diff
  are available.

High-score outcome: either strict positives lead to a small frozen behavior run, or a credible
human-reviewed null makes the external-boundary paragraph much harder to attack.

### P1: Call- and information-matched controller check

Claim tested: the primary Lifecycle-Gated advantage is not explained only by fewer actor calls or
different information routing.

Alternative explanation excluded: call asymmetry inflates the package-level result.

Minimum viable protocol:

- freeze a small but balanced subset from the primary/actionable core;
- compare Generic, CTA, and a call-matched CTA-shadow condition where a second actor call is made
  and logged but the valid Preserve mutation still uses the compiled target;
- separately report behavioral target accuracy and shadow-call disagreement rate;
- do not present this as a causal component estimate if the gate ignores the shadow actor.

High-score outcome: shadow actors often disagree on Preserve, while the enforced mutation remains
correct. This would support the controller-constraint framing and make the call-asymmetry caveat
less damaging.

### P2: Composition repair only if the main scalar story is already frozen

Claim tested: a role-indexed or event-graph variant repairs the negative two-refresh result.

Alternative explanation excluded: TRI only works for one scalar referent.

Minimum viable protocol:

- freeze task inventory, role schema, prompts, and ITT treatment before calls;
- run only if there is enough space to report negative and positive composition results together;
- if mixed, keep it in the supplement and do not expand the main claim.

## Recommendation for the submission window

The best use of the remaining time is P0 independent-language holdout plus P0 reject/fallback
human adjudication if the required people are genuinely available today. If not, do not replace
them with author paraphrases or LLM-only labels. In that case, spend the remaining time on the
current manuscript: make evidence status visible, keep the new results dashboard, finish artifact
checks, and keep external nulls in the main text.
