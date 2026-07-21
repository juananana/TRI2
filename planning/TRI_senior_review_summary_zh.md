# TRI 论文阶段总结与 AAAI-27 投稿分析材料

本文件汇总论文摘要草稿、研究设计、实验结果、贡献边界与投稿计划。正式研究进展报告见 `planning/TRI_paper_progress_report_zh.md`。

更新时间：2026-07-21

拟投稿：AAAI-27 Main Technical Track

论文题目：**Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents**

中文题目建议：**更新世界状态不等于重新绑定操作目标：工具型智能体中的时序指称完整性**

## 1. 一句话概括

当 Agent 刷新外部环境后，最新状态可能让另一个对象更符合原来的描述，但这不代表用户授权 Agent 把已经选定的操作目标换成新对象；本文把这种“世界知识更新”和“指称目标变化”的区别形式化，并用受控实验、真实数据库写入和公开 benchmark 审计验证。

## 2. 中文摘要

工具型语言模型智能体在执行用户任务时会持续刷新外部状态，但新的观察并不自动授权智能体改变先前指称所对应的实体。本文将这一正确初始绑定之后的授权问题形式化为“时序指称完整性”：世界状态更新与指称目标变化是两个不同的控制决策。在冻结的 160 任务诊断集上，普通结构化记录在 Qwen3.5-122B 和 GLM-5.1 上达到 64.4% 和 71.9%，刷新前“目标承诺编译”达到 95.0% 和 96.2%；始终锁定与始终重选均只有 60%，且错误互补。在独立冻结的 240 任务复制中，普通记录在正确初始绑定后的核心机会中漂移 43/72、38/80 和 59/79 次（Qwen、GLM、DeepSeek），目标承诺编译均为 0，全部 140 次漂移都可重放为错误数据库写入。三模型匹配强基线进一步表明：完整对话轨迹仅达到 63.3%/67.1%/68.8%，最终一步明确提醒“保持或重选”提高到 69.6%/80.8%/75.8%，但仍分别发生 56/38/42 次保持型目标替换；目标承诺编译为 70.8%/94.2%/91.2%，其中 Qwen 总准确率与提醒基线统计持平，GLM 和 DeepSeek 显著更高。三名盲标注者在 100 条原始或自然改写指令上获得 Fleiss kappa 0.708 和 86% 多数票一致率。公开 benchmark 原生严格机会接近零；但对冻结 ToolSandbox-compatible 干预 pilot 的 post-hoc 严格审计发现 GLM Generic 在 3/6 个机会中发生条件 TRI，而低干预外部闭环仍为 null。因此本文是因果隔离的机制诊断和评测盲区分析，不是现实发生率或通用安全保证。

## 3. English Abstract Draft

Refreshing external state does not by itself authorize a tool-using agent to change the entity denoted by an earlier reference. We formalize this post-binding problem as temporal referent integrity (TRI), separating belief updates from referent transitions. On a frozen 160-task diagnostic, a Generic Structured Ledger reaches 64.4%/71.9% with Qwen3.5-122B/GLM-5.1, whereas pre-refresh Compile-then-act (CTA) reaches 95.0%/96.2%; Always-Lock and Always-Reevaluate each reach 60.0% and fail opposite modes. In a separately frozen 240-task replication, conditional on correct initial binding, Generic drifts on 43/72, 38/80, and 59/79 opportunities with Qwen, GLM, and DeepSeek, while CTA drifts on none; all 140 drifts replay as wrong-entity SQLite writes. Matched ordinary full-history baselines reach 63.3%/67.1%/68.8%, and a final TRI-aware reminder improves them to 69.6%/80.8%/75.8% but leaves 56/38/42 anchored substitutions. CTA reaches 70.8%/94.2%/91.2%, tying the aware Qwen baseline in overall accuracy. Three blind annotators obtain Fleiss' kappa=.708 and 86% majority-gold agreement on 100 original/rewrite items. Native public benchmark opportunities are rare; a post-hoc strict audit of a frozen ToolSandbox-compatible intervention finds 3/6 GLM Generic violations, while lower-intervention external loops are null. TRI is therefore a causally isolated, model- and controller-conditional diagnosis, not a prevalence or safety claim.

## 4. 引言思路

### 4.1 直观例子

