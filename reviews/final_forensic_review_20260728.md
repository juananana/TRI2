# AAAI-27 匿名评审：Temporal Referent Integrity

## 总评

本文提出 Temporal Referent Integrity（TRI），用共享状态转移、但具有相反正确目标的 Preserve/Reevaluate 配对，诊断工具代理是否在执行前错误地重新解析已经绑定的对象。论文不是把 CTA 或生命周期记录包装成唯一架构，而是把贡献限定为问题定义、可识别性诊断和受控行为证据；这一定位是可信的。主文的论证链完整：定义与三策略可识别性、条件替换、模型发起的 SQLite 错写、复合决策块干预，以及外部和人工负结果都在正文出现。

仅阅读主文时，我的初步判断为“边缘接收/弱接收”：诊断构造清楚，分母意识和负结果披露优于通常的代理评测论文；主要疑虑是作者构造语言上的强效应能否代表自然任务，以及干预能否归因。补充材料没有推翻该判断。它显著增强了可审计性，也确认了这些边界确实存在，而非主文篇幅造成的表述缺口。

## 核心主张与状态

| 主张 | 状态 | 依据与边界 |
|---|---|---|
| 成对 changed-winner PairAcc 能在 Always-Lock、Always-Reevaluate、Selective 三种确定性精确目标策略中识别选择性重解析 | **支持** | Proposition 1 的两行最小性论证正确；结论明确限于三策略类、actionable rows 和 exact-target observation。 |
| 高总体准确率不能一般地认证正 PairAcc | **支持** | Proposition 2 的计数界 `PairAcc >= max(0, 1-M(1-A)/n)` 及 sharpness 论证成立；论文也诚实报告五个候选集中的实际 aggregate selection regret 均为 0。 |
| Generic 在作者构造的跨 schema 任务中，于正确初始绑定后经常替换到刷新后赢家 | **支持但条件化** | 共享可用行上三模型分别为 41/66、30/70、50/69，CTA 均为 0；这是控制器与任务条件下的行为，不是模型普遍机制或部署风险。 |
| 这种替换会到达实际写操作 | **支持但样本有限** | 模型面对的 40 任务 SQLite 测试中，严格机会为 Qwen 8/8、GLM 6/8，Stable 对照均 0/4；另有固定执行器把跨 schema 的目标错误确定性映射为错写。后者只是执行一致性检查。 |
| 显式决策表示改善性能 | **部分支持** | 等调用主实验中，Decision-visible 相对 History-only 的 authored PairAcc 为 Qwen 5/32→13/32、GLM 8/32→25/32。该干预同时暴露 mode、bound ID 和 selector restatement，只支持“完整复合块”的效果，不能识别单字段因果作用。 |
| 方法能迁移到外部/开放语言 | **未建立** | source-derived 仅 GLM 的 E2E 区间排除 0；Rule* 在 authored inventory 很强却在 source-derived 上仅 15/60、PairAcc 2/30；低干预外部测试多数为 0，模型作者语言没有获得双判断器认可的完整 pair。 |
| TRI 在自然任务或真实流量中常见 | **未建立且论文明确不声称** | 六套公共基准审计未找到严格原生机会，但检索召回未独立校准；没有自然流量分母。 |
| CTA、显式字段或某一序列化是唯一必要实现 | **不支持且论文明确否认** | post-hoc Rule*、历史 CTA、Lifecycle 和 full-history 结果共同表明实现非唯一；Qwen 的强 full-history 对比与 CTA 区间包含 0。 |

## 经核实的优点

1. **构造定义和误差归因干净。** 条件替换分母要求正确可观察初始绑定、刷新完成、赢家改变、旧对象仍存在且可执行；初始 grounding、tool order、invalid target、rejection 和 wrong write 分开报告，没有把所有失败重新命名为 TRI。
2. **对互补坏策略的控制有价值。** Stable-only 或单边测试确实可以奖励固定策略；PairAcc 的联合正确性比两个边际更直接。公式、Fréchet 界和风险链式分解均未发现逻辑错误。
3. **负证据和事后性披露充分。** Rule* 明确标为 post-hoc；primary、post-primary、secondary frozen、transport repair 和 failed gate 均区分；外部零结果、组合失败、Qwen enforcement harms、人工后续失败都没有被隐藏。
4. **从目标到后果的链条完整。** 论文同时给出模型发起的数据库写和固定执行器重放，并明确二者证据强度不同。
5. **呈现质量高。** 主文 8 页和补充 33 页逐页可读，公式、表格、图例未见裁切或重叠；正文 claim-to-evidence map 很有帮助。

