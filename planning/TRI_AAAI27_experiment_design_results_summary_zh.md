# TRI 实验设计与结果总览

> 对应论文：*Temporal Referent Integrity: A Controlled Diagnostic of Referential Resolution Timing in Tool-Using Agents*  
> 文档性质：面向论文写作、内部汇报和投稿核查的中文实验总览  
> 更新日期：2026-07-23  
> 证据口径：以当前正文、补充材料和 `current_claim_provenance.md` 为准

## 1. 一页式结论

本文研究工具型智能体中的一个评测盲区：环境刷新提供了新的世界信息，但不会自动授权智能体改变已经解析完成的操作对象。用户可能在刷新前已经选定实体，也可能有意把选择推迟到刷新后；这两种指令面对相同的初始状态、刷新后状态、选择器和动作，却要求相反的目标。

我们将这一指令条件化的差异称为**时序指称完整性**（Temporal Referent Integrity，TRI），并把论文定位为问题定义、受控诊断和设计原则，而不是通用 Agent 架构。核心实验结论是：

1. 本文审计的固定 benchmark 版本没有严格原生机会，而 Stable、单侧 Preserve 或单侧 Reevaluate 评分无法识别“按话语条件选择性保持或重选”的策略；成对的 changed-winner PairAcc 才能同时排除 Always-Lock 和 Always-Reevaluate。
2. 在冻结的受控任务上，Generic Structured Ledger 即使保留原指令、初始 ID、状态快照、选择器和动作信息，仍会把正确绑定且继续有效的旧目标替换为刷新后的选择器赢家。
3. Compile-then-act（CTA）和生命周期控制器显著减少这一特定替换，但低 Qwen PairAcc、其他绑定与执行错误表明它们不是通用解法。
4. 确定性 SQLite 重放把受控实验中的目标替换逐一转化为错误实体写入，闭合了“评测差异—行为错误—执行后果”的证据链。
5. CTA、类型化生命周期状态、完整历史提示和确定性话语规则的比较说明，论文支持的是“需要一个可执行的话语敏感型指称转换决策”，而不是 CTA、显式字段、特定序列化或确定性 gate 的唯一必要性。
6. ToolSandbox、AppWorld 和 tau3-bench 的固定版本中没有发现严格原生机会，低干预外部实验也没有复现受控失败。因此，现有证据不支持真实流量发生率、普遍 LLM 故障或通用安全结论。

论文的完整论证链是：

> 授权对比与可识别性要求 → 对称 matched diagnostic → 正确初始绑定后的条件替换 → 错误目标写入 → 非唯一实现与外部边界。

## 2. 研究问题

实验围绕六个问题展开：

1. **评测可识别性**：Stable、单侧或聚合准确率能否区分选择性策略与无条件锁定/重选？
2. **受控行为诊断**：控制器已经正确记录初始目标后，状态刷新是否仍会导致未授权替换？
3. **实现机制**：改善来自 mode 字段、提前规划、绑定 ID、类型化合同，还是确定性执行 gate？
4. **执行后果**：错误目标预测是否会转化为真实数据库中的错误写入？
5. **稳健性与构念效度**：结果能否跨状态簇、新 schema、模型家族、人工改写和人工 gold 敏感性分析保持？
6. **外部与组合边界**：自然工具任务是否包含严格机会，单刷新标量控制能否直接扩展到多刷新、多角色场景？

## 3. 核心任务设计

### 3.1 事件结构

每个任务由四类事件构成：

1. `Observe`：在初始状态 $S_0$ 中观察候选实体；
2. `Bind/Defer`：在刷新前绑定具体实体，或有意推迟选择；
3. `Refresh`：外部变化产生新状态 $S_1$；
4. `Write`：对授权目标执行回复、评论、更新、部署等操作。

设选择器为 $q$，刷新前赢家为 $e_0=q(S_0)$，刷新后赢家为 $e_1=q(S_1)$：

- **Preserve**：话语在刷新前已经解析目标，正确结果是保留 $e_0$；
- **Reevaluate**：话语明确要求刷新后再选择，正确结果是计算并使用 $e_1$。

这里的 authorization 指“指令规定的解析时机”，不是访问控制权限。

### 3.2 对称最小对

每个 Preserve/Reevaluate 对共享：

- 初始和刷新后状态；
- 选择器与排序规则；
- 动作和动作 schema；
- 状态变化；
- 候选实体和正确目标频率。

二者只改变话语顺序和指称表达。这使结果不能被领域难度、状态变化或目标频率解释。

### 3.3 状态变化

- **Stable**：刷新后选择器赢家不变，是检测过度反应的负控制；
- **Flip**：另一个仍有效的实体成为新赢家；
- **Name collision**：不同稳定 ID 具有相同或冲突的显示名称；
- **Remove**：旧目标被移除；
- **Invalidate**：旧目标仍存在，但不再满足动作前置条件。

