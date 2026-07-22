# TRI AAAI-27 Innovation and Naturalism Restructure

Status: internal decision record, not empirical evidence.

## Target paper identity

The strongest defensible identity is not a new runtime architecture. It is an evaluation paper
showing that current agent benchmarks omit a decision variable needed to distinguish two opposite
but observationally similar policies:

> A world-state update changes evidence. It does not, by itself, authorize changing an already
> resolved action referent.

TRI contributes (1) the missing authorization variable, (2) necessary conditions for an identifying
evaluation, (3) matched workflow diagnostics, and (4) controlled evidence that ordinary
model-mediated controllers can fail while conventional aggregate or one-sided scores look good.

## Reviewer battle: likely objection and strongest answer

| Objection | Weak answer to avoid | Defensible answer |
|---|---|---|
| Binding Drift already studies replacement | TRI is a better lock | Binding Drift conditions on preservation; TRI varies whether preservation or reevaluation is authorized under the same transition, making the evaluation symmetric and policy-identifying. |
| Tasks are synthetic | We used many domains | The synthetic pairs are interventions that identify causality. Public suites lack the strict opportunity, which is itself a measurable benchmark-coverage gap. AppWorld traces support the workflow motif but not failure prevalence. |
| CTA is a simple prompt trick | CTA improves accuracy | CTA, Lifecycle, and a post-hoc deterministic rule all instantiate the same separation principle. Method simplicity narrows algorithmic novelty but strengthens the diagnosis. |
| Natural incidence is unknown | TRI is common in agents | Incidence is not estimated. Report strict-opportunity coverage, near-match motifs, auditable denominators, and conditional errors separately. |
| Composition is weak | Scalar success should transfer | It does not automatically transfer. Keep v5/v6 as a negative boundary and motivate role-indexed authorization as future work. |

## Two-day priorities

### P0: Main-paper narrative

1. Lead abstract, introduction, and contributions with benchmark identifiability, not CTA.
2. Define the workflow grammar as Observe--Bind--Refresh--Write and explain why all four events
   must be visible to score TRI.
3. Treat v3/v7 as controlled interventions; treat AppWorld/ToolSandbox/tau3 as coverage audits.
4. Keep the Binding Drift distinction in the first related-work paragraph that discusses it.
5. Preserve the post-hoc rule disclosure and all external/compositional null results.

### P1: Naturalism without unsupported prevalence

Report three different quantities rather than one ambiguous "occurrence rate":

- motif coverage: tasks containing a binding, update, and later same-role action;
- strict-opportunity coverage: motif plus changed winner and surviving old target;
- conditional error rate: substitutions only after a correct observable initial binding.

The current evidence supports 0 strict native families in the three audited public suites, one
AppWorld near-match family, and 0/16 substitutions in its auditable continuations. These values
support benchmark undercoverage and the realism of the workflow motif, not deployment prevalence.

### P1: Composition framing

Do not promote v5/v6 into a success story. Use them to state a sharper boundary: scalar
authorization records do not compose automatically when a workflow contains multiple referential
roles or refresh epochs. The future method target is a role-indexed transition relation, but the
current paper remains a problem-definition and diagnostic contribution.

## Only experiment worth considering before the gate closes

A new model run is justified only if it directly addresses the structural reject risk and follows
the project experiment gate. The bounded candidate is a frozen, workflow-grounded opportunity set:

- claim tested: the controlled finding survives ordinary selector APIs and multi-step app language;
- excluded alternative: the effect is induced by TRI terminology, sidecars, or direct mode labels;
- inventory: 24--40 matched tasks over at least three app motifs, with Preserve/Reevaluate and
  Stable/Flip crossed within each state instance;
- primary denominator: correct observable initial binding, completed refresh, old target still
  actionable, distinct refreshed winner, and attempted later mutation;
- outcomes: positive conditional substitution strengthens external validity; a clean null narrows
  the result to the controlled controllers; tool-order failures are reported separately;
- stopping rule: zero-API validation, four-task smoke, then one frozen full run; no prompt tuning.

Because the existing lower-intervention AppWorld study is null and the external review record says
new external evidence is the only remaining structural lever, this experiment should run only if
the inventory is frozen and genuinely more natural than the completed custom study. Otherwise it
adds volume without changing a skeptical reviewer's decision.

## Score calibration

With the current evidence, a realistic skeptical score remains around 4--5 because novelty and
external validity are debatable. A clean narrative can raise correctness, clarity, and perceived
originality, but a stable 6 requires reviewers to accept benchmark identifiability as the main
contribution. A 7 is unlikely without independent naturalistic opportunity evidence or a broader
validated compositional result; wording alone cannot honestly create that evidence.
