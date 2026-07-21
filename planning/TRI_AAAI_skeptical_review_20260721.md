# AAAI 模拟审稿：创新性、合成性与 Binding Drift 重合

审稿日期：2026-07-21

## 一句话结论

当前版本是一篇证据管理较严谨、问题切分清楚的受控诊断论文，但不是强方法论文；其
AAAI 竞争力主要取决于审稿人是否认可“Binding Drift 的 Preserve 问题扩展为对称的
Preserve/Reevaluate 授权问题”足以构成独立贡献。

## 论文实际上完成了什么

论文构造了共享 $S_0$、$S_1$、selector 和 action、但因话语时序而要求相反目标的
Preserve/Reevaluate 对照，证明只看刷新后状态的 mode-blind controller 不可能同时正确；
随后在合成任务上比较 structured ledger、完整历史、pre-refresh CTA、typed lifecycle 和
规则控制器，显示显式执行转移授权可减少正确初始绑定后的目标替换。SQLite replay、三模型
复现和人工语义判断支持该受控现象；公共基准审计和组合压力测试则明确限制外部有效性。

## 最强拒稿攻击

### P0：创新性可能不足

Binding Drift 已直接研究“step 1 正确绑定后，后续工具步骤静默换实体”，并比较 Entity
Lock 与 LLM re-verification。TRI 明确承认 Preserve 分支实质重合，这是必要的诚实，但也
意味着“发现 binding drift”不再是本文贡献。剩余创新是把用户授权的 Reevaluate 加入同一
matched transition，形成对称决策并给出 mode-blind impossibility。该增量是否足够，取决于
审稿人是否把它视为新的控制变量，还是对已有 lock/reverify 问题的自然补全。

当前最小防御已经正确：不要声称 disjoint/first；把问题贡献精确写成“symmetric transition
authorization diagnostic”；保留与 Binding Drift 的信息矩阵和非信息匹配适配限制。提交前
不应再用新术语扩大新颖性主张。

### P0：合成基准可被后验规则高分解决

post-hoc rule v2 在 v3/v7 达到 92.5/91.7%，在人类改写上达到 96.0%。这排除了“必须使用
复杂 Agent memory/runtime”的叙事，也引入了更严重的替代解释：当前基准可能主要测试有限
事件顺序词汇。由于无法获得真正独立的新写作者与盲标注者，论文不能证明 CTA 比规则更能
泛化到开放语言。

当前最小防御已经正确：摘要披露 92.5%；正文明确 post-hoc/benchmark-aware；不把 volunteer
rewrite 错称为 prospective holdout；结论降为 problem definition、controlled diagnosis 和
executable design principle。此风险无法靠更多同模板或 LLM 改写实验修复。

### P0：外部有效性不足

ToolSandbox、AppWorld 和 tau3 的原生严格机会为零；custom pilots 混合或为 null。因而论文
不能证明现象在真实 agent traffic 中常见，也不能证明 CTA 在自然工作流中总体提高安全性。
SQLite 只证明受控错误可产生真实数据库副作用，不证明现实频率。

验收标准：摘要、贡献、讨论和结论必须持续使用 controller/model-conditional、coverage gap、
not prevalence/general safety。当前版本基本达到；不得在 rebuttal 或补充材料中重新放大。

## 重大但非致命问题

1. **方法深度有限。** CTA 本质上是 pre-refresh 解析 ID，Lifecycle 是 typed record 加 gate，
   rule 是事件顺序程序。强点是问题和诊断，不是算法复杂度。标题、摘要和贡献应继续围绕问题
   与授权分离，而不是“提出新 runtime”。
2. **人类验证边界。** 三名标注者验证了 scalar Preserve/Reevaluate，但 Reject agreement 低；
   因此 fallback policy 是规范性设计，不是被人类数据充分支持的自然语义。当前正文已区分。
3. **机制证据是控制层行为，不是模型内部机制。** Generic 失败与 state--authorization confusion
   一致，但不能推出模型内部如何表示 referent。当前措辞必须保留 “behavioral/controller-level”。
4. **Qwen v7 CTA 总体表现弱。** post-hoc rule 明显高于 Qwen CTA，且 CTA 对强 late prompt 的
   总体差异接近零。这否定 universal superiority，但不否定 conditional-drift diagnosis。
5. **复现稳定性有限。** temperature-zero 的逐题 unanimity 不高。论文正确报告 aggregate paired
   direction 与 endpoint nondeterminism；不应把一次运行当确定性属性。

## 主要优点

