# TRI 文本、代码、对比与消融审计

更新时间：2026-07-21

## 结论

当前主线在核心语义上是一致的：普通结构化记录保存了事实，但没有显式保存“该事实是否已经成为承诺身份”；刷新前目标承诺编译先判断 Preserve/Reevaluate，再决定保存初始 ID 还是把选择留到刷新后。生命周期 gate 只保护正确编译出的 Preserve 分支。

审计后需要修正一处补充材料表述：标量 TRI-v3 生命周期记录实际使用 `reference_mode`、`bound_target_id`、`selector`、`invalidity_policy`；`guard_type` 和 `fallback_policy` 只属于 TRI-v4 条件生命周期扩展。已在 `paper/supplementary_material.tex` 修正。

## 文本与代码对照

| 项目 | 论文描述 | 实际代码 | 判断 |
|---|---|---|---|
| Generic Structured Ledger | 保存初始 ID、快照、selector、action、preconditions；不显式保存模式 | `run_generic_structured_ledger_then_act` 输出 `selected_entity_id`、快照、selector、action、preconditions | 一致；原始 instruction 由第二次调用单独传入，不是 ledger 字段 |
| Exact CTA | 编译 `binding_time`、selector、bound ID；第二步按编译记录执行 | `run_compile_then_act` 两次调用；第二次只接收 ledger 与刷新状态，不接收 action schema | 一致；论文已披露 CTA actor 缺少 action schema，这是历史邻近基线的公平性限制 |
| Lifecycle-free | 类型化 `reference_mode`、ID、selector、invalidity policy；自由 actor | `run_factorized_schema_compile_then_act` 编译后始终调用 actor | 一致 |
| Lifecycle-Gated | Preserve 且动作有效时确定性输出；否则按策略或 actor | `run_factorized_schema_compile_then_act(..., hybrid_gate=True)` 对有效 Preserve 跳过 actor | 一致 |
| TRI-v4 conditional | `guard_type` 区分 action-validity / selector-match，`fallback_policy` 允许重新选择 | `run_guarded_lifecycle` 使用这两个字段并在必要时调用 actor | 一致，但不得与 v3 scalar record 混写 |
| 金标准隔离 | compiler/actor 不看 gold target、generator selector field | runner 的 prompt 只传 instruction、state、action schema、future event | 一致；确定性 oracle 只用于离线 executor 检查，不是 learned baseline |
| 请求数 | Generic/CTA/Lifecycle-free 两次；Gated 有效 Preserve 一次 | 代码与 supplement 表一致 | 一致 |

## 对比实验判定

### 必须保留

1. Generic Structured Ledger：直接邻近基线，主结果核心对照。
2. Exact CTA（刷新前目标承诺编译）：当前最强简单 scalar 对照，也是论文主方法。
3. Lifecycle-free 与 Lifecycle-Gated：拆分“编译收益”和“确定性执行保护”。
4. Always-Lock / Always-Reevaluate：确定性对称控制，证明问题不是单纯锁定或单纯重选。
5. Untyped pre-refresh plan、Generic + reference mode、Generic + validity gate：表示与机制消融。
6. 普通 full-history / ReAct 类运行：已有冻结结果应放补充材料或外部边界，不与 CTA 做不公平的同表主结论。已有报告中的 Qwen/GLM full-history 结果来自独立冻结 inventory，正式引用前必须在 provenance 中标清数据集版本。

### 不应伪装成官方复现

- Binding Drift：官方 `Entity Lock` 与 Always-Lock 语义重合；官方 `reverify` 在当前 commit 的确定性路径读取 `gold_target`，是 oracle upper bound。已完成 25/25 离线断言审计，但不把它放进 learned-method 主表。
- LedgerAgent、Bounded Autonomy、Entity Binding Failures：相关问题分别偏结构化状态/执行合同/初始绑定；当前没有已验证的、可直接映射 TRI-v3 任务和公开运行入口。临时改写 prompt 会混入实现者选择，不应称为“官方复现”。在 supplement 说明概念关系和不可比性即可。

## 消融是否足够

当前消融已经回答三个关键因果问题：

- 只加 `reference_mode` 是否足够：否，Generic+mode 仍显著低于 CTA。
- 只把计划提前是否足够：不稳定，untyped plan 跨模型差异明显。
- gate 是否是主要收益来源：不是，Lifecycle-free 已接近或达到 CTA，gate 主要增加执行保护。

还需要补强的不是更多方法，而是以下两项审稿风险：

1. **第三模型全量复现**：DeepSeek 冻结 v7 240-task 已完成；Generic/CTA 为 73.8/91.2，配对 +17.5 points [10.8,23.3]，conditional drift 为 59/79 对 0/70，0 API/parse error。
2. **实现可复现性**：长跑 runner 已加入 `--resume`、逐行 flush 和 `api_usage` 记录，防止长实验中断或无法核对成本。

## 今晚运行矩阵

| 阶段 | 数据 | 模型 | 方法 | 目的 | 停止条件 |
|---|---|---|---|---|---|
| 已完成 | v7 4-task health | DeepSeek | Generic、CTA | endpoint/schema 健康 | 已通过，0 API/parse error |
| 已完成 | v7 scalar 16-task | DeepSeek | Generic、CTA | pilot 方向 | 已完成：11/16 vs 15/16；drift 5/6 vs 0/6 |
| 已完成 | v7 full 240-task | DeepSeek | Generic、CTA | 降低两模型限制 | 480 tasks、960 requests、0 error/retry；结果通过方向和完整性检查 |
| 已完成 | v7 SQLite replay 480 episodes | deterministic | Generic、CTA predictions | 验证错误写入后果 | Generic core TRI writes 59/79；CTA 0/70 |
| 暂不运行 | v7 full | DeepSeek | Event Graph/M2/Binding Drift learned reimplementation | 已知不改变主线，成本高且可比性弱 | 不启动 |

## 统计与写作规则

- 240-task 结果按 40 个 state clusters bootstrap；报告 conditional core drift、initial binding、stable errors、API/parse errors 和 paired delta。
- 不把 third-model full run 与原始 Qwen/GLM 结果混合成无分层 pooled accuracy；先按模型报告，再报告方向一致性。
- 若 DeepSeek CTA 在 full set 上不稳定，不能删除结果；作为 robustness boundary，保留 raw run 和失败分解。
- 若端点中断，使用 `--resume` 继续；不能覆盖已有部分 JSONL，也不能把未完成任务从分母中静默删除。最终 ITT 把 API/parse failure 计为错误。
