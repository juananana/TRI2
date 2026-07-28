# Reviewer A - AAAI-27 Main Technical Track Phase 1 Review

Evidence reviewed: `paper/AnonymousSubmission2027.pdf` (8 pages), `paper/supplementary_material.pdf` (32 pages), and `paper/ReproducibilityChecklist.pdf` (2 pages). No other submission, review, planning, experiment, repository-history, or non-anonymous material was used.

## 1. 论文概述

本文研究工具智能体在环境刷新前后如何解析动作对象：若指令在刷新前已选定实体，则刷新后应保持该实体（Preserve）；若选择被推迟到刷新后，则应重新应用 selector（Reevaluate）。作者将二者形式化为 `bound(e0)` 与 `deferred(qr)`（正文 p.2，式 1-2），构造共享状态、selector、transition、action 和 schema、但要求相反 gold target 的匹配对，并以 changed-winner PairAcc 要求一对中两项都正确（正文 pp.2-3，表 1、式 3-4）。

论文进一步定义 conditional substitution：只在初始绑定正确、刷新成功、winner 改变、旧实体仍存在且 action-valid 时，统计控制器是否把已绑定对象替换成刷新后的 winner（正文 p.3）。作者在 authored diagnostic、跨 schema authored replication、40-task SQLite 工具回路、source-derived 对、人工改写和公开 benchmark 审计上测试 Generic、CTA、Lifecycle、history-only/decision-visible 等控制器。

最强内部结果是：在 240 个 authored cross-schema tasks 上，Generic 在 shared-eligible Preserve 行中对 Qwen/GLM/DeepSeek 分别出现 41/66、30/70、50/69 substitutions，而 CTA 为 0（正文 p.5，图 3；补充 p.18，表 25）。40-task SQLite 测试把该错误落实为 Qwen 8/8、GLM 6/8 strict-opportunity wrong writes，Stable controls 均为 0/4（正文 pp.5-6，图 4；补充 pp.19-21，图 7）。equal-call、equal-base-payload 的 Decision-visible block 也提升 authored PairAcc，尤其是 GLM（正文 p.5；补充 pp.14-15，表 21）。

但外部效度很弱：30 个 source-derived matched pairs 上只有 GLM 的 E2E interval 排除 0（正文 p.6；补充 pp.20-22，表 28-29）；96-task lower-intervention extension 为 0 substitutions；六个公开套件中未找到 strict native opportunity（正文 p.6；补充 pp.22-24，图 9、表 30）；自然语言 gold 的独立验证未完成（正文 pp.4,7；补充 pp.28-31，表 34-35、39）。因此我把本文视为“严谨但范围很窄的诊断构造”，而不是已证明具有普遍或实际选择价值的 agent evaluation advance。

## 2. 最强优点

1. **诊断变量和分母定义清楚。** 论文把 referent identity、selector reevaluation、action validity 和 fallback policy 分开，conditional substitution 的四个纳入条件能排除初始 grounding、tool order 和 validity 混淆（正文 pp.2-3；补充 p.4）。这比直接报告最终 accuracy 更能定位 post-binding replacement。

2. **匹配设计确实揭示互补策略。** Preserve/Reevaluate pair 保持任务内容与 transition 不变，changed PairAcc 对 Always-Lock 与 Always-Reevaluate 都给出 0，同时展示 marginals 的互补成功（正文 pp.3-4，表 1、图 2；补充 pp.4-5、11-12，表 15-17）。结论在限定的 deterministic exact-target policy class 内是正确的。

3. **从 target choice 到真实写入的证据链完整。** 作者没有停在离线标签：SQLite model-facing trace 显示错误 ID 被实际送入 mutation tool，且 fixed replay 对 240-task replication 的 target-to-write mapping 做了规模化一致性检查（正文 pp.5-6；补充 pp.18-21，图 6-7）。这支持“错误不仅是评分表象”的局部主张。