Flip 和 name collision 构成主要 changed-winner 指称核心。Remove/Invalidate 需要额外的 fallback 或 Reject 规范，因此作为单独的执行策略切片，不与人类支持更强的 Preserve/Reevaluate 核心等同解释。

## 4. 控制器和对照

| 方法 | 刷新前输出 | 用途与边界 |
|---|---|---|
| Generic Structured Ledger | 初始 ID、快照、选择器、动作和前置条件 | 信息充足的直接邻近基线，但没有可执行的保持/重选状态 |
| Generic + reference mode | 在 Generic 上增加 Preserve/Reevaluate 标签 | 检验单个 mode 字段是否足够 |
| Untyped pre-refresh plan | 自由文本计划 | 检验“提前想一下”能否替代结构化合同 |
| Historical CTA | 绑定时间、ID、选择器和理由 | 简洁的刷新前承诺实现；不是论文唯一主张 |
| Lifecycle-free | mode、ID、选择器和 fallback policy，由自由 actor 执行 | 分离类型化表示和确定性执行 |
| Lifecycle-Gated | 同一类型化记录，Preserve 分支由 gate 检查并执行 | 可审计的执行实现；gate 不能修复错误 mode/ID/schema |
| Always-Lock + validity | 无条件保留旧 ID，失效时拒绝 | 一侧策略极端，不是完整 Agent 基线 |
| Always-Reevaluate | 无条件在 $S_1$ 重跑选择器 | 另一侧策略极端 |
| Ordinary full history | 保留普通完整交互历史 | 检查结果是否只是 Generic ledger 序列化诱发 |
| Final-step aware history | 刷新后提供强语义提醒 | 检查后置提醒能否恢复授权判断 |
| Deterministic Rule v2 | 基于事件顺序和 benchmark 词表的规则 | 强但 post-hoc，限制算法新颖性，不证明开放语言泛化 |

所有模型都能看到指令中的自然语言 selector，但看不到 gold target、生成器规范化 selector 字段或刷新前后 winner ID。Generic 不是删信息构造的弱基线。Historical CTA、Lifecycle-free 和 Generic 均使用两次模型调用；Lifecycle-Gated 在有效 Preserve 分支可跳过 actor 调用。

## 5. 指标、分母与统计

### 5.1 主要指标

- **端到端准确率（E2E）**：最终目标或最终状态是否与 benchmark gold 一致；
- **初始绑定准确率**：刷新前公开记录的 ID 是否等于 $e_0$；
- **PairAcc**：同一 Preserve/Reevaluate matched pair 的两条任务是否同时正确；
- **条件替换率**：在正确可观察初始绑定、刷新完成、旧目标仍存在且动作有效、刷新后赢家不同的情况下，是否改写为新赢家；
- **shared-eligible 条件替换**：只统计 Generic 和 CTA 在同一任务上都正确绑定的机会，排除控制器特定分母选择；
- **最终状态成功率**：执行后数据库状态是否完全正确；
- **错误实体写入**：动作是否真实写到非授权实体；
- **无效尝试、不必要拒绝和 collateral change**：与 wrong write 分开报告。

### 5.2 为什么不能只看总准确率

Stable 条件下，锁定和重选得到相同实体；单侧 changed-winner 条件又会奖励其中一个无条件极端。因此，高 Stable、Preserve-only、Reevaluate-only 或 Aggregate 分数都不必然代表控制器学会了选择性授权。PairAcc 要求同一状态变化下的 Preserve 和 Reevaluate 同时正确，才能排除两端极端。

### 5.3 统计与失败处理

- v3 以 20 个语言模板簇为 bootstrap 单位；
- v7 以 40 个状态簇为 bootstrap 单位；
- 主要置信区间使用 10,000 次簇级 bootstrap；
- 缺失、API、解析和协议错误按 intention-to-treat（ITT）计为失败；
- 条件替换率不是通用任务成功率，分母排除了初始绑定等上游错误；
- 零次观察到的 CTA 条件替换不代表总体风险为零。

## 6. 证据时间线

