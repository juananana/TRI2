# Method Upgrade Compiler Smoke

| Model | Method | N | Schema | Mode | Bound ID | Selector initial | Selector final | Authorized target | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | event_graph | 20 | 20/20 | 20/20 | 20/20 | NA | NA | NA | 0 |
| Pro/zai-org/GLM-5.1 | event_graph_selector | 20 | 18/20 | 18/20 | 18/20 | 19/20 | 19/20 | 19/20 | 1 |
| Qwen/Qwen3.5-122B-A10B | event_graph | 20 | 14/20 | 12/20 | 11/20 | NA | NA | NA | 6 |
| Qwen/Qwen3.5-122B-A10B | event_graph_selector | 20 | 15/20 | 14/20 | 15/20 | 15/20 | 15/20 | 15/20 | 5 |

## Go/No-Go

- preflight_closed_loop: False
- two_complete_models: True
- schema_valid_at_least_95pct: False
- selector_equivalence_at_least_95pct: False
- api_parse_failure_at_most_5pct: False
- go_to_v7: False
