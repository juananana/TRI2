# TRI-v7 Conditional SQLite Write Audit

Core TRI writes require a correct initial binding, an anchored flip/name-collision,
continued validity of the old entity, and an executed write to the refreshed winner.
Dynamic-old writes are the opposite error: preserving the old target when reevaluation
was authorized. Invalid attempts are blocked by action preconditions and are not writes.

| Model | Controller | n | Core TRI writes | All wrong writes | Dynamic-old writes | Stable wrong writes | Other wrong writes | Invalid attempts | Unneeded rejects |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | 240 | 0/70 | 14 | 4 | 0 | 10 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | 240 | 0/79 | 7 | 6 | 0 | 1 | 0 | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | 240 | 38/80 | 38 | 0 | 0 | 0 | 0 | 34 |
| Qwen3.5 | compile_then_act | 240 | 0/71 | 8 | 6 | 0 | 2 | 50 | 12 |
| Qwen3.5 | factorized_hybrid_compile_then_act | 240 | 0/64 | 17 | 13 | 0 | 4 | 30 | 22 |
| Qwen3.5 | generic_structured_ledger_then_act | 240 | 43/72 | 44 | 0 | 0 | 1 | 33 | 49 |
