# TRI 论文阶段总结与 AAAI-27 投稿评估材料

更新时间：2026-07-20

拟投稿：AAAI-27 Main Technical Track

论文题目：**Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents**

中文题目建议：**更新世界状态不等于重新绑定操作目标：工具型智能体中的时序指称完整性**

## 1. 一句话概括

当 Agent 刷新外部环境后，最新状态可能让另一个对象更符合原来的描述，但这不代表用户授权 Agent 把已经选定的操作目标换成新对象；本文把这种“世界知识更新”和“指称目标变化”的区别形式化，并用受控实验、真实数据库写入和公开 benchmark 审计验证。

## 2. 中文摘要

工具型语言模型智能体在执行用户任务时会持续刷新外部状态，但新的观察并不自动授权智能体改变先前指称所对应的实体。本文将这一正确初始绑定之后的授权问题形式化为“时序指称完整性”：世界状态更新与指称目标变化是两个不同的控制决策。在一个冻结的 160 任务最小对诊断集上，保存指令、初始目标 ID、实体快照、选择条件和动作前置条件的普通结构化记录，在 Qwen3.5-122B 和 GLM-5.1 上分别达到 64.4% 和 71.9%；在刷新前显式编译目标绑定时间与身份的“目标承诺编译”方法达到 95.0% 和 96.2%。始终锁定旧目标和始终重新选择目标都只有 60%，且错误互补，说明问题不是单纯的记忆或锁定，而是判断用户是否授权目标转换。在另一个独立冻结的 240 任务复制实验中，当初始绑定正确时，普通结构化记录在 43/72 和 38/80 个机会中漂移到刷新后的选择器赢家，而目标承诺编译和带生命周期保护的方法均为 0；这 81 次漂移全部可以重放为对错误数据库实体的实际写入。三名盲标注者在 100 条原始或自然改写指令上获得 Fleiss kappa 0.708 和 86% 的多数票一致率。对 ToolSandbox、AppWorld 和 tau3-bench 的公开任务及轨迹审计发现，现有基准几乎没有严格覆盖这种“正确绑定后、状态变化、可替代同角色实体、可评分错误写入”的机会；外部 full-history Agent 实验中也未观察到条件 TRI。因此，本文提供的是一个受控、依赖模型和控制器的机制诊断与评测盲区分析，而不是现实流量发生率或通用安全保证。

## 3. English Abstract Draft

Refreshing external state does not by itself authorize a tool-using agent to change the entity denoted by an earlier reference. We formalize this post-binding problem as temporal referent integrity (TRI), separating belief updates from referent transitions. On a frozen 160-task diagnostic, a Generic Structured Ledger reaches 64.4%/71.9% with Qwen3.5-122B/GLM-5.1, whereas pre-refresh Compile-then-act reaches 95.0%/96.2%. Always-Lock and Always-Reevaluate each reach 60.0% and fail opposite modes. In a separately frozen 240-task replication, conditional on correct initial binding, Generic drifts on 43/72 and 38/80 opportunities; Compile-then-act and Lifecycle-Gated drift on none, and all 81 Generic drifts replay as wrong-entity SQLite writes. A typed Lifecycle reaches 98.1%/100.0% on the primary set, but its gate adds only 1.2--1.9 points over a matched free actor. Three blind annotators obtain Fleiss' kappa=.708 and 86% majority-gold agreement on 100 original/rewrite items. Public ToolSandbox, AppWorld, and tau3 audits find almost no strict TRI opportunities, and external full-history studies observe zero conditional TRI. TRI is therefore a controlled, model- and controller-conditional mechanism diagnosis, not a prevalence or safety claim.

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
| 第三模型探索性复制 | 冻结 v7 标量子集 16 tasks，DeepSeek-V4-Pro | Generic 11/16；CTA 15/16；在 6 个正确初始绑定的 core opportunities 中，Generic 漂移 5 次、CTA 漂移 0 次 | 第三个模型家族上复现同方向机制，但样本小、配对 cluster CI 含 0，暂不作为主结果 |

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

在查看正式子集结果前，我们冻结 DeepSeek-V4-Pro、普通结构化记录与目标承诺编译两个方法，以及 16 条 v7 标量任务。4 条平衡任务健康检查无 API 错误后，完整子集同样 0 API/parse error。普通结构化记录准确率为 11/16（68.8%），目标承诺编译为 15/16（93.8%），配对差为 +25.0 points，state-cluster bootstrap 95% CI 为 [0.0, 50.0]。

更关键的机制分解是：普通结构化记录在 6 个“初始目标已正确绑定、刷新后出现同角色新赢家”的机会中漂移 5 次；目标承诺编译漂移 0 次。目标承诺编译唯一错误发生在刷新前把 BAT-3B 错认成 oldest batch，属于 initial binding error，不是 post-binding drift。该结果支持现有问题分解，但 16 条不足以单独承担跨模型泛化主张。明天需要决定是扩到冻结的 v7 全量，还是只把它作为 pilot 并在限制中保留两模型主结果。

## 9. 当前论文贡献

1. 提出并形式化正确初始绑定之后的“指称转换授权”问题，区别于初始实体绑定、普通 coreference 和状态过期。
2. 构造 Stable/Flip、Preserve/Reevaluate 配对的受控诊断，分离初始绑定、post-binding drift、selector grounding 和动作失效。
3. 证明普通结构化状态即使保存充分事实仍会发生可复制的漂移，并将错误直接连接到 SQLite wrong writes。
4. 通过对称控制和表示消融，定位刷新前目标承诺编译为主要有效机制，并限定 gate 的作用。
5. 通过人工语义验证、自然改写、独立状态复制和外部公开 benchmark 审计，给出内部有效性、语言泛化和外部边界。
6. 发现现有公开 benchmark 对严格 TRI opportunity 覆盖不足，提供后续 benchmark 设计原则。

## 10. 当前论文质量与风险判断

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
4. **第三模型证据仍小**：DeepSeek 16-task 子集方向一致，但配对区间仍触及 0；若要在摘要或主表写三模型，需要扩大冻结样本并完成同等 provenance。
5. **组合能力**：role indexing 的提升只在 Qwen 明显，不能写成通用扩展成功。
6. **相关工作可比性**：Binding Drift 的确定性 reverify 使用 gold target，不能作为 learned baseline；Entity Lock 与 Always-Lock 语义接近。

## 11. 希望师姐重点评估的问题

1. 这个问题定义和最小对是否足以支撑 AAAI 的 novelty？
2. 论文应更偏“Agent memory/controller mechanism”，还是“diagnostic benchmark blind spot”？
3. DeepSeek 的 16-task 同方向结果是否值得扩到冻结 v7 全量，还是两模型主结果加第三模型 pilot 已足够？
4. CTA 很简单，是否应突出“问题发现与因果机制分解”，而不是包装成复杂新方法？
5. 外部 benchmark 零 opportunity/null TRI 应放主结果还是限制？
6. 20-task Event Graph/Executable Selector 负面结果是否只放 supplement？
7. 标题是否需要更直接出现 authorization 或 post-binding drift？

## 12. 接下来八天

详细计划见 `planning/TRI_AAAI27_eight_day_submission_plan_zh.md`。总体原则是：7 月 21 日根据师姐反馈锁定摘要和叙事；7 月 22 日完成摘要提交与数字溯源；7 月 23--25 日完成统计、补充材料、artifact 和 reviewer pass；7 月 26 日冻结实验；7 月 27 日冻结提交包，保留后续时区缓冲。