| 证据 | 状态 | 在论文中的作用 |
|---|---|---|
| v3 Generic vs Lifecycle-Gated | **primary/frozen** | 预先指定的整套控制器 package 效应；Qwen 主对比及 GLM 复制 |
| v3 组件 addenda | **post-primary；各自在调用前冻结** | free actor、validity gate、mode-only、untyped plan 和 exact CTA；不能重写为 primary 因果分解 |
| v7 core replication | **post-primary replication，调用前冻结** | 新状态、新 schema 和第三模型方向复制 |
| Matched full-history baselines | **post-primary strong baseline；自身调用前冻结** | 三模型 ordinary history 与 final-step aware history |
| PairAcc、identifiability、shared eligibility | **post-primary，zero API** | 用冻结输出重构可识别性和公平条件分母 |
| Evaluation selection regret | **post-primary，zero API** | 量化错误评分制度可能许可错误策略的后果 |
| 40-task model-facing SQLite | **secondary/frozen execution test；GLM 后续复制** | 模型实际发出 mutation 并检查最终数据库状态 |
| v7 deterministic replay | **post-primary，zero API** | 冻结 target output 的 consequence verification，不是新行为复现 |
| 三人盲标 | **post-primary construct validation** | 验证标量 Preserve/Reevaluate 语义；Reject 支持较弱 |
| 50 条 rewrite 模型运行 | **post-primary replication；自身调用前冻结** | unchanged controllers 在志愿者改写上的结果 |
| Rule v2 | **post-hoc** | 强规则基线，主动收窄方法创新主张 |
| Public-suite audits | **post-primary/descriptive** | 描述固定版本的机会覆盖，不估计发生率 |
| 外部低干预和组合压力测试 | secondary boundary evidence | 保留零结果和方法失效边界 |
| Event Graph / Executable Selector | exploratory Go/No-Go smoke | 未达冻结升级门槛，不进入主方法 |

计划中但未执行的独立自然语言真实工具 holdout、独立 public-suite recall 审计和 dialogue-aware verifier 都不是证据，不得写成结果。

## 7. 主实验：TRI-v3

### 7.1 设计

- 160 条任务；
- 20 个预先指定的语言模板分析簇，不代表从自然请求总体独立随机抽样；
- 每簇覆盖 8 个领域；
- 4 种 reference style 与 5 种 update type 平衡；
- Qwen3.5-122B-A10B 为主模型，GLM-5.1 为冻结复制；
- 温度 0，thinking disabled，最大输出 1,200 tokens；
- 预指定主估计量：整套 Lifecycle-Gated controller package 减 Generic 的簇级准确率差；组件归因依赖后续审计。

### 7.2 主结果

| 模型 | Generic | Lifecycle-Gated | 差值及簇级 95% CI |
|---|---:|---:|---:|
| Qwen3.5 | 103/160（64.4%） | 157/160（98.1%） | +54/160，即 +33.8 点；[+18.1, +50.0] |
| GLM-5.1 | 115/160（71.9%） | 160/160（100.0%） | +45/160，即 +28.1 点；[+18.1, +38.1] |

Historical CTA 为 95.0% 和 96.2%；Lifecycle-free 为 96.9% 和 98.1%。因此，原始主对比成立，但后续结果不支持把全部增益唯一归因于确定性 gate 或复杂生命周期 schema。

### 7.3 指称核心与 Reject 切片

| 模型/控制器 | 128 条 actionable core | 32 条 Reject policy |
|---|---:|---:|
| Qwen Generic | 95/128（74.2%） | 8/32（25.0%） |
| Qwen CTA | 126/128（98.4%） | 26/32（81.2%） |
| Qwen Lifecycle-Gated | 125/128（97.7%） | 32/32（100.0%） |
| GLM Generic | 93/128（72.7%） | 22/32（68.8%） |
| GLM CTA | 127/128（99.2%） | 27/32（84.4%） |
| GLM Lifecycle-Gated | 128/128（100.0%） | 32/32（100.0%） |

Reject 是作者规定的执行策略，人工一致性较弱；它不能与核心指称语义同强度解释。

### 7.4 v3 changed-winner PairAcc

| 模型/控制器 | changed PairAcc（32 对） | Stable PairAcc（16 对） |
|---|---:|---:|
| Qwen Generic | 3/32（9.4%） | 16/16 |
| GLM Generic | 7/32（21.9%） | 16/16 |
| Qwen CTA | 30/32（93.8%） | 16/16 |
| GLM CTA | 31/32（96.9%） | 16/16 |
| Qwen Lifecycle-Gated | 32/32 | 16/16 |
| GLM Lifecycle-Gated | 32/32 | 16/16 |
| Always-Lock | 0/32 | 16/16 |
| Always-Reevaluate | 0/32 | 16/16 |

两个无条件策略都能通过 Stable，却在 changed PairAcc 上归零。这是论文“评测必须对称”的最直接证据。

## 8. 独立受控复制：TRI-v7

### 8.1 设计

- 240 条 core tasks；
- 10 个未用于 v3 主实验或 schema transfer 的新 schema；
- 每个 schema 4 个独立参数化状态，共 40 个状态簇；
- Preserve/Reevaluate 各 120；Flip/Stable/Name collision 各 80；
- 显式/隐式表达各 120；
- 每个旧目标在刷新后仍存在且动作有效；
- Qwen、GLM 和 post-primary DeepSeek 三个模型家族；
- 任务、hash、停止规则和解释阈值均在对应调用前冻结。

### 8.2 核心结果

