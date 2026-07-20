# TRI-v3 Experiment Decision Log

This file records decisions made after the TRI-v3 protocol was frozen. It is an audit aid,
not a paper draft. Numbers below come only from complete run files unless explicitly marked
as smoke-test results.

## Frozen protocol

- Protocol: `reports/TRI_v3_preregistered_protocol.md`.
- Primary comparison: Generic Structured Ledger versus Lifecycle-Gated Controller.
- Primary dataset: 160 language-cluster tasks, with 20 template clusters.
- Transfer dataset: 80 unseen-domain tasks, with four new schemas and 20 template clusters.
- Qwen3.5-122B-A10B runs first; GLM-5.1 proceeds only after an informative Qwen result.
- Temperature is zero, thinking is disabled, and API failures are audited separately.
- No controller prompt or frozen dataset was changed after inspecting TRI-v3 outputs.

## Qwen language-cluster decision

Both runs are complete (160/160), with zero API errors and zero retries.

| Controller | Accuracy | Anchored | Dynamic | Wrong SQLite writes |
|---|---:|---:|---:|---:|
| Generic Structured Ledger | 64.4 | 33.8 | 95.0 | 32.5 |
| Lifecycle-Gated Controller | 98.1 | 100.0 | 96.2 | 0.0 |

The pre-specified cluster-resampled difference is +33.8 percentage points, with 95% CI
[+18.1, +50.0]. This passed the gate for unseen-domain evaluation and GLM replication.

Stage analysis shows that the lifecycle compiler correctly produced mode, bound identity,
and policy on all 160 tasks. Its three errors were dynamic-branch actor errors. The generic
ledger failures concentrate on anchored references despite retaining identity, a snapshot,
the selector, and action preconditions.

## Qwen unseen-domain decision

Both runs are complete (80/80), with zero API errors and zero retries.

| Controller | Accuracy | Anchored | Dynamic | Wrong SQLite writes |
|---|---:|---:|---:|---:|
| Generic Structured Ledger | 46.2 | 27.5 | 65.0 | 22.5 |
| Lifecycle-Gated Controller | 82.5 | 70.0 | 95.0 | 0.0 |

The cluster-resampled difference is +36.2 points, with 95% CI [+25.0, +47.5]. McNemar's
discordant counts are 0 ledger-only and 29 lifecycle-only, exact p=3.725e-9.

This result supports schema transfer of the reference-mode mechanism, but it also exposes a
separate selector-grounding limitation. For inventory and deployment, Qwen sometimes ignored
the filter in compound selectors such as `lowest-stock reorderable` and `oldest failing`.
The lifecycle compiler then bound an ineligible entity. The gate safely rejected it, yielding
no wrong writes but unnecessary rejection. Final accuracy therefore must be reported together
with stage accuracy and error type; invalid cases can be correct even when the compiled ID is
wrong.

## Cost evidence

On Qwen language clusters, Generic Structured Ledger uses two API requests per task.
Lifecycle-Gated uses one request for anchored tasks because its deterministic preserve gate
skips the actor, and two for dynamic tasks. The frozen runner logs request count, retry count,
and wall-clock latency, but not API token usage. Token cost must not be estimated or claimed.

## GLM decision

The balanced 20-task smoke test completed without API errors or retries:

| Controller | Accuracy |
|---|---:|
| Generic Structured Ledger | 70.0 |
| Lifecycle-Gated Controller | 100.0 |

This passed the pre-registered gate for the full 160-task language-cluster replication. The
full runs were executed sequentially to reduce overload risk. Both files passed the dataset-
aware audit: 160/160 unique expected tasks, no missing or extra rows, zero API errors, and zero
retries.

| Controller | Accuracy | Anchored | Dynamic | Wrong SQLite writes |
|---|---:|---:|---:|---:|
| Generic Structured Ledger | 71.9 | 56.2 | 87.5 | 11.2 |
| Lifecycle-Gated Controller | 100.0 | 100.0 | 100.0 | 0.0 |

The template-cluster bootstrap difference is +28.1 points, with 95% CI [+18.1, +38.1].
McNemar's discordant counts are 0 ledger-only and 45 lifecycle-only, exact p=5.684e-14.
The lifecycle compiler's mode, bound identity, and policy fields were all correct, and no actor
failure occurred. This independently replicates the language-cluster mechanism found with
Qwen, while absolute generic-ledger performance differs by model.

## Claims allowed by current evidence

1. A generic structured state containing identity, entity snapshot, selector, and action
   preconditions is not sufficient to reliably preserve discourse-established identity across
   a refresh.