1. matched Preserve/Reevaluate pair 真正排除了 world transition、selector 和 action 差异，论证
   链比普通 benchmark gain 更干净。
2. mode-blind impossibility proposition 精确说明需要的是 discourse-sensitive decision，而不是
   某个特定字段或 CTA 序列化。
3. 分母管理严格：E2E、initial binding、conditional TRI、wrong write、reject 分开报告。
4. 强负面证据没有隐藏：规则基线、Qwen tie、公共基准零机会、组合失败和 repeat instability 均
   进入正文。
5. artifact 包含冻结协议、原始输出、报告程序、去标识化人工数据和测试，复现质量高于平均水平。

## 模拟评分

| 维度 | 1--10 | 依据 |
|---|---:|---|
| 问题重要性 | 7 | wrong-entity mutation 真实重要，但现实发生率未建立 |
| 原创性 | 5 | Reevaluate 对称化有价值；Preserve 与 Binding Drift 高度重合 |
| 技术正确性 | 7 | 形式化与分母清楚，主张经过收缩；没有强理论或端到端保证 |
| 方法深度 | 4 | CTA、typed state、gate 和规则均较简单 |
| 实验严谨性 | 7 | matched design、cluster bootstrap、强基线和负结果完整 |
| 机制/因果证据 | 5 | 支持控制层解释，不能证明内部模型机制或唯一因果组件 |
| 基线充分性 | 8 | full history、late authorization、rule、extreme policies、ledger 齐全 |
| 一般化能力 | 4 | 主要为合成 scalar single-refresh；公共外部证据弱 |
| 可复现性 | 8 | 原始 rows、协议、代码、测试、匿名 artifact 完整 |
| 写作与结构 | 8 | 主张边界清楚，信息密度高；结果段仍较密集 |
| AAAI 整体竞争力 | 5 | Borderline / Weak Reject，取决于 reviewer 对问题贡献的认可 |

## 模拟决定

- 推荐：**Weak Reject / Borderline**
- 非官方总分：**5/10**
- 信心：**4/5**
- 当前版本主观接收概率：**20--35%**。假设分到熟悉 agent evaluation/tool safety 的审稿人；
  若审稿人把 Binding Drift 视为已覆盖核心问题，区间更低。
- 完成当前非实验硬化后的概率：**25--40%**。提升来自消除引用、数字、匿名性和过度主张风险，
  不是改变基础创新性。
- 没有 prospective human holdout 时，不应给出更高概率；剩余不确定性主要是 novelty judgment。

## 三名模拟审稿人

### R1：创新性与问题价值

优点：对称 minimal pair 使“刷新事实”和“重绑授权”的区别很清楚。质疑：Binding Drift 已研究
最有安全意义的 Preserve failure，Reevaluate 可能只是自然补充；CTA 不是强方法。评分 4/10，
信心 4，Reject。

### R2：实验、统计与复现

优点：cluster-level statistics、冻结协议、raw rows、分母和 negative results 罕见地完整。质疑：
benchmark-aware rule 和有限写作者说明语言多样性不足；公共 benchmark audit 不能替代自然任务
验证。评分 6/10，信心 4，Weak Accept/Borderline。

### R3：Agent 机制与实际适用性

优点：mutation-boundary enforcement 和 validity/identity 分离具有工程价值。质疑：初始编译正确是
关键前提；多 referent、身份迁移、合法重绑和开放式澄清仍未解决；full-history baseline 的失败
是 controller/model conditional。评分 5/10，信心 4，Weak Reject。

## 投稿前动作

1. 保持实验冻结；不得再做同模板、同 provider 或 LLM-only paraphrase 扩展。
2. 完成所有 2025--2026 primary-source 元数据核验，并把 Binding Drift 称为 closest neighbor。
3. 完成 main-text number-to-artifact audit，任何无法一跳追溯的数字删除或移到补充材料。
4. OpenReview 摘要同步披露 post-hoc 92.5% rule；否则注册摘要比论文更强，会构成风险。
5. 重建 PDF/checklist/supplement/artifact，检查七页正文、匿名性、绝对路径、secret、manifest 和
   clean-room tests。

## 最可能改变总体判断的单一证据

真正 prospective、规则冻结后、由未接触模板的独立写作者产生并由独立标注者验证的自然语言
holdout，若 CTA 比 rule v2 高至少 10 个百分点且 writer/scenario-cluster interval 排除零，会
显著增强方法与泛化贡献。当前招募条件不满足，因此本次投稿明确 NO-GO；用作者、便利样本或
LLM 改写替代会降低而不是提高可信度。
