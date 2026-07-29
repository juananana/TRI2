# TRI Deployment-Style Evaluation-Decision Protocol

**Evidence status:** `planned/unverified`.

**Protocol version:** `TRI-deployment-evaluation-decision-v1`.

**Freeze date:** 2026-07-28 (Asia/Shanghai). The design and analysis rules below are frozen before
workflow collection or model calls. Environment commits, the final inventory hash, prompt hashes,
and participant-policy determination must be added to the manifest before the first model call.

## Question and claim boundary

This study asks whether TRI changes a controller-selection decision on independently authored,
executed workflows rather than only explaining an authored diagnostic. It does not estimate
natural-traffic prevalence: the inventory is intentionally enriched for workflows with a strict
TRI opportunity.

A selection-change claim is allowed only under the frozen complete candidate set and rule below.
No controller, model, environment, workflow, metric, denominator, or tie rule may be removed after
outcomes are inspected.

## Human, ethics, and independence gate

Before recruitment, the study team records the applicable institutional approval, exemption, or
policy determination. Workflow authors and gold adjudicators must be adults, give informed
consent, and be independent of TRI task-template design, Rule* development, model prompting, and
result analysis. LLM-generated workflows or LLM judges cannot satisfy participant counts.

Identity-bearing recruitment and payment records remain private. The anonymous artifact may
contain only de-identified instructions, adjudications, eligibility fields, hashes, and aggregate
reports.

## Environments and cluster inventory

- At least two released stateful tool environments, pinned to immutable commits before collection.
- Exactly 40 eligible workflow clusters, allocated 20 per environment.
- Each cluster contains three executed rows over the same entities, selector, action, and tool
  schema: one changed-winner Preserve row, one changed-winner Reevaluate row, and one Stable
  Preserve control. Total: 120 rows.
- The changed pair shares $S_0$, $S_1$, selector, action, and transition while changing only
  commitment timing. The Stable control preserves the Preserve instruction and action but uses a
  matched refresh that does not change the selector winner.
- Every changed cluster must have a unique $S_0$ winner, a distinct unique $S_1$ winner, a
  surviving action-valid old target, and a target-level state diff after execution.

Workflow authors select tasks from the pinned environment states and tools without seeing TRI
templates, model outputs, alternate pair members, or Rule* vocabulary. Different authors produce
the two changed-pair instructions. Three separate adjudicators label intended target and action
validity with opaque IDs. A row is clear when at least two of three adjudicators agree with the
author's determinate intent; a cluster is eligible only when all three rows are clear.

The collection continues in a preassigned author/environment order until exactly 40 eligible
clusters are obtained. Every rejected or replaced cluster and its exclusion reason remains in a
private eligibility ledger. The locked 120-row inventory and its SHA-256 are written before model
calls. If 40 eligible clusters cannot be obtained, the study stops and reports only the collection
gate; no reduced model experiment is permitted.

## Executed agent interface

Every non-deterministic controller must perform the workflow through the environment's real tool
interface. The trace must retain the initial selection event and ID, refresh request and response,
final target proposal, mutation call, tool result, and final state diff. The ordinary agent must
produce its own initial selection; no gold or resolver-produced ID is injected.

All controllers receive the same natural instruction, environment observations, and tool schema.
Conditions that add a compiler call or decision representation record the extra request and token
cost. Gold target, normalized selector, refreshed winner, and adjudicator labels are withheld.

## Frozen candidate set

The complete candidate set is evaluated for Qwen, GLM, and DeepSeek:

1. ordinary full history;
2. matched History-only;
3. matched Decision-visible;
4. historical Compile-then-act (CTA);
5. deterministic Always-Lock;
6. deterministic Always-Reevaluate.

History-only and Decision-visible use equal actor calls, identical base payloads, and the frozen
composite-block interface. CTA is a complete package comparison and is not treated as call-matched.
The two deterministic strategies are diagnostic controls and remain in all selection calculations.

Exact model IDs, provider endpoint, temperature, token cap, reasoning controls, retry policy,
timeouts, prompt hashes, parser, and actor-order rotation must be recorded in the final freeze
manifest. API, transport, parse, schema, and missing-output failures remain incorrect under ITT.
No task or controller result may be retried at the logical-call level except the predeclared
transport retry policy.

## Endpoints and denominators

For every environment--model--controller cell:

1. changed PairAcc over the 20 frozen Preserve/Reevaluate pairs in that environment;
2. row-level E2E over the 60 rows in that environment;
3. Preserve conditional substitution, requiring a correct observable initial binding, completed
   refresh, distinct refreshed winner, and surviving action-valid old target;
4. strict wrong-entity writes, all wrong writes, invalid attempts, unnecessary rejection, and
   collateral state changes;
5. request count, token count, and wall-clock latency as descriptive resource outcomes.

Stable errors and changed errors remain separate. Zero conditional substitutions is not overall
success, and refusal is not counted as a correct actionable task.

The unchanged benchmark-aware Rule* is executed once on all 120 locked rows as a formal post-hoc
strong baseline. It is labeled post-hoc, its source hash is frozen before execution, and it is not
added to or substituted for any member of the six-controller selection set.

## Frozen selection comparison

Within every environment--model cell, enumerate all exact maximizers over the full six-controller
candidate set for:

- aggregate E2E; and
- changed PairAcc.

All ties are retained. A **strong selection change** occurs only when the two maximizer sets are
disjoint. If they overlap but aggregate E2E also licenses a controller with lower PairAcc, report
the exact optimistic and worst-case tie regret; call this tie sensitivity, not a demonstrated
selection change. Pooled or hand-selected controller subsets cannot support the claim.

An abstract-level practical-evaluation claim additionally requires at least one strong selection
change that reproduces in two environment--model cells, with the selected PairAcc-maximizing
controller producing no higher wrong-write rate than every aggregate-E2E maximizer in those cells.
Otherwise the result may support localization or tie sensitivity only.

## Inference and stopping

- Cluster unit: workflow cluster; complete three-row clusters are resampled together.
- Bootstrap: 10,000 percentile replicates, seed `20260728`.
- PairAcc contrasts preserve complete pairs.
- Exact paired discordance tests are auxiliary; Holm correction is applied within each model over
  the predeclared controller contrasts and three primary behavioral endpoints.
- No accuracy-based stopping rule. Every frozen controller runs on all 120 rows for every model.

Negative, null, mixed, failed, and adverse results are retained. Prompt tuning, controller
selection, task deletion, or metric changes after the first model call invalidate promotion to
paper evidence and may be reported only as post-hoc exploratory work.

## Required outputs

The completed study must retain the protocol and freeze manifest, pinned-environment metadata,
de-identified locked inventory, adjudication and eligibility reports, every raw executed trace,
an executable report script, machine-readable and Markdown reports, cost report, input/output
hashes, and tests for pairing, denominator, tie, ITT, and state-diff rules.