| 模型/控制器 | E2E | changed PairAcc | 条件替换 | core/all wrong writes |
|---|---:|---:|---:|---:|
| Qwen Generic | 114/240（47.5%） | 7/80 | 43/72 | 43/44 |
| Qwen CTA | 170/240（70.8%） | 31/80 | 0/71 | 0/8 |
| GLM Generic | 168/240（70.0%） | 15/80 | 38/80 | 38/38 |
| GLM CTA | 226/240（94.2%） | 66/80 | 0/70 | 0/14 |
| DeepSeek Generic | 177/240（73.8%） | 17/80 | 59/79 | 59/60 |
| DeepSeek CTA | 219/240（91.2%） | 64/80 | 0/70 | 0/17 |

三点必须同时保留：

1. Generic 在三模型中都出现大量正确绑定后的 refreshed-winner substitution；
2. CTA 在严格条件分母中为 0，但仍有其他错误和 wrong writes；
3. Qwen CTA changed PairAcc 只有 31/80，说明“无条件替换被抑制”不等于任务总体解决。

### 8.3 shared-eligible 审计

| 模型 | 两控制器共同可判定任务 | Generic 替换 | CTA 替换 |
|---|---:|---:|---:|
| Qwen | 66 | 41 | 0 |
| GLM | 70 | 30 | 0 |
| DeepSeek | 69 | 50 | 0 |

该审计只保留 Generic 与 CTA 都正确暴露初始 ID 的同一批任务，说明差异不是由各控制器不同的条件分母选择造成。

### 8.4 PairAcc 差异区间

| 模型 | Generic PairAcc | CTA PairAcc | CTA − Generic，状态簇 95% CI |
|---|---:|---:|---:|
| Qwen | 7/80 | 31/80 | +30.0%，[16.2%, 43.8%] |
| GLM | 15/80 | 66/80 | +63.7%，[52.5%, 75.0%] |
| DeepSeek | 17/80 | 64/80 | +58.8%，[43.8%, 72.5%] |

## 9. 评测可识别性与策略选择后果

### 9.1 无条件策略为何会获得好分数

在 v7 上，Always-Lock 与 Always-Reevaluate 均获得 66.7% aggregate 和 100% Stable accuracy，却都只有 0/80 changed PairAcc。Generic 的 Reevaluate-only 分数为 Qwen 56.7%、GLM 95.0%、DeepSeek 100.0%，但对应 changed PairAcc 只有 7/80、15/80 和 17/80。

这证明一侧准确率可以掩盖另一侧完全失败，Aggregate 也不是天然的可识别性检验。

### 9.2 Evaluation selection regret

该 post-primary、zero-API 审计在 5 个数据集/模型候选集上，比较 Aggregate、Preserve-only、Reevaluate-only 和 Stable-only 评分会选择哪些已测试策略：

- 共 20 个 proxy evaluation；
- 所有 15 个 Stable-only 或单侧 maximizer set 都包含 changed PairAcc 为 0 的无条件策略；
- 最大 worst-case changed-PairAcc regret 为 96.9 个百分点；
- Aggregate 在 4/5 候选集中选到最佳 PairAcc 策略；
- v3 GLM 中 Aggregate 选择 Lifecycle-free，相比 CTA 损失 6.2 PairAcc 点。

该结果的正确解释是：错误的评分制度**可能许可**错误策略；worst-case tie 不代表实际使用者一定选择最差策略，候选集也不是所有可能政策的穷举。

## 10. 组件消融与非唯一实现

| 控制器/组件 | Qwen v3 | GLM v3 | 主要解释 |
|---|---:|---:|---|
| Generic | 64.4% | 71.9% | 信息存在但授权状态未落实 |
| Generic + validity gate | 65.0% | 73.1% | 单独有效性检查贡献很小 |
| Generic + reference mode | 75.0% | 75.0% | mode 有帮助，但不足以解释全部差异 |
| Untyped plan | 81.2% | 70.6% | 自由文本提前规划不稳定 |
| Historical CTA | 95.0% | 96.2% | 简洁的承诺实现 |
| Lifecycle-free | 96.9% | 98.1% | 类型化合同已解释大部分收益 |
| Lifecycle-Gated | 98.1% | 100.0% | gate 再增加 1.2/1.9 点 |

结论不是“某字段数学上必需”，而是：受控最小对需要能够访问指令历史或授权信息，并把 Preserve/Reevaluate 决策转化为可执行约束。CTA、Lifecycle 和规则都只是这一原则的不同实现。

### 10.1 强 post-hoc 规则

初始 deterministic Rule v1 在 v3 仅为 60.6%。检查失败后开发的 benchmark-aware Rule v2 达到：

- v3：148/160（92.5%）；
- 人工改写：48/50（96.0%）；
- v7：220/240（91.7%）。

