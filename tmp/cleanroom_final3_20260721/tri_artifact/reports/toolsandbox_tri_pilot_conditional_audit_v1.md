# ToolSandbox 24-Task Pilot: Strict Conditional TRI Audit

Preserve+Flip; compiled initial ID equals manifest initial/gold ID; old ID remains present; refreshed winner is a different stable ID; no protocol error. A violation writes the refreshed winner. Untyped plans have no auditable compiled ID and are excluded from the conditional denominator.

This is a benchmark-compatible intervention using ToolSandbox's reminder database and
native search/modify tools. It is not an unmodified ToolSandbox leaderboard result or a
prevalence estimate. The inventory was frozen before these model outputs, but this strict
conditional audit is post-hoc and must be labeled accordingly.

| Model | Controller | n | Initial binding | Strict opportunities | Conditional TRI | Stable wrong writes | All wrong writes |
|---|---|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | matched_generic | 24 | 14/23 | 6 | 3/6 | 0/2 | 3 |
| Pro/zai-org/GLM-5.1 | matched_lifecycle | 24 | 10/11 | 5 | 0/5 | 0/2 | 1 |
| Pro/zai-org/GLM-5.1 | matched_lifecycle_gate_replay | 24 | 10/11 | 5 | 0/5 | 0/2 | 1 |
| Pro/zai-org/GLM-5.1 | matched_untyped | 24 | 0/0 | 0 | 0/0 | 0/0 | 1 |
| Qwen/Qwen3.5-122B-A10B | matched_generic | 24 | 15/24 | 6 | 0/6 | 0/2 | 1 |
| Qwen/Qwen3.5-122B-A10B | matched_lifecycle | 24 | 11/17 | 6 | 2/6 | 0/2 | 4 |
| Qwen/Qwen3.5-122B-A10B | matched_lifecycle_gate_replay | 24 | 11/17 | 6 | 0/6 | 0/2 | 2 |
| Qwen/Qwen3.5-122B-A10B | matched_untyped | 24 | 0/0 | 0 | 0/0 | 0/0 | 5 |

Violation task IDs:

- Pro/zai-org/GLM-5.1 / matched_generic: `ts2-newest-created-preserve-flip`, `ts2-oldest-created-preserve-flip`, `ts2-alpha-last-preserve-flip`
- Qwen/Qwen3.5-122B-A10B / matched_lifecycle: `ts2-due-latest-preserve-flip`, `ts2-newest-created-preserve-flip`