2. Explicit lifecycle mode plus an enforcement gate substantially reduces temporal rebinding
   on independent language clusters and transfers to four new schemas for Qwen.
3. SQLite mutation replay shows that target-resolution errors can become actual wrong-entity
   writes, while lifecycle gating trades some unsafe execution for conservative rejection.
4. In a separately frozen 40-task model-facing SQLite trajectory, Generic Structured Ledger
   achieves 67.5% final-state success and produces 13 wrong-entity writes (32.5%), while the
   Lifecycle-Gated Controller achieves 100.0% final-state success with zero wrong writes. The
   template-cluster difference is +32.5 points, 95% CI [+15.0, +50.0]. Both runs are complete,
   contain no API errors or retries, and execute actual SQL mutations after a database refresh.

## Claims not yet allowed

1. The evaluation does not establish universal reliability or natural user-distribution
   prevalence; all TRI-v3 tasks are synthetic diagnostics.
2. The model-facing SQLite experiment is controller-orchestrated: query and required refresh
   order are fixed by the runtime, while the model compiles target state and selects unresolved
   mutation targets. It is not an external benchmark or a fully autonomous planning evaluation.
3. TRI-v3 does not vary invalidity policy: preserved targets are rejected when action-invalid.
   It therefore cannot establish the necessity of multiple fallback policies.
4. The unseen-domain set repeats one state layout per domain across language templates. It tests
   new schemas and IDs, but not broad procedural state-instance diversity.
5. Token usage and monetary cost are not available from the frozen run logs.

## Next Go/No-Go experiments

1. Finish and audit both GLM language-cluster runs. Stop and diagnose if API/parse errors exceed
   one per controller; do not interpret service failures as model behavior.
2. Add a policy-guard extension only as a separately frozen experiment. It must distinguish
   `preserve if action-valid, else reevaluate` from `preserve if selector still holds, else
   reevaluate`; a single conditional label is insufficient.
3. The model-facing SQLite trajectory is complete. Keep the larger mutation replay as a
   consequence analysis and present the 40-task trajectory as the execution check.
4. Do not run GLM unseen-domain by default: Qwen transfer, two-model language replication, and
   model-facing writes now cover the main empirical risks. Reconsider only if another analysis
   exposes a model-specific transfer ambiguity.
5. Run the separately frozen TRI-v4 policy smoke. Expand only if it passes its own gate; retain
   a negative result as an explicit scope boundary rather than delaying the main paper.
6. Do not rewrite paper prose until these decisions are resolved. Related-work verification and
   figure planning may proceed without changing empirical claims.

## TRI-v4 guarded-policy decision

The 10-task Qwen smoke passed the API/parse gate and produced an interpretable 40.0% versus
80.0% difference, so both controllers were run on the complete 40-task frozen set. Both full
files passed the dataset-aware audit and contain zero API errors or retries.

| Controller | Overall | Action-validity guard | Selector-match guard |
|---|---:|---:|---:|
| Generic Structured Ledger | 52.5 | 40.0 | 65.0 |
| Guarded Lifecycle Controller | 85.0 | 80.0 | 90.0 |

The template-cluster difference is +32.5 points, with 95% CI [+15.0, +52.5]. Paired
discordance is 2 generic-only versus 15 guarded-only, exact McNemar p=0.00235. The result
supports the need to represent conditional guards rather than collapsing all references into
preserve or reevaluate.

Stage analysis also limits the claim. Guard classification is 100% for action-validity tasks
and 75% for selector-match tasks, while bound-ID accuracy is low on compound unseen-domain
selectors. Guarded control improves final decisions but does not solve initial selector
grounding. TRI-v4 should be reported as a secondary extension, with the cleaner TRI-v3
preserve/reevaluate comparison remaining the primary result.

## Experiment freeze decision

Stop adding model matrices before the paper rewrite. The current evidence includes:

- two-model replication on 20 independent language-template clusters;
- Qwen transfer to four unseen schemas;
- an information-matched, two-stage Generic Structured Ledger direct-neighbor baseline;
- cluster-aware confidence intervals and paired tests;
- large mutation replay and a separately frozen model-facing SQLite trajectory;
- stage-wise compiler/actor analysis and logged request/latency cost;
- a guarded conditional-policy extension.

GLM unseen-domain, GLM TRI-v4, a third model, and larger external benchmarks are optional future
work unless paper review exposes a specific unresolved ambiguity. With the AAAI-27 full-paper
deadline on 2026-07-28, the next priority is a complete seven-page main paper using the official
AuthorKit, followed by reproducibility packaging and a concise supplement.

