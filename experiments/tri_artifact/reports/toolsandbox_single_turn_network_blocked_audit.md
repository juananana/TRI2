# ToolSandbox Single-Turn Network Audit

The file
`runs/toolsandbox_tri_single_turn_qwen_full_history_network_blocked_v1.jsonl` records an invalid
eight-task health-check attempt. Every row failed before the first model response with the same
DNS-resolution error for the SiliconFlow endpoint.

- Model responses received: 0/8.
- Tool trajectories started: 0/8.
- Correct initial bindings observed: 0/8.
- TRI opportunities reached: 0/8.
- Scientific interpretation: none.

These rows are retained only to document infrastructure failure. They are excluded from every
accuracy, mechanism, write-safety, and paper-facing analysis. A valid health check must overwrite
the intended `health_v1` output or write a new versioned file after the endpoint is reachable.
