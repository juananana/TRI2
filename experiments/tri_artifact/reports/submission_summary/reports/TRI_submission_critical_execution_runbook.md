# Submission-Critical Experiment Execution Runbook

This runbook executes the frozen addendum in
`TRI_submission_critical_replication_addendum_20260728.md`. It contains no credential. Run it only
from a trusted local terminal after exporting the SiliconFlow key into the process environment.

## 1. Enter the artifact environment

```bash
cd ./experiments/tri_artifact
export LLM_API_KEY='set-this-in-your-terminal-only'
export PYTHONPATH=.
export PYTHONDONTWRITEBYTECODE=1
```

Do not place the real key in a shell script, `.env`, report, notebook, or command history. If the
shell records exported commands, use its secure credential mechanism or clear the single history
entry afterward. Rotate any credential previously pasted into a chat.

## 2. Re-run zero-API validation

```bash
../../.venv-toolsandbox/bin/pytest -q \
  tests/test_convention_told_control.py \
  tests/test_revision_matched_audit.py \
  tests/test_revision_repeat_stability.py \
  tests/test_toolsandbox_health_gate.py \
  tests/test_toolsandbox_single_turn_report.py

../../.venv-toolsandbox/bin/python scripts/run_submission_critical_matrix.py --dry-run
../../.venv-toolsandbox/bin/python scripts/run_toolsandbox_null_repeat.py --dry-run
```

Expected: tests pass; the dry run prints 4 Convention cells, 2 full-diagnostic extension cells,
4 source-repeat cells, and 4 ToolSandbox-style cells with zero network calls.

## 3. Run the critical matrices in priority order

Each command runs model processes concurrently but keeps rows sequential within a model. Existing
versioned output is validated/resumed or refused; historical v1 outputs are never overwritten.

```bash
../../.venv-toolsandbox/bin/python scripts/run_submission_critical_matrix.py \
  --phase convention --workers 4

../../.venv-toolsandbox/bin/python scripts/run_submission_critical_matrix.py \
  --phase extension --workers 2

../../.venv-toolsandbox/bin/python scripts/run_submission_critical_matrix.py \
  --phase source-repeat --workers 4

../../.venv-toolsandbox/bin/python scripts/run_toolsandbox_null_repeat.py --workers 4
```

Stop after any failed smoke gate. Do not edit a prompt, parser, task, denominator, or continuation
rule and then resume the same version. Preserve the failed output and diagnose it as transport or
schema evidence.

## 4. Expected outputs

Convention:

- `runs/convention_told_{qwen,glm,deepseek,minimax}_{smoke,full}_v1.jsonl`
- `reports/convention_told_natural_history_v1.{json,md}`

Full diagnostic extension:

- `runs/revision_full_diagnostic_{deepseek,minimax}_{health_smoke,full}_v2.jsonl`
- `reports/revision_full_diagnostic_four_model_v1.{json,md}`

Source-derived repeat:

- `runs/revision_source_grounded_{qwen,glm,deepseek,minimax}_{health_smoke,full}_v2.jsonl`
- `reports/revision_source_grounded_repeat_v1.{json,md}`

ToolSandbox-style null repeat:

- four `runs/toolsandbox_tri_single_turn_*_v2.jsonl` smoke/full pairs;
- four `reports/toolsandbox_single_turn_*_repeat_v2.{json,md}` reports.

## 5. Generate the paper figure after complete reports exist

```bash
cd .
.venv-toolsandbox/bin/python paper/tri_final_figures/plot_submission_critical_effects.py
pdffonts paper/tri_final_figures/outputs/fig_submission_critical_pairacc_effects_v1.pdf
```

The plotting script refuses to draw unless all four Convention and full-diagnostic model cells are
complete. Do not bypass this check or create a partial-model main-text figure.

## 6. Evidence lock

- Add only complete cells to the manuscript.
- Keep every null, adverse, mixed, API, parse, and enforcement-harm outcome.
- Source-repeat runs do not increase the 30-pair sample size.
- ToolSandbox-style runs are controlled external-style trajectories, not official/native scores.
- If the main-paper lock has passed, update only the supplement and artifact.