其 v3 区间与 CTA 重叠，且在 v7 Qwen 上高于 CTA。因为 Rule v2 是查看失败后加入 benchmark 事件词表的 post-hoc 规则，它不能证明开放语言泛化；但它明确限制了算法新颖性，支持把贡献定位为问题定义、诊断和可执行设计原则。

## 11. SQLite 执行后果

### 11.1 40 条模型面对 SQLite 的轨迹实验

| 模型/控制器 | 最终状态 | wrong write | unneeded reject |
|---|---:|---:|---:|
| Qwen Generic | 27/40（67.5%） | 13 | 0 |
| Qwen Lifecycle-Gated | 40/40 | 0 | 0 |
| GLM Generic | 26/40（65.0%） | 8 | 6 |
| GLM Lifecycle-Gated | 40/40 | 0 | 0 |

严格条件审计中，Qwen 和 GLM Generic 分别在 8/8、6/8 个 core opportunities 中写到 refreshed winner，而两模型 Stable control 均为 0/4。其余 5 和 2 次错误写入来自 Remove/Invalidate 的 fallback policy，不被重新标记为 TRI。

### 11.2 v7 冻结输出重放

对 v7 Generic/CTA 输出进行确定性内存 SQLite 重放后，Generic 的 43、38、59 次严格 core substitution 全部成为 wrong-entity write。CTA 对应 core write 为 0，但仍分别有 8、14、17 次其他错误写入，因此重放没有把 CTA 描述成总体安全。

### 11.3 普通完整历史重放

对 Qwen、GLM、DeepSeek 的 ordinary full history 和 final-step aware history 共 1,440 个 episode 重放：

| 模型 | ordinary full history wrong writes | aware history wrong writes |
|---|---:|---:|
| Qwen | 87 | 70 |
| GLM | 79 | 46 |
| DeepSeek | 75 | 57 |

这些 history 基线没有单独可评分的刷新前绑定，因此其 anchored replacement 只能描述为无条件替换或 wrong write，不能冒充 conditional TRI。

## 12. 完整历史强基线

| 模型 | Ordinary full history | Final-step aware history | CTA |
|---|---:|---:|---:|
| Qwen | 63.3% | 69.6% | 70.8% |
| GLM | 67.1% | 80.8% | 94.2% |
| DeepSeek | 68.8% | 75.8% | 91.2% |

CTA 与 aware Qwen 的总准确率基本持平，只在 GLM 和 DeepSeek 上明显更高。完整历史结果说明 Generic ledger 不是唯一会发生目标替换的接口，但也不能单凭该结果建立内部机制因果或普遍 Agent 故障结论。

## 13. 人类构念验证与人工改写

### 13.1 设计

- 1 名未参与 TRI 设计的成年人自然改写 50 条指令；
- 另外 3 名成年人独立盲标 100 个随机化原始/改写项目；
- 仅展示 opaque IDs，不展示 condition、update type 或 gold；
- 可选答案为具体 ID、Reject 或 Clarify；
- 100 条均无缺失、重复、无效或 payload mismatch；
- 所有参与者均知情同意；提交 artifact 仅包含去标识化结果。

### 13.2 人类一致性

| 切片 | majority–gold | determinate majority–gold | unanimity | Fleiss κ / Krippendorff α |
|---|---:|---:|---:|---:|
| 全部 100 条 | 86.0% | 91.5%（94 条） | 72.0% | .708 / .709 |
| Dynamic | 98.0% | 98.0% | 96.0% | .924 / .925 |
| Anchored actionable | 86.7% | 100.0% | 63.3% | .538 / .543 |
| Anchored Reject | 55.0% | 61.1% | 25.0% | .087 / .102 |

人工证据支持单目标 Preserve/Reevaluate 核心，但不充分支持 Reject/fallback policy。论文因此把 Reject 结果降级为执行政策，而不是同等强度的自然指称语义。

### 13.3 按人类多数票重评分

在 46 条原始任务的 determinate majority 上：

- Qwen Generic/CTA：69.6% / 91.3%；
- GLM Generic/CTA：73.9% / 89.1%。

在 48 条人工改写 determinate majority 上，CTA 为 Qwen 89.6%、GLM 93.8%。

### 13.4 50 条人工改写模型实验

| 模型 | Generic | CTA | Lifecycle-free | Lifecycle-Gated |
|---|---:|---:|---:|---:|
| Qwen，benchmark gold | 60.0% | 90.0% | 88.0% | 90.0% |
| GLM，benchmark gold | 74.0% | 98.0% | 92.0% | 94.0% |
| Qwen，human majority | 60.4% | 89.6% | 83.3% | 85.4% |
| GLM，human majority | 68.8% | 93.8% | 83.3% | 85.4% |

该实验支持“预刷新承诺编译在志愿者改写上仍有效”，不建立 CTA 对类型化变体的显著优势，也不是独立自然任务 elicitation。

## 14. Schema transfer、重复稳定性与方法升级

### 14.1 未见 schema transfer

