# TRI-v2 Go/No-Go Interim Interpretation

Generated while the full Go/No-Go matrix was still running on 2026-07-16.

## What has completed

Completed clean full runs:

- `state_overwrite_once`: 160/160, 0 API errors.
- `full_history_once`: 160/160, 0 API errors.
- `generic_plan_then_act`: 160/160, 0 API errors.
- `schema_compile_then_act`: 160/160, 0 API errors, from the standalone v2 scalar run.

Still running at the time of this note:

- `compile_then_act` in the Go/No-Go matrix.
- The final matrix `schema_compile_then_act` may run after that, although a clean standalone schema run is already complete.

## Key result

| Controller | Overall | Anchored | Dynamic |
|---|---:|---:|---:|
| state_overwrite_once | 60.6 | 21.2 | 100.0 |
| full_history_once | 76.2 | 52.5 | 100.0 |
| generic_plan_then_act | 78.1 | 56.2 | 100.0 |
| schema_compile_then_act | 95.0 | 90.0 | 100.0 |

This is an important Go signal. Full history and a generic two-stage plan improve over the lossy overwrite baseline, but they do not close the gap to schema-grounded lifecycle state.

## Paired comparisons

All paired comparisons use the same 160 task ids and count API errors as failures.

| A | B | Delta B-A | A-only | B-only | Exact p |
|---|---|---:|---:|---:|---:|
| state_overwrite_once | schema_compile_then_act | +34.4 | 0 | 55 | 5.551e-17 |
| full_history_once | schema_compile_then_act | +18.8 | 0 | 30 | 1.863e-09 |
| generic_plan_then_act | schema_compile_then_act | +16.9 | 0 | 27 | 1.49e-08 |

The strongest immediate implication is that schema lifecycle does not merely recover information missing from the overwrite baseline. It also outperforms controllers that receive full history or receive a generic two-stage planning opportunity.

## Mechanistic pattern

Dynamic references are easy for all completed controllers:

- Every completed controller is 100% on dynamic cases.

The difference is anchored references:

- overwrite: 21.2
- full history: 52.5
- generic plan: 56.2
- schema lifecycle: 90.0

This directly supports the new paper framing:

> The issue is not just whether the model sees old and new facts. The issue is whether the controller state represents a binding commitment and action-relative validity.

## Explicit vs implicit

| Controller | Explicit anchored | Implicit anchored |
|---|---:|---:|
| full_history_once | 82.5 | 22.5 |
| generic_plan_then_act | 92.5 | 20.0 |
| schema_compile_then_act | 100.0 | 80.0 |
| state_overwrite_once | 22.5 | 20.0 |

This is perhaps the most valuable result for the upgraded story. Full history and generic planning perform well on explicit anchored references, but collapse on implicit anchored references. Schema lifecycle remains much stronger, though it is still not perfect.

Paper implication:

> Generic access to the transcript is not enough when the binding commitment is implicit. The controller must make the commitment explicit in its execution state.

## Validity gap

| Controller | Remove | Invalidate |
|---|---:|---:|
| state_overwrite_once | 0.0 | 0.0 |
| full_history_once | 50.0 | 6.2 |
| generic_plan_then_act | 43.8 | 37.5 |
| schema_compile_then_act | 75.0 | 75.0 |

This supports the action-validity part of the thesis. Full history still largely fails when a bound entity remains present but becomes invalid. Generic planning helps but remains far below schema lifecycle.

Paper implication:

> Presence tracking and history retention do not reliably imply action-relative validity checking.

## Current verdict

This interim result strengthens the AAAI direction substantially. The strongest reviewer criticism was:

> Maybe the baseline is weak because it deletes old state; full history or generic planning may solve the problem.

The current completed runs do not support that criticism. Full history and generic planning improve performance, but schema lifecycle remains clearly better, especially on implicit anchored references and invalid-but-present cases.

## Caution

Do not finalize the paper table until the running matrix completes. We still need:

- full `compile_then_act` in the same Go/No-Go matrix;
- ideally the matrix-run `schema_compile_then_act`, even though the standalone schema run is already clean;
- Qwen or another second clean model if budget permits.

## Next analysis after completion

Once the matrix finishes:

1. Recompute the model report over the five full Go/No-Go files only.
2. Recompute factor report.
3. Recompute paired significance:
   - full_history vs compile;
   - generic_plan vs compile;
   - compile vs schema;
   - full_history vs schema;
   - generic_plan vs schema.
4. Update paper tables and figures.