考虑两个请求：

1. “现在找出优先级最高的未读邮件。刷新邮箱，然后回复它。”
2. “先刷新邮箱。然后找出优先级最高的未读邮件并回复。”

假设刷新前邮件 A 的优先级最高，刷新后邮件 B 变成最高。两个任务经历完全相同的环境变化，但第一个任务应该回复 A，第二个任务应该回复 B。第一个任务已经把 A 变成一个身份承诺；第二个任务则有意把选择推迟到刷新之后。

普通 Agent 很容易把“最新状态更准确”误解为“应该重新执行原来的选择条件”。即使完整对话、旧 ID、实体快照和选择条件都仍然保存在结构化状态里，下游模型仍可能把选择条件应用到新状态，从而把操作目标从 A 换成 B。相反，永远保留旧 ID 又会破坏第二类确实要求刷新后重新选择的任务。

因此，可靠控制需要的不是简单记住对象，也不是永远锁定，而是“选择性保持”：有些描述在被解析后已经成为固定身份，有些描述仍然是要在未来状态中执行的查询，失效目标还需要明确的拒绝或重新选择策略。

### 4.2 研究问题

本文主要回答：

1. 在初始实体已经正确选择的情况下，普通结构化 Agent 状态是否仍会发生目标漂移？
2. 这种错误是否只存在于字符串标签，还是会造成真实数据库错误写入？
3. 主要收益来自记录更多字段、提前规划、目标承诺编译，还是执行 gate？
4. 人类是否能够一致地区分“保持原目标”和“刷新后重新选择”？
5. 现有公开 Agent benchmark 是否覆盖了这种错误机会？
6. 该机制能否组合到多刷新、多指称角色场景？

## 5. 方法概述

### 5.1 普通结构化记录

基线在刷新前保存：任务目标、初始实体 ID、完整实体快照、自然语言选择条件、动作和动作前置条件。刷新后，模型读取这些信息和最新状态并自由决定目标。这个基线并没有故意删除信息；它测试的是“事实都在，但事实之间的授权关系仍然隐含”是否足够。

### 5.2 刷新前目标承诺编译

在刷新发生前，模型先判断：

- 用户是否已经选定了一个具体实体，需要刷新后继续作用于同一 ID；
- 还是用户要求先刷新，再在新状态中执行选择条件。

如果目标在刷新前确定，就保存具体 ID；如果选择被推迟，就保存选择条件。该方法是当前最强且最简单的主方法。

### 5.3 类型化生命周期与执行保护

更完整的控制器把“指称模式、绑定 ID、选择条件、目标失效策略”分开记录。对于已经保持的目标，确定性 gate 检查该实体是否仍满足动作前置条件；gate 可以阻止下游 actor 违反正确承诺，但不能修复错误的模式、ID 或选择条件。

### 5.4 多指称角色扩展

在多次刷新任务中，中间可能出现“仅用于观察的当前选择器赢家”，同时还存在“最终允许修改的操作目标”。角色索引方法分别记录 action target 和 monitoring reference，避免中间观察覆盖最终操作目标。

## 6. 已有实验结果