4. **证据边界和失败结果披露得很负责。** 主文主动承认 call asymmetry、composite intervention、Rule* post-hoc、source-derived 非 native、公开检索 recall 未校准、human evidence mixed，以及 scalar representation 不自动组合（正文 pp.4-7）。补充材料还披露 spurious selection-regret 输入遗漏、model-authored ID parser 错误、transport/source-replay 修复、failed human gate 和 post-primary chronology（补充 pp.1-2、12、16、25、28-31）。这种透明度值得肯定。

## 3. 主要问题（按严重度）

### 3.1 [Critical] 论文没有证明 TRI 在实际模型/控制器选择中是必要的

- **具体位置：** 正文 p.4 Policy Discrimination 最后一段；正文 p.6 External Coverage and Composition；补充 p.12 表 17；补充 pp.22-24 图 9、表 30。
- **影响主张：** “PairAcc 揭示 aggregate E2E 会漏掉的重要评估结论”以及该诊断对当前 agent evaluation 的实际价值。
- **类型：** significance / necessity / external validity。
- **能否靠澄清解决：** **不能。** 需要新的中心证据，而非文字澄清。
- **严重度理由：** 修正后的 selection-regret audit 明确显示，aggregate E2E 在五个完整 candidate sets 中都选到 PairAcc-optimal candidate，worst regret 为 0（补充 p.12，表 17）。Preserve-only、Reevaluate-only、Stable-only 在理论上会许可坏策略，但论文没有展示实际研究结论或系统选择因此发生错误。进一步地，六个公开套件的 strict native opportunities 为 0，96-task lower-intervention extension 也为 0 substitutions。一个诊断可以低 prevalence 仍然有效，但 AAAI main-track 的贡献需要证明它改变了一个重要结论，或提供更强的理论新意；本文目前两者均不足。

### 3.2 [Critical] 自然语言构念效度尚未建立，authored-template 成功可能主要是事件顺序 cue extraction

- **具体位置：** 正文 p.4 Construct Scope；正文 p.5 Human rewrites；正文 p.7 Limitations；补充 pp.28-31 表 34-35、38-39。
- **影响主张：** TRI gold target 的语义真实性、open-language generalization、以及高 authored PairAcc 是否代表 referential reasoning。
- **类型：** construct validity / generalization。
- **能否靠澄清解决：** **不能。** 需要预先冻结、独立、足量且通过质量门槛的自然指令完整配对标注。
- **严重度理由：** 早期三人 convenience sample 在 dynamic items 上很强（98% majority-gold），在 anchored actionable 上尚可（86.7%），但它不是足以支撑开放语言的独立 benchmark。冻结 follow-up 因 eligibility gate 失败，11 名合格参与者不足以产生任何五标签 item；其 retained labels 只有 38.6% referent-gold agreement（补充 pp.28-29，表 35），所以只能视为“没有完成验证”，不能当作正证据。一个 volunteer 的 rewrites 只有 3 个完整 actionable changed pairs（补充 pp.30-31，表 38）。model-authored audit 中两位 judge 的交集只有 11/48 rows 且没有完整 pair（补充 p.31，表 39）。Rule* 从 authored inventories 的 91.7%-96.0% 跌到 source-derived 的 2/30 PairAcc（补充 pp.9-10，表 10-11），进一步说明表面 cue、selector parsing 与真实泛化尚未分离。

### 3.3 [Major] 技术创新相对 contrast sets 与 Binding Drift 更像窄扩展，而非新的理论或方法层级

