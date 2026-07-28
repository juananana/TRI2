# 实验结果数据说明

这里集中存放用于重新构思图表的实验结果数据，不包含 raw API traces、完整任务 payload、
私人人类平台导出、annotator 原始文件、consent 记录或密钥。

## 数据层次

- `key_results_long.csv`：347 条归一化 headline metrics，最适合快速筛选和原型绘图。
- `experiment_registry.csv`：32 个 paper-facing 实验族及其结果/边界。
- `figure_ready/`：当前绘图脚本直接使用的 8 个冻结 summary CSV。
- `paper_facing_result_bundle/reports/`：投稿结果包中的 JSON/CSV/Markdown 报告。
- `additional_result_reports/`：主结果包尚未覆盖的 primary、identifiability、decision-block、
  full-history、stability、failed-gate human、public candidate 和 composition 结果。
- `paper_facing_result_bundle/reports/construct_validity_cue_overlap_v1.{json,md}`：触发词、
  event-order 与 Rule*--模型错误 overlap 的 post-hoc 零 API 审计。
- `paper_facing_result_bundle/reports/TRI_convention_told_natural_history_protocol.md`：
  Convention-told 对照的冻结方案；状态为 planned/unverified，不是实验结果。
- `result_files_manifest.csv`：所有收集结果文件的大小、SHA-256 和原始路径。

## 使用规则

- 优先从 JSON/CSV 作图；Markdown 用于确认分母、failure rule 和证据状态。
- 同名指标只有在分母一致时才能合并。
- `post-hoc`、`failed frozen gate` 和 `planned/unverified` 不得与 frozen confirmatory evidence
  使用同一无标注色标。
- 若仓库报告更新，运行资料夹根目录的 `collect_result_data.py`、`build_inventory.py` 和
  `build_key_results_long.py` 刷新结果。
