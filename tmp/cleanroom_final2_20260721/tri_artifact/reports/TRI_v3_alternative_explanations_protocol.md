# TRI-v3 Alternative-Explanation Baselines

Frozen on 2026-07-17 before any model call for these baselines. This is a disclosed
reviewer-prompted addendum. It tests whether the primary lifecycle-representation effect can be
explained by an ordinary reminder or by action-time reinterpretation.

## Fixed Source State

Both baselines reuse the exact `compiled_ledger` from each completed Generic Structured Ledger
row. They replace the original generic actor call with one new call. Thus each complete
condition represents two calls per task: the frozen generic compiler call and the new final
call. No lifecycle compiler output, benchmark label, gold target, binding field, or selector
implementation is provided.

## Baselines

1. **Generic + ordinary reminder.** The final actor receives the original instruction, generic
   ledger, refreshed state, and action schema. Its system message adds only this ordinary-language
   reminder: a world refresh does not by itself change an entity selected before refresh; decide
   whether selection was fixed before refresh or deliberately deferred. The actor returns only
   an action and target ID, never a lifecycle record.
2. **Action-time semantic compiler + gate.** After refresh, one call receives the same inputs and
   emits `reference_mode` plus a dynamic target when needed. A deterministic executor uses the
   generic ledger's existing selected ID for preserve, rejects it when action-invalid, and uses
   the emitted dynamic target for reevaluate. No semantic state is persisted before refresh.

The first tests whether a sentence-level reminder explains the lifecycle gain. The second tests
whether persistent pre-refresh compilation is necessary or whether late reinterpretation is
sufficient in the controlled scalar family.

## Inputs and Inference

- Qwen primary source: complete 160-task Generic Structured Ledger run.
- Qwen smoke source: frozen 20-task balanced Generic Structured Ledger run.
- Qwen3.5-122B-A10B, temperature zero, thinking disabled, 1,200 output-token cap.
- At most one API or parse failure per 20-task condition is allowed before expansion.
- Prompts and decision rules will not change after smoke inspection.
- GLM replication is conditional on the Qwen result being scientifically informative and the
  API budget remaining reasonable.

## Outcomes and Interpretation

Report exact accuracy, anchored/dynamic slices, template-cluster intervals, API/parse failures,
and paired differences against generic-free and lifecycle-free execution.

- If the reminder matches lifecycle-free, withdraw any necessity claim for typed lifecycle state
  and reposition the result as explicit temporal-commitment prompting.
- If late compilation matches lifecycle-free, do not claim that pre-refresh persistence is
  empirically necessary in the scalar setting.
- If both remain materially below lifecycle-free, the persistent representation claim is
  strengthened, but only for the controlled scalar task family.
