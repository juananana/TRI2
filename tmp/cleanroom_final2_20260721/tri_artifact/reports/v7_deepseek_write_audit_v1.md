# TRI-v7 Conditional SQLite Write Audit

Core TRI writes require a correct initial binding, an anchored flip/name-collision,
continued validity of the old entity, and an executed write to the refreshed winner.
Dynamic-old writes are the opposite error: preserving the old target when reevaluation
was authorized. Invalid attempts are blocked by action preconditions and are not writes.

| Model | Controller | n | Core TRI writes | All wrong writes | Dynamic-old writes | Stable wrong writes | Other wrong writes | Invalid attempts | Unneeded rejects |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | compile_then_act | 240 | 0/70 | 17 | 8 | 0 | 9 | 0 | 4 |
| DeepSeek | generic_structured_ledger_then_act | 240 | 59/79 | 60 | 0 | 0 | 1 | 0 | 3 |