| 实验 | 规模 | 主要结果 | 支持的结论 |
|---|---:|---|---|
| v3 主实验 | 160 tasks，20 clusters，8 domains，Qwen/GLM | Generic 64.4/71.9%；CTA 95.0/96.2%；Lifecycle-Gated 98.1/100% | 普通结构化记录仍会漂移；刷新前编译是主要收益来源 |
| 对称控制 | 同一 160 tasks | Always-Lock 与 Always-Reevaluate 均为 60% | 不能永远锁定或永远重选，必须理解授权语义 |
| 表示消融 | 同一 160 tasks | Generic+mode 75/75%；untyped plan 81.2/70.6% | 单个 mode 字段或普通提前规划不够 |
| 机制分解 | 同一 160 tasks | CTA 95%+；gate 只增加 1.2--1.9 points | 主要收益来自目标承诺编译，gate 是执行保护 |
| v7 独立复制 | 240 tasks，40 新 state clusters，10 新 schemas | Generic core drift 43/72、38/80；CTA/Gated 均为 0 | 漂移可复制，不依赖 v3 模板或状态 |
| v7 SQLite replay | 1,440 个预测重放 | 81 次 Generic core drift 全部成为 wrong writes | 指称漂移会直接造成错误数据库修改 |
| v3 model-facing SQLite | 40 tasks | Generic wrong writes 13/8；Gated 0/0 | 端到端模型输出也会产生真实错误写入 |
| 人工语义 | 100 tasks，3 annotators | Fleiss kappa 0.708；majority-gold 86% | Preserve/Reevaluate 区分具有人类可操作性 |
| 独立英文改写 | 50 tasks | CTA 90/98%；Generic 60/74% | 效果不只存在于原始模板 |
| v6 多指称组合 | 40 tasks | Qwen role-indexed 39/40，scalar 35/40；GLM 均为 40/40 | 角色索引有潜力，但优势未跨模型稳定 |
| 第三模型完整复制 | 冻结 v7 全量 240 tasks，DeepSeek-V4-Pro | Generic 73.8%，CTA 91.2%，配对 +17.5 points [10.8,23.3]；conditional drift 59/79 对 0/70 | 第三个模型家族完整复现同方向机制；仍标为 post-primary robustness result |
| 三模型匹配完整历史强基线 | v7 240 tasks x 3 models x 2 baselines | 普通完整历史 63.3/67.1/68.8%；语义提醒 69.6/80.8/75.8%；CTA 70.8/94.2/91.2% | 失败不是 Generic ledger 特有；事后提醒有帮助但不等于可执行的刷新前承诺 |
| 完整历史 SQLite 重放 | 1,440 episodes | 普通历史 wrong writes 87/79/75；语义提醒 70/46/57（Qwen/GLM/DeepSeek） | 强基线错误同样会修改错误实体，不是标签误差 |
| ToolSandbox-compatible 条件审计 | 冻结 24-task pilot，6 selector clusters | GLM Generic 3/6 conditional TRI、Stable 0/2；Qwen Lifecycle-free 2/6，gate replay 0/6 | TRI 可在原生数据库/API substrate 中出现；审计 post-hoc，不是官方分数或 prevalence |

## 7. 外部验证与边界

公开数据审计结果：

- ToolSandbox：129 个语义任务家族，严格原生 TRI opportunity 为 0，1 个 near-match。
- AppWorld：732 tasks、244 families，1 个自然 near-match；公开轨迹没有观察到 post-binding substitution。
- tau3-bench：2,449 tasks、10,832 trajectories，严格原生 TRI opportunity 为 0。
- 低干预 AppWorld Agent：28 次正确及时绑定，conditional TRI 为 0；两个错误发生在首次选择之前，属于 pre-binding order error。

这些结果不能证明 TRI 在真实部署中常见。它们支持的结论是：现有 benchmark 很少构造“正确初始绑定后，状态变化导致同角色竞争实体出现，且后续错误目标可评分”的机会，因此不能直接测量这一机制。

## 8. 方法升级闭环及决策

我们在冻结的 20-task smoke 上比较了普通结构化记录、目标承诺编译、生命周期方法、事件图、可执行选择规则、角色索引以及两个确定性控制。

新方法总体结果：

- Event Graph：Qwen 9/20，GLM 20/20；模型间极不稳定。
- Executable Selector：Qwen 15/20，GLM 18/20。
- Exact CTA：Qwen 13/20，GLM 20/20。
- Executable Selector 相对 CTA 在 Qwen 上增加 2 条，在 GLM 上减少 2 条，效果方向冲突。
- Executable Selector 的 schema 与 selector equivalence 没有在两个模型上同时达到 95% 预设门槛。

决策：

- 不把 Event Graph 或 Executable Selector 升级为主方法；
- 主方法保留 Exact CTA；
- Role-Indexed Lifecycle 保留为组合扩展；
- 20-task 结果只作为方法选择和负面消融，不作为有统计功效的主结果。

### 8.1 今晚新增的第三模型检查

在 4-task 健康检查和 16-task pilot 通过后，我们未修改模型、提示词、方法或数据，直接扩到冻结 v7 全量 240 tasks。普通结构化记录达到 177/240（73.8%），目标承诺编译达到 219/240（91.2%），配对提升 +17.5 points，40-cluster bootstrap 95% CI 为 [10.8,23.3]；两个运行均 0 API/parse error、0 retry。

