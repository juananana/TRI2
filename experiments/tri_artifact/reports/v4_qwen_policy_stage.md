# TRI-v4 Guarded Policy Stage Report

| Model | Controller | Guard | Update | n | Guard | Bound ID | Final | Actor-only | Compiler-induced | API err. |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | flip | 4 | NA | NA | 0.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | invalidate | 4 | NA | NA | 75.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | name_collision | 4 | NA | NA | 25.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | remove | 4 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | action_validity | stable | 4 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | flip | 4 | NA | NA | 75.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | invalidate | 4 | NA | NA | 75.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | name_collision | 4 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | remove | 4 | NA | NA | 75.0 | 0 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | selector_match | stable | 4 | NA | NA | 50.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | flip | 4 | 100.0 | 50.0 | 75.0 | 0 | 1 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | invalidate | 4 | 100.0 | 50.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | name_collision | 4 | 100.0 | 50.0 | 75.0 | 0 | 1 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | remove | 4 | 100.0 | 50.0 | 50.0 | 2 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | action_validity | stable | 4 | 100.0 | 50.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | flip | 4 | 100.0 | 75.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | invalidate | 4 | 75.0 | 50.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | name_collision | 4 | 75.0 | 50.0 | 50.0 | 0 | 2 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | remove | 4 | 75.0 | 50.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | selector_match | stable | 4 | 75.0 | 50.0 | 100.0 | 0 | 0 | 0 |
