# Parallel API Plan for TRI-v2

The current desktop run is executing the baseline matrix:

- GLM-5.1 state overwrite: complete.
- GLM-5.1 compile-then-act: complete.
- Qwen3.5 state overwrite: complete.
- Qwen3.5 compile-then-act: in progress.
- MiniMax state overwrite and compile should run afterward if the original
  script continues.

## Safe parallel work

Do not start another Qwen compile run while the current file is still growing.
It would duplicate expensive calls and make audit harder.

If a second terminal is available and API rate limits look healthy, the most
useful parallel run is **schema-aware GLM only** after syncing the updated code:

```bash
PYTHONPATH=. python3 -m tri.run_models \
  --model Pro/zai-org/GLM-5.1 \
  --mode schema_compile_then_act \
  --split dev \
  --paraphrase all \
  --condition all \
  --data data/temporal_referent_v2_api_scalar.jsonl \
  --output runs/$(date -u +%Y%m%dT%H%M%SZ)_Pro_zai-org_GLM-5.1_schema_compile_then_act_v2_scalar.jsonl \
  --temperature 0.0 \
  --timeout 90
```

This run is the highest-value next experiment because it directly tests whether
schema preconditions repair the anchored-invalidate failures seen in baseline
compile-then-act.

## After baseline finishes

Run:

```bash
python3 -m tri.v2_run_audit \
  --data data/temporal_referent_v2_api_scalar.jsonl \
  --input runs/*20260716T07*GLM-5.1*dev_all.jsonl runs/*20260716T08*Qwen*dev_all.jsonl \
  --output reports/v2_run_audit_latest.json
```

Then aggregate:

```bash
python3 -m tri.v2_model_report \
  --input runs/*20260716T07*GLM-5.1*dev_all.jsonl runs/*20260716T08*Qwen*dev_all.jsonl \
  --output reports/v2_model_report_latest.json
```

When `schema_compile_then_act` files are available, include them in the same
report and compare anchored-invalidate accuracy against baseline
`compile_then_act`.