80 条 transfer task 覆盖项目管理、费用审批、库存和云部署等 4 个新领域、20 个模板簇：

- Qwen Generic：46.2%；
- Lifecycle-Gated：82.5%；
- 差值：+36.2，[+25.0, +47.5]。

post-primary oracle decomposition 显示 mode 仍为 80/80，但 Preserve bound ID 只有 21/40；将 bound ID 替换为 oracle 后 Gated 从 66/80 升到 78/80，而只替换 mode 无改善。主要 transfer 瓶颈是初始 selector grounding，不应算作 TRI。

### 14.2 温度零重复稳定性

在冻结的 40-task v7 子集上，Qwen 和 GLM 的 Generic/CTA 各有三轮：

- CTA−Generic 方向六次均为正；
- CTA 在所有可判定机会中仍为 0 conditional drift；
- 逐任务目标三轮一致率仅为 Qwen Generic/CTA 70.0%/72.5%，GLM 85.0%/97.5%。

冻结结论为 **MIXED**：方法方向稳定，但 temperature 0 不等于端点逐任务完全确定。

### 14.3 新方法 Go/No-Go

20-task 探索性 closed loop 测试 Event Graph（M1）和 Executable Selector（M2）：

- Qwen：M1 9/20，M2 15/20；
- GLM：M1 20/20，M2 18/20；
- M2 未达到两个模型 schema/selector ≥95%、不低于 CTA 超过 2 点及方向一致的冻结门槛。

结论为 **No-Go**：不把更复杂的新方法提升为主方法，继续以 Exact CTA 作为简洁 probe。该 20-task matrix 是方法选择 smoke，不是正式效应量。

## 15. 最近邻 Binding Drift 边界实验

Binding Drift 已覆盖“正确初始绑定后发生替换”。TRI 的新增变量是“这次替换是否被指令中的解析时机授权”。因此：

- Entity Lock 对应 Always-Lock，只能覆盖 Preserve；
- re-verification 若无条件在新状态重解 selector，只能覆盖 Reevaluate；
- Binding Drift 的 gold-target re-verifier 是 oracle，不是 learned baseline；
- TRI author adaptation 不是官方 Binding Drift 分数。

在 240-task v7 GLM author adaptation 中：

| 方法 | 总准确率 | Preserve | Reevaluate | pair success |
|---|---:|---:|---:|---:|
| Entity-lock analogue | 160/240 | 120/120 | 40/120 | 40/120 |
| GLM self-reverify adaptation | 155/240 | 39/120 | 116/120 | 38/120 |
| Frozen CTA | 226/240 | 110/120 | 116/120 | 106/120 |
| Rule v2（post-hoc） | 220/240 | 110/120 | 110/120 | 100/120 |

但 adapted verifier 只看到指令和 $S_1$，看不到 $S_0$ 或解析后的旧 ID，因此该结果是接口审计，不是与 CTA 信息匹配的性能比较。论文的公平强基线仍是 Generic ledger 和 matched full-history 条件。

## 16. 外部环境与公开 benchmark 边界

### 16.1 24-task ToolSandbox-compatible pilot

这是自定义任务和注入 transition 的外部工具基底实验，不是官方 ToolSandbox 分数。方法排名在 Qwen 与 GLM 间反转，Gated 仍产生 wrong writes。post-hoc 严格审计得到：

- GLM Generic：3/6 个 eligible Flip 发生替换，Stable 0/2；
- GLM Lifecycle-free：0/5；
- Qwen Generic：0/6；
- Qwen Lifecycle-free：2/6，deterministic gate replay 为 0/6。

该结果只提供小规模、post-hoc 的 benchmark-compatible 正例，不能作为确认性外部复现或发生率估计。

### 16.2 冻结 96-task ToolSandbox-style extension

四个 paper-facing 条件中，严格 post-binding substitution 均为 0：

- Qwen/GLM full history：0/70、0/73；
- Qwen/GLM matched Generic：0/64、0/87。

这些运行仍有 wrong writes，但均来自初始 selector、grounding、tool-name 或流程错误。该零结果反对“任何模型或工具循环都会发生 TRI”的普遍主张。

另有一个 Qwen-only `generic_state_observed` 探索性条件：0/73 substitution、6 次 wrong write，
但包含 13 个 prohibited-schema/process errors，且没有 GLM 匹配条件。其原始输出和报告继续
保留在 artifact 中，但不计入上述四个 paper-facing 条件，也不与其合并以强化零结果。

### 16.3 固定公开版本的机会审计

| Suite | 审计单位 | 严格原生机会 | near-match / 轨迹结果 |
|---|---:|---:|---|
| ToolSandbox | 129 个语义任务家族 | 0 | 1 个 near-match |
| AppWorld | 244 个生成家族、732 个实例 | 0 | 1 个 family；16 次 post-binding comment 均保留同一 ID |
| tau3-bench | 2,449 个任务、10,832 条公开轨迹 | 0 | 8 个不同角色的 near-match，不构成同角色替换 |

