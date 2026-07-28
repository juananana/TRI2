# TRI 论文实验进展简报（合作者版）

> 论文：*Temporal Referent Integrity: A Controlled Diagnostic of Referential Resolution Timing in Tool-Using Agents*  
> 日期：2026-07-24  
> 用途：向合作者说明当前投稿版本的实验设计、主要结果、负面证据与剩余风险  
> 证据口径：只汇报已完成结果，并区分 primary、post-primary、post-hoc 与 planned/unverified

## 1. 一句话结论

论文发现了一个受控评测盲区：环境刷新会更新世界信息，但不会自动授权 Agent 改变已在刷新前解析完成的操作对象。现有受控实验表明，普通完整状态记录仍可能在正确初始绑定后把旧目标替换为刷新后的 selector winner；对称 Preserve/Reevaluate 最小对和 PairAcc 能识别这种错误，而单侧评分不能。该替换可以被确定性重放为错误实体写入。新的 STATE-Bench/AgentDojo source-anchored transfer 只在 AgentDojo 的 Qwen ordinary-history 切片复现 2/7 Preserve/Changed substitution（Stable 0/7），并且 execution record 没有稳定优势。因此，论文定位仍是 evaluation/diagnostic contribution，不是通用运行时架构、官方 benchmark 结果或真实流量发生率研究。

## 2. 论文具体测什么

同一组初始状态 $S_0$、刷新后状态 $S_1$、选择器、动作和状态变化，被写成两个只改变解析时机的指令：

- **Preserve**：刷新前已经选定具体实体，刷新后仍应操作原 ID；
- **Reevaluate**：指令要求刷新后再选择，应操作 $S_1$ 中的新 winner。

当 $q(S_0)\neq q(S_1)$ 且旧目标仍有效时，Always-Lock 和 Always-Reevaluate 分别只能答对一侧。论文据此使用 matched changed-winner PairAcc，而不是只看 Stable 或单侧准确率。

严格的 conditional substitution 分母还要求：

1. 初始绑定可观察且正确；
2. refresh 已完成；
3. 旧实体仍存在并可执行当前动作；
4. 刷新后的 selector winner 与旧实体不同。

这避免把初始 selector grounding、tool order、API/parse failure 或无效目标处理错误重新命名为 TRI。

## 3. 证据时间线

| 实验 | 证据状态 | 作用 |
|---|---|---|
| v3 Generic vs Lifecycle-Gated | **primary/frozen** | Qwen 预指定 package-level 主对比；GLM 为复制 |
| v3 组件分解 | **post-primary；各自在调用前冻结** | 检查 mode、plan、typed record 和 gate 的作用 |
| v7 新 schema/新状态复制 | **post-primary replication** | Qwen、GLM、DeepSeek 三模型的条件替换和 PairAcc |
| SQLite trajectory/replay | secondary 或 post-primary zero-API | 验证 target error 是否成为真实 wrong write |
| 人工标注与人工改写 | **post-primary validation/replication** | 检查核心语义和模板依赖 |
| Full-history baselines | **post-primary strong baseline** | 排除问题只由 Generic ledger 序列化造成 |
| Rule v2 | **post-hoc** | 强规则基线，限制方法新颖性 |
| Public-suite/低干预审计 | descriptive/boundary evidence | 检查外部机会和零结果 |
| STATE-Bench/AgentDojo source-anchored transfer | **post-primary；自身调用前冻结** | 单仓库有限行为转移，同时否定稳定 execution-record 优势 |

所有 planned/unverified 方案均不作为当前论文证据。

## 4. Primary：TRI-v3

### 设计

- 160 条任务，20 个冻结语言模板簇；
- 8 个领域，4 种 reference style，5 种 update type；
- Qwen3.5-122B-A10B 为主模型，GLM-5.1 为复制；
- 主估计量是完整 Lifecycle-Gated package 减 Generic 的簇级 E2E 差异；
- 该比较是 call-asymmetric package contrast，不是某个组件的因果效应。

### 结果

