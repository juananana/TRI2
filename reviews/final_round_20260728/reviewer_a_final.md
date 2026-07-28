# Reviewer A 最终评审（AAAI-27 Phase 1）

## 决定与评分

- **Phase 1：Reject**
- **Overall score：4/10（Weak Reject）**
- **Confidence：4/5**
- **Expertise：4/5**

## 总评

本文把“世界状态更新”与“是否授权重新解析既有行动指称”分离，并用共享状态转移、选择器、动作和 schema 的 Preserve/Reevaluate 反向金标对构造 Temporal Referent Integrity（TRI）诊断。这个问题定义清楚，PairAcc 对 Always-Lock 与 Always-Reevaluate 的双向排除也是合理的。论文尤其值得肯定的是证据纪律：正文表 2、补充表 1/3 明确区分 primary、post-primary、post-hoc、descriptive 与 failed-gate 证据；不利结果（Rule*、外部零结果、组合失败、人工 follow-up 失败）均被保留。

但最终我仍建议 Phase 1 Reject。决定性原因不是“没有提出一个更复杂的 agent runtime”，而是：相对最近邻的新增概念与形式结果偏窄；最强行为证据集中在作者设计分布；自然语言构念、原生机会和外部迁移均没有形成稳定闭环。当前工作更像一个严谨、可复用的受控单元测试，而尚未成为具有足够广泛经验支持的 AAAI 评测贡献。

## 主要优点

1. **诊断可识别性和条件分母定义扎实。** 正文第 3 页式 (1)–(4)、表 1及补充第 4–5 页 Proposition 1–2 清楚说明 Stable-only、单边 changed-winner 与 aggregate score 的盲点。正文第 3/5 页及补充 Proposition 3 又把机会、正确初始绑定、替换和执行错误分解，避免将初始 grounding、tool order、fallback 与 TRI 混为一谈。

2. **从目标替换到错误写入有可执行证据。** 正文第 5–6 页图 2–3以及补充第 18–21 页显示，在正确初始绑定且旧实体仍可行动的受控机会中，Generic 对三个模型出现 41/66、30/70、50/69 的 shared-eligible refreshed-winner substitution，而 CTA 为 0；固定 replay 把这些替换落实为错误实体写入，40-task 模型面对 SQLite 又观察到 8/8 与 6/8 的 strict-opportunity 写入。这支持一个受控的 controller-level 行为诊断。

3. **实验 provenance 和负面结果披露优于常见投稿。** 补充第 1–2、14–19、27–33 页记录冻结状态、接口、ITT、transport repair、parser failure、重复运行和模型/环境限制；复现清单对未完整满足的项目使用 partial，而非一律 yes。版面和表图可读，没有发现遮挡或截断。

## 决定性问题

### 1. 相对最近邻的实质新增仍偏窄，形式结果接近定义性结论

正文第 2 页将 TRI 与 Entity Binding / Binding Drift 区分为：Binding Drift 固定“已经提交的 referent”，TRI 进一步改变是否授权在刷新后解析。这个边界是成立的，但新增主要是把 persistence test 对称化为 opposite-gold Preserve/Reevaluate pair，再用联合正确率计分。

补充第 11–12 页表 13 的 Binding Drift adaptation 确实显示 entity lock 偏向 Preserve、self-reverification 偏向 Reevaluate，而 CTA 在两侧更平衡；但这个 adaptation 明确不给 verifier `S0` 或已解析旧 ID，因此不是 information-matched CTA 对照，也不是官方 reproduction。它证明的是两种无条件策略按构造会失败，尚未证明 TRI 相比最近邻评测在自然 controller 候选上揭示了新的排名或决策：补充第 13 页表 17甚至显示，五个候选集中 aggregate E2E 均选到了 PairAcc-optimal candidate，观测到的 aggregate selection regret 为 0。

形式贡献也不足以弥补这一点。Proposition 1 只在确定性的 `{Always-Lock, Always-Reevaluate, Selective}`、exact-target、actionable、无 tie 的三策略类中说明至少需要一条 changed Preserve 和一条 changed Reevaluate；Proposition 2 是从错误条数推出的 sharp counting bound；Proposition 3 是 chain-rule factorization。它们都正确且限制写得清楚，但主要是对评测构造的形式化说明，不构成足够深的独立理论贡献。

### 2. 最强正结果仍依赖作者构造分布，干净干预的可归因性和迁移性有限

