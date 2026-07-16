# Temporal Referent Integrity

This project extends the round-1 candidate tournament with a focused round-2
idea: tool-using agents should preserve the identity of entities that were
bound before an environment refresh, while still re-evaluating references that
are intentionally dynamic.

The benchmark has four matched conditions:

- anchored + flip: bind before refresh; refreshed state changes the selector.
- anchored + stable: bind before refresh; refreshed state preserves the selector.
- dynamic + flip: evaluate after refresh; refreshed state changes the selector.
- dynamic + stable: evaluate after refresh; refreshed state preserves the selector.

The key diagnostic compares direct semantic resolution with interactive
tool use. If a model succeeds in direct mode but fails interactively, the error
is not just language understanding; it is identity persistence across state
updates.

