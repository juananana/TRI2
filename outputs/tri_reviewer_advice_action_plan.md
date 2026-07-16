# TRI Reviewer-Style Advice: Action Plan

Source: user-provided ChatGPT review memo, 2026-07-16.

## Main Takeaway

The direction has real AAAI main-track potential, but the paper must move from
"interesting counterexample" to:

> a general sufficient-state problem for agent controllers, with evidence that
> referent drift can arise from realistic state compression and with a
> principled referent lifecycle representation.

## Adopted Changes

### 1. Reframe as Sufficient State

The paper should explicitly say state-overwrite is not merely a model reasoning
failure. It is an insufficient controller representation:

```text
latest_state + original_goal is not sufficient for anchored references.
```

Required sufficient state:

```text
z = (r, binding_time, bound_entity_id, selector, validity_condition, provenance)
```

### 2. Add Field Ablation

Add an oracle representation ablation:

- raw goal + latest state
- selector memory
- entity only
- time + entity
- full ledger

This proves the ledger is not just "save an ID"; validity and binding-time
fields solve different cases.

### 3. Treat Natural Memory Honestly

Natural memory succeeds on simple p0 examples. The paper should not claim typed
ledgers are the only solution. It should claim typed ledgers are more
verifiable and robust under compression, invalidation, and lifecycle events.

### 4. Expand Benchmark Semantics

Already added:

- flip
- stable
- removed entity
- compressed memory

Still needed:

- renamed entity
- action invalidity
- merge/split
- multiple referents
- multi-refresh trajectories

### 5. Real Controller Evidence

The strongest next experiment is to use actual controller styles:

- full ReAct/history
- automatic summary memory
- bounded latest-state controller
- compressed memory controller

Success criterion:

> A controller-generated memory, not an author-deleted state, causes anchored
> drift while dynamic controls remain correct.

## Not Adopted As Main Claim

Do not market TRI as a new referential semantics discovery. Reference,
coreference, and situated dialogue are old areas. The contribution is specific
to tool-using LLM agent state management under observation updates.

