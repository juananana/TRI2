# AppWorld Ordinary Full-History Selector-API Addendum

**Status:** frozen after the sidecar-based AppWorld study and before any model call in this
addendum. This is post-primary evidence and must not be described as preregistered or as an
unmodified AppWorld leaderboard result.

## Motivation

The earlier AppWorld pilot exposed binding through a required `record_binding` sidecar and told
the Agent to follow temporal ordering and reference meaning. Sidecar omission affected 8/32
trajectories, so that protocol can perturb an otherwise ordinary tool workflow. This addendum
removes both interventions.

## Frozen Design

- Apps: Todoist and Simple Note.
- Existing frozen scenarios: Preserve/Reevaluate x Stable/Flip x two paraphrases per app.
- Models: Qwen3.5-122B-A10B and GLM-5.1, temperature zero, thinking disabled.
- Controller: ordinary full conversation history; no ledger, lifecycle state, reference-mode
  field, commitment reminder, or deterministic gate.
- System prompt: tool names, argument schemas, one-tool-per-turn constraint, and JSON syntax only.
  It does not mention TRI, temporal authorization, binding, Preserve, Reevaluate, or the correct
  interpretation of ordering.
- Calls: AppWorld-native database/API wrappers and stable IDs; no LLM judge.

The normal selector API returns exactly one winner and its stable ID:
`find_earliest_incomplete_task` for Todoist and `find_alphabetically_first_note` for Simple Note.
The runner logs this ordinary tool result as an observable binding event. The model does not call
an instrumentation tool. Synchronization then adds a Stable distractor or a Flip winner. Mutation
uses the ID chosen by the Agent.

## Frozen Estimands

The primary estimand is conditional TRI after a correct, correctly timed selector call. A
Preserve/Flip error requires the pre-sync selector to return A and the final database write to B.
A Reevaluate/Flip premature lock requires the post-sync selector to return B and the write to A.
Stable errors, selector/tool-order failures, API errors, rejected writes, and collateral writes are
reported separately. Results are clustered by application/selector, not by row.

## Interpretation

This addendum tests ordinary function-calling behavior with lower measurement intervention. It
remains a custom, opportunity-conditioned AppWorld experiment, not uncontrolled traffic and not a
prevalence estimate. A positive result strengthens external mechanism evidence; a null result
bounds the phenomenon for these full-history Agents.