| 模型 | Generic | Lifecycle-Gated | 差值及 cluster 95% CI |
|---|---:|---:|---:|
| Qwen | 103/160（64.4%） | 157/160（98.1%） | +33.8 点，[+18.1, +50.0] |
| GLM | 115/160（71.9%） | 160/160（100.0%） | +28.1 点，[+18.1, +38.1] |

Aggregate 包含 128 条 actionable entity target 和 32 条作者规定的 Reject policy。拆开后：

| 模型/控制器 | Actionable core | Reject policy |
|---|---:|---:|
| Qwen Generic | 95/128（74.2%） | 8/32（25.0%） |
| Qwen Historical CTA | 126/128（98.4%） | 26/32（81.2%） |
| Qwen Lifecycle-Gated | 125/128（97.7%） | 32/32 |
| GLM Generic | 93/128（72.7%） | 22/32（68.8%） |
| GLM Historical CTA | 127/128（99.2%） | 27/32（84.4%） |
| GLM Lifecycle-Gated | 128/128 | 32/32 |

人工对 Reject 的支持明显弱于核心指称语义，因此正文不会用 Reject slice 单独支撑 TRI 主张。

### Matched-pair 结果

| 控制器 | Qwen changed PairAcc | GLM changed PairAcc | Stable PairAcc |
|---|---:|---:|---:|
| Generic | 3/32 | 7/32 | 16/16 |
| Historical CTA | 30/32 | 31/32 | 16/16 |
| Lifecycle-Gated | 32/32 | 32/32 | 16/16 |
| Always-Lock | 0/32 | 0/32 | 16/16 |
| Always-Reevaluate | 0/32 | 0/32 | 16/16 |

Stable 上的满分不能区分两个方向相反的无条件策略。

## 5. Post-primary replication：TRI-v7

v7 包含 240 条任务、10 个新 schema 和 40 个状态簇。所有旧目标在刷新后都仍存在且动作有效，因此 changed-winner 错误不依赖 invalid-target policy。

| 模型/控制器 | E2E | Changed PairAcc | Conditional substitution | Core/all wrong writes |
|---|---:|---:|---:|---:|
| Qwen Generic | 47.5% | 7/80 | 43/72 | 43/44 |
| Qwen CTA | 70.8% | 31/80 | 0/71 | 0/8 |
| GLM Generic | 70.0% | 15/80 | 38/80 | 38/38 |
| GLM CTA | 94.2% | 66/80 | 0/70 | 0/14 |
| DeepSeek Generic | 73.8% | 17/80 | 59/79 | 59/60 |
| DeepSeek CTA | 91.2% | 64/80 | 0/70 | 0/17 |

解释时必须同时保留三点：

- Generic 在三个模型中都出现正确初始绑定后的定向替换；
- CTA 的 conditional numerator 为 0，但仍有 binding、grounding 和 execution errors；
- Qwen CTA PairAcc 只有 31/80，说明“没有该类替换”不等于总体任务解决。

在 Generic 和 CTA 都正确绑定的 shared-eligible 同一任务上，替换计数为 Qwen 41/66 vs 0/66、GLM 30/70 vs 0/70、DeepSeek 50/69 vs 0/69，排除了控制器特定分母选择这一解释。

## 6. 评测可识别性和一次重要更正

v7 的 Always-Lock 与 Always-Reevaluate 都有 66.7% aggregate、100% Stable，但 changed PairAcc 都是 0/80。所有 15 个 Stable-only 或单侧 proxy maximizer set 都包含零 PairAcc 的无条件策略，最大 worst-case regret 为 100 点。

2026-07-23 检查发现，selection-regret 初版实现错误地漏掉了已经报告的 Lifecycle-Gated 行，因此原先“v3 GLM aggregate 损失 6.25 PairAcc 点”的结论不成立。修正后的结果是：

- Aggregate E2E 在 5/5 个完整候选集中都选择 PairAcc 最优方法；
- selection failure 只在 Stable-only 和单侧 proxy 中得到实证支持；
- 协议、报告、测试、正文和 claim provenance 均已同步更正；没有新增 API 调用。

