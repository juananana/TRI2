# ToolSandbox-Based TRI External Pilot

Rows: 72; tasks: 24; models: Qwen/Qwen3.5-122B-A10B; duplicate keys: 0.

## Main Results

| Model | Controller | N | Success | Accuracy | Wrong writes | Invalid attempts | Errors |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen/Qwen3.5-122B-A10B | generic | 24 | 22 | 91.7 | 2 | 2 | 0 |
| Qwen/Qwen3.5-122B-A10B | lifecycle | 24 | 20 | 83.3 | 3 | 2 | 0 |
| Qwen/Qwen3.5-122B-A10B | untyped | 24 | 18 | 75.0 | 6 | 0 | 0 |

## Paired Descriptive Contrasts

- Qwen/Qwen3.5-122B-A10B: generic -> untyped -16.7 points; wins/ties/losses 0/20/4 over 24 tasks.
- Qwen/Qwen3.5-122B-A10B: untyped -> lifecycle +8.3 points; wins/ties/losses 4/18/2 over 24 tasks.

This is a custom ToolSandbox-based TRI extension, not an official ToolSandbox score. The 24-task pilot is exploratory; paired counts are descriptive and not a basis for broad population-level inference.
