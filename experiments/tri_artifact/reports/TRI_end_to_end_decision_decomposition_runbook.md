# End-to-End Decision Decomposition Runbook

## Current status

- Protocol, inventory, prompts, parser, contrasts, retry policy, and stopping rule are frozen.
- Qwen and GLM smoke/full dry runs pass with zero network calls.
- Three local smoke files record sandbox DNS failures. They contain no provider response and are
  infrastructure provenance only. Do not use them as a health smoke or scientific result.
- No full model run has completed. The experiment remains planned/unverified.

Use a newly issued API key. Do not place credentials in a command history, source file, JSONL,
report, or shell script.

## Preflight

Run from `experiments/tri_artifact`:

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/pytest -q \
  tests/test_end_to_end_decision_decomposition.py

PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model qwen --stage smoke --dry-run

PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model glm --stage smoke --dry-run
```

Set `LLM_API_KEY` only in the runtime environment before the next commands.

Every non-dry run prints the task, prompt, settings, protocol, runner, and core-source provenance.
If any persisted row differs from those manifests, the runner refuses to continue.

## Health smoke

Use new output names so the retained DNS-failure files are not overwritten:

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model qwen --stage smoke \
  --output runs/end_to_end_decision_decomposition_qwen_smoke_provider_v1.jsonl

PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model glm --stage smoke \
  --output runs/end_to_end_decision_decomposition_glm_smoke_provider_v1.jsonl
```

Each command must finish with four complete rows, 24/24 completed logical calls, and no API,
parse, or schema failure. The full runner validates this gate again and refuses to proceed if it
does not pass.

If a command is interrupted, rerun the exact same command and output path. The runner locks the
file, validates the existing rows as the exact frozen prefix, repairs only a crash-torn final byte
fragment, and resumes at the next task. It never reruns a valid persisted row. Do not rename,
concatenate, hand-edit, or delete rows to force resume.

## Full runs

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model qwen --stage full \
  --health-smoke runs/end_to_end_decision_decomposition_qwen_smoke_provider_v1.jsonl \
  --output runs/end_to_end_decision_decomposition_qwen_full_v1.jsonl

PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/run_end_to_end_decision_decomposition.py \
  --model glm --stage full \
  --health-smoke runs/end_to_end_decision_decomposition_glm_smoke_provider_v1.jsonl \
  --output runs/end_to_end_decision_decomposition_glm_full_v1.jsonl
```

Each full file must contain 80 ITT rows. Failures remain in place and are not rerun at the logical
call level. Do not edit prompts, parsers, tasks, or fields after either smoke begins.

Before reporting, rerun either full command without a key if desired. A completed file is validated
and returns with `new_rows: 0`; an incomplete file reports that a key is required to resume.

## Frozen report

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/report_end_to_end_decision_decomposition.py \
  --input runs/end_to_end_decision_decomposition_qwen_full_v1.jsonl \
          runs/end_to_end_decision_decomposition_glm_full_v1.jsonl
```

The reporter requires exactly 80 full-scope rows for each frozen model. It writes JSON and
Markdown reports with 10,000 state-cluster bootstrap replicates, exact discordance tests, Holm
adjustment, and input hashes. Only the generated full report may be promoted into the manuscript.
It also writes `reports/end_to_end_decision_decomposition_v1_claim_promotion.json`, which applies
the predeclared bounded-composite and adjacent-increment promotion gates. It cannot promote
orthogonal field effects, a unique internal mechanism, open-language transfer, or deployment
prevalence.
