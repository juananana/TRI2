# TRI-v2 Live Model Results Note

This note summarizes the currently observed SiliconFlow v2 scalar runs while
the full matrix is still running. Do not treat partial rows as final paper
numbers.

## Completed files audited

Audit source: `reports/v2_run_audit_partial.md`.

Complete v2 scalar files:

- GLM-5.1 `state_overwrite_once`: 160/160 rows, 0 API errors.
- GLM-5.1 `compile_then_act`: 160/160 rows, 0 API errors.
- Qwen3.5 `state_overwrite_once`: 160/160 rows, 0 API errors.

Incomplete file:

- Qwen3.5 `compile_then_act`: currently partial; do not report as final until
  it reaches 160/160 rows.

## Interim aggregate results

Source: `reports/v2_model_report_partial.md`. Accuracy counts API errors as
failures.

| Model | Controller | n | Accuracy | Notes |
|---|---|---:|---:|---|
| GLM-5.1 | state_overwrite_once | 160 | 61.3 | anchored 22.5, dynamic 100.0 |
| GLM-5.1 | compile_then_act | 160 | 89.4 | anchored 78.8, dynamic 100.0 |
| Qwen3.5 | state_overwrite_once | 160 | 60.0 | anchored 20.0, dynamic 100.0 |

## Mechanistic finding

GLM-5.1 `compile_then_act` repairs almost all referent-drift cases but fails
the action-specific validity condition:

- anchored flip: 15/16
- anchored stable: 16/16
- anchored remove: 16/16
- anchored name collision: 16/16
- anchored invalidate: 0/16
- all dynamic updates: 80/80

This is a clean result for the next paper iteration: the first compiler stores
binding time and identity, but only checks target presence. It does not check
whether a still-present target satisfies action preconditions. The planned
`schema_compile_then_act` run directly tests whether exposing action
preconditions repairs this gap.

## Next actions

1. Wait for the current baseline matrix to finish.
2. Audit all new JSONL files with `tri.v2_run_audit`.
3. Generate the strict model report with `tri.v2_model_report`.
4. Run `schema_compile_then_act` after syncing the updated code to the active
   project directory.
5. Compare `compile_then_act` vs. `schema_compile_then_act` specifically on
   anchored invalidate cases.
