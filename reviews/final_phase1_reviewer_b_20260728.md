# AAAI-27 Phase-1 Reviewer B 评审

## 审阅范围与主文-only 初判

我先完整审阅匿名主文 `AnonymousSubmission2027.pdf`，在打开任何补充材料前记录如下初判：**Weak Accept / Advance，Overall 6/10，Confidence 4/5，Expertise 4/5**。理由是：论文把一个容易被稳定样例或单边样例掩盖的选择时序问题形式化为 matched opposite-gold 诊断，并给出了从正确初始绑定、目标替换到 SQLite 错写的完整可观测链条；但自然语言构念效度、原生任务出现率和跨环境效应均很有限，主要干预证据又分别受包级混杂和复合干预限制。

随后我完整审阅了 `supplementary_material.pdf` 与 `ReproducibilityChecklist.pdf`。补充材料增强了分母、ITT、统计敏感性、强基线和复现细节，但没有改变上述决定。

## 论文概述

论文提出 Temporal Referent Integrity（TRI）：当实体在刷新前已被绑定时，刷新世界状态本身不授权重新解析；若选择被明确推迟到刷新后，则应在新状态上解析。作者用共享状态、选择器、动作和转移、但具有相反金标的 Preserve/Reevaluate 配对，并以 changed-winner PairAcc 评价两边同时正确。实验包括作者构造的跨 schema 任务、三个模型后端、确定性极端策略、CTA/Lifecycle/Generic 等控制器、模型发起的 SQLite 写入、matched-call 对比、人工语义检查、source-derived 适配和原生机会审计。

## 最强接收与拒绝理由

| 类型 | 理由与证据 | 重要性/严重度 | rebuttal 可解决性 |
|---|---|---:|---|
| 接收 | **诊断定义清楚且有可识别性价值。** 主文 p.3 的 “Restricted identifiability observation”、Eq. (4) 与 Table 1 明确说明稳定或单边测试为何无法排除 Always-Lock/Always-Reevaluate；补充 p.4 的 Propositions 1–2 给出限制条件与 sharp bound。 | 高 | 不需要修复 |
| 接收 | **实验到受限主张的链条较完整。** 主文 p.5 RQ2/Fig. 2 严格条件化于正确初始绑定、完成刷新、winner 改变且旧目标仍可执行；主文 pp.5–6、Fig. 3 再用模型发出的 SQLite 调用显示错误会成为 wrong-entity write。补充 pp.18–21、Tables 24–25/Figs. 6–7 给出不同分母与错误分解。 | 高 | 不需要修复 |
| 接收 | **负面结果和证据状态披露异常充分。** 主文 Table 2、RQ4 与 Limitations 保留 post-hoc Rule*、外部零结果、失败的人体后续 gate 和组合失败；补充 p.2 Table 1 列明 chronology，p.10 Table 10 明示 Rule* 为 benchmark-aware post-hoc。 | 中高 | 不需要修复 |
| 拒绝 | **外部与开放语言构念效度仍弱。** 主文 p.6 RQ4、p.7 Limitations 已承认：单人改写只有 3 个完整 changed pair；公开套件没有严格 native opportunity 且 retrieval recall 未校准。补充 p.24 Fig. 9、pp.25–27 Tables 30–32 显示普通历史下仅 AgentDojo/Qwen 一小格出现 2/7 替换，多个外部设置为零；p.30 Table 35 的冻结人工后续未达 eligibility gate，p.32 Table 39 的模型生成语言没有一对同时通过两位模型判定。 | **重大** | **不能仅靠 rebuttal 修复**；需新的独立、预先冻结语言/任务证据 |
| 拒绝 | **因果归因受限。** 主文 p.4 “Controller Probes” 与 p.5 “Primary package comparison” 明示 primary 是 call-asymmetric package contrast；p.6 RQ3 的 equal-call 干预同时暴露 mode、bound ID、selector restatement，且 initial ID 已给出。补充 pp.15–16 Table 21 虽控制调用数和 base payload，但仍是 post-primary composite block；其 post-treatment stratification 也不能作 mediation。故证据支持“某个可执行决策块能改变行为”，不支持字段、CTA 或机制的独立因果效应。 | **重大** | 可在 rebuttal 中澄清措辞，**不能**分离组件效应 |
| 拒绝 | **最强基线缩小方法性和广泛影响。** 补充 p.10 Tables 9–10 显示 post-hoc Rule* 在作者库存达到 92.5–96.0%，但 p.11 Table 11 在 source-derived 上仅 15/60、PairAcc 2/30；pp.19–20 Table 26 的强 full-history/late-aware 基线中，Qwen 的 CTA–Aware 区间跨零。结果更像一个重要的评测单元与设计原则，而不是稳健的新控制器方法。 | 中等 | 可在 rebuttal 中定位贡献，不能新增普适性 |

## 方法学评价

**实验—主张对齐。** 对论文实际声称的“受控、模型和控制器条件化诊断”，证据基本对齐。作者没有把条件替换率解释成总体风险：主文 p.3 Eq. (5) 将机会率、正确绑定、替换和执行分开；主文 p.5 Fig. 2 与补充 p.18 Table 24 分别报告 E2E、initial bind、conditional substitution、wrong writes 和 Stable errors。Reject/Invalidate 也与 actionable referent core 分开（主文 p.4；补充 p.14 Table 18）。这一点是明显优点。