正文第 5 页 primary package comparison 同时改变结构和调用次数；补充第 7 页表 5显示 Lifecycle-Gated 的 Preserve 分支跳过 actor，因此 103/160→157/160 和 115/160→160/160 只能解释为 package-level 对比。补充第 15–18 页的 matched-call 实验修复了 call count/base payload 混杂，这是重要加强；但 Decision-visible 同时提供 predicted mode、bound ID 与 selector restatement，依然无法分离 timing variable、compiler quality 与 salience/representation effect。其 authored actionable E2E 对 Qwen 仅为 100/128→106/128，offline enforcement 又造成 18 repairs/8 harms；在 cross-schema matched-call 中 Qwen enforcement 反而把 PairAcc 从 20/40 降到 17/40（补充表 21、23）。

更关键的是迁移结果不稳定。补充第 22–23 页表 28–29中，30 对 source-derived tasks 上 Decision-visible 的 PairAcc 变化为 Qwen 12→13、GLM 11→20、DeepSeek 19→22，只有 GLM 的 E2E 区间排除 0；Rule* 从 authored inventory 的 92.5%/91.7% 降到 source-derived 15/60 row accuracy、2/30 PairAcc（补充第 10–11 页）。补充第 26 页 source-anchored external transfer 更显示 execution record 相对 ordinary history 对 GLM 为 **−8.75 points [−16.25,−2.5]**，对 Qwen 为 **−1.25 [−6.25,3.75]**，而真正的 Preserve substitution 只出现在 Qwen/AgentDojo ordinary-history 一格的 2/7。也就是说，诊断现象在作者构造环境中稳定，但“显式 decision record 改善行为”并未稳定迁移。

### 3. 构念有效性与自然机会覆盖仍未闭合，限制了 AAAI 广泛意义

第一轮三人便利样本对 dynamic items 的 majority–gold agreement 为 98%，但 anchored actionable 只有 86.7%，anchored reject 为 55%（补充第 29 页表 34）。这尚可支持核心、否定 fallback gold；然而单独冻结的 six-form follow-up 没有达到每题五个有效标签的 gate，11 个 eligible submissions 的 referent agreement 仅 51/132（38.6%），即使忽略 assistance exclusion 仍为 38.3%（补充第 29–30 页表 35）。作者正确地将其标为 failed-gate 而非验证，但它意味着更严格、分离 referent/execution judgment 的人工审计没有复现构念一致性。模型生成语言审计也因两名 judge 没有共同接受任何完整 pair 而失败（补充第 32 页表 39）。因此 open-language generalization 不只是“尚未扩大规模”，而是已有更强审计未能通过。

原生覆盖同样薄弱。正文第 6–7 页及补充第 23–26 页在 ToolSandbox、AppWorld、τ³-Bench、API-Bank、BFCL、ToolTalk 中找不到 strict native opportunity；96-task 低干预扩展的四个条件也全部得到零 conditional substitution。公开套件检索 recall 未经独立校准，作者也没有部署流量，因此这些零结果既不能证明 TRI 不重要，也不能证明其普遍存在。问题在于，论文目前能够证明的是“我们可以构造一个可识别且会触发错误写入的诊断”，而不是“这个诊断覆盖了足够多的自然 agent workflow，足以改变广泛评测实践”。正文第 7 页将范围限制在 single-refresh scalar workflow，补充第 27 页又显示两刷新/多 referent 下 scalar Lifecycle 反而落后 Generic（28/40 vs. 32/40），进一步限制广泛意义。

## Supplement 是否改变初判

**没有改变决定或分数：仍为 Reject，4/10。**

补充材料提高了我对以下方面的评价：实验记录完整，ITT 与修复 provenance 清楚，Binding Drift 最近邻被实际审计，matched-call 对照确实排除了调用次数和 base actor payload 的部分混杂。因此我不再担心论文主要结果来自隐蔽的失败过滤或粗糙计分。

但补充也强化了拒稿理由：Binding Drift 对照不是信息匹配比较；五个候选集没有 aggregate ranking reversal；source-derived/source-anchored 的方法收益模型依赖或为负；更严格的人类 follow-up 和模型语言审计均未通过；原生公开任务仍无 strict opportunity。综合而言，证据质量高，但证据所覆盖的科学主张仍太窄，尚不足以达到 AAAI 的新颖性与广泛影响门槛。
