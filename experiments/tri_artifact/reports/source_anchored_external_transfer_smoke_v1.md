# Source-Anchored External Transfer Smoke Report

- Rows: 32/32
- Valid: 0 (0.0%)
- Smoke gate: NO-GO
- Transport failures: 0
- Parse/schema failures: 1
- Source execution failures: 31

| Model and condition | Rows | Valid | Initial selection | Exact target | Wrong write |
|---|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | execution_record | 8 | 0 | 4 | 0 | 0 |
| Pro/zai-org/GLM-5.1 | ordinary_full_history | 8 | 0 | 4 | 0 | 0 |
| Qwen/Qwen3.5-122B-A10B | execution_record | 8 | 0 | 8 | 0 | 0 |
| Qwen/Qwen3.5-122B-A10B | ordinary_full_history | 8 | 0 | 8 | 0 | 0 |

This is an author-adapted matched evaluation on external source states and tools. It is not a native benchmark score or a prevalence estimate.