## Post-freeze 2x2 attribution addendum

A reviewer-risk audit found that the original primary comparison did not separate lifecycle
representation from deterministic enforcement. We froze a factorial addendum before running
the missing cells. Existing outputs were reused wherever represented state and actor were
identical; only missing lifecycle-free preserve branches required new model calls.

| Evaluation | Generic free | Generic validity gate | Lifecycle free | Lifecycle gate |
|---|---:|---:|---:|---:|
| Qwen primary (160) | 64.4 | 65.0 | 96.9 | 98.1 |
| GLM primary (160) | 71.9 | 73.1 | 98.1 | 100.0 |
| Qwen unseen schemas (80) | 46.2 | 46.2 | 87.5 | 82.5 |
| Qwen SQLite final state (40) | 67.5 | 67.5 | 100.0 | 100.0 |

The principal effect is lifecycle representation, not deterministic gating. On Qwen primary,
lifecycle-free exceeds generic validity-gated control by 31.9 points, cluster 95% CI
[17.5, 47.5]. The corresponding GLM effect is +25.0 points, CI [15.6, 35.0]. Generic
action-validity gating changes primary accuracy by at most 1.2 points and does not reduce the 13
wrong writes in SQLite. The lifecycle gate adds only 1.2--1.9 points on the primary tests.

On unseen schemas, lifecycle gating is 5.0 points worse than lifecycle-free execution because
the deterministic boundary conservatively rejects wrong compound-selector IDs that a free actor
occasionally repairs. This negative result narrows the method claim: lifecycle state is the core
contribution; deterministic mutation-boundary enforcement is an optional executor variant that
can reduce calls and enforce correct compiled commitments but cannot repair a wrong mode or ID.

The paper must therefore use `Lifecycle-Compiled Controller` or `Temporal Authorization State`
for the main method, with free and gated executors as variants. It must not describe generic and
lifecycle-gated conditions as call-matched. On the 40 SQLite tasks, lifecycle-gated execution
uses 60 model requests versus 80 for generic structured state; lifecycle-free uses 80.

## Second-model SQLite replication

The frozen 40-task model-facing SQLite subset was replicated with GLM-5.1 after an 8-task smoke
gate. Generic Structured Ledger obtains 26/40 correct final states (65.0%), with eight
wrong-entity writes, six unnecessary rejections, and zero API errors. Lifecycle-gated execution
obtains 40/40 with no wrong write, unnecessary rejection, collateral modification, API error, or
retry. The paired final-state gain is +35.0 points with template-cluster 95% CI [+17.5, +52.5].
Qwen's corresponding paired gain is +32.5 points, CI [+15.0, +50.0]. Across the 80 paired
model-task trajectories, Generic produces 21 wrong writes and 53/80 correct final states;
Lifecycle-gated produces zero wrong writes and 80/80 correct final states.

## Oracle component decomposition

Qwen primary mode and anchored bound-ID compilation are both 100%, and oracle replacement does
not improve the learned 98.1% gated result. On unseen schemas, mode remains 100% but anchored
bound-ID accuracy falls to 52.5%; replacing only the ID raises gated accuracy from 82.5% to
97.5%. The transfer bottleneck is therefore selector grounding, not post-binding mode semantics.
Oracle results are a representation-sufficiency and error-localization check, not evidence of a
general performance guarantee.

## Revised claim boundary

The contribution is post-binding temporal authorization: after an initially resolved reference,
a world update changes its denotation only when language authorizes a reference transition.
Results support this claim in controlled scalar diagnostics and controller-orchestrated SQLite
trajectories. They do not establish prevalence in natural traffic, broad autonomous planning, or
correctness under compilation errors. Independent human construct validation remains required
before claiming that the prescribed implicit readings match broad user interpretation.

## TRI-v5 multi-refresh and multi-referent stress decision

The frozen 40-task Qwen stress test inserts two refreshes, a monitoring-only selector referent,
an unrelated count call, and a real SQLite mutation. Generic structured state obtains 80.0%
(32/40), while the unchanged scalar lifecycle controller obtains 70.0% (28/40). The paired
difference is -10.0 points, template-cluster 95% CI [-35.0, +12.5], with 11 generic-only and 7
lifecycle-only successes (exact McNemar p=0.481). One lifecycle response contains no parseable
JSON; it is retained as failure in the intention-to-treat result and reported separately from
API errors.

