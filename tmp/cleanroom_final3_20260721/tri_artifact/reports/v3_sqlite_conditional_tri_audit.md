# Conditional Audit of SQLite Wrong-Entity Writes

A core TRI write is counted only when the pre-refresh binding is correct, the instruction
preserves that identity, the old entity remains present and action-valid, and the final
mutation instead writes the refreshed selector winner. Remove/invalidate cases are reported
separately as invalidity-policy errors.

| Model | Controller | n | Correct anchored binding | All wrong writes | Core opportunities | Core TRI writes | Policy opportunities | Policy wrong writes | Stable wrong writes | Unclassified |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | sqlite_generic_structured_ledger | 40 | 20/20 | 8 | 8 | 6 | 8 | 2 | 0/4 | 0 |
| Pro/zai-org/GLM-5.1 | sqlite_lifecycle_gated | 40 | 20/20 | 0 | 8 | 0 | 8 | 0 | 0/4 | 0 |
| Qwen/Qwen3.5-122B-A10B | sqlite_generic_structured_ledger | 40 | 20/20 | 13 | 8 | 8 | 8 | 5 | 0/4 | 0 |
| Qwen/Qwen3.5-122B-A10B | sqlite_lifecycle_gated | 40 | 20/20 | 0 | 8 | 0 | 8 | 0 | 0/4 | 0 |
