# AAAI-27 Phase 1 SPC 综合判断与修订后风险

## 评审范围与独立性

Reviewer A 与 Reviewer B 分别在互不读取对方意见的情况下完成主文初判，再读取补充材料和 Reproducibility Checklist。AI Supplementary Review 独立核查定义、数字、接口、统计边界和复现信息，不给分。SPC 综合时使用当前匿名投稿包，不使用旧评审或作者身份信息。

两名人类审稿人的原始结果：

- Reviewer A：4/10，Reject，Confidence 4/5，Expertise 5/5。
- Reviewer B：6/10，Advance，Confidence 4/5，Expertise 4/5。

这是真实的边界分歧：双方都认可内部技术正确性，分歧集中在“一个受控但窄的诊断是否已达到 AAAI Main Track 的重要性门槛”。

## 一、Phase 1 事实摘要（150-250 字）

论文把刷新前已绑定实体与刷新后才求值的 selector 区分为两种授权状态，构造共享状态、动作和 transition、但 gold 相反的 Preserve/Reevaluate 配对，并用 PairAcc 与 conditional substitution 检查选择性重解析。作者在自建任务中观察到 Generic 控制器会在正确初始绑定后替换目标，且 40 题 SQLite 回路显示该替换可造成错实体写入；复合 decision block 在部分 authored 条件中提升 PairAcc。论文未证明该现象在原生任务中的发生率，也未完成开放语言完整配对验证；source-derived 效果依模型而异，五组候选中 PairAcc 未改变 aggregate E2E 的最终选择。

## 二、最强录用理由

1. **诊断设计直接对应中心构念。** opposite-gold changed pairs 能排除 Always-Lock 与 Always-Reevaluate 两个互补极端，conditional substitution 又排除了初始 grounding、tool order 和 validity 混淆。
2. **错误链条从目标选择追到执行结果。** model-facing SQLite trace 证明错误 ID 被送入 mutation tool，而不是仅在离线标签上丢分。
3. **证据边界透明。** post-primary、post-hoc、复合干预、外部 null、失败的人类 gate 和不可精确复跑的 provider 条件都被保留。

## 三、最强拒稿理由

### 1. 重要性与增量决策价值未被证明

- **问题：** aggregate E2E 在五个候选集中已经选到 PairAcc-optimal controller；六个公开套件在未校准检索下没有 strict native opportunity，低干预扩展也没有 conditional substitution。
- **影响主张：** TRI 是否会改变当前 agent evaluation 的实质结论，而不只是提供更细的行为解释。
- **类型：** 证据不足 / 外部效度 / 重要性。
- **能否仅澄清：** 不能。当前修订只能准确把贡献定位为 diagnostic。
- **严重度：** Major，最可能决定 Phase 1。

### 2. 独立自然语言构念验证未完成

- **问题：** 有效 convenience sample 支持 actionable core，但冻结 follow-up 未通过 eligibility gate、没有预声明 item-level endpoint；rewrites 只有三个完整 actionable changed pairs，model-authored audit 没有被两位 judge 同时接受的完整 pair。
- **影响主张：** authored-template 高分是否代表一般 referential reasoning，而不是事件顺序 cue coverage。
- **类型：** 构念效度 / 外部效度。
- **能否仅澄清：** 不能；本轮已把 failed follow-up 明确标为 descriptive、非 validation。
- **严重度：** Major。

### 3. 新颖性容易被读成 contrast-set 与 persistence test 的窄组合

- **问题：** 两行最小性在限定三策略类中近乎由定义推出，PairAcc 是共正确率；论文需要让读者理解新增科学价值是授权方向的 crossed evaluation unit 和 post-binding localization，而不是新术语本身。
- **影响主张：** 是否达到 AAAI Main Track 的 originality 门槛。
- **类型：** 创新不足 / 表达问题。
- **能否仅澄清：** 部分可以。本轮已强化与 Binding Drift 的边界，但实质显著性仍取决于审稿人判断。
- **严重度：** Major。

## 四、正文与补充材料关系

- **仅正文能否评审：** 能完成中心定义、主结果和边界判断；正文现在明确给出诊断而非架构主张、五类证据的分工及复合干预边界。
- **只在补充中的重要信息：** 完整 prompts/parser、证据 chronology、component ladder、full-history baselines、pairing 细则、source-specific slices、failed human gate 全部统计、修复记录、repeat/composition 和 provider provenance。
- **补充是否改变初判：** 没有改变方向。它提高内部可信度，同时确认外部效度、构念验证和确认性证据的边界。
- **是否由补充替正文承担核心论证：** 修订前部分存在；修订后正文能独立看到核心链条，但复合干预的可复核细节和强 baseline 仍依赖补充。这在页限内可接受，但仍是审稿风险。

## 五、必要性检查

真正可能改变评分的新增证据只有：

1. 一个预先冻结、独立作者/标注者、质量门通过的自然语言完整 changed-pair 研究；
2. 一个现实或原生 candidate set，显示 TRI 发现会改变评估结论或揭示 aggregate E2E 无法定位的执行风险；
3. 若坚持单字段因果主张，再做 matched-call factorial ablation；当前论文已收缩为 composite-block claim，因此不是录用必要条件。

不建议再增加一般性模型、authored schema、固定 executor replay、普通 latency 表或无中心假设的新 benchmark。它们不会解决当前决定性问题。

## 六、评分（修订后模拟）

