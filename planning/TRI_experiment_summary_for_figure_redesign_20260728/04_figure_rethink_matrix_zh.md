# 图表重构矩阵

目标不是把所有实验塞进正文，而是让每张图回答一个 review-critical question。下面列出
可画证据块、最自然的视觉结构，以及必须保留的反例/边界。

| 论证问题 | 最适合的实验 | 可画指标 | 合适视觉语法 | 必须同时显示 | 不应混在一起 |
|---|---|---|---|---|---|
| 评测能否识别 selective authorization？ | v3/v7 PairAcc + Always-Lock/Reevaluate | Preserve、Reevaluate marginals；changed PairAcc；Stable | 两个 policy rulers + PairAcc key；或小型 phase map | 两个极端 Stable=100%、changed PairAcc=0 | Aggregate、Stable、PairAcc 不能共享一个“accuracy”轴而无标签 |
| controlled failure 是否在正确初始绑定后发生？ | v7 shared eligibility | shared-eligible substitution 与 PairAcc | 双面 slope/forest；每模型一行 | Generic 大量 substitution、CTA 0/N；CTA 仍有低 PairAcc/其他错误 | conditional rate 与 E2E 不共用分母 |
| 错目标是否真的写入？ | 40-task model-facing SQLite + v7 replay | correct final state、strict TRI write、fallback write、reject；strict-opportunity rate | outcome decomposition + opportunity calibration | Stable 0/4；Changed 8/8、6/8；CTA non-core wrong writes | model-facing execution 与 deterministic replay 不合并成同一实验 |
| decision visibility 是否有增益？ | full diagnostic matched-call | PairAcc effect、actionable E2E effect、substitution effect | 共享行双端点 forest | Qwen 较小、GLM 较大；独立 CI | PairAcc 与 E2E 的 CI 不能画成 joint confidence region |
| visibility 与 enforcement 是否不同？ | 40-pair matched ablation | History→Visible→Enforced 的 paired outcome | 每模型两段 slope 或 repair/harm balance | Qwen 4 repairs/8 harms、GLM 0/0 | 不把 zero-call enforcement 当新 actor condition |
| 收益是否 transfer？ | rewrites + three-source | endpoint effects by model/dataset/source | small-multiple forest；source×model heatmap 作为补充 | rewrite Qwen null；source Qwen null；DeepSeek CI 跨零；GLM positive | rewrite PairAcc n=3 不与 n=30 PairAcc 同权；不 pooled universal effect |
| 非唯一实现边界是什么？ | component addenda、full history、Rule*、Binding Drift | E2E/PairAcc by method；Preserve/Reevaluate marginals | aligned method dotplot，按 evidence status 分层 | Rule* post-hoc；aware Qwen≈CTA；Lock/Reverify complementary | official vs author adaptation；post-hoc vs frozen 不同视觉语义 |
| 人类构念支持到哪里？ | 3-annotator study + six-form failed gate | majority–gold、unanimity、κ/α；eligibility funnel | slice dotplot + failed-gate funnel | Dynamic 强、Reject 弱；six-form 11/31 valid | 两次 human study 不能 pooling；eligible diagnostics 非 confirmatory |
| 外部证据边界是什么？ | public audits、96-task zero、source-anchored transfer | opportunity funnel；conditional substitutions by repository/interface | evidence funnel + sparse matrix | strict public 0；AgentDojo Qwen 2/7 vs Stable 0/7；其他 cells 0 | 0 strict opportunities ≠ 0 prevalence；author-adapted ≠ native score |
| 单刷新方案能否组合？ | v5/v6 composition、method-upgrade No-Go | scalar vs role-indexed；model-specific success/failure | model×method matrix with explicit Mixed/No-Go | scalar failure、role cross-model instability、M2 direction inconsistent | exploratory smoke 不与 frozen main effect 同色/同 legend |

## 可直接复用的数据快照

- `data/figure_ready/matched_pairacc_and_marginals.csv`：policy rulers / phase map。
- `data/figure_ready/v7_shared_eligible_pairacc_and_substitution.csv`：行为诊断。
- `data/figure_ready/v7_e2e_wrong_writes.csv`：E2E、PairAcc、substitution 与 wrong writes。
- `data/figure_ready/sqlite_model_facing_outcomes.csv`：完整执行结果分解。
- `data/figure_ready/main_figure_paired_scores.csv`：matched-call Figure 5 两端点 effects。
- `data/figure_ready/revision_source_grounded_by_source.csv`：source×model heterogeneity。
- `data/figure_ready/revision_enforcement_and_failures.csv`：repairs、harms 与失败。

## 视觉编码建议

- evidence status 使用边框/填充或分面表达，不用“颜色越深证据越强”的连续映射。
- 模型用圆/方/菱形冗余编码；dataset 用空间分组；post-hoc 用固定 amber 或星号。
- 零结果和不利结果保留原位置，不做只显示 positive gain 的筛选。
- exact counts 只在一个位置出现；区间图优先展示 estimand，分母放组标题或 caption。
- 单栏图以 8 cm / 3.25--3.35 in 作为最终画布，先在实际插入尺寸检查，而不是放大预览。
