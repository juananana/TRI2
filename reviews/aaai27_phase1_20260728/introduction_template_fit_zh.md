# Introduction 模板适配判断

## 结论

**判定：Adapt（选择性改写），不应直接套用。**

这份“漏斗式四段结构”提供的信息顺序适合 TRI：从具体工作流问题进入，说明现有评测为何看不见该问题，再给出关键区分、诊断设计和证据边界。但模板默认的是典型方法/算法论文：先穷举方法路线，再制造三重挑战，随后介绍多模块方案并用 SOTA 改进收束。TRI 是问题定义、受控诊断和设计原则贡献，照搬会扭曲论文类型并诱发过度主张。

## 可以采用的部分

- 用跨领域读者能理解的具体工作流开场；当前邮件刷新例子有效。
- 由“状态更新”和“是否授权重新解析”的区别自然导向研究缺口。
- 在 Introduction 内清楚交代 matched Preserve/Reevaluate、PairAcc 和 conditional substitution 分别测量什么。
- 在贡献声明附近直接给出最强正向证据，同时保留外部迁移和自然发生率边界。
- 让 Related Work 承担最近邻工作的区分，尤其是 Entity Binding、Binding Drift、contrast sets 和 stateful tool benchmarks。

## 不应采用的部分

- 不应强行把相关工作写成“互斥且穷尽”的两到三类；现有邻域跨 discourse semantics、entity tracking、agent memory 和 behavioral evaluation，MECE 分类会显得人为。
- 不应制造 `three-fold challenge`。论文的中心不是同时解决表示、优化和泛化三类算法难题，而是区分世界证据与重新解析授权。
- 不应把 CTA、Lifecycle、gate 和 rule 包装成一条新方法流水线；正文已正确把它们称为 controller probes/operationalizations。
- 不应使用 “the first”, “novel framework” 或 SOTA 式贡献句。当前外部证据混合，且 Rule* 与强历史基线限制算法新颖性。
- 不应以较高数值本身结束引言；必须同步说明 authored inventory、composite intervention、model dependence 和 unresolved prevalence。

## 对当前 Introduction 的判断

当前版本总体上比通用模板更适合 TRI：它先给出具体例子，再解释一侧评测的不可辨识性，随后定义诊断、报告关键结果并列出贡献。主要写作风险不是缺少“四段八股”，而是信息过密和贡献层级不够突出：第一页到第二页连续引入 TRI、PairAcc、conditional substitution、三类 controller probe、SQLite、matched-call 和 source-derived boundary，Phase 1 审稿人可能记住大量审计名词，却仍不确定最主要的科学贡献究竟是新构念、评测单元还是工程设计原则。

投稿前更合适的 Introduction 结构是：

1. 具体失败与状态--授权区分；
2. 最近邻评测为何不能识别 Preserve/Reevaluate 的选择性行为；
3. TRI 的最小配对构造及其可证伪主张；
4. 一段事实化结果摘要，先给 controlled diagnosis，再给外部边界；
5. 贡献按“定义/诊断证据/执行后果与边界”分层，避免把指标定义和实验清单并列成同等创新。

## 与 Phase 1 风险的关系

套用通用算法模板不会修复当前最主要风险，反而可能放大它。审稿人更可能质疑的是：严格 TRI 机会在原生公开任务中是否有足够意义、作者构造诊断上的正向结果能否支持广义 AAAI 贡献、以及复合 decision block 的效果是否被写成了过强的方法性结论。Introduction 应让这些边界变得更清楚，而不是通过更强的“挑战--方案”叙事掩盖它们。