机制分解更重要：普通结构化记录在 79 个“初始目标正确、旧目标仍存在且 action-valid、刷新后新赢家出现”的机会中漂移 59 次，目标承诺编译在 70 个同类机会中漂移 0 次。SQLite 重放后 59 次全部成为错误实体写入。CTA 仍有 17 次 wrong writes，但来自模式、初始 ID 或动态 selector 错误，而不是正确初始绑定后的 drift。因此第三模型支持现有主线，同时进一步证明 gate/CTA 不是通用写安全方案。

## 9. 当前论文贡献

1. 提出并形式化正确初始绑定之后的“指称转换授权”问题，区别于初始实体绑定、普通 coreference 和状态过期。
2. 构造 Stable/Flip、Preserve/Reevaluate 配对的受控诊断，分离初始绑定、post-binding drift、selector grounding 和动作失效。
3. 证明普通结构化状态即使保存充分事实仍会发生可复制的漂移，并将错误直接连接到 SQLite wrong writes。
4. 通过对称控制和表示消融，定位刷新前目标承诺编译为主要有效机制，并限定 gate 的作用。
5. 通过人工语义验证、自然改写、独立状态复制和外部公开 benchmark 审计，给出内部有效性、语言泛化和外部边界。
6. 发现现有公开 benchmark 对严格 TRI opportunity 覆盖不足，提供后续 benchmark 设计原则。

## 10. 当前论文质量与风险判断

### “受控”到底意味着什么

“受控”首先是研究问题本身要求的因果隔离，不是单纯因为实验没做够。若不固定初始状态、刷新事件、候选实体、动作有效性和用户话语，只观察最终 wrong write，就无法判断错误来自首次选择错误、先刷新后选择的工具顺序错误、selector grounding，还是正确绑定后的未授权换目标。条件 TRI 的分母必须要求“初始绑定正确、旧目标仍存在且可执行、刷新后出现同角色新赢家”，否则会把不同错误混在一起。

实验不足主要影响外部有效性和模型覆盖，而不改变这种受控定义。三模型复制、自然改写、held-out schema、SQLite、ToolSandbox/AppWorld 和匹配 full-history 基线已经补强鲁棒性；但即使再扩更多合成任务，也不能推出真实流量发生率。公开数据中严格 opportunity 接近零，所以本稿最稳定位仍是“机制诊断 + benchmark blind spot + authorization principle”。

### 最新强基线的公平解释

| 模型 | 普通完整历史 | 最终语义提醒 | 目标承诺编译 | 编译减提醒（cluster 95% CI） | 提醒后的保持型替换 |
|---|---:|---:|---:|---:|---:|
| Qwen3.5 | 63.3% | 69.6% | 70.8% | +1.2 [-6.7, 9.2] | 56/80 |
| GLM-5.1 | 67.1% | 80.8% | 94.2% | +13.3 [8.8, 17.9] | 38/80 |
| DeepSeek | 68.8% | 75.8% | 91.2% | +15.4 [9.2, 21.7] | 42/80 |

普通完整历史是两次调用、保留完整对话且不提示 TRI；语义提醒是一轮强上界提示，明确要求判断保持、重选或拒绝。它们都没有单独可评分的刷新前选择，因此替换数是无条件 anchored substitution，不能写成 conditional TRI。Qwen 上 CTA 与语义提醒总准确率持平，必须如实报告；CTA 更强的机制证据是：它暴露刷新前绑定，在绑定正确的机会中三模型 conditional drift 均为 0，而后置提示无法提供同样的可审计承诺。

### 优势

- 问题直观，最小对反例容易解释；
- v3 与 v7 形成发现加独立复制；
- 有真实数据库错误后果，而不只是标签准确率；
- 对称控制、表示消融和 gate 分解较完整；
- 人工语义与自然改写缓解纯模板质疑；
- 外部 null 结果如实报告，主张相对克制；
- 正文已经压到 7 页，正式 PDF 为 8 页总计。

### 主要风险

