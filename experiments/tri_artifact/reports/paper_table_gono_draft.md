# Paper Table Draft: Go/No-Go Strong Baselines

This table is based on completed GLM-5.1 TRI-v2 scalar runs available as of 2026-07-16 21:48 Asia/Shanghai. It should be regenerated after the running Go/No-Go matrix finishes.

## Main Table

| Controller | Information available | Calls | Overall | Anchored | Dynamic | API err. |
|---|---|---:|---:|---:|---:|---:|
| State overwrite | Instruction + refreshed state | 1 | 60.6 | 21.2 | 100.0 | 0.0 |
| Full history | Instruction + initial state + refreshed state | 1 | 76.2 | 52.5 | 100.0 | 0.0 |
| Generic plan-then-act | Initial plan + refreshed state | 2 | 78.1 | 56.2 | 100.0 | 0.0 |
| Schema lifecycle | Lifecycle record + action schema + refreshed state | 2 | 95.0 | 90.0 | 100.0 | 0.0 |

## Stress Table

| Controller | Explicit anchored | Implicit anchored | Anchored remove | Anchored invalidate |
|---|---:|---:|---:|---:|
| State overwrite | 22.5 | 20.0 | 0.0 | 0.0 |
| Full history | 82.5 | 22.5 | 50.0 | 6.2 |
| Generic plan-then-act | 92.5 | 20.0 | 43.8 | 37.5 |
| Schema lifecycle | 100.0 | 80.0 | 75.0 | 75.0 |

## Paired Tests vs Schema Lifecycle

| Baseline | Delta schema - baseline | Baseline-only correct | Schema-only correct | Exact p |
|---|---:|---:|---:|---:|
| State overwrite | +34.4 | 0 | 55 | 5.551e-17 |
| Full history | +18.8 | 0 | 30 | 1.863e-09 |
| Generic plan-then-act | +16.9 | 0 | 27 | 1.49e-08 |

## Paper Interpretation

The strongest immediate claim is no longer merely that state overwrite loses old information. Full history and a generic two-stage plan both preserve more information than state overwrite, yet they still fail many anchored cases, especially implicit anchored references and invalid-but-present targets. Schema-grounded lifecycle state remains substantially better.

Recommended wording:

> Full history and generic planning recover some explicit commitments, but do not reliably convert implicit linguistic commitments into executable state, nor do they consistently enforce action-relative validity. This supports TRI as a state-semantics problem rather than a simple context-retention problem.

## Caveat

This draft currently uses a standalone complete schema run and completed Go/No-Go baseline runs. Replace it with the final five-mode matrix once the running `compile_then_act` and matrix `schema_compile_then_act` finish.
