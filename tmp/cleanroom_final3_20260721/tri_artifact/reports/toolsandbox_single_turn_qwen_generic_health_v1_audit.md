# Qwen Generic Health-Check Audit

Run file:
`runs/toolsandbox_tri_single_turn_Qwen_Qwen3.5-122B-A10B_generic_health_v1.jsonl`

This was an instrumentation audit, not a valid generic-controller result. The generic controller
placed a target ID in its own persistent state before `sync_reminders`, but the runner required a
separate `record_binding` tool call. The model often attempted mutation first, then emitted the
binding record after the environment rejected the mutation.

- API or parser errors: 0/8.
- Preserve/Stable opportunities: 0.
- Preserve/Flip opportunities: 0.
- Reevaluate/Stable opportunities: 2.
- Reevaluate/Flip opportunities: 1.
- Full run decision: blocked by the health gate.

These rows are retained to document the measurement problem. They are not evidence for or against
TRI and must not be combined with the versioned `generic_state_observed` condition. That condition
logs a unique reminder ID already present in the model's generic state without inserting an agent
step.
