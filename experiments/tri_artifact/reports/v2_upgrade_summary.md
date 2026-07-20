# TRI-v2 Upgrade Summary

This note records the experiment-side upgrade after the first AAAI draft. It is
intended as input for the next paper rewrite, not as a polished paper section.

## Reviewer-risk addressed

- Small synthetic grid: added `data/temporal_referent_v2.jsonl` with 246 tasks
  across 8 app-style domains.
- Over-explicit language: added implicit anchored and implicit dynamic
  instructions.
- "Just save the ID" criticism: added action-specific invalidity, removed
  entities, display-name collisions, conditional validity, collection
  references, and nested owner references.
- Weak validity handling: added `tri/reference_lifecycle.py`, where
  `schema_lifecycle` uses action preconditions rather than model guesses.
- Static-only evaluation: added `tri/v2_tool_ablation.py`, producing 1476
  observe-refresh-action app-style episodes.

## New deterministic results

Source reports:

- `reports/v2_ablation.json`
- `reports/v2_ablation.md`
- `reports/v2_tool_ablation.json`
- `reports/v2_tool_ablation.md`
- `runs/v2_tool_ablation.jsonl`

Overall representation ablation over 246 v2 tasks:

| Representation | Accuracy | 95% CI |
|---|---:|---:|
| latest_state | 64.6 | [58.5, 70.3] |
| bound_name_only | 58.9 | [52.7, 64.9] |
| binding_time_only | 58.1 | [51.9, 64.1] |
| bound_id_only | 41.9 | [35.9, 48.1] |
| time_plus_id | 74.0 | [68.2, 79.1] |
| schema_lifecycle | 100.0 | [98.5, 100.0] |

Key interpretation: time plus identity is much better than latest-state
control, but still fails conditional validity and invalid-but-present cases.
The schema lifecycle representation is an oracle architecture target: it shows
which state fields and action preconditions are sufficient under structured
observation, not that model compilation is solved.

## API-ready model subset

The file `data/temporal_referent_v2_api_scalar.jsonl` contains 160 scalar
anchored/dynamic tasks compatible with the existing LLM runner. It excludes
collection and nested targets because the current parser is scalar-ID oriented.

Run after setting `LLM_API_KEY` in the shell:

```bash
scripts/run_v2_siliconflow_matrix.sh
```

The script runs GLM-5.1, Qwen3.5, and MiniMax-M2.5 on
`state_overwrite_once` and `compile_then_act` over the v2 scalar subset. It does
not store the key.

The baseline `compile_then_act` intentionally preserves the old weakness: it
checks whether a bound target is still present, but not whether it satisfies
action preconditions. This makes anchored `invalidate` cases a direct test of
the validity gap.

After that baseline finishes, run:

```bash
scripts/run_v2_schema_siliconflow_matrix.sh
```

This uses `schema_compile_then_act`, which gives the actor explicit
`action_schema.preconditions` and asks it to reject pre-bound targets that no
longer satisfy them. The contrast between `compile_then_act` and
`schema_compile_then_act` is the key method-upgrade experiment.

Aggregate model runs with:

```bash
scripts/report_v2_model_runs.sh
```

The report counts API errors as failures and reports Wilson 95% confidence
intervals.

## Remaining gaps

- This is still a local app-style environment, not an external AppWorld or
  ToolSandbox replication.
- The schema lifecycle result is an oracle/symbolic architecture result. The
  model-facing compiler still needs v2 API runs and likely a schema-aware
  compiler mode.
- Related work still needs expansion around entity tracking, dialogue/task
  state tracking, versioned memory, and structured ledger agents.