## 已确认的主要问题

1. **外部与构念效度仍是决定性限制。** 最强结果来自作者生成的状态、模板和时序对比。更接近外部的证据明显变弱：source-derived 干预仍由作者编写；公开套件无严格原生机会；96-task 低干预扩展的四个主要条件均为零条件替换；source-anchored 正例只出现在 Qwen/AgentDojo 的 2/7 单一切片。早期三标注者结果支持动态和 anchored-actionable 核心（98.0%、86.7%），但样本很小；后续预冻结人类研究资格门失败，合格标签与作者 gold 的 referent agreement 仅 51/132。因而本文目前证明的是“一个有用的受控单元测试可以发现该行为”，不是该行为在自然代理任务中的重要性或频率。论文已基本按此边界措辞，所以这是显著的意义限制，而不是发现了未披露的反例。
2. **方法效果不能归因到某个表示或架构组件。** primary Qwen/GLM 比较既改变控制器包又改变调用数（103/160→157/160；115/160→160/160）。后续 matched-call 修复了调用数和基础 actor payload，但 Decision-visible 同时加入预测 mode、bound ID、selector 重述和“follow it”语义，且实验在给 actor `initial_selected_id` 之后开始。因此它是合法的复合 controller probe，却不是“显式字段”或 CTA 的单因素因果估计。补充中的 mode-only、validity gate、untyped plan、full-history 和 enforcement harms 进一步证实不可唯一归因。
3. **PairAcc 的实际模型选择增益尚未展示。** 理论上，一侧指标可选择到零 PairAcc 策略；但在五个实际候选集中，aggregate E2E 都选择了 PairAcc-optimal 候选，实际 aggregate-to-PairAcc regret 为 0。因此当前价值主要是诊断和错误定位，而非已证明会改变实际系统/模型选择。主文承认这一点，但它削弱了新增评测指标的经验效用论证。

## 潜在问题／需要澄清

1. **开发集与调参边界。** “在各自完整调用前冻结”不能单独排除任务模板、Generic/CTA prompt、parser 或 controller ladder 曾根据同类 smoke/development 输出调整。Checklist 4.2 也只填 partial。请明确 primary inventory 与提示的开发数据、看过的模型输出、允许的 smoke 范围，以及 Qwen primary 之前和之后各发生了哪些设计选择。
2. **人工研究治理。** 论文说明获得知情同意但没有正式伦理审查或 exemption determination。请确认这是否符合作者机构和 AAAI 对低风险人类标注研究的要求，并说明为何无需事前 determination。
3. **统计总体。** cluster bootstrap 和 two-way pigeonhole sensitivity 对固定 authored inventory 内的依赖处理合理，但区间不能自然外推到开放语言或真实工作流。建议最终版本继续把这些区间称为构造内不确定性，而不是泛化置信区间。
4. **API 可复现性。** 三个 provider model ID、参数、时间戳和 raw JSONL 已记录，但服务商没有不可变权重修订号；因此可以复现离线分析，不能保证精确重放推理结果。

## 数值与图文一致性核查

