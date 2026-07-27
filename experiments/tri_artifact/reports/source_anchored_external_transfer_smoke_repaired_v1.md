# Source-Anchored External Transfer Smoke Report

- Rows: 32/32
- Valid: 31 (96.9%)
- Smoke gate: GO
- Exact target (ITT): 26/32
- Initial selection: 24/32
- Wrong-entity writes: 5
- Transport / parse-schema / source-execution failures: 0 / 1 / 0
- Offline execution repairs: 32 rows, 0 added model requests

## Changed Conditions

- Conditional exact target: 11/12
- Preserve unauthorized substitutions: 0/6
- Reevaluate failed substitutions: 1/6
- Changed matched pairs both exact: 5/8 (conditional 5/6)

## Model Conditions

| Model and condition | Rows | Valid | Initial selection | Exact target | Wrong write |
|---|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | execution_record | 8 | 8 | 4 | 5 | 3 |
| Pro/zai-org/GLM-5.1 | ordinary_full_history | 8 | 7 | 4 | 6 | 1 |
| Qwen/Qwen3.5-122B-A10B | execution_record | 8 | 8 | 8 | 7 | 1 |
| Qwen/Qwen3.5-122B-A10B | ordinary_full_history | 8 | 8 | 8 | 8 | 0 |

## Shared Initial Selection

- Pro/zai-org/GLM-5.1: ordinary 4/4; execution record 4/4; record-better 0, ordinary-better 0.
- Qwen/Qwen3.5-122B-A10B: ordinary 8/8; execution record 7/8; record-better 0, ordinary-better 1.

## Boundary

Author-adapted matched evaluation on external source states and tools; not native benchmark prevalence, natural traffic, or an official benchmark score.
