# TRI 本地补跑说明

如果我这里的硅基接口长尾卡住，你可以在本地继续跑正式矩阵。

```bash
cd /Users/chu/Documents/Codex/2026-07-15/k-y/work/temporal_referent_integrity
bash scripts/run_submission_matrix.sh
```

脚本默认从以下文件读取硅基 API key：

```text
/Users/chu/Downloads/硅基流动密钥.rtf
```

跑完后检查是否有 API timeout：

```bash
python3 - <<'PY'
import json, glob
for p in glob.glob('runs/*.jsonl'):
    bad = 0
    total = 0
    for line in open(p):
        if not line.strip():
            continue
        total += 1
        r = json.loads(line)
        if r.get('status') != 'ok' or r.get('result', {}).get('errors'):
            bad += 1
    if bad:
        print(p, bad, '/', total)
PY
```

当前论文使用的主结果表由以下脚本生成：

```bash
python3 -m tri.paper_tables --exclude-result-errors \
  --input runs/*.jsonl \
  --output reports/paper_main_results_all.json
```

注意：`runs/*.jsonl` 会把早期 smoke、partial 和中断文件也纳入。正式写论文时最好只选择完整 run 文件，或者先筛掉中断/重复 run。

## Lifecycle Stress Test

生成 30 个 lifecycle cases：

```bash
python3 -m tri.lifecycle_tasks --output data/lifecycle_referent.jsonl
```

GLM 全 paraphrase 运行：

```bash
python3 scripts/run_silicon_batch.py \
  --models Pro/zai-org/GLM-5.1 \
  --modes state_overwrite_once compile_then_act \
  --split dev --paraphrase all --condition all \
  --data data/lifecycle_referent.jsonl --timeout 120
```

Qwen/MiniMax p0 跨模型复核：

```bash
python3 scripts/run_silicon_batch.py \
  --models Qwen/Qwen3.5-397B-A17B Pro/MiniMaxAI/MiniMax-M2.5 \
  --modes state_overwrite_once compile_then_act \
  --split dev --paraphrase p0 --condition all \
  --data data/lifecycle_referent.jsonl --timeout 120
```

Oracle representation ablation:

```bash
python3 -m tri.lifecycle_ablation \
  --input data/lifecycle_referent.jsonl \
  --output reports/lifecycle_ablation.json
```

论文图由完整 run logs 自动生成：

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

## Stateful Tool Controller 小矩阵

本地工具环境实验使用 `observe -> refresh -> process` 的真实工具循环。GLM p0 三域复现实验可以这样跑：

```bash
cd /Users/chu/Documents/Codex/2026-07-15/k-y/work/temporal_referent_integrity

python3 scripts/run_tool_controller_batch.py \
  --models Pro/zai-org/GLM-5.1 \
  --modes tool_latest_state tool_full_history tool_lossy_summary tool_compile_then_act \
  --split dev --paraphrase p0 --condition anchored-flip \
  --domains incident,meeting,ticket --timeout 90

python3 scripts/run_tool_controller_batch.py \
  --models Pro/zai-org/GLM-5.1 \
  --modes tool_latest_state tool_full_history tool_lossy_summary tool_compile_then_act \
  --split dev --paraphrase p0 --condition dynamic-flip \
  --domains incident,meeting,ticket --timeout 90
```

生成工具控制器报告时建议显式列出完整 run 文件：

```bash
python3 -m tri.paper_tables --deduplicate-tasks --exclude-result-errors \
  --output reports/tool_controller_results_v1.json \
  --input runs/*tool_latest_state_dev_p0.jsonl \
          runs/*tool_full_history_dev_p0.jsonl \
          runs/*tool_lossy_summary_dev_p0.jsonl \
          runs/*tool_compile_then_act_dev_p0.jsonl
```

## AAAI-27 官方模板论文

正式匿名提交版在：

```text
/Users/chu/Documents/Codex/2026-07-15/k-y/outputs/aaai_submission
```

其中：

```text
tri_aaai2027_submission.tex
tri_references.bib
aaai2027.sty
aaai2027.bst
```

在有 TeX 的环境中编译：

```bash
cd /Users/chu/Documents/Codex/2026-07-15/k-y/outputs/aaai_submission
pdflatex tri_aaai2027_submission.tex
bibtex tri_aaai2027_submission
pdflatex tri_aaai2027_submission.tex
pdflatex tri_aaai2027_submission.tex
```

当前 Codex 环境没有 `pdflatex`/`latexmk`/`tectonic`，所以这里没有生成 PDF。
