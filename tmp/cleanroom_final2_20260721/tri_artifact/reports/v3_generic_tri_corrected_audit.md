# Corrected Generic Ledger TRI Audit

This audit reads Generic Ledger's `selected_entity_id`; the older stage report incorrectly
looked for lifecycle-only `bound_target_id` and therefore undercounted correct initial bindings.

Rows: 320; core opportunities: 64.

| Model | Update | N | Initial binding correct | Opportunities | Drift to refreshed leader | Drift rate | Final wrong target |
|---|---|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | flip | 32 | 31 | 16 | 3 | 18.8% [0.0, 43.8] | 13 |
| Pro/zai-org/GLM-5.1 | invalidate | 32 | 32 | 0 | 0 | NA | 0 |
| Pro/zai-org/GLM-5.1 | name_collision | 32 | 32 | 16 | 7 | 43.8% [17.6, 70.6] | 12 |
| Pro/zai-org/GLM-5.1 | remove | 32 | 32 | 0 | 0 | NA | 0 |
| Pro/zai-org/GLM-5.1 | stable | 32 | 32 | 0 | 0 | NA | 0 |
| Qwen/Qwen3.5-122B-A10B | flip | 32 | 31 | 16 | 15 | 93.8% [78.6, 100.0] | 15 |
| Qwen/Qwen3.5-122B-A10B | invalidate | 32 | 32 | 0 | 0 | NA | 0 |
| Qwen/Qwen3.5-122B-A10B | name_collision | 32 | 32 | 16 | 14 | 87.5% [69.2, 100.0] | 14 |
| Qwen/Qwen3.5-122B-A10B | remove | 32 | 32 | 0 | 0 | NA | 0 |
| Qwen/Qwen3.5-122B-A10B | stable | 32 | 32 | 0 | 0 | NA | 0 |

Core opportunities are anchored tasks with flip or name-collision updates where the
pre-refresh selected_entity_id is correct and the old entity remains present and actionable.
Remove/invalidate cases are excluded because they test invalidity policy rather than
the referential-core TRI transition.
