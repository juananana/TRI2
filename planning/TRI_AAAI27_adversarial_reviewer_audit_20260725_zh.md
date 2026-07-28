# TRI AAAI-27 对抗性内部审稿（2026-07-25）

性质：内部决策记录，不是论文证据，不进入匿名提交材料。

## 当前判断

- 最新独立 PDF-only 审稿分数：5/10；信心 4/5；Phase 1 略偏不通过。完成本轮叙事与
  headline 修订后，内部预期约 6/10，但外部效度证据没有改变，不能据此估到 7 分。
- 最可信的定位是“matched evaluation identifiability + executed consequence”，不是通用
  agent runtime 或独特算法。
- 双模型 call/information-matched ablation 已排除最直接的调用次数与 actor payload
  差异解释，但独立审稿人将更高权重放在科学重要性、开放语言和自然工作流证据。
  若再有可信的独立语言或自然工作流证据，才有稳定进入 7 分区间的可能。

## 最可能压分的质疑

1. 强化 deterministic rule 在已知 inventory 上达到 92.5/96.0/91.7，说明 authored
   language 很可能主要测 temporal parsing；它削弱 CTA/Lifecycle 的算法新颖性。
2. primary/frozen 仍是 call-asymmetric package comparison。补充 matched ablation 只识别
   authored Flip pairs 上 decision visibility 的作用，不能识别完整 Lifecycle package；Qwen
   hard enforcement 还出现 8 harms 对 4 repairs。
3. 公共 benchmark strict native opportunities 为零，低干预与多数 source-anchored 结果为
   零；现有证据不能支持真实流量 prevalence 或稳定外部收益。
4. Qwen Cross-Schema CTA 的 PairAcc 较低；零 conditional substitution 不等于完整任务可靠。
5. reject policy 只有 55% majority-gold、25% unanimity，应与 referential core 分开。
6. 单一 template-cluster bootstrap 可能低估 crossed generator dependence。

## 已落实的修复

- 主文明确区分 primary/frozen、post-primary replication/audit 与 post-hoc。
- CTA 改写为 controller probe；核心图保留 outside-core wrong writes，避免“零 TRI=安全”。
- 增加 post-primary zero-API crossed domain--template bootstrap；最宽区间仍高于零。
- reject policy 与 actionable referential core 分开报告。
- 外部零结果保留，并将“find zero”限定为 retrieval and author audit 的结果。
- 未公开的相邻工作不再被点名、引用或在补充材料中直接比较。
- 完成 Qwen/GLM call/information-matched ablation：changed PairAcc 分别提高 20 和 30 个
  百分点，Preserve substitution 分别降低 42.9 和 50 个百分点；负面 enforcement 结果保留。
- 摘要已加入 matched ablation，并继续明确 primary package contrast 不是组件因果估计。
- 摘要 headline 已改为 128-task actionable core；32 个低共识 Reject outcomes 明确分离。
- Rule* 数值和 external nulls 已提前到摘要；Results 改为四个问题导向的段落。
- 首图改为 matched opposite-gold 诊断并保留 source-validated wrong-write consequence。
- Discussion 将科学意义限定为 benchmark coverage criterion：没有 opposite-gold
  opportunity 的 suite 不能支持 selective re-resolution 能力主张，但这不是 prevalence 证据。
- Checklist 对每个 partial 给出具体边界，并列明完整 final settings。

## 剩余最高优先级

1. 若能获得真正独立来源，补独立撰写语言或自然 workflow；LLM-only 版本只能叫
   model-assisted stress test。
2. 公开 benchmark 的 recall calibration 仍需独立人工复核；LLM judge 不能替代。
3. 不再扩展新的作者模板或 API 模型矩阵；它们不会解决当前最高权重的外部效度问题。