这项更正缩小了 identifiability 的经验后果，但使论文的报告边界更可靠。

## 7. 组件、强基线与非唯一实现

| 方法 | Qwen v3 | GLM v3 | 解释 |
|---|---:|---:|---|
| Generic | 64.4% | 71.9% | 信息存在，但授权决定未可靠落实 |
| Generic + reference mode | 75.0% | 75.0% | mode 有帮助但不充分 |
| Generic + validity gate | 65.0% | 73.1% | action validity 不能决定 referent |
| Untyped pre-refresh plan | 81.2% | 70.6% | 提前自由规划不稳定 |
| Historical CTA | 95.0% | 96.2% | 简洁的 commitment realization |
| Lifecycle-free | 96.9% | 98.1% | typed record 已解释大部分收益 |
| Lifecycle-Gated | 98.1% | 100.0% | deterministic gate 额外增加 1.2/1.9 点 |

后续证据不支持 CTA、typed tuple、pre-refresh timing 或 gate 的唯一必要性。论文能够支持的共同点是：控制器需要访问话语敏感的 resolution-status/transition decision，并把它落实到执行目标。

### Full-history baseline

| 模型 | Ordinary history | Final-step aware history | CTA |
|---|---:|---:|---:|
| Qwen | 63.3% | 69.6% | 70.8% |
| GLM | 67.1% | 80.8% | 94.2% |
| DeepSeek | 68.8% | 75.8% | 91.2% |

Qwen aware history 与 CTA 的总体准确率统计上不可区分；GLM 和 DeepSeek 上 CTA 更高。该结果说明现象不只存在于 Generic ledger，但不能识别唯一内部机制。

### Post-hoc deterministic rule

Rule v2 在查看 v1 失败后加入 benchmark event vocabulary，达到 v3 92.5%、人工改写 96.0%、v7 91.7%。它不是开放语言泛化证据，却说明当前任务的成功可由相对简单的事件顺序规则实现，因此算法新颖性必须主动收窄。

## 8. 执行后果

40-task 模型面对 SQLite 的实验中：

| 模型/控制器 | Final state | Wrong writes |
|---|---:|---:|
| Qwen Generic | 27/40 | 13 |
| Qwen Lifecycle-Gated | 40/40 | 0 |
| GLM Generic | 26/40 | 8 |
| GLM Lifecycle-Gated | 40/40 | 0 |

在 v7 的确定性重放中，Generic 的 43、38、59 次 core substitution 全部成为 wrong-entity write。CTA core write 为 0，但仍分别有 8、14、17 次其他错误写入。安全收益没有通过拒绝工作来冒充成功，wrong write、invalid attempt、rejection 和 utility 分开报告。

## 9. 人类验证

- 1 名未参与设计的志愿者改写 50 条英文指令；
- 3 名其他志愿者独立盲标 100 个 original/rewrite item；
- 总体 majority--gold 为 86.0%，94 个 determinate majority 中为 91.5%；
- Fleiss $\kappa=.708$，Krippendorff $\alpha=.709$；
- Dynamic majority--gold 为 98.0%；
- Anchored actionable 为 86.7%，但 Anchored Reject 只有 55.0%，unanimity 25.0%。

来源任务使用固定 seed 按 20 个 style--update 单元分层抽取。任务要求能够处理英文，但语言背景未独立测试；招募渠道、既有关系、实际时长和精确报酬未进入研究数据。因此这是一项支持 scalar construct 的便利样本验证，不支持 Reject policy 或人口统计泛化。

在 50 条志愿者改写上，Qwen/GLM CTA benchmark-gold accuracy 为 90.0%/98.0%，但该实验是 authored-task adaptation，不是独立自然请求 elicitation，也不证明 CTA 优于 typed variants。

## 10. 外部结果和组合性负证据

这些结果是论文边界的一部分：