- primary 差值一致：Qwen `(157-103)/160=33.75` 个百分点；GLM `(160-115)/160=28.125`。
- matched-call authored PairAcc 差值一致：Qwen `(13-5)/32=25.0`；GLM `(25-8)/32=53.125` 个百分点。Actionable E2E 变化 6/128 和 18/128 也与 4.7、14.1 个百分点一致。
- 跨 schema 的 all-eligible 与 shared-eligible 分母没有混用：43/72、38/80、59/79 对应 Generic 自身可用行；41/66、30/70、50/69 对应 Generic/CTA 共同正确绑定行。
- 固定重放分解一致：Generic 核心 TRI 写为 `43+38+59=140`，总 wrong writes 为 `44+38+60=142`；CTA 为 `0/39`。
- 40-task SQLite 组成一致：Qwen `27+8+5=40`；GLM `26+6+2+6=40`。
- 调用总数一致：authored matched-call 为 320 个 task-model rows、640 actor outputs、320 compiler outputs，共 960；source-derived 为 540；rewrite matched-call 为 300。
- 人工 follow-up 计数一致：`36x1+12x2+24x3=132` labels；51/132=38.6%，34/132=25.8%。
- 未发现会改变结论的表—图—正文冲突。个别百分比在句中只给后一项（例如 126/128 与 127/128 后仅标 99.2%），属于轻微表达问题。

## 可复现性评价

文档层面的复现性很强：补充材料给出精确 prompt、parser 规则、ITT 处理、调用数、重试与修复记录、冻结阶段、哈希前缀、模型 ID、温度、输出上限、聚类单位、随机种子、匿名 artifact 目录和一键 evidence-audit 命令。Checklist 对 hyperparameter development、注释、随机性、硬件和统计检验诚实填写 partial。此次评审只核验了三份 PDF 的说明与内部一致性，没有执行匿名代码包，因而不能声称测试或 artifact clean-room 复现已通过。最大剩余风险是 provider 权重不可版本锁定，以及大量 post-primary 分支使独立读者需要依赖 chronology table 才能重建证据等级。

## 给作者的问题

1. 在 Qwen primary 冻结前，作者具体用什么开发任务和模型输出设计 Generic、CTA/Lifecycle 提示与 20 个语言模板？是否有任何与最终 160 行共享模板或状态生成规则的调参反馈？
2. 若必须选一个最小、可部署且不依赖 gold-like scaffolding 的 controller，现有证据支持哪一个？请用完全 ordinary history、没有预供正确 `initial_selected_id` 的统一接口回答，而不是把 package 和 matched-call 结果合并解释。
3. 既然五个候选集上的 aggregate selection regret 都为 0，作者认为 PairAcc 最可能在哪类真实评测决策中改变结论？能否给出预注册、非作者构造的检验计划，而不把未来计划写成当前证据？
4. 人类研究是否取得了机构层面的“无需审查/豁免”确认？若没有，发布数据和最终论文前将采取什么合规步骤？

## 评分与建议

- **评分：5/10（Weak Accept / 边缘接收）**
- **置信度：4/5**
- **专业度：3/5**（熟悉 agent evaluation、paired diagnostics 与实验统计；不是话语语义学或人类研究伦理的专门评审）
- **Advance / Reject：Advance**
- **最终建议：Weak Accept**

理由是：本文的核心诊断定义、受控证据和后果追踪是扎实且诚实的，形式化没有发现致命问题；其新颖性主要在评测构造而非算法。外部效度、单组件归因和实际模型选择价值都未解决，但作者没有把这些空白包装成已完成结论。若会议重视严谨的失败模式诊断，我倾向让其进入下一阶段；若门槛要求自然任务上的广泛实证影响，则会落到 Borderline/Weak Reject。

## Reviewer self-check

- 先完整阅读并逐页检查主论文，记录仅主文初判，再阅读补充材料和复现清单。
- 未查看作者身份、非匿名版本、对话历史、其他评审或 reviewer 文件；未联网或调用外部 API。
- 区分了 primary、post-primary、post-hoc、secondary frozen、failed gate 与 transport repair。
- 同时核查正结果、零结果、负迁移、拒绝/无效尝试、错写和条件分母，没有把 absence of evidence 写成 evidence of absence。
- 未把控制器层行为诊断解释为模型内部机制，也未把 supplied initial ID 或 oracle decomposition 当作可部署基线。
- 数值结论均有 PDF 中的明确分子/分母支持；对开发泄漏、伦理合规和代码可运行性只提出澄清，没有作无证据指控。
