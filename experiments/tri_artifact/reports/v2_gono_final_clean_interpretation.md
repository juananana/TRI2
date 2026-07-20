# TRI-v2 Go/No-Go Final Clean Interpretation

This report uses the clean GLM-5.1 Go/No-Go files completed on 2026-07-16:

- `state_overwrite_once`: matrix full run, 160/160, 0 API errors.
- `full_history_once`: matrix full run, 160/160, 0 API errors.
- `generic_plan_then_act`: matrix full run, 160/160, 0 API errors.
- `compile_then_act`: matrix full run, 160/160, 0 API errors.
- `schema_compile_then_act`: standalone full scalar run, 160/160, 0 API errors.

The matrix-run `schema_compile_then_act` also completed 160 rows, but had 31 transient API failures due to SSL EOF/timeout concentrated in CRM/repo. It should be retried or excluded from final model-performance claims. The standalone schema run is clean and uses the same model, mode, and 160-task scalar data.

## Main Result

| Controller | Overall | 95% CI | Anchored | Dynamic | API err. |
|---|---:|---:|---:|---:|---:|
| state_overwrite_once | 60.6 | [52.9, 67.9] | 21.2 | 100.0 | 0.0 |
| full_history_once | 76.2 | [69.1, 82.2] | 52.5 | 100.0 | 0.0 |
| generic_plan_then_act | 78.1 | [71.1, 83.8] | 56.2 | 100.0 | 0.0 |
| compile_then_act | 89.4 | [83.6, 93.3] | 78.8 | 100.0 | 0.0 |
| schema_compile_then_act | 95.0 | [90.4, 97.4] | 90.0 | 100.0 | 0.0 |

## Key Finding

This is a strong Go result for the repositioned paper. The strongest critique was that `state_overwrite_once` is too weak because it deletes old state and binding information. The new results show that:

- Full history improves over overwrite, but remains far below lifecycle state.
- Generic two-stage planning improves over overwrite, but remains far below lifecycle state.
- Compile-then-act gives a large additional gain.
- Schema lifecycle gives the strongest result, especially on invalid-but-present cases.

Thus the paper no longer only shows "do not delete old information." It shows that simply providing old and new facts, or giving the model a generic planning step, does not reliably convert linguistic binding commitments and action validity into executable state.

## Paired Significance

| Baseline | Schema delta | Baseline-only correct | Schema-only correct | Exact p |
|---|---:|---:|---:|---:|
| state_overwrite_once | +34.4 | 0 | 55 | 5.551e-17 |
| full_history_once | +18.8 | 0 | 30 | 1.863e-09 |
| generic_plan_then_act | +16.9 | 0 | 27 | 1.49e-08 |
| compile_then_act | +5.6 | 3 | 12 | 0.03516 |

The comparison against full history and generic plan is the most important for rebutting the weak-baseline criticism.

## Explicit vs Implicit Anchored References

| Controller | Explicit anchored | Implicit anchored |
|---|---:|---:|
| state_overwrite_once | 22.5 | 20.0 |
| full_history_once | 82.5 | 22.5 |
| generic_plan_then_act | 92.5 | 20.0 |
| compile_then_act | 80.0 | 77.5 |
| schema_compile_then_act | 100.0 | 80.0 |

This is one of the strongest scientific findings:

> Full history and generic planning handle explicit anchored language reasonably well, but collapse on implicit anchored references. Lifecycle compilation remains strong on implicit references.

This supports the claim that the relevant object is not mere access to history, but explicit representation of a binding commitment.

## Action-Validity Stress

| Controller | Anchored remove | Anchored invalidate |
|---|---:|---:|
| state_overwrite_once | 0.0 | 0.0 |
| full_history_once | 50.0 | 6.2 |
| generic_plan_then_act | 43.8 | 37.5 |
| compile_then_act | 93.8 | 0.0 |
| schema_compile_then_act | 75.0 | 75.0 |

This confirms the second major thesis:

> Identity preservation and entity presence are not enough. The agent must evaluate action-relative validity.

Compile-then-act preserves identity well but fails invalid-but-present targets. Schema lifecycle trades a small drop on remove for a major gain on invalidate, producing the best overall anchored validity behavior.

## Error Taxonomy

| Controller | invalid_but_processed | temporal_rebinding |
|---|---:|---:|
| state_overwrite_once | 32 | 31 |
| full_history_once | 23 | 15 |
| generic_plan_then_act | 19 | 16 |
| compile_then_act | 17 | 0 |
| schema_compile_then_act | 8 | 0 |

This progression gives a clean story:

1. Overwrite fails by temporal rebinding and invalid processing.
2. Full history and generic plans reduce but do not remove these errors.
3. Compile removes temporal rebinding but leaves invalid processing.
4. Schema lifecycle further reduces invalid processing.

## Paper-Level Conclusion

The upgraded AAAI framing is now substantially stronger:

> Dynamic tool agents must distinguish changing facts about the world from commitments created by prior language grounding. Full history and generic planning preserve more information than overwrite, but they still fail to reliably operationalize implicit binding commitments and action-relative validity. Explicit lifecycle state provides a more reliable execution representation.

## Next Steps

1. Retry only the 31 API failures in the matrix-run `schema_compile_then_act` if we want every row in the matrix to come from the same script invocation.
2. Run the same Go/No-Go matrix for one additional clean model, preferably Qwen, if budget permits.
3. Add stage-wise compiler evaluation:
   - binding mode classification;
   - bound identity extraction;
   - selector extraction;
   - validity decision.
4. Build a small real-write environment and report wrong-entity write and invalid-write rates.
5. Update the AAAI paper draft around this new result: strong baselines are now part of the central story, not an appendix.