**基线。** Always-Lock、Always-Reevaluate、Generic、Historical CTA、Lifecycle、post-hoc Rule*、ordinary/full-history 和 late-aware 基线覆盖较全面（主文 pp.4–7；补充 pp.9–13、19–20）。问题不在“缺少一个显而易见的基线”，而在主文核心数字最醒目的仍是人工构造 Generic 与包级 CTA/Lifecycle 对比；最强历史基线和其 Qwen null 主要留在补充。它们并不推翻 PairAcc 诊断，但显著削弱“特定表示优于充分历史”的一般性。

**泄漏、调参与冻结。** 未发现把调参后结果伪装成 held-out 的明显问题。Rule* 被清楚标为看过错误后的 post-hoc，且其 source-derived 失败被保留（补充 pp.10–11）。多个 post-primary 实验声称在各自调用前冻结（补充 p.2 Table 1），原始失败、transport repair 和 ITT 行也被记录。不过这些冻结多为内部协议而非外部预注册；大量后续分析仍复用作者库存，因此应把它们视为审计/复现而不是独立确认。

**统计。** 主比较按语言模板 cluster bootstrap，跨 schema 按 state cluster bootstrap，且补充 p.15 Table 20 提供 domain/template 两轴敏感性；McNemar 仅作辅助，API/parse/missing 均按 ITT。做法总体合理。局限是大量 post-primary slice/interval 未做全局 multiplicity 调整（主文 p.4；补充 p.15），而 bootstrap 的随机性只覆盖作者生成库存中的 cluster，不覆盖自然语言、任务选择或部署分布的不确定性。小分母如 SQLite strict opportunities 的 8/8、6/8，以及改写集的 3 对，应按描述性证据理解。

**构念、内部与外部效度。** 简单 scalar 动态语义的人类支持较强（补充 p.29 Table 34：Dynamic 98% majority–gold），但 anchored actionable 仅 86.7%，Reject 为 55%；失败的后续研究不能补强金标。内部控制较好地排除了初始绑定、tool order、稳定刷新反应和拒绝策略的混淆，但“Generic 为何重解析”仍是 controller-level 行为诊断，不是模型内部机制。外部效度是最弱环节：source-derived 仍由作者设计 opposite-gold 干预，native recall 未校准，低干预外部设置多为零。作者对这些边界的表述是诚实且一致的。

**可复现性与伦理。** 补充 pp.7–8 给出 verbatim matched-call 接口和严格 parser/ITT 规则，p.33 给出模型 ID、endpoint、时间范围、输出上限和离线环境；并声称匿名 artifact 包含 frozen inventories、raw JSONL、报告脚本、hash 和测试。由于供应商无 immutable weight revision/serving hardware，精确重跑推理不可保证，但冻结输出上的分析应可复核。Checklist 对超参开发、代码注释、seed、计算基础设施和显著性检验均诚实填为 partial，而不是过度声称。人体部分有知情同意、去标识和非按结果付酬，但未取得正式 IRB/exemption determination（主文 p.4；补充 p.29）；该程序性问题值得会务确认，不过从所述低风险任务看不是我拒绝的主因。

## 必要实验过滤器

对当前严格限定的**问题定义 + 受控诊断**主张，我不认为缺少一个必须在本轮新增、否则结论无效的决定性实验。相反，论文已经用极端策略、matched calls、执行写入和负面外部审计回答了核心识别问题。因此我不会把“再加模型/基准”列为必要条件。

若作者要升级为以下任一更强主张，则相应实验才是必要的：

- 对开放语言泛化：由独立人员预先编写并由独立标注者确认的完整 changed Preserve/Reevaluate pairs；
- 对原生出现率或实际风险：具有校准召回率的 native-opportunity 抽样与可观测执行分母；
- 对某个字段/CTA 的独立因果作用：随机化组件级消融，保持 compiler、actor、调用数和提示框架一致。

这些缺口无法在 rebuttal 中用解释替代，但论文目前也没有作这些越界主张。

## 评分

- Originality / 诊断新意：**7/10**
- Technical soundness：**7/10**
- Empirical rigor：**7/10**
- Construct validity：**5/10**
- External validity：**3/10**
- Clarity：**8/10**
- Reproducibility：**7/10**
- Broad AAAI significance：**6/10**
- **Overall：6/10（Weak Accept）**
- **Confidence：4/5**
- **Expertise：4/5**
- **Phase-1 decision：Advance**

## 决定稳健性

决定为**中等稳健**，合理评分区间约为 5–7。若标准要求已在原生任务上证明广泛效应，我会降至 5；若认可“新评测单元、可识别性和严谨的负面边界”本身构成 AAAI 贡献，则为 6–7。补充材料没有造成接收/拒绝翻转：它提高了我对数字、分母和复现性的信心，同时也确认外部效度和干预归因不是靠未展示细节即可消除的问题。综合当前稿件而非任何想象中的 rebuttal，我倾向 **Advance**。
