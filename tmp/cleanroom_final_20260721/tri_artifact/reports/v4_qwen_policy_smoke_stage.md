# TRI-v4 Guarded Policy Stage Report

| Model | Controller | Guard | Update | n | Guard | Bound ID | Final | Actor-only | Compiler-induced | API err. |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | flip | 1 | NA | NA | 0.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | name_collision | 2 | NA | NA | 0.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | remove | 1 | NA | NA | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | stable | 1 | NA | NA | 0.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | flip | 2 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | invalidate | 2 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | stable | 1 | NA | NA | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | flip | 1 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | name_collision | 2 | 100.0 | 50.0 | 50.0 | 0 | 1 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | remove | 1 | 100.0 | 100.0 | 0.0 | 1 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | stable | 1 | 100.0 | 0.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | flip | 2 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | invalidate | 2 | 50.0 | 50.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | stable | 1 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
