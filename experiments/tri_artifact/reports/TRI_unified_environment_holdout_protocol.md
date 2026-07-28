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

The writer's determinate intent and a 2/3 annotator majority must agree for an item to be clear. A
pair is clear only when both members are clear and action validity, old-target survival, distinct
winner, and target-level state-diff checks pass. The processor takes the first 20 clear pairs per
environment in the preassigned candidate order. If either environment has fewer than 20, no model
call is permitted and the collection is reported as a failed gate.

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
maximizers and ties are retained for both E2E and PairAcc.

## Promotion gate

A practical-selection claim requires disjoint E2E and PairAcc maximizer sets in at least two
environment-model cells and no higher wrong-write rate for the PairAcc-selected controller. If the
sets overlap, report tie regret only. Passing the writer/annotation gate supports independent
controlled-language construction, not natural traffic or prevalence.