- **Overall Score：5/10**
- **Confidence：4/5**
- **Expertise：4/5**
- **Phase 1 Decision：Reject（真正边界）**
- **Decision Robustness：Low**

理由：写作和交付问题已显著减轻，技术正确性足以支撑 5-6 分；但重要性、native occurrence 和独立语言构念仍是当前版本无法通过文字消除的中心风险。由于 Reviewer B 已给出 6/10 Advance，早拒决定并不稳健，另一组评审完全可能让论文进入 Phase 2。

## 七、最可能出现的真实审稿意见

### Summary

The paper introduces TRI, a matched diagnostic for whether an agent preserves a referent committed before refresh while reevaluating a selector deferred until afterward. The construction is technically coherent, and the execution trace usefully separates initial grounding, post-binding substitution, and wrong-entity mutation.

### Strengths

- Clean opposite-gold matched design with appropriate unconditional policy controls.
- Careful conditional denominator and model-facing SQLite evidence.
- Unusually transparent evidence chronology, negative results, and scope boundaries.

### Weaknesses

- The strongest positive evidence remains author-constructed; native occurrence and open-language validity are unresolved.
- PairAcc does not change aggregate-E2E selection in the studied candidate sets, weakening practical necessity.
- The matched-call intervention is a composite mode/ID/selector block and cannot support field-specific or architectural claims.
- The novelty over contrast sets and binding-persistence evaluation may be viewed as incremental.

### Questions

1. What empirical outcome would falsify the actionable Preserve/Reevaluate gold under independent natural-language annotation?
2. Can the authors identify a realistic evaluation decision that TRI changes or uniquely diagnoses?
3. Is every claim about the intervention explicitly restricted to the complete composite block after initial ID exposure?

### Overall Assessment

This is a careful and potentially useful diagnostic paper, but the current evidence establishes a controlled unit test more strongly than a broadly consequential evaluation advance. I am near the boundary and would reject at Phase 1 mainly on significance and external validity, not technical correctness.

### Score and Confidence

Score: 5/10. Confidence: 4/5.

## 八、给作者的风险提示

- **最可能导致 Phase 1 Reject 的一个问题：** 审稿人认为“内部诊断有效”不足以证明对 AAAI 广泛社区有足够影响，因为 native opportunity、ranking change 和开放语言验证都未建立。
- **最可能被另一位审稿人误解的地方：** 把 `0 conditional substitutions` 读成总体安全或零 wrong writes；实际 CTA 仍有 non-core wrong writes，指标是条件诊断率。
- **投稿前最值得修复的一项内容：** 已完成——把贡献固定为 diagnostic、把五类证据分工写进正文，并把 matched-call 统一为 composite decision-block claim。

## 本轮作者视角修订

1. 摘要和 Conclusion 将 `composite timing block` 统一为 `composite decision block`。
2. Introduction 明确“diagnostic rather than architectural”，并把贡献重写为诊断定义、受控现象与执行后果、操作实现与外部边界。
3. Related Work 明确 TRI 不是另一种 persistence defense，而是同时交叉两种 authorization direction。
4. Methods 增加五类证据各自回答什么问题的导航段，减少 primary/post-primary 与多 controller 混读。
5. Construct Scope 明确 failed follow-up 没有产生预声明 endpoint，38.6% 仅是 descriptive，不是 validation。
6. matched-call 小节改名为 `Composite Decision-Block Test`，Discussion 明确其不是 field-specific 或 unique-architecture evidence。
7. Discussion 解释 PairAcc 的价值是排除互补固定策略和定位执行失败，不要求每个候选池产生 ranking reversal。
8. Reproducibility Checklist 将 theoretical-contribution 回答从非法 `NA` 改为 `yes`，并把所有答案恢复为模板允许的单一选项。
9. 更新两项自动审计的旧图注匹配和 human-boundary 匹配；相关窄测试全部通过。

## 最可能的最终结果

- **模拟结果：Borderline Reject**
- **主观概率区间：进入 Phase 2 / 最终录用约 30%-50%**

该区间只是基于本次 4/10 与 6/10 分裂评审及修订后 5/10 SPC 判断的主观不确定性，不是真实 AAAI 录用概率。

## 修改优先级

### 必须在投稿前修复

- 保持当前 diagnostic-only claim，不回退到 unique architecture、universal failure 或 prevalence 叙事。
- 确认匿名 artifact 的 headline audit、manuscript audit 和 checklist 与最终 PDF 完全一致。
- 核实人类参与研究是否满足 AAAI 政策；当前没有 formal review/exemption determination 是合规风险。

### 可利用现有证据完成

- 保持修订后的 evidence map、Binding Drift 边界与 failed-gate 解释。
- 在投稿摘要/关键词/系统字段中使用与正文一致的窄贡献描述。
- 清晰区分 240-task fixed replay 与 40-task model-facing loop。

### 需要新增分析

- 若时间允许，仅做现有 frozen rows 的合法 pairing sensitivity，并明确 cluster bootstrap 保留完整 pair；不增加模型调用。

### 需要新增实验

- 独立、监控、预冻结的自然语言完整 paired validation。
- 有现实选择后果的 native/deployment-style candidate set。

### 不建议为了迎合审稿人而修改

- 不制造 MECE 相关工作分类、triple challenge 或模块化新算法故事。
- 不删除外部 null、Rule*、failed gate、negative composition 或 aggregate-selection null。
- 不增加与中心主张无关的模型/数据集数量。