- **具体位置：** 正文 p.2 Related Work；正文 p.3 Restricted identifiability observation、式 4；补充 p.4 restricted proof；补充 pp.10-11 表 13-14。
- **影响主张：** originality，以及“TRI”是否是独立的新评估原理而非已有 binding persistence/contrast-set 方法的组合。
- **类型：** novelty / related-work differentiation。
- **能否靠澄清解决：** **部分可以。** 更明确的逐项对照能改善定位，但显著性仍需要实质新结论。
- **严重度理由：** 在 `{Always-Lock, Always-Reevaluate, Selective}` 内，一个 changed Preserve 与一个 changed Reevaluate 才能区分三者，直接由定义得到；PairAcc 是两个 correctness indicators 的 conjunction。匹配能控制难度，是好的实验设计，但作者也承认它对 cardinality 结论不是必要的（正文 p.3；补充 p.4）。补充中的 Binding Drift adaptation 进一步显示 entity-lock 和 self-reverify 正好是两种互补极端（补充 pp.10-11，表 13），这验证了诊断，却也表明 TRI 的新增部分主要是“把两个方向交叉成 contrast pair 并联合计分”。当前稿件尚未证明这一步带来既有方法无法获得的模型选择或科学结论。

### 3.4 [Major] 最强干预结果仍是 composite、post-primary，不能归因于 timing field 或唯一架构

- **具体位置：** 正文 pp.4-5 Controller Probes 与 Matched-Call Decision Visibility；补充 pp.6-9 表 5-10；补充 pp.14-17 表 21-24。
- **影响主张：** “显式 timing decision 改善性能”的因果解释，以及 Lifecycle/CTA 的方法贡献。
- **类型：** causal attribution / experimental design。
- **能否靠澄清解决：** **部分可以。** 论文已谨慎说是 complete block，不应再作 field-specific claim；若要 field-level 主张则需 matched-call factorial ablation。
- **严重度理由：** primary comparison 同时改变 controller、actor call count 与 deterministic gating（Qwen 103/160 到 157/160；正文 p.5）。更强的 matched-call test 虽控制 calls 和 base actor payload，却一次加入 predicted mode、bound ID 与 selector restatement（补充 pp.6-7、14-15）。单加 mode 只对 Qwen 有清晰增益，对 GLM interval 跨 0；untyped plan 的结果也不稳定（补充 pp.9-11，表 9）。Decision enforcement 在 authored Qwen 上修 18 行但伤 8 行，cross-schema 上还有 PairAcc 下降（补充 pp.14-17）。因此证据支持“某些 authored settings 中一个完整 decision block 有用”，不支持 timing field 的独立效果或通用架构结论。论文大体承认这一点，但 contribution framing 仍容易被读得过强。

### 3.5 [Major] 证据体系高度 post-primary，且多次分析/实现修复降低确认性

- **具体位置：** 正文 p.4 Evidence Status；补充 pp.1-2 表 1；补充 p.12 selection-regret correction；补充 p.16 Qwen smoke correction；补充 p.25 source replay repair；补充 p.31 parser repair。
- **影响主张：** 统计确认性与研究流程稳定性。
- **类型：** evidence chronology / reproducibility risk。
- **能否靠澄清解决：** **可以澄清但不能提升现有证据等级。**
- **严重度理由：** 唯一 primary/frozen estimand 是 call-asymmetric Qwen package contrast；cross-schema attribution、human studies、matched-call contrasts、external audits、PairAcc identifiability audits 均是 post-primary，Rule* 是 post-hoc（补充 pp.1-2）。作者透明披露了至少三个会改变汇总结果或执行有效性的修复：candidate omission 曾产生假的 aggregate regret，model-authored ID normalizer 曾产生全零结果，source smoke 因临时 checkout 消失需 replay；另有 token-cap empty content 修复。修复本身看起来有界且被记录，但整体应被视为探索性证据链，而非多个独立预注册确认。

## 4. 次要问题

1. **正文信息密度过高。** Generic、CTA、Lifecycle-free/Gated、History-only、Decision-visible/enforced、Aware、Rule* 与多个 inventory/status 在 8 页内交错，读者很难保持清楚的比较图（正文 pp.3-6）。建议主文只保留中心诊断、一个强 matched-call 对照和一个外部边界表，而不是继续增加术语。

2. **图 2 混合证据状态。** Qwen primary/frozen、GLM post-primary replication 和 Rule* post-hoc 放在同一视觉排序中（正文 p.4，图 2 caption），虽有注明，但容易产生同等证据等级的印象。

