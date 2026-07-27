# TRI AAAI-27 One-Week Research-Value Plan

Status: active internal plan; not empirical evidence. The zero-API P0 audit is complete and has
been integrated; API and independent-evidence decisions remain gated.

## Objective

Use the remaining submission week to deepen the paper's scientific consequence without adding
model count, tuning on evaluation outcomes, or converting TRI into a general runtime paper. The
target is a defensible 6-level evaluation contribution. A reliable 7 still requires genuinely
independent external evidence.

## Reviewer consensus to address

Both independent PDF reviewers scored the paper 5/10 with confidence 4/5. They agree on two
decision-critical risks:

1. the increment over Binding Drift may look like a narrow contrast-set extension; and
2. positive evidence is controlled while public and lower-intervention evidence is null.

The paper already addresses controller non-uniqueness, temporal parsing, evidence status,
denominators, wrong writes, and negative results. More templated rows or another endpoint model
would not repair the two structural risks above.

## Priority portfolio

| Priority | Work | Expected value | Feasibility | Decision |
|---|---|---:|---:|---|
| P0 | Evaluation-selection regret from frozen v3/v7 outputs | High: turns identifiability into benchmark-level policy-selection consequence | High; zero API | Complete; retain in main text |
| P0 | Tighten the formal contribution around evaluation equivalence classes and decision regret | Medium-high | High | Complete; retain with candidate-set and tie boundaries |
| P1 | Actionable-core/Reject construct sensitivity synthesis | Medium | High; existing evidence | Keep source-derived and compact |
| P1 | Independent recall audit of public-suite opportunities | High if genuinely independent | Low-medium | Go only with at least two independent auditors |
| P1 | Blind independently authored linguistic/workflow holdout | Highest possible score impact | Low | Go only if the existing six-writer/three-annotator gate can genuinely pass |
| P2 | New low-intervention agent architecture | Potentially high but severe p-hacking risk after existing nulls | Low | No-Go without a pre-existing natural inventory and frozen protocol |
| Reject | Another model on v3/v7, more templates, prompt/rule tuning, larger author-written pilot | Low | High | Do not run |

## New conceptual layer

The current paper shows observational non-identifiability. The proposed deeper layer asks what that
means for benchmark use:

> If a benchmark selects or fails to reject policies using Stable-only or one-sided scores, how
> much matched changed-winner performance can be lost by choosing a score-maximizing policy?

This yields an evaluation decision object rather than another accuracy table:

- the proxy-score maximizing set under each evaluation regime;
- the range of matched PairAcc within that set;
- worst-case selection regret relative to the best available matched policy;
- whether a zero-PairAcc unconditional policy remains a proxy maximizer.

The result does not estimate deployment prevalence. It demonstrates that the omitted authorization
contrast can change which policy a benchmark licenses, directly answering why the evaluation gap
matters scientifically.

The completed audit sharpens this consequence. Across five dataset/model-family candidate sets,
all 15 Stable-only or one-sided maximizer sets contain a zero-PairAcc unconditional policy;
worst-case regret is 100 points. A 2026-07-23 correction added reported Lifecycle-Gated rows that
the first implementation had omitted; Aggregate accuracy is PairAcc-optimal in all five complete
sets. These are descriptive
candidate-set results, not a claim about how benchmark users break ties or deployment prevalence.

## Experiment decision ladder

1. **Go without API:** complete the source-derived actionable-core/reject sensitivity narrative,
   provenance, and artifact checks. This improves construct validity but should not become another
   headline result because it is already visible in the current paper.
2. **Go only with real independent people:** run the frozen public-suite recall audit if at least
   two auditors who did not design the checklist are available; run the blind language/workflow
   holdout only if six independent writers and three independent annotators are available under
   the existing packet. These are the only feasible additions that directly address reviewer
   doubts about author-designed coverage.
3. **No-Go even if a key is available:** another model on v3/v7, more author-written templates,
   prompt or rule tuning, LLM-only paraphrases, or a larger version of a lower-intervention setup
   that has already returned a null. They add rows without excluding the two main review-critical
   alternatives: narrowness relative to Binding Drift and lack of independent external evidence.

## API experiment gate

No API credential is currently injected into the working environment. Do not store or paste a key
in the repository, planning files, or chat. If a key is securely re-injected, first perform a
read-only `/models` authentication check. A paid run remains forbidden until all of the following
are frozen in a protocol file:

1. claim and excluded alternative;
2. task inventory and hash;
3. prompt, endpoint, model IDs, temperature, token cap, retry and ITT policy;
4. primary metric and denominator;
5. budget and stopping rule;
6. outcomes that strengthen, narrow, or overturn the claim;
7. zero-API validation and a bounded smoke gate.

No new model experiment starts after 2026-07-24 except transport repair or validation of a fatal
review concern.

### July 23 decision update

A credential pasted into chat is treated as compromised and was not used or stored. The owner must
revoke it. As of July 23, additional API experiments remain **No-Go**: no independent public-suite
auditors or six-writer/three-annotator holdout team has been confirmed, and another model or
author-written extension would not address the two review-critical alternatives. This decision may
change before the July 24 gate only if one of those independent-resource conditions is genuinely
met and its protocol is frozen before any call.

The current-submission decision is also **No-Go for additional human annotation**. Existing blind
labels support the scalar Preserve/Reevaluate construct; repeating ordinary gold-agreement
annotation has low expected value, while the independent resources required for a valid coverage
recall audit or naturally elicited holdout are unavailable. These remain future evidence needs.

## Calendar (Asia/Shanghai)

- **July 22:** freeze and run the zero-API selection-regret audit; inspect whether it adds a new
  scientific conclusion beyond the existing identifiability table.
- **July 23:** complete actionable-core synthesis; determine whether independent human writers or
  public-suite auditors are actually available. Freeze any qualifying API protocol before calls.
- **July 24:** final Go/No-Go for all API work. No prompt iteration after seeing smoke/full results.
- **July 25--26:** integrate only decision-changing results; compile and run skeptical review.
- **July 27:** internal main-paper freeze.
- **July 28:** final anonymity, artifact, page, and claim-provenance audit.
- **July 29:** submission buffer before the 19:59 deadline.

## Success criteria

- The new audit must show a benchmark-selection consequence not already visible from a single
  accuracy column; otherwise it remains supplement-only or is dropped.
- All new analyses are labeled post-primary and zero-API.
- Null or favorable results are retained under the frozen stopping rule.
- No title or registered-abstract change is required.