该审计是 post-primary descriptive coverage audit，没有独立候选召回率或双人一致性，不得写成“公共 benchmark 普遍失效”或“真实任务中不存在 TRI”。

### 16.4 Custom AppWorld 与低干预 addendum

- 两 app、两模型的 custom study：24 个正确及时绑定中 conditional substitution 为 0/24；唯一 wrong write 发生在刷新后才绑定，属于 tool-order error；
- 去掉显式 binding sidecar 和 TRI 术语的低干预 addendum：0/28，包括 Preserve/Flip 0/6；两次 wrong write 均因模型在首次 selector call 前先同步，属于 pre-binding temporal-order error。

因此，受控失败尚未在冻结低干预自然语言工具循环中得到阳性复现。当前无法区分 public benchmark undercoverage、作者 checklist 漏检和受控接口放大效应。

## 17. 组合性负结果

### 17.1 两刷新、多指称压力测试

40 条 Qwen SQLite 任务包含两次刷新、监控 referent、无关工具调用和最终 mutation：

- Generic：32/40 final states，1 wrong write；
- Scalar Lifecycle：28/40，6 wrong writes，1 parse/internal error；
- Lifecycle−Generic：−10.0 点，簇级区间 [−35.0, +12.5]。

Scalar Lifecycle 的 mode 只有 25/40，说明单一记录混淆了 monitoring referent 与 action target。该结果不是对 TRI 原理的否定，而是现有标量实现的组合边界。

### 17.2 Role-indexed addendum

在 4 个 unseen schema、40 条 held-out task 上：

- Qwen scalar 35/40，role-indexed 39/40；
- GLM ITT scalar 40/40，role-indexed 37/40，后者含 3 个 transport failures；
- 串行 recovery 后 GLM 两者均为 40/40。

Role indexing 值得继续研究，但没有形成跨模型稳定优势。论文因此把结论限制在 controller-orchestrated、single-refresh、scalar mutation。

## 18. 证据闭环与研究价值

| 审稿问题 | 对应证据 | 得出的有限结论 |
|---|---|---|
| 这只是“记住 ID”吗？ | Always-Lock 与 Always-Reevaluate 的互补失败 | 必须识别何时保持、何时重选 |
| Generic 是否故意删信息？ | Generic 保存 ID、snapshot、selector、action、preconditions | 错误不是简单信息缺失 |
| Stable 或总准确率是否足够？ | PairAcc、identifiability、selection regret | 单侧评价可能许可零 PairAcc 策略 |
| 是否只是某模型/模板偶然？ | v3 两模型、v7 三模型、新 schema、人工改写、重复运行 | 受控方向具有模型/控制器条件下的稳健性 |
| 错误是否真的有后果？ | 模型面对 SQLite 和 deterministic replay | 条件替换可直接成为 wrong-entity write |
| CTA 是唯一办法吗？ | Lifecycle、history、Rule v2、组件消融 | 否；支持实现无关的分离原则 |
| 人类认同 gold 吗？ | 三人盲标和多数票重评分 | 支持 scalar core；Reject 较弱 |
| 自然任务中普遍发生吗？ | 外部零结果和 public coverage audit | 未建立；外部成立性仍是主要边界 |
| 标量方法能组合吗？ | v5/v6 组合测试 | 尚不能稳定组合，需要角色化表示 |

这使论文形成一个完整但有边界的 evaluation/diagnostic 闭环：它不依赖把 CTA 包装成复杂算法，也不依赖声称真实世界中 TRI 高频发生；研究价值来自发现一个可形式化、可区分、会改变策略选择并能产生执行后果的评测变量。

## 19. 论文必须保留的不利结果

以下结果是可信度的一部分，不应在压缩正文时删除：

1. Qwen v7 CTA changed PairAcc 只有 31/80；
2. Qwen aware-history 与 CTA 总准确率基本持平；
3. Rule v2 达到 v3 92.5%、rewrite 96.0%、v7 91.7%，且为 post-hoc；
4. 96-task ToolSandbox-style extension 的四个 paper-facing 条件均为零替换；额外 Qwen-only 条件仅作探索性披露；
5. Custom AppWorld 为 0/24，lower-intervention addendum 为 0/28；
6. Generic 在两刷新压力测试中为 32/40，高于 Scalar Lifecycle 的 28/40；
7. Reject slice 的人类一致性明显较弱；
8. temperature-zero 重复方向稳定，但逐任务输出一致性不完整；
9. CTA 的 zero core substitution 不消除其他 wrong writes；
10. public-suite coverage audit 没有独立 recall 校准。

## 20. 最终可支持和不可支持的主张

### 可以支持

