# Reviewer A：仅正文初判（AAAI-27 Phase 1）

## 总体结论

- **Phase 1：Reject**
- **评分：4/10（Weak Reject）**
- **Confidence：4/5**
- **Expertise：4/5**

本文提出 Temporal Referent Integrity（TRI）：在同一状态转移下，把“刷新前已经绑定实体”与“刷新后才解析选择器”构造成 Preserve/Reevaluate 的反向金标配对，并用 PairAcc 检查控制器能否选择性地重解析。这个问题定义清楚，正文对证据边界也相当诚实；尤其是将初始绑定、刷新完成、旧目标仍有效、选择器赢家变化与最终错误写入分开，避免把一般 grounding/tool-order 错误混成 TRI（第 3 页“Observable substitution”、第 5 页 RQ2、图 2）。但仅凭正文，我认为其新颖性、概念深度和外部证据尚不足以达到 AAAI 主会标准。

## 决定性优点

1. **诊断对象可识别且双向控制合理。** 第 1–3 页的最小对与表 1 清楚说明：Stable-only 或单边 changed-winner 测试无法排除 Always-Lock/Always-Reevaluate，而 opposite-gold changed PairAcc 能同时排除两种极端策略。式 (4) 也明确区分 PairAcc 与两个边际准确率。这是一个有用的评测设计原则。

2. **主张—证据边界总体克制。** 表 2 明确区分 formal、primary、post-primary、post-hoc 与 descriptive 证据；第 6–7 页保留 Rule* 的强作者任务结果、source-derived 的模型依赖结果、native opportunity 的大量零结果以及组合失败，没有把这些不利证据藏入补充材料。

3. **从目标替换到执行后果的链条较完整。** 第 5 页 RQ2 和第 6 页图 3 把 conditional substitution、固定执行器 replay 与模型面对的 SQLite tool loop 分开报告。至少在受控机会条件下，错误目标会落实为错误实体写入，而不只是文本层面的分类错误。

## 决定性问题

### 1. 相对最近邻工作的新增概念很窄，形式结果没有提供足够独立的新颖性

第 2 页“Initial binding, persistence, and timing”把 TRI 与 Entity Binding / Binding Drift 区分为：后者测试已经提交的 referent 是否持久，TRI 还改变“是否在刷新前提交”。这个边界在逻辑上成立，但当前新增量主要是给已有的 referent persistence 问题增加一个 opposite-gold Reevaluate 成员并联合计分。正文对最近邻只给出概念叙述和一句 author adaptation 结果，详细计数放在补充材料（第 2 页右栏），因此主文无法判断 TRI 是否揭示了 Binding Drift 型测试真正漏掉的模型排序/失败，还是仅把已知的 persistence test 对称化。

形式部分也不足以独立承担贡献。第 3 页“Restricted identifiability observation”只在确定性的 `{Always-Lock, Always-Reevaluate, Selective}` 三策略、exact-target、无 tie 的受限类中证明至少需要一条 changed Preserve 和一条 changed Reevaluate；这是几乎由策略定义直接得到的两行区分。式 (4) 是二元联合正确率的 Fréchet 界，aggregate certification gap 也是计数界。作者正确地加了限制，但限制之后该“理论”更像评测构造的说明，而不是显著的理论贡献。

### 2. 最有利的行为证据仍主要来自作者设计分布，且主要因果比较存在混杂

第 5 页的 primary package comparison 同时改变控制器结构和调用次数：Generic 103/160，Lifecycle-Gated 157/160，但作者也承认这是 call-asymmetric package contrast，不能归因于 timing field。更干净的 matched-call 结果位于第 5–6 页 RQ3，却是 post-primary，并把 predicted mode、bound ID、selector restatement 作为一个复合 block 一起暴露，不能分离哪一部分起作用；其 Qwen E2E 只从 100/128 到 106/128，同时 offline enforcement 对 Qwen 修复 18 条又伤害 8 条。因而现有实验能说明“某些作者构造任务中，一个复合表示改变行为”，但不能支持强的表示或控制器结论。

更关键的是，正结果集中在 authored inventory/cross-schema authored language。第 6 页 RQ4 的 30 对 source-derived 对比中，Qwen PairAcc 12/30→13/30，DeepSeek 19/30→22/30，只有 GLM 的 E2E 区间排除 0；作者后验 Rule* 在 authored inventory 很强，却在 source-derived 上只有 2/30 PairAcc。人类改写只有一名 volunteer，且只有三对完整 actionable changed pairs。第 6 页 native-opportunity coverage 又在四条件 96-task 扩展中得到零 substitution，并在多个公开 benchmark 中找不到 strict native opportunity，而检索 recall 未校准。论文诚实地把这些列为边界，但这些结果也直接削弱了“该诊断对应一个具有现实普遍性的研究问题”的证据。

### 3. AAAI 广泛意义尚未建立；目前更像高质量受控单元测试而非成熟评测贡献

第 7 页 Discussion/Limitations 将范围限定为 single-refresh scalar workflow，并承认 open-language generalization、原生 prevalence、multi-refresh composition、ambiguity/repair/partial observability 等均未解决。作者任务上的 Rule* 强表现说明当前 inventory 很大程度可以由 event-order cues 解决，而 source-derived 上的失败又转为 selector parsing/grounding；这使诊断在两端都面临问题：受控分布可能过于模板化，外部分布又难以隔离“授权时序”本身。正文没有展示足够规模、自然发生且可审计的真实任务机会，也没有证明加入 PairAcc 会改变五个候选集中的模型/控制器选择（第 4–5 页 RQ1 明确说 aggregate E2E 在五组中都选到 PairAcc-optimal candidate）。因此其当前价值主要是解释性诊断，而非对广泛 agent evaluation 实践产生已证实影响的基准或方法。

## 仅正文的最终判断依据

若把论文定位为“问题定义 + 受控诊断”，它是清楚、谨慎并有负面结果意识的；我不因缺少 SOTA 提升而否定它。拒稿的关键在于：最近邻增量偏小，形式结论接近定义性事实，最强正证据依赖作者设计分布，而外部/自然机会证据没有建立实际覆盖或稳定迁移。补充材料若能给出强而公平的最近邻对照、完整协议证明与不依赖作者模板的盲构造证据，可能改变判断；否则正文中的限制已足以支持 Reject。
