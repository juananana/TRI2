# TRI 实验与结果资料夹（图表重构版）

更新时间：2026-07-28（Asia/Shanghai）

这个资料夹面向“重新构思论文图表”，而不是替代原始实验仓库。数字、证据状态和 claim
边界以 `sources/current_experiment_registry.md`、`sources/current_claim_provenance.md` 及其中
指向的冻结报告为准。

## 建议阅读顺序

1. `01_master_experiment_index_zh.md`：32 个当前 paper-facing 实验族，加上补充材料中的
   关键附加审计；用于确认没有漏实验。
2. `02_detailed_results_zh.md`：截至 2026-07-24 的完整中文实验说明，含 v3、v7、组件、
   SQLite、人类、外部和组合性结果。
3. `03_recent_and_boundary_results_zh.md`：补充 2026-07-24 后完成或定稿的 matched-call、
   decision-block、source-derived、六表人类审计、公共候选和 model-authored stress 结果。
4. `04_figure_rethink_matrix_zh.md`：按论文论证问题整理可画指标、推荐视觉语法和禁止合并项。
5. `05_metric_denominator_guide_zh.md`：PairAcc、E2E、conditional substitution、wrong write
   等指标的分母与不可混用规则。
6. `data/experiment_registry.csv`：从当前注册表自动抽取的机器可筛选总表。
7. `data/key_results_long.csv`：从 figure-ready CSV 自动归一化的长表，适合快速分面和筛选。
8. `data/figure_ready/`：现有绘图脚本使用的冻结 summary CSV 快照。
9. `data/source_catalog.csv`：实验族到权威报告/绘图数据的路径索引。
10. `data/paper_facing_result_bundle/`：完整 paper-facing JSON/CSV/Markdown 结果包。
11. `data/additional_result_reports/`：主结果包之外的 primary、稳定性、人类和外部结果。
12. `data/result_files_manifest.csv`：结果文件大小、SHA-256 与原始路径。
13. `figure_code/`：与本资料夹数据快照配套的可复现绘图代码。
14. `figure_outputs/`：由上述代码生成的 PDF、SVG、400-dpi PNG 与视觉 QA 版本。

## 本资料夹的范围

- “实验”按研究问题和冻结 inventory 归并为实验族；smoke、health gate、transport retry
  不单独计作更多实验，但失败和修复会保留在对应实验备注中。
- 包含正结果、零结果、负结果、混合结果、post-hoc 结果和 failed-gate 人类审计。
- `planned/unverified` 单列，不能画成结果。
- 不把 author adaptation 写成官方 benchmark 结果；不把 source-derived intervention 写成
  native prevalence；不把 conditional substitution 的零观察写成总体任务安全。

## 快照与原仓库

原仓库：TRI 仓库根目录

本资料夹中的 CSV 和权威 Markdown 是 2026-07-28 的快照。若原仓库继续更新，应先运行
`build_inventory.py` 重新抽取注册表，并重新复制 `paper/tri_final_figures/data/summary_csv/`
下的绘图数据。

当前 `data/figure_ready/` 已与 `paper/tri_final_figures/data/summary_csv/` 逐文件校验一致。
更新数据后，应重新运行 `figure_code/plot_result_closure_v2.py`；脚本会在生成前校验论文图
使用的精确计数、分母、效应量和置信区间，并把源文件哈希写入 manifest。