3. **PairAcc 对配对方案敏感。** 正文 p.3 承认 re-pairing 可在 marginals 不变时改变 PairAcc。当前配对规则（explicit anchor 配 implicit dynamic 等）在补充 p.11 才说明；主文应更直接解释为何该 pairing 是语义上唯一或预先冻结的合理 pairing。

4. **full-history baseline 的定位可更清楚。** Qwen 上 CTA 相对 Aware 的 interval 跨 0，而 GLM/DeepSeek 为正（补充 pp.18-19，表 26）。这说明 pre-refresh compilation 不是普遍必要条件，主文 Discussion 应更突出这一点。

5. **固定 replay 的证据增量有限。** 一旦 selected target 错误且 executor 确定，wrong write 基本由实现定义推出。真正有价值的是 40-task model-facing trace，应避免把 240-task deterministic replay 当作独立行为复制。

6. **人类研究程序需要更明确的伦理合规说明。** 参与者同意、去标识化且风险低，但没有 formal institutional review 或 exemption determination（正文 p.4；补充 p.28）。Reproducibility Checklist p.1-2 也只说明 private returns withheld。若会议政策要求人类参与研究审查，作者需说明为何无需审查或补充正式决定。

7. **模型复现受 provider 限制。** 补充 p.32 和 Checklist p.2 坦诚说明无 immutable weight revision、无 inference seed、无 provider hardware；温度 0 的 task-level outputs 仍变化（正文 p.7；补充 p.27）。因此 frozen outputs 可复核，但无法精确重跑 inference。

## 5. 给作者的实质问题

1. 能否给出至少一个 realistic/native 或 deployment-style candidate set，其中使用 TRI/PairAcc 会选择与 aggregate E2E 不同、且后续结果更好的 controller？如果仍不存在，论文的实际必要性应如何成立？

2. 对自然发生或独立写作的 instructions，作者将采用什么预冻结标注协议来分别确定 referent identity 与 execution fallback？请给出足量 complete changed-winner pairs 上的 agreement，而不是 row-level 或 failed-gate labels。

3. 相比 Binding Drift、entity-lock/self-reverification 和一般 contrast-set evaluation，TRI 唯一产生了什么新的可证伪结论？请用同一输入、gold、policy class、metric 和 failure localization 做逐项对照。

4. 为什么当前 PairAcc pairing（包括 explicit/implicit 的交叉配对）是语义上自然且不可任意重排的？若在保持每个 state-transition family 内合法的其他 pairing 下重算，方法排名是否稳定？

5. 在 matched-call setting 下，单独加入 mode、bound ID、selector restatement 及其交互的结果是什么？若不做此实验，作者是否愿意把方法主张严格收缩为“complete composite decision block on authored tasks”？

## 6. 九项分项评价

| 维度 | 等级 | 理由 |
|---|---|---|
| Originality | **Fair** | 把 resolution timing 变成 opposite-gold matched pair 有一定新意，但 formal result 很初等，且与 contrast sets、Binding Drift 的概念距离有限。 |
| Technical soundness | **Good** | 定义、ITT 计分、conditional denominator、policy controls 和错误分解基本正确；主要问题不是明显技术错误，而是结论范围。 |
| Significance | **Poor** | 五个 candidate sets 中 aggregate E2E 已选到 PairAcc optimum，六个公开套件无 strict native opportunity，未展示改变实际选择的价值。 |
| Empirical evaluation | **Fair** | authored 内部证据充分且含三模型、SQLite trace、强 baselines；但绝大多数为 post-primary，外部迁移不稳定且 native evidence 近乎为空。 |
| Construct validity | **Poor** | 早期 convenience sample 对 core 有支持，但冻结 follow-up 失败、rewrite complete pairs 仅 3、model-authored audit 无 jointly accepted complete pair。 |
| Related-work differentiation | **Fair** | 已包含 Binding Drift adaptation 和 persistence/reverification controls，但更像展示互补极端，尚未建立 substantial advance。 |
| Clarity and self-containment | **Fair** | 写作精确且限制披露充分，但术语、controller variants、denominators 与 evidence statuses 过密；关键 operational detail 依赖 32 页补充。 |
| Reproducibility | **Good** | 提供 frozen inventories、literal prompts、hashes、raw outputs、tests 与 chronology，Checklist 也较坦诚；但 provider 无 immutable revision/seed，且多次修复增加复跑风险。 |
| Ethics and responsible reporting | **Fair** | 去标识、同意、补偿非 contingent、AI 使用披露较好；但人类研究无 formal review/exemption determination，需要合规解释。 |

