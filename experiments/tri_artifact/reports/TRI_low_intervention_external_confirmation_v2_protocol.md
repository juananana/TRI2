# TRI Low-Intervention External Confirmation v2 Protocol

**Status:** prospective protocol; API execution is not authorized unless the zero-API inventory
gate returns `GO`. This is post-primary work and cannot replace the v3 primary estimand.

## Claim and Alternative Explanation

Claim tested: conditional unauthorized rebinding can occur in ordinary full-history tool loops
that expose only normal selector results, stable IDs, refresh tools, and mutations.

Alternative explanation excluded: the controlled v3/v7 effect is induced by the Generic ledger,
explicit selector fields, TRI terminology, a binding sidecar, or a two-stage compiler/actor
interface.

## Required Inventory

Before any API call, freeze an inventory satisfying all of the following:

- at least four application domains with native or AppWorld-style tools;
- at least 20 independent workflow clusters;
- instructions authored by people not involved in TRI task or rule development;
- Preserve/Reevaluate x Stable/Flip matched cells within every cluster;
- a normal selector API that returns one stable ID;
- an externally injected or synchronization-style transition after binding;
- a later mutation whose final state diff identifies the written entity;
- no prompt fields named TRI, authorization, Preserve, Reevaluate, reference mode, or gold target.

The completed Todoist/Simple Note ordinary-agent study does not satisfy the domain, cluster, or
independent-author requirements. It is retained as completed null evidence and must not be rerun
or expanded by author-written paraphrases merely to seek a positive result.

## Frozen Agent Conditions

If and only if the inventory gate passes:

1. ordinary full-history function calling;
2. Generic Structured Ledger;
3. historical CTA;
4. an information-matched dialogue-aware mutation verifier.

Use Qwen3.5-122B-A10B and GLM-5.1, temperature zero, thinking disabled, a 500-token output cap,
a 180-second request timeout, and at most one transport retry. API and parse failures remain in
the intention-to-treat denominator and are also reported separately.

## Metrics and Denominators

The primary mechanism denominator requires:

1. a correct observable selector binding;
2. binding before refresh for Preserve or after refresh for Reevaluate;
3. a completed refresh before mutation;
4. a surviving and action-valid old target;
5. a distinct refreshed selector winner for Flip;
6. an attempted entity-directed mutation.

Report initial binding, tool-order error, conditional TRI substitution, premature locking, Stable
error, wrong-entity write, rejection, invalid attempt, collateral write, API/parse failure, and
final-state success separately. Changed-winner PairAcc is clustered by workflow cluster.

## Zero-API and Smoke Gates

Run `scripts/audit_external_confirmation_gate.py` first. `NO-GO` forbids API calls. After a `GO`,
run deterministic oracle, state-transition, stable-ID, mutation-diff, duplicate-ID, and prompt
leakage tests, followed by one frozen four-task cluster as a transport/parse smoke. Do not inspect
smoke accuracy to modify prompts. Expand only if the smoke has no protocol error and at most one
API/parse failure per condition.

## Outcomes and Stopping Rule

- Strengthen: at least two model-controller cells show Preserve/Flip refreshed-winner
  substitution, near-zero matched Stable error, and wrong-entity writes after correct binding.
- Narrow: the effect appears in only one model or controller, or confidence intervals are wide.
- Overturn the external-occurrence claim: all ordinary-agent cells are null and errors are instead
  pre-binding, selector, or tool-order failures.

Complete the frozen inventory exactly once. No prompt or rule tuning is permitted after smoke or
full-run output inspection. Retain every attempted row and publish raw JSONL, report code, JSON,
Markdown, cost, retries, and the final Go/No-Go decision.
