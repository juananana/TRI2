# TRI Unified Environment Holdout Protocol

**Status:** planned/unverified until ethics, independent writing, blind adjudication, and the
clear-cluster gate pass.

This protocol combines the independent-language and deployment-style studies without claiming
natural prevalence. It uses AgentDojo at commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` and
ToolSandbox at commit `165848b9a78cead7ca7fe7c89c688b58e6501219`.

## Collection design

Twelve independent writers create 60 candidate changed pairs, 30 per environment. The two members
of each pair are written by different people. Writers see only a neutral S0 state, selector,
action, tool capability, and required operation order; they do not see the alternate member, S1,
gold, Rule*, model output, or TRI templates. Three independent annotators label each instruction.

The writer's determinate intent must match the target implied by the assigned operation order, and
a 2/3 annotator majority must agree with that intent for an item to be clear. A pair is clear only
when both members are clear and action validity, old-target survival, distinct
winner, and target-level state-diff checks pass. The processor takes the first 20 clear pairs per
environment in the preassigned candidate order. If either environment has fewer than 20, no model
call is permitted and the collection is reported as a failed gate.

Writer intent and all three adjudications are serialized as refreshed-state target IDs (or
`CLARIFY`), not as Preserve/Reevaluate labels. The processor independently derives the expected
target ID from the assigned operation order and winner fields, then requires equality among that
target, writer intent, and the annotator majority.

The executable gate requires exactly 30 candidate pairs per environment and a unique frozen
`candidate_order` of 0--29 before writer forms are produced. Selection sorts by this field rather
than file or return order. The freeze command also requires a hash-matched human-provenance record
with the pre-recruitment ethics determination, all 12 independent writer gates, all three blind
annotator gates, and the exact status `complete-locked-before-model-calls`. A merely complete or
unverified record cannot unlock model calls.

The executable validator requires both pair members to share environment commit, selector, action,
schema, S0, changed S1, Stable S1, and all winner IDs. It checks action preconditions for the old
and new changed-state targets, the surviving Stable old target, and requires the Stable winner to
remain the pre-refresh winner. It also requires nonempty environment preflight diffs for changed-old,
changed-new, and Stable-old mutations; each diff may change only its intended target.

## Frozen execution set

Each clear pair produces three rows: changed Preserve, changed Reevaluate, and Stable Preserve
using the same Preserve instruction/action but a refresh that leaves the selector winner unchanged.
The final inventory therefore has exactly 40 clusters and 120 rows. The locked JSONL includes
environment commit, state snapshots, selector, action schema, anonymized writer IDs, adjudications,
eligibility reasons, and a SHA-256 manifest. Private consent, compensation, and identity records
remain outside the artifact.

## Model stage

The complete candidate set is ordinary full history, matched History-only, matched Decision-visible,
historical CTA, Always-Lock, and Always-Reevaluate. Non-deterministic controllers use the real tool
interface and retain initial selection, refresh, proposal, mutation, tool result, and final state
diff. All failures remain ITT errors; refusal, invalid attempts, and wrong writes are separate from
actionable success.

Primary endpoints are changed PairAcc, all-row E2E, conditional Preserve substitution, wrong-entity
writes, invalid attempts, rejection, collateral changes, calls, tokens, and latency. All exact
maximizers and ties are retained for both E2E and PairAcc. Reporting requires the complete
AgentDojo/ToolSandbox by Qwen/GLM/DeepSeek matrix, with every frozen controller present exactly once
per cell. Cross-metric regret is reported as a range over all tied maximizers.

Each environment--model--controller cell contains 20 changed pairs and 60 executed rows. The raw
execution interface is the source of every reported endpoint and must retain the initial selection,
refresh completion, target proposal, mutation target, ordered real-tool trace, final state diff,
collateral-change count, failure status, calls, tokens, and latency. Missing matrix rows are fatal;
API and parse failures remain incorrect under ITT. Rule* is run unchanged as a separately labeled
post-hoc baseline on the same locked rows and is never inserted into the six-controller maximizer
set.

The final state diff is computed between the post-refresh observation immediately before mutation
and the state after the mutation attempt. The validator requires trace events in interface order,
requires every successful or wrong-entity write to name a changed target, and derives the set of
collateral targets from that diff; a supplied collateral count that disagrees with the diff is a
schema failure rather than a reportable outcome.

## Promotion gate

A practical-selection claim requires disjoint E2E and PairAcc maximizer sets in at least two
environment-model cells and no higher wrong-write rate for the PairAcc-selected controller. If the
sets overlap, report tie regret only. Passing the writer/annotation gate supports independent
controlled-language construction, not natural traffic or prevalence.