## 7. 总体评分与 Phase 1 决定

- **Overall score: 4/10 - Weak Reject**
- **Confidence: 4/5 - High**
- **Expertise: 5/5 - Closely familiar with tool-agent evaluation, stateful benchmark design, contrast sets, and entity/reference tracking**
- **Phase 1 decision: Reject**
- **首要因素：** 提出的诊断在受控 authored tasks 上有效，但论文没有证明它在自然/原生任务中改变任何重要评估或模型选择结论；aggregate E2E 在已测试候选集中已经做出相同选择，构念与外部效度又未完成。

这不是因明显 correctness flaw 而拒绝。若把目标定位为 diagnostic/resource paper，本文的内部设计与透明度是有价值的；但以 AAAI Main Technical Track 的创新与影响标准看，目前证据更像一个经过充分审计的窄行为单元测试，而不是已建立必要性和普适性的主要技术贡献。

## 正文与补充材料关系

补充材料对理解和审计论文至关重要，而非只提供非关键细节。它补齐了：(i) evidence chronology（补充 pp.1-2）；(ii) verbatim matched-call prompts 与完整 pair（pp.6-7）；(iii) mode-only、validity gate、untyped plan、Rule*、Binding Drift adaptation（pp.8-11）；(iv) PairAcc/regret、oracle decomposition、reject slice（pp.11-13）；(v) crossed bootstrap 与 matched-call statistics（pp.13-17）；(vi) full-history baselines、source-derived source breakdown、public-suite funnels（pp.18-24）；(vii) negative composition、repeat stability、人类验证与 parser repair（pp.25-32）。

这些材料提高了对内部结论的信心，也使论文的限制更明确，但没有推翻 main-only 初判。相反，补充材料确认了决定性边界：corrected aggregate regret 为 0；source transfer 只在部分 model-source cells 为正；公开 suite strict opportunity 为 0；open-language 完整配对验证未成功；大多数关键分析是 post-primary。故最终分数仍为 4/10。

Reproducibility Checklist 与补充材料大体一致：代码/数据/提示词声称随匿名 artifact 提供，offline analysis 可重建；同时如实标注 hyperparameter search、randomness、provider infrastructure 和 significance testing 仅 partial（Checklist pp.1-2）。唯一需要额外关注的是 checklist 没有单列人类参与研究的 formal review/exemption 状态，而正文/补充明确说未取得。

## 必要性检查

**中心结论所必需、而当前缺失的证据只有两类：**

1. **决策必要性证据。** 至少一个自然或现实的完整 candidate set，显示 PairAcc/TRI 会纠正 aggregate E2E 的模型/控制器选择，并改善 target-level execution。没有这一点，论文只能主张“理论上可漏掉”，不能主张现实评估需要该指标。

2. **自然语言构念证据。** 预先冻结、独立、质量门槛通过的完整 Preserve/Reevaluate changed pairs，分别标注 referent identity 与 fallback execution，并有足量 inter-annotator agreement。没有这一点，authored-template 上的高分仍可能主要反映 event-order cue coverage。

**不是中心结论必需的实验：** 不需要再堆更多模型、更多 authored schemas、更多 deterministic replay、更多一般性 latency/cost 结果，也不需要泛泛润色。若作者坚持 field-specific 或 architecture-specific 方法主张，matched-call factorial ablation 才变为必要；若严格收缩为 composite-block diagnostic，则该消融是次要的。