- 本文审计的三个固定 benchmark 版本没有严格原生机会，且 Stable/单侧评分不能识别 resolution timing；
- Stable 或单侧评分无法识别选择性 referent-transition policy；
- matched changed-winner PairAcc 能同时排除 Always-Lock 与 Always-Reevaluate；
- 在冻结受控接口上，Generic controller 会在正确初始绑定后发生 controller-conditional substitution；
- 该 substitution 可以转化为真实错误实体写入；
- CTA、Lifecycle 和规则说明 world evidence 与 referential authorization 可以被操作性分离；
- public benchmark 固定版本对严格机会的覆盖有限，外部正例仍未建立。

### 不可以支持

- TRI 是真实 Agent 中普遍或高频的故障；
- 所有 LLM、所有工具循环或所有 public benchmark 都存在该问题；
- CTA 是唯一、数学上必要或通用最优的解法；
- 显式 `reference_mode`、某个字段或某种序列化不可替代；
- CTA 已建立一般安全性或消除所有 wrong writes；
- Rule v2 证明开放语言泛化；
- public-suite 零机会等价于真实世界零发生率；
- human validation 已验证 Reject/fallback policy；
- author adaptation 是 Binding Drift 官方结果。

## 21. 复现与证据索引

### 21.1 关键源文件

- 主论文：[`paper/AnonymousSubmission2027.tex`](../paper/AnonymousSubmission2027.tex)
- 补充材料：[`paper/supplementary_material.tex`](../paper/supplementary_material.tex)
- claim-to-artifact map：[`current_claim_provenance.md`](../experiments/tri_artifact/reports/current_claim_provenance.md)
- paper-facing experiment registry：[`current_experiment_registry.md`](../experiments/tri_artifact/reports/current_experiment_registry.md)
- v3 protocol：[`TRI_v3_preregistered_protocol.md`](../experiments/tri_artifact/reports/TRI_v3_preregistered_protocol.md)
- v7 protocol：[`TRI_v7_core_replication_protocol.md`](../experiments/tri_artifact/reports/TRI_v7_core_replication_protocol.md)
- PairAcc：[`matched_pair_consistency.md`](../experiments/tri_artifact/reports/matched_pair_consistency.md)
- identifiability：[`v7_identifiability_regimes_v1.md`](../experiments/tri_artifact/reports/v7_identifiability_regimes_v1.md)
- selection regret：[`evaluation_selection_regret_v1.md`](../experiments/tri_artifact/reports/evaluation_selection_regret_v1.md)
- v7 shared eligibility：[`v7_shared_eligible_pairacc_v1.md`](../experiments/tri_artifact/reports/v7_shared_eligible_pairacc_v1.md)
- SQLite consequences：[`v3_two_model_sqlite_trajectory_report.md`](../experiments/tri_artifact/reports/v3_two_model_sqlite_trajectory_report.md)
- external boundary：[`TRI_external_validation_v1_summary.md`](../experiments/tri_artifact/reports/TRI_external_validation_v1_summary.md)
- human validation：[`human_validation/analysis.md`](../experiments/tri_artifact/human_validation/analysis.md)
- main evidence audit：[`main_paper_evidence_audit_v1.md`](../experiments/tri_artifact/reports/main_paper_evidence_audit_v1.md)

### 21.2 关键验证命令

在 `experiments/tri_artifact/` 下：

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/pytest -q tests
PYTHONPATH=. python scripts/audit_main_paper_evidence.py
PYTHONPATH=. python scripts/audit_manuscript_consistency.py
```

在 `paper/` 下：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error AnonymousSubmission2027.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_material.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error ReproducibilityChecklist.tex
```

最终 artifact 必须保留 frozen JSONL、原始输出、protocol、hash、报告脚本、SQLite replay、tests 和匿名扫描；private consent、原始参与者工作簿、API key、本地路径和作者身份不得进入提交包。

## 22. 最简汇报版本

如果只用一段话介绍实验，可以表述为：

> We construct matched Preserve/Reevaluate tasks that keep the states, selector, action, and refresh fixed while requiring opposite targets, and condition post-refresh substitution on a correct observable initial binding. In the frozen v3 comparison and post-primary v7 replications across Qwen, GLM, and DeepSeek, Generic ledger controllers frequently replace a still-valid bound entity with the refreshed selector winner, whereas CTA shows no such substitutions in the eligible denominators but retains other binding and execution errors. Changed-winner PairAcc rejects both Always-Lock and Always-Reevaluate, and a zero-API selection audit shows that Stable or one-sided scoring can license zero-PairAcc policies. Deterministic SQLite replay converts every observed Generic core substitution into a wrong-entity write. Human validation supports the scalar Preserve/Reevaluate distinction, while a strong post-hoc rule, negative composition tests, public-suite undercoverage, and lower-intervention null results delimit the claim to a controlled evaluation diagnostic rather than natural prevalence or universal safety.
