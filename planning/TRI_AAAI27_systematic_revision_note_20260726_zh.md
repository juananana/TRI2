# TRI AAAI-27 系统修订说明（2026-07-26）

性质：内部修改记录，不是论文证据，不进入匿名提交材料。

## 本轮结构调整

1. 论文统一定位为解析时序的 evaluation-identifiability diagnostic。CTA、Lifecycle、
   Gated 和 Rule* 均称 controller probes/executable realizations。
2. 摘要证据顺序改为 matched diagnostic、正确绑定后的定向替换、matched-call ablation、
   fixed-executor consequence、Rule* 与 external nulls。
3. 正文新增 `Evidence map and denominators`，联合报告：
   - Qwen primary/frozen 与 GLM post-primary package；
   - 160 = 128 actionable + 32 Reject；
   - v3 32 changed pairs、v7 80 changed pairs；
   - 240 rows/120 pairs 与 66/70/69 shared-eligible；
   - 80-row/40-pair matched-call ablation；
   - 六个 public suites、320 个 source-transfer attempts；
   - Rule* post-hoc。
4. Related Work 的边界表统一区分 initial binding、entity memory、temporal reasoning、
   persistence check 与 TRI matched pair。
5. Figure 3 同时显示 conditional substitution、全 240 行 E2E、total wrong writes 与
   outside-core wrong writes。
6. human validation 明确拆分 referent identity 与 Reject/Clarify/reselect execution policy。

## 删除或降级的主张

- 不将 Lifecycle-Gated 写成核心新方法或唯一架构。
- 不把 primary package contrast 解释为 component causal effect。
- 不把 Cross-Schema 称为 open-language transfer；它共享 authored templates。
- 不把 fixed-executor replay 称为独立自治执行验证。
- 不声称 PairAcc 已改变当前五个 candidate sets 的 aggregate ranking；这些集合中 E2E
  均选择 PairAcc-optimal candidate。
- 不从零 strict native opportunity 推出系统性 benchmark undercoverage 或自然 prevalence。
- 不把 Reject gold 当作与 actionable referential core 同等可靠的人类语义判断。

## 数字与分母同步

- actionable core：128；Reject slice：32；aggregate：160。
- v3 changed-winner core：32 matched pairs；v7：80 matched pairs。
- Cross-Schema：240 rows = 120 pairs；shared eligible 为 Qwen/GLM/DeepSeek 66/70/69。
- 全 240 行 Generic/CTA E2E：47.5/70.8、70.0/94.2、73.8/91.2。
- total wrong writes：44/8、38/14、60/17。
- matched-call：80 rows = 40 Flip pairs/model；PairAcc 30.0→50.0 和 30.0→60.0。
- Qwen hard enforcement：8 harms、4 repairs；保留为负面结果。

本轮没有改写冻结结果。所有新增正文数字原先已存在于 source-derived Supplement tables
或审计报告，并继续由 main-paper evidence audit 检查。

## 现有材料不足，不能加入的增强

### 独立开放语言确认集：不足

当前只有一名 volunteer 对 authored instructions 的 50 条 rewrites。它不是从语义规范
独立创作的新任务，且 Rule* 已看过相关 inventory。不能包装为 blind open-language test。

### Public-suite recall calibration：不足

现有 parser/unit tests 和模型辅助候选标签不能替代独立人工 recall audit。没有对过滤单元
的独立分层复核，也没有 blind planted-positive protocol。正文继续保留
`without independent recall calibration`。

### Confirmatory matched-call replication：不足

Qwen/GLM matched-call ablation 已完成且信息匹配，但它是 post-primary、只覆盖 authored
Flip pairs，并直接提供 observable initial ID。不能追溯性改称 primary/confirmatory，也不能
证明完整 lifecycle、hard gate 或 open-language generalization。

## 仍决定评分上限的问题

1. 外部与开放语言效度弱；多数低干预结果为零。
2. 没有 strict native public-benchmark opportunity 和独立 recall calibration。
3. primary 仍是 call-asymmetric package comparison。
4. post-hoc Rule* 接近 CTA，限制方法新颖性。
5. multi-refresh/multi-role composition 结果 mixed。

因此，文字与证据组织可提高 Phase 1 可读性和可信度，但只有独立开放语言或原生工作流
证据才能实质把严格评分从 5--6 推到稳定 7 分区间。