- 冻结 96-task ToolSandbox-style extension 的四个 paper-facing 条件均为 0 conditional substitution（机会数 70/73/64/87）；
- custom AppWorld 为 0/24，去掉显式 binding sidecar 的 addendum 为 0/28；
- 固定 ToolSandbox 129 families、AppWorld 244 families、$\tau^3$-Bench 2,449 tasks 的作者审计均没有严格原生机会；该审计没有独立 recall 校准；
- API-Bank/BFCL/ToolTalk 的零 API 扫描同样得到 0 个 strict native opportunities；冻结双模型候选标注完成 160/160 pairs，145 条有效、15 条失败/无效，strict-positive 并集/交集为 0/0。该结果只是模型辅助候选标注，不是独立复核或 prevalence；
- 两刷新 Qwen 压力测试中 Generic 32/40，高于 scalar Lifecycle 28/40；
- role-indexed addendum 在 Qwen 为 39/40 vs 35/40，但 GLM ITT 因三次 transport failure 为 37/40 vs 40/40，恢复后持平。

因此目前不能区分：公开 benchmark 欠覆盖、作者 opportunity checklist 漏检，或受控 controller interface 放大了现象。论文只主张 controlled, model- and controller-conditional diagnosis。

## 11. 当前论文可以和不可以说什么

### 可以支持

- 状态更新与 referent transition authorization 是可分离的评测变量；
- Stable/单侧评分无法识别选择性保持与重选；
- matched changed-winner PairAcc 可以同时排除两个无条件极端；
- 受控接口上存在正确初始绑定后的 controller-conditional substitution；
- 该 substitution 可以成为实际 wrong-entity write；
- 多种实现可以落实同一分离原则，且简单规则已经很强。

### 不可以支持

- TRI 在真实用户流量中高频发生；
- 所有 LLM 或工具 Agent 普遍失败；
- CTA、显式字段或特定序列化是唯一或数学上必要的方案；
- CTA 消除所有 wrong write 或建立一般安全性；
- Rule v2 在开放语言中泛化；
- 三个固定 public suite 的零机会代表真实世界零发生率；
- Binding Drift author adaptation 是官方或信息匹配的性能基线。

## 12. 当前复现和投稿状态

- 主论文：7 页正文 + 2 页参考文献；
- Supplement：20 页；Checklist：2 页；
- 开发树测试：217 passed；clean-room artifact：216 passed；
- 主文证据审计：13/13；跨文档一致性审计：23/23；
- 匿名 artifact：1,066 个 manifest 条目，4,129,751 bytes；
- artifact SHA-256：`866a3368e4a535c58d2d3baa64a828a8427ed7765cb9c2b7f7c34897917267ee`；
- ZIP CRC、manifest、密钥/本地路径/显式身份模式扫描通过。

## 13. 希望师姐重点帮忙判断

1. 现在把贡献定位为“evaluation identifiability + controlled behavioral diagnosis + execution consequence”，是否足以支撑 AAAI 主会的重要性？
2. Primary package comparison 的 call asymmetry 和后续组件分解是否披露得足够早、足够清楚？
3. Rule v2、full-history Qwen near-tie、混合外部证据和组合负结果是否与正面结果处于合适的可见度？
4. 主文是否已把 closest-neighbor 边界讲清：TRI 不发现 drift 本身，而是评估 drift 是否被解析时机授权？
5. 在不增加新实验的前提下，哪些段落或表格最值得继续压缩或强化？

## 14. 关键文件

- 主论文：[`paper/AnonymousSubmission2027.pdf`](../paper/AnonymousSubmission2027.pdf)
- Supplement：[`paper/supplementary_material.pdf`](../paper/supplementary_material.pdf)
- 完整实验总览：[`TRI_AAAI27_experiment_design_results_summary_zh.md`](TRI_AAAI27_experiment_design_results_summary_zh.md)
- 证据 provenance：[`current_claim_provenance.md`](../experiments/tri_artifact/reports/current_claim_provenance.md)
- 实验 registry：[`current_experiment_registry.md`](../experiments/tri_artifact/reports/current_experiment_registry.md)
- 匿名 artifact：[`submission/tri_anonymous_artifact_current.zip`](../submission/tri_anonymous_artifact_current.zip)
