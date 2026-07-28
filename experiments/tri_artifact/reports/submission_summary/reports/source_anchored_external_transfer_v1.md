# Source-Anchored External Transfer Full Report

- Rows: 320/320
- Valid: 306 (95.6%)
- Smoke gate: GO
- Exact target (ITT): 256/320
- Initial selection: 252/320
- Wrong-entity writes: 50
- Transport / parse-schema / source-execution failures: 0 / 14 / 0
- Offline execution repairs: 32 rows, 0 added model requests

## Changed Conditions

- Conditional exact target: 118/126
- Preserve unauthorized substitutions: 2/64
- Reevaluate failed substitutions: 3/62
- Changed matched pairs both exact: 56/80 (conditional 54/62)

## Model Conditions

| Model and condition | Rows | Valid | Initial selection | Exact target | Wrong write |
|---|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | execution_record | 80 | 73 | 59 | 57 | 16 |
| Pro/zai-org/GLM-5.1 | ordinary_full_history | 80 | 73 | 60 | 64 | 9 |
| Qwen/Qwen3.5-122B-A10B | execution_record | 80 | 80 | 65 | 67 | 13 |
| Qwen/Qwen3.5-122B-A10B | ordinary_full_history | 80 | 80 | 68 | 68 | 12 |

## Shared Initial Selection

- Pro/zai-org/GLM-5.1: ordinary 57/59; execution record 52/59; record-better 1, ordinary-better 6.
- Qwen/Qwen3.5-122B-A10B: ordinary 62/65; execution record 63/65; record-better 2, ordinary-better 1.

## Boundary

Author-adapted matched evaluation on external source states and tools; not native benchmark prevalence, natural traffic, or an official benchmark score.
