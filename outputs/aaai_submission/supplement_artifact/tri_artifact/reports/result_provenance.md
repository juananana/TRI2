# Result Provenance for the TRI AAAI Draft

This file maps paper claims to concrete artifacts. All model-facing metrics are
computed from JSONL run logs with exact-match scoring; no LLM judge is used.

## Core Paired Benchmark

Paper table: `Table 2: State-overwrite controllers drift on anchored-flip tasks`.

Primary report:

- `reports/paper_main_results_v6.json`
- `reports/paper_main_results_v6.md`

Important source runs:

- GLM-5.1 state overwrite: `runs/20260716T020027Z_Pro_zai-org_GLM-5.1_state_overwrite_once_dev_all.jsonl`
- GLM-5.1 heldout state overwrite: `runs/20260716T020530Z_Pro_zai-org_GLM-5.1_state_overwrite_once_heldout_all.jsonl`
- Qwen3.5 state overwrite: `runs/20260716T031158Z_Qwen_Qwen3.5-397B-A17B_state_overwrite_once_dev_all.jsonl`
- MiniMax-M2.5 state overwrite: `runs/20260716T032119Z_Pro_MiniMaxAI_MiniMax-M2.5_state_overwrite_once_dev_all.jsonl`
- DeepSeek-V4-Pro pilot: `runs/20260716T023024Z_deepseek-ai_DeepSeek-V4-Pro_state_overwrite_once_dev_p0.jsonl`

The DeepSeek rows are explicitly treated as a pilot because longer endpoint
runs were unstable.

## Stateful Tool Loop

Paper table: `Table 3: GLM-5.1 in a stateful observe-refresh-process tool loop`.

Primary report:

- `reports/tool_controller_results_v2.json`
- `reports/tool_controller_results_v2.md`

Important source runs:

- Latest-state all paraphrases: `runs/20260716T044002Z_Pro_zai-org_GLM-5.1_tool_latest_state_dev_all.jsonl`
- Latest-state all paraphrases retry/dedup: `runs/20260716T043100Z_Pro_zai-org_GLM-5.1_tool_latest_state_dev_all.jsonl`
- p0 full-history, lossy-summary, compile-then-act: `runs/20260716T041935Z_Pro_zai-org_GLM-5.1_tool_full_history_dev_p0.jsonl`, `runs/20260716T042357Z_Pro_zai-org_GLM-5.1_tool_lossy_summary_dev_p0.jsonl`, and `runs/20260716T042319Z_Pro_zai-org_GLM-5.1_tool_compile_then_act_dev_p0.jsonl`

The tool-loop benchmark is local and stateful, but not an external ToolSandbox
or AppWorld evaluation.

## Compiler and Memory Repairs

Paper table: `Table 4: Repair and memory results`.

Primary reports:

- `reports/compiler_analysis_v2.json`
- `reports/compiler_analysis_v2.md`
- `reports/lossy_summary_case_study.md`

Important source runs:

- GLM-5.1 compile-then-act: `runs/20260716T031003Z_Pro_zai-org_GLM-5.1_compile_then_act_dev_all.jsonl`
- Qwen3.5 compile-then-act: `runs/20260716T034843Z_Qwen_Qwen3.5-397B-A17B_compile_then_act_dev_all.jsonl`
- MiniMax-M2.5 compile-then-act: `runs/20260716T040616Z_Pro_MiniMaxAI_MiniMax-M2.5_compile_then_act_dev_all.jsonl`
- GLM-5.1 lossy summary: `runs/20260716T033535Z_Pro_zai-org_GLM-5.1_lossy_summary_controller_dev_all.jsonl`

The compile-then-act claim in the main repair table applies to the core
flip benchmark. The lifecycle stress test below shows that action-specific
validity remains unresolved.

## Oracle Field Ablation

Paper table: `Table 5: Oracle representation ablation over all 300 tasks`.

Primary report:

- `reports/field_ablation.json`
- `reports/field_ablation.md`

Regeneration command:

```bash
python3 -m tri.field_ablation \
  --input data/temporal_referent.jsonl \
  --output reports/field_ablation.json
```

## Lifecycle Stress Test

Paper table: `Table 6: Oracle representation ablation on 30 lifecycle stress tasks`.
Paper figure: `Figure 2: Lifecycle stress-test accuracy from real model runs`.
The paper uses `figures/lifecycle_accuracy_column.pdf`, a single-column
rendering generated from the same run logs as the wider
`figures/lifecycle_accuracy.pdf` artifact.

Primary reports:

- `reports/lifecycle_ablation.json`
- `reports/lifecycle_ablation.md`
- `reports/lifecycle_model_results_v2.json`
- `reports/lifecycle_model_results_v2.md`

Source data:

- `data/lifecycle_referent.jsonl`

Source runs:

- GLM-5.1 overwrite, all paraphrases: `runs/20260716T045815Z_Pro_zai-org_GLM-5.1_state_overwrite_once_dev_all.jsonl`
- GLM-5.1 compile, all paraphrases: `runs/20260716T050103Z_Pro_zai-org_GLM-5.1_compile_then_act_dev_all.jsonl`
- Qwen3.5 overwrite, p0: `runs/20260716T051338Z_Qwen_Qwen3.5-397B-A17B_state_overwrite_once_dev_p0.jsonl`
- Qwen3.5 compile, p0: `runs/20260716T051411Z_Qwen_Qwen3.5-397B-A17B_compile_then_act_dev_p0.jsonl`
- MiniMax-M2.5 overwrite, p0: `runs/20260716T051800Z_Pro_MiniMaxAI_MiniMax-M2.5_state_overwrite_once_dev_p0.jsonl`
- MiniMax-M2.5 compile, p0: `runs/20260716T051902Z_Pro_MiniMaxAI_MiniMax-M2.5_compile_then_act_dev_p0.jsonl`

Regeneration commands:

```bash
python3 -m tri.lifecycle_tasks --output data/lifecycle_referent.jsonl
python3 -m tri.lifecycle_ablation \
  --input data/lifecycle_referent.jsonl \
  --output reports/lifecycle_ablation.json
```

Figure generation:

```bash
/Users/chu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/make_figures.py \
  --runs runs/20260716T045815Z_Pro_zai-org_GLM-5.1_state_overwrite_once_dev_all.jsonl \
         runs/20260716T050103Z_Pro_zai-org_GLM-5.1_compile_then_act_dev_all.jsonl \
         runs/20260716T051338Z_Qwen_Qwen3.5-397B-A17B_state_overwrite_once_dev_p0.jsonl \
         runs/20260716T051411Z_Qwen_Qwen3.5-397B-A17B_compile_then_act_dev_p0.jsonl \
         runs/20260716T051800Z_Pro_MiniMaxAI_MiniMax-M2.5_state_overwrite_once_dev_p0.jsonl \
         runs/20260716T051902Z_Pro_MiniMaxAI_MiniMax-M2.5_compile_then_act_dev_p0.jsonl \
  --outdir /Users/chu/Documents/Codex/2026-07-15/k-y/outputs/aaai_submission/figures
```

Known limitation: GLM-5.1 uses all three lifecycle paraphrases, while Qwen3.5
and MiniMax-M2.5 currently use the p0 subset. This is stated in the figure
caption and should not be reported as a full cross-paraphrase lifecycle matrix.

## Verification Status

Last verified commands:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile tri/*.py scripts/*.py
rg 'sk-[A-Za-z0-9_-]{20,}' -n outputs work/temporal_referent_integrity
```

The API key scan should return no matches.