1. **外部有效性**：自然环境没有观察到 conditional TRI，论文必须定位为机制诊断和评测盲区。
2. **方法新颖性**：CTA 很简单，贡献需要依靠问题定义、受控证据、错误后果和 benchmark audit，而不是复杂控制器。
3. **合成任务**：需要强调 cluster 设计、独立状态复制、人类改写和真实写入，而不能把样本量本身当泛化。
4. **第三模型是 post-primary**：DeepSeek 全量结果方向稳定且区间不含 0，但不是最初预注册主比较，必须标为 robustness replication。
5. **组合能力**：role indexing 的提升只在 Qwen 明显，不能写成通用扩展成功。
6. **相关工作可比性**：Binding Drift 的确定性 reverify 使用 gold target，不能作为 learned baseline；Entity Lock 与 Always-Lock 语义接近。

### 投稿可行性判断

当前建议是**可以投稿，但应按机制发现型论文而不是通用安全控制器投稿**。问题定义、最小对、对称控制、三模型独立复制、强基线、真实写入后果、人类验证和公开 benchmark 审计已经形成完整证据链。决定分数的主要不再是“是否还有一个明显缺失的小消融”，而是审稿人是否认可 TRI 相对 Binding Drift/实体绑定的概念新颖性，以及是否接受受控诊断在外部正例稀少时仍有价值。

投稿可行性可从问题新颖性、因果识别、基线完整度、外部有效性和稿件清晰度五个方面判断。当前前三项已具投稿基础；外部有效性是明确短板且不能靠临时扩充合成样本解决；稿件仍需完成最终数字溯源和一次独立 reviewer pass。若按 10 分投稿建议尺度，当前更接近“6-7，值得投稿但并非稳收”，不应描述为无懈可击或高把握接收。

### 预期审稿攻击与正文内回答

| 可能质疑 | 已有回答 | 投稿前动作 |
|---|---|---|
| Generic ledger 人为诱发失败 | 三模型普通完整历史与强语义提醒全量基线 | 已进入主文和 supplement |
| CTA 只是多一次调用/提示更强 | interactive 两调用；untyped pre-refresh plan；one-shot TRI-aware reminder | 明确 Qwen 总准确率持平，不作普遍优越性主张 |
| 条件分母挑选有利样本 | 同时报初始绑定、总体 accuracy、stable、dynamic、API failures | provenance 固化分母代码与任务覆盖 |
| 错误只是字符串标签 | v3 model-facing SQLite、v7 预测重放、最新 1,440 次强基线重放 | 报 wrong writes 与 invalid attempts |
| Preserve/Reject 金标准主观 | 三人盲标；Preserve/Reevaluate 高一致，Reject 低一致 | 缩窄核心主张，Reject 明确为规范性策略 |
| 合成任务不能代表真实 Agent | 人工改写、held-out schema、ToolSandbox/AppWorld、公开轨迹审计 | 坚持 blind-spot 定位，不宣称 prevalence |
| 与 Binding Drift 重复 | 动态重选对称控制；官方 lock/reverify 代码审计 | 相关工作写清 oracle 与任务定义差异 |
| 方法太简单 | 强调问题定义、因果诊断和授权不变量；复杂 M1/M2 负结果 | 不包装复杂度，不把失败升级方法放主表 |
| 温度 0 单次运行不稳定 | 三模型、40 cluster、原始输出和 retry 审计 | 40-task 重复稳定性列为最后可选补实验，而非主结论前提 |

## 11. 仍需进一步论证的问题

1. 这个问题定义和最小对是否足以支撑 AAAI 的 novelty？
2. 论文应更偏“Agent memory/controller mechanism”，还是“diagnostic benchmark blind spot”？
3. DeepSeek 全量结果应进入正文复制实验段，还是只进入 supplement 以保持主文叙事简洁？
4. CTA 很简单，是否应突出“问题发现与因果机制分解”，而不是包装成复杂新方法？
5. 外部 benchmark 零 opportunity/null TRI 应放主结果还是限制？
6. 20-task Event Graph/Executable Selector 负面结果是否只放 supplement？
7. 标题是否需要更直接出现 authorization 或 post-binding drift？

## 12. 接下来八天

详细计划见 `planning/TRI_AAAI27_eight_day_submission_plan_zh.md`。总体原则是：7 月 21 日锁定摘要和叙事；7 月 22 日完成摘要提交与数字溯源；7 月 23--25 日完成统计、补充材料、artifact 和 reviewer pass；7 月 26 日冻结实验；7 月 27 日冻结提交包，保留后续时区缓冲。
