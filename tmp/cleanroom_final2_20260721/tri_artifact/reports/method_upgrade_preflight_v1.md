# Method Upgrade Compiler Smoke

| Model | Method | N | Schema | Mode | Bound ID | Selector initial | Selector final | Authorized target | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | event_graph | 1 | 1/1 | 1/1 | 1/1 | NA | NA | NA | 0 |
| Pro/zai-org/GLM-5.1 | event_graph_selector | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0 |
| Pro/zai-org/GLM-5.1 | exact_cta | 1 | 1/1 | 1/1 | 1/1 | NA | NA | NA | 0 |
| Qwen/Qwen3.5-122B-A10B | event_graph | 1 | 1/1 | 1/1 | 1/1 | NA | NA | NA | 0 |
| Qwen/Qwen3.5-122B-A10B | event_graph_selector | 1 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 | 0 |
| Qwen/Qwen3.5-122B-A10B | exact_cta | 1 | 1/1 | 1/1 | 1/1 | NA | NA | NA | 0 |

## Go/No-Go

- preflight_closed_loop: True
- two_complete_models: False
- schema_valid_at_least_95pct: False
- selector_equivalence_at_least_95pct: False
- api_parse_failure_at_most_5pct: False
- go_to_v7: False