Lifecycle performance decomposes into 100% anchored accuracy and 40% dynamic accuracy. The
compiler assigns the correct action-reference mode on only 25/40 tasks, although anchored bound
IDs are 20/20. It frequently treats the intermediate monitoring referent as if it were the
action referent, compiling dynamic instructions as preserve. This creates six wrong writes and
six unnecessary rejections. The generic controller creates one wrong write and four unnecessary
rejections.

This negative stress result is a useful scope boundary. A single scalar lifecycle record handles
one action referent but is not a compositional account of multiple simultaneously active
references and their discourse roles. TRI-v5 remains secondary and must not be pooled with the
single-action-referent primary evaluation. A future reference graph should assign distinct
lifecycle records and roles to action and monitoring referents; that extension is not evaluated
in the current paper.

## Post-freeze alternative-explanation baselines

Following a reviewer-risk audit, we froze two additional Qwen primary conditions that reuse the
exact Generic Structured Ledger outputs and replace only the action-time actor. The first adds an
ordinary sentence-level TRI reminder without a lifecycle record. The second rereads the original
instruction at action time, predicts preserve versus reevaluate, and applies a semantic gate.

| Qwen primary condition (160) | Overall | Anchored | Dynamic | API errors |
|---|---:|---:|---:|---:|
| Generic free actor | 64.4 | 33.8 | 95.0 | 0 |
| Generic + ordinary reminder | 58.8 | 77.5 | 40.0 | 0 |
| Action-time semantic compiler + gate | 68.1 | 37.5 | 98.8 | 0 |
| Lifecycle free actor | 96.9 | 97.5 | 96.2 | 0 |

The ordinary reminder does not explain the lifecycle effect: it raises anchored accuracy but
over-preserves dynamic references, moving rather than resolving the error. Relative to Generic,
its paired difference is -5.6 points with template-cluster 95% CI [-30.0, +18.8]. Lifecycle-free
exceeds the reminder by 38.1 points, CI [+27.5, +49.4], and wins on 18 of 20 templates with two
ties.

Action-time semantic compilation is also insufficient. It improves over Generic by only 3.8
points, CI [-0.6, +8.8], and retains the same anchored failure pattern. Lifecycle-free exceeds it
by 28.7 points, CI [+12.5, +45.6], with nine template wins, nine ties, and two losses. These
results support pre-refresh compilation into persistent lifecycle state in this controlled
setting; they do not prove that the particular full tuple is mathematically minimal.

## Matched pre-refresh untyped baseline

A stronger audit baseline compiles one free-form plan before refresh, prohibits lifecycle field
names, and uses the same two-call budget, temporal boundary, and free actor as Lifecycle-free.

| Model / controller | Overall | Anchored | Dynamic |
|---|---:|---:|---:|
| Qwen Generic | 64.4 | 33.8 | 95.0 |
| Qwen Untyped | 81.2 | 71.2 | 91.2 |
| Qwen Typed lifecycle | 96.9 | 97.5 | 96.2 |
| GLM Generic | 71.9 | 56.2 | 87.5 |
| GLM Untyped | 70.6 | 42.5 | 98.8 |
| GLM Typed lifecycle | 98.1 | 96.2 | 100.0 |

Typed minus untyped is +15.6 points for Qwen, template-cluster 95% CI [+7.5, +25.0],
and +27.5 for GLM, CI [+15.0, +41.2]. Both intervals exclude zero. This supports typed
persistent state over a matched free-form contract on the controlled scalar family, not
mathematical minimality.

## ToolSandbox-based autonomous extension

ToolSandbox is pinned at commit `165848b9a78cead7ca7fe7c89c688b58e6501219`.
The custom extension reuses its Reminder database, snapshots, stable IDs, search, and mutation,
while adding an exogenous sync and lock policy. It is not an official ToolSandbox score.
Twenty-four held-out paraphrases cross six selectors, both reference modes, and four transition
types. The agent autonomously chooses tools; one matched compiler call occurs after its first
successful search. Three snapshots separate environment transitions from agent writes.

| Model | Generic | Untyped | Lifecycle-free | Gate replay |
|---|---:|---:|---:|---:|
| Qwen3.5 | 91.7 | 79.2 | 83.3 | 91.7 |
| GLM-5.1 | 79.2 | 91.7 | 87.5 | 91.7 |

Gate replay improves Lifecycle-free by +8.3 points for Qwen and +4.2 for GLM but only ties each
model's strongest baseline. Remaining wrong writes arise from grounding, initial binding, or
free-actor noncompliance. GLM makes the same pluralized unknown-tool call on one task under all
three controllers; it is retained as a common protocol failure rather than retried. This
exploratory result establishes autonomous write consequences and a scope boundary, not broad
method superiority.
