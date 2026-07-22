# TRI Theory Scope and Claim Registry v1

**Status:** theory and reporting decision record. This document introduces no empirical result,
does not alter the frozen primary estimand, and must not be cited as evidence.

## Purpose

TRI is a controlled diagnostic for whether an evaluation can distinguish an already resolved
action referent from a selector that the instruction leaves to be resolved after a refresh. Its
central object is **discourse-conditioned re-resolution timing**. The word `authorization` in
TRI means instruction semantics, not identity, access-control, permission, or security
authorization.

The paper does not claim to discover post-binding drift, to identify a model-internal mechanism,
or to introduce a universally necessary controller representation. Its contribution is a matched
evaluation variable and a controller-level behavioral diagnosis.

## Referential Core

Let `S0` and `S1` be the pre-refresh and post-refresh states, `q` a selector, `a` a
target-specific action, and `H` the instruction and dialogue history. Suppose `e0 = q(S0)` and
`e1 = q(S1)`. A referent state is either a bound entity `B(e0)` or an unresolved query `U(q)`.

The instruction induces a resolution-timing value:

```text
Gamma(H) = Preserve   if the action refers to the entity resolved before refresh
Gamma(H) = Reevaluate if the action asks to resolve q after refresh
```

For the actionable referential core, all candidate entities relevant to the comparison remain
present and action-valid in `S1`. The authorized target is therefore:

```text
target(H, S0, S1, q) = e0  when Gamma(H) = Preserve
target(H, S0, S1, q) = e1  when Gamma(H) = Reevaluate
```

Action validity is a separate question. If a preserved target is invalid, the executor may
reject, clarify, or follow another explicit action policy. That response is not part of the
core referential target claim and must be scored separately.

## Identifiability Observation

Consider a changed-winner matched pair with identical `S0`, `S1`, `q`, and `a`, where
`e0 != e1`. The two members differ only in `Gamma(H)`. A mode-blind post-refresh policy
`f(e0, q, S1, a)` receives the same inputs for both members and must emit the same output. It
cannot equal both `e0` and `e1`.

This is an evaluation-design observation, not a lower bound on algorithmic complexity and not a
claim that an explicit field, pre-refresh compilation, Lifecycle, or CTA is mathematically
necessary. It explains why aggregate, Stable-only, Preserve-only, and Reevaluate-only evaluation
can reward incompatible unconditional policies. PairAcc on changed-winner matched pairs is the
minimal reported score that exposes this failure mode.

## Scope Conditions

The controlled diagnosis requires all of the following:

1. a correct, observable initial binding when the error claim is conditional TRI;
2. a completed refresh before a later action;
3. stable identities across the comparison;
4. an action-valid old target in the Preserve changed-winner core;
5. a distinct post-refresh winner for changed-winner rows;
6. a target-level action outcome or state diff for a wrong-write claim.

The current evidence covers scalar, single-target, single-refresh, controller-orchestrated
mutations. It does not cover identity migration, user correction, ambiguity repair, multiple
referential roles, repeated refresh epochs, or deployed-traffic frequency.

## Error Taxonomy

Keep the following categories disjoint in text, tables, and reports:

| Category | Definition | TRI status |
|---|---|---|
| Initial binding error | The pre-refresh selector/ID is wrong | Not TRI |
| Tool-order error | Refresh or mutation occurs in the wrong temporal order | Not TRI |
| Conditional TRI substitution | Correct bound old ID is replaced by the changed refreshed winner on Preserve | TRI mechanism |
| Premature lock | A Reevaluate row retains an old bound ID | Complementary policy error |
| Selector grounding error | The controller picks another entity without the defined substitution pattern | Not TRI |
| Reject-policy error | A fallback action conflicts with the chosen execution policy | Separate execution-policy result |
| Wrong-entity write | An executed mutation changes an unauthorized target | Consequence, not a synonym for TRI |

## Claim Registry

| Claim | Evidence status | Permitted conclusion | Excluded conclusion |
|---|---|---|---|
| Matched authorization contrast identifies mode-blind policies | Controlled construction and deterministic controls | One-sided/Stable scoring is insufficient in this diagnostic | All benchmarks are unidentifiable |
| Generic controllers substitute refreshed winners after correct binding | Frozen v3/v7 controller runs | A controller- and model-conditional behavior exists in tested scaffolds | A universal LLM mechanism |
| Substitutions can cause wrong writes | Deterministic SQLite replay and model-facing SQLite rows | The target error has executable consequences in the controlled substrate | Deployed safety prevalence |
| Executable timing decisions reduce the controlled error | CTA, Lifecycle, and rule probes | Multiple implementations can operationalize the distinction | CTA/Lifecycle is uniquely necessary or generally safest |
| Audited suites have zero strict native opportunities | Frozen descriptive audits of three versions | These audited regimes lack the listed conjunction under the checklist | All current tool-agent evaluations lack TRI |
| Lower-intervention loops are null | Completed custom external-style studies | The controlled behavior has not been stably reproduced there | The controlled identifiability result is false |

## Falsifiers and Interpretation Gates

- If independently authored instructions do not produce determinate, interpretable timing
  judgments, TRI remains a template-bound diagnostic rather than a supported language construct.
- If a frozen rule remains comparable to CTA on independently authored language, retain the
  evaluation contribution but drop any method-generalization implication.
- If ordinary full-history native loops remain conditionally null after a qualifying independent
  inventory, report that the controlled behavior was not externally reproduced; do not seek a
  positive result through prompt or task tuning.
- If a second human audit finds missed strict public-suite opportunities, revise the coverage
  claim to the audited recall-supported subset rather than defending the original zero.
- If an initial-misbinding boundary shows lock-like policies propagate errors, report this as a
  deployment limitation. It cannot enter the conditional TRI numerator.

## Paper Consequences After Completed Analyses

1. Use `discourse-authorized re-resolution` or `instruction-conditioned resolution timing` when
   security authorization could be inferred; define the shorter TRI term once.
2. Call the Preserve/Reevaluate x Stable/Changed-winner structure a **crossed factorial
   diagnostic**, not a compositional controller result.
3. Lead results with changed-winner PairAcc and actionable referential-core accuracy. Retain the
   frozen all-row aggregate and reject-policy slice as separately labeled outcomes.
4. Describe CTA, Lifecycle, gates, and rules as probes/realizations. Do not attribute controlled
   gains to an internal model mechanism.
5. Keep public-suite findings scoped to the three audited versions and distinguish strict native
   opportunities, near-matches, action-induced cases, and custom interventions.
