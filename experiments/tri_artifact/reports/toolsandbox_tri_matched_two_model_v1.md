# ToolSandbox-Based TRI External Pilot

Rows: 192; tasks: 24; models: Pro/zai-org/GLM-5.1, Qwen/Qwen3.5-122B-A10B; duplicate keys: 0.

## Main Results

| Model | Controller | N | Success | Accuracy | Wrong writes | Invalid attempts | Execution/protocol errors |
|---|---|---:|---:|---:|---:|---:|---:|
| Pro/zai-org/GLM-5.1 | matched_generic | 24 | 19 | 79.2 | 3 | 3 | 1 |
| Pro/zai-org/GLM-5.1 | matched_lifecycle | 24 | 21 | 87.5 | 1 | 3 | 1 |
| Pro/zai-org/GLM-5.1 | matched_lifecycle_gate_replay | 24 | 22 | 91.7 | 1 | 0 | 1 |
| Pro/zai-org/GLM-5.1 | matched_untyped | 24 | 22 | 91.7 | 1 | 3 | 1 |
| Qwen/Qwen3.5-122B-A10B | matched_generic | 24 | 22 | 91.7 | 1 | 3 | 0 |
| Qwen/Qwen3.5-122B-A10B | matched_lifecycle | 24 | 20 | 83.3 | 4 | 3 | 0 |
| Qwen/Qwen3.5-122B-A10B | matched_lifecycle_gate_replay | 24 | 22 | 91.7 | 2 | 0 | 0 |
| Qwen/Qwen3.5-122B-A10B | matched_untyped | 24 | 19 | 79.2 | 5 | 4 | 0 |

## Paired Descriptive Contrasts

- Pro/zai-org/GLM-5.1: matched_generic -> matched_untyped +12.5 points; wins/ties/losses 3/21/0 over 24 tasks.
- Qwen/Qwen3.5-122B-A10B: matched_generic -> matched_untyped -12.5 points; wins/ties/losses 2/17/5 over 24 tasks.
- Pro/zai-org/GLM-5.1: matched_untyped -> matched_lifecycle -4.2 points; wins/ties/losses 1/21/2 over 24 tasks.
- Qwen/Qwen3.5-122B-A10B: matched_untyped -> matched_lifecycle +4.2 points; wins/ties/losses 3/19/2 over 24 tasks.
- Pro/zai-org/GLM-5.1: matched_lifecycle -> matched_lifecycle_gate_replay +4.2 points; wins/ties/losses 1/23/0 over 24 tasks.
- Qwen/Qwen3.5-122B-A10B: matched_lifecycle -> matched_lifecycle_gate_replay +8.3 points; wins/ties/losses 2/22/0 over 24 tasks.

This is a custom ToolSandbox-based TRI extension, not an official ToolSandbox score. The 24-task pilot is exploratory; paired counts are descriptive and not a basis for broad population-level inference.
