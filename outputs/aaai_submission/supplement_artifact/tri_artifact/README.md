# Temporal Referent Integrity Artifact

This anonymous artifact contains the task generator, evaluator, controller runners, tests, and aggregate reports for the TRI experiments.

## Contents

- `tri/`: task generation, model runners, tool-loop controller, scoring, and analysis utilities.
- `data/temporal_referent.jsonl`: generated TRI task set.
- `data/lifecycle_referent.jsonl`: lifecycle stress-test task set.
- `reports/`: aggregate tables used in the paper.
- `runs/`: raw JSONL model transcripts used to compute the reported API-backed tables.
- `scripts/`: figure generation utilities.
- `figures/`: generated PDF figures used in the paper.
- `tests/`: unit tests for task generation, parsing, and tool environment behavior.

The reports are generated from JSONL run files by `tri.paper_tables`, `tri.compiler_analysis`, and `tri.summary_analysis`. No LLM judge is used for scoring.

## Basic Checks

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
python3 -m tri.field_ablation --input data/temporal_referent.jsonl --output reports/field_ablation_recomputed.json
python3 -m tri.lifecycle_ablation --input data/lifecycle_referent.jsonl --output reports/lifecycle_ablation_recomputed.json
```

Regenerate lifecycle tasks:

```bash
python3 -m tri.lifecycle_tasks --output data/lifecycle_referent.jsonl
```

## API-Backed Runs

Set API credentials through environment variables:

```bash
export LLM_API_KEY=...
export LLM_BASE_URL=https://api.siliconflow.cn/v1
```

Example single run:

```bash
PYTHONPATH=. python3 -m tri.run_models \
  --model Pro/zai-org/GLM-5.1 \
  --mode state_overwrite_once \
  --split dev --paraphrase p0 \
  --condition anchored-flip \
  --domains incident,meeting,ticket
```

Example stateful tool-loop run:

```bash
PYTHONPATH=. python3 -m tri.run_tool_controllers \
  --model Pro/zai-org/GLM-5.1 \
  --mode tool_latest_state \
  --split dev --paraphrase p0 \
  --condition anchored-flip \
  --domains incident,meeting,ticket
```

## Metrics

Accuracy is exact match against the oracle target ID. Drift is counted when the model selects the post-refresh selector winner in an anchored-flip case where the correct answer is the pre-refresh bound entity.
