# TRI 方法升级、补实验与 AAAI-27 推进计划

更新日期：2026-07-20（Asia/Shanghai）

## 0. 执行状态

- Phase A 零 API 原型已实现：`tri/event_graph_controller.py`。
- v3 160、v7 240、v6 40 共 440 tasks：mode、selector initial/final、authorized target、capability binding 均为 440/440。
- Atomic Gate 已完成 120 个确定性序列：40 legal writes、0 false blocks、0 wrong writes；其余 80 个 stale/delete/invalidate/alias 序列全部阻断。
- 报告：`reports/event_graph_oracle_v1.json` 和 `reports/event_graph_oracle_v1.md`。
- 20-task smoke 已冻结：16 v7 + 4 v6，16 个 v7 state clusters，覆盖两种 binding、两种语言现象及 flip/stable/name-collision/remove。
- Smoke 文件：`data/temporal_referent_method_upgrade_smoke_v1.jsonl`；SHA-256 `e651f4db45275877ca09a5e70187baca6d5ee8901bf983bb1ecc3885ef879181`。
- Binding Drift 官方源码已拉取到 `external_sources/binding-drift`；其可复现性和 TRI 可比性已完成审计。
- Binding Drift 已审计 commit `0e040e0954b18d4621a6f9b16f6e6e9591c822e1`：临时路径适配后官方 25/25 离线断言通过；当前 clean checkout 的测试路径失效。
- 其 `reverify` 确定性配置读取 `gold_target`，必须标为 oracle upper bound；`lock` 与现有 Always-Lock 对应。详见 `reports/binding_drift_repro_audit.md`。
- 主文已完整 BibTeX 编译为 8 页：7 页正文 + 1 页参考文献，满足 7/9 页限制；不再把无参考文献的 9 页中间 PDF 当正式页数。
- Compiler-only smoke runner、token/provenance 记录和自动 Go/No-Go 汇总已实现并通过本地测试；外部 API 运行等待数据出境明确授权。
- 6 请求最小闭环已完成：Qwen/GLM 各 1 task x 3 compiler，均 schema 合法、0 API/parse error、0 retry；GLM 该条全对，Qwen 的 M2 selector 执行正确但 action-target ID 绑定错误。该结果只验证管线并提示 M2 风险，不构成效果结论。
- 论文级 20-task 闭环已完成：复用 Generic/CTA/Lifecycle/role-indexed 冻结原始输出，新跑 M1/M2 共 95 请求、0 retry，并加入 Always-Lock/Always-Reevaluate。
- M1：Qwen 9/20、GLM 20/20；M2：Qwen 15/20、GLM 18/20。M2 schema 为 15/20、18/20，selector equivalence 为 15/20、19/20，未达到双模型 95% 门槛。
- 对照 CTA：Qwen 13/20，M2 +2；GLM 20/20，M2 -2，方向冲突。Go/No-Go 判定为不升级 M2，标量主方法保留 Exact CTA。
- v6 四条组合压力：Qwen CTA/scalar Lifecycle/role-indexed/M2 为 2/2/4/4；GLM 均为 4/4。Role-Indexed Lifecycle 保留为组合扩展，M2 只作探索性结果。
- DeepSeek 第三模型冻结 v7 全量已完成：Generic 73.8%，CTA 91.2%，conditional drift 59/79 对 0/70，配对提升 +17.5 points [10.8,23.3]；SQLite replay 将 59 次 core drift 全部重放为 wrong writes。
- 统一报告：`reports/method_upgrade_closed_loop_v1.json` 与 `reports/method_upgrade_closed_loop_v1.md`。

## 1. 截止日期与当前判断

- 摘要截止：2026-07-21 23:59 UTC-12，即北京时间 2026-07-22 19:59。
- 全文截止：2026-07-28 23:59 UTC-12，即北京时间 2026-07-29 19:59。
- 补充材料和代码截止：2026-07-31 23:59 UTC-12，即北京时间 2026-08-01 19:59。
- 从 2026-07-20 到全文标称截止日还剩 **8 个日历日**；按北京时间实际提交时刻计算，约有 9 天，但计划不得消耗这一天时区余量。
- AAAI-27 主文最多 7 页正文、9 页总计；第 8 页起只能是参考文献。当前 `paper/AnonymousSubmission2027.pdf` 为 8 页，正文止于第 7 页，参考文献从第 8 页开始。

结论：原计划科学上完整，但无法在截止前同时可靠完成 M1--M5、多个外部方法复现、1,500--2,500 次模型请求和论文重写。投稿前必须采用“保底主线 + 有门槛升级”，不能把未经充分验证的新控制器强行设为主方法。

## 2. 投稿主张与方法定位

### 2.1 保底主张

论文的可守主张是：

1. 在正确初始绑定后，普通结构化状态仍会发生 post-binding referent drift；
2. 该漂移在受控任务中可复制，并可直接转化为 wrong-entity writes；
3. pre-refresh commitment compilation（Exact CTA / factorized lifecycle）显著减少漂移；
4. 现有公开 Agent benchmark 几乎不产生严格 TRI opportunity，因此本文同时揭示一个评测盲区；
5. 结果不证明 TRI 在所有模型或真实部署中普遍、高频发生。

论文优先定位为 **phenomenon + benchmark blind spot + authorization mechanism**，而不是“通用 Agent 安全控制器”。

### 2.2 方法升级原则

- `M0 Exact CTA` 是投稿保底主方法和最重要强基线。
- 截止前只优先实现一个合并升级：`M2 Event Graph + Executable Selector`。
- capability 与 atomic version gate 先作为确定性执行保护和系统消融，不默认宣称为新的 LLM reasoning 方法。
- proof validator、confidence calibration、clarification controller 只有在已有模型输出可离线评分时进入本稿；否则移至后续工作。
- 若 M2 未通过零 API oracle 或 20-task smoke，立即停止升级，论文保持 CTA 主线。

## 3. 已有证据与可支持结论

| 证据 | 已有结果 | 可支持结论 |
|---|---:|---|
| TRI-v3，160 tasks，Qwen/GLM | Generic 64.4/71.9%；CTA 95.0/96.2%；Lifecycle-Gated 98.1/100% | 结构化状态仍会漂移；预刷新编译有效 |
| Always-Lock / Always-Reevaluate | 均为 60%，错误互补 | 不能固定锁定或固定重选，必须识别授权语义 |
| Generic+mode / untyped plan | 75/75%；81.2/70.6% | 单字段或普通提前规划不足 |
| TRI-v7，240 tasks，40 clusters | Generic core drift 43/72、38/80；CTA/Gated core drift 0 | 漂移独立复制，CTA 消除核心条件漂移 |
| v3 SQLite | Generic wrong writes 13/8；Gated 0/0 | 语义错误会成为真实错误写入 |
| v7 写入重放 | 81 次 core drift 全部成为 wrong writes | drift 与错误副作用直接对应 |
| 人工语义，100 tasks，3 人 | Fleiss kappa 0.708；majority-gold 86% | Preserve/Reevaluate 区分具有人类可操作性 |
| Human rewrites，50 tasks | CTA 90/98%；Generic 60/74% | 效果不只存在于原模板 |
| multi-refresh / multi-referent | 部分负面 | 明确现有方法组合边界 |

公开环境边界必须如实报告：

- ToolSandbox：129 个任务家族，严格原生 TRI opportunity 为 0，1 个 near-match；
- AppWorld：732 tasks、244 families，1 个 near-match，公开轨迹未观察到 post-binding substitution；
- tau3-bench：2,449 tasks、10,832 trajectories，严格原生 TRI opportunity 为 0；
- 低干预 AppWorld：28 次正确及时绑定，conditional TRI 为 0；两个错误属于 pre-binding order error。

这些结果是 benchmark coverage evidence，不是现实 prevalence evidence。

## 4. 截止前方法版本

### M0：Exact CTA

刷新前编译 reference mode、selector、bound ID 和 invalidity policy。保留为主基线和失败回退方案。

### M1：Event Graph CTA

将用户指令编译为带角色的事件图，而不是直接预测单个 mode 标签：

```json
{
  "events": [
    {"id": "E1", "type": "SELECT", "state": "initial", "role": "action_target"},
    {"id": "E2", "type": "REFRESH"},
    {"id": "E3", "type": "ACT", "referent": "E1"}
  ],
  "edges": [["E1", "E2"], ["E2", "E3"]]
}
```

`preserve/reevaluate` 必须由 action referent 指向刷新前或刷新后 SELECT 事件确定性推出，不由模型额外输出。

### M2：Event Graph + Executable Selector

Selector 使用受限 AST：

```json
{
  "filters": [{"field": "status", "op": "eq", "value": "pending"}],
  "order_by": {"field": "score", "direction": "desc"},
  "limit": 1
}
```

程序执行 selector；模型不能在 action 阶段自由重解释 selector。投稿前的新方法最多推进到 M2。

### S1：Referential Capability（系统组件）

确定性记录 entity ID、action scope、source event、binding epoch、release condition 和 action preconditions。Refresh 只能更新 world belief，不能静默改写 capability。

### S2：Atomic Version Gate（系统组件）

执行时在同一事务中检查 entity ID、action scope、preconditions、expected version 并写入。该组件证明可以阻止 stale/TOCTOU write，但不能证明编译器理解了用户语义。

### 截止后方法

Proof-carrying evidence span、独立 verifier、confidence calibration、clarification policy 和完整 M5 留作后续版本，除非在 7 月 22 日前已有可复用实现和明确正结果。

## 5. 研究问题

- RQ1：普通结构化状态在正确初始绑定后是否发生 TRI？
- RQ2：Exact CTA 是否在不同模型、改写和 held-out domain 上降低 TRI 与 wrong writes？
- RQ3：Event Graph 是否减少 mode/event-order/reference-role 编译错误？
- RQ4：Executable Selector 是否减少 selector grounding、dynamic-old 和 multi-referent 错误？
- RQ5：Capability/version gate 能否阻止 unauthorized、invalid 和 stale writes，且不误阻合法写入？
- RQ6：收益是否依赖拒绝、额外调用或不可接受的 token/latency？
- RQ7：现有公开 benchmark 为什么无法直接估计 TRI prevalence？

## 6. 必须比较与可选比较

### 主结果表

1. Generic Structured Ledger（已有）；
2. Exact CTA（已有或 matched rerun）；
3. M2，仅在通过 Go/No-Go 后进入主表。

Binding Drift 不再强制塞入同一主表：官方 `lock` 与已有 Always-Lock 语义重合，官方
`reverify` 使用 `gold_target`，而 LLM re-verifier 解决初始指称，不原生表达授权后的
Preserve/Reevaluate。其官方 benchmark 复现与 matched adaptation 分表报告。

若 Binding Drift 官方实现无法在 7 月 22 日前完成可审计适配，则：

- 保留官方 benchmark 原结果的引用；
- 在 TRI matched tasks 上使用明确标注的 `author adaptation`；
- 报告仓库 commit、适配 diff、输入输出映射和失败原因；
- 不把不可比数字并入同一显著性检验。

### 消融表

- Ordinary full-history/ReAct；
- Always-Lock + validity；
- Always-Reevaluate；
- Lifecycle-free；
- Lifecycle-Gated；
- M1 Event Graph；
- M2 Event Graph + Executable Selector；
- S1 capability without version gate；
- S1 + S2 atomic version gate（确定性并发实验）。

### 投稿前不再强制

LedgerAgent、Bounded Autonomy、Entity Binding Failures 的新重实现，第三模型家族，大规模 AppWorld 重跑，confidence/AURC 全套分析均降为 P1/P2。透明但仓促的重实现不一定比清楚说明比较边界更有说服力。

## 7. 分阶段实验

### Phase A：零 API oracle 与 property tests（P0）

数据：v3 language 160、v7 240、v6 40，以及 100 个确定性并发注入序列。

检查：

- Event Graph schema 和 DAG 合法；
- action referent 唯一指向 `action_target`；
- oracle mode accuracy 100%；
- selector execution equivalence 100%；
- authorized-target accuracy 100%；
- unauthorized rebind 0；
- injected stale writes 0；
- legal-write false block 0。

任何一项未通过，先修执行器或任务映射，不调用模型。

### Phase B：20-task compiler smoke（P0，有 API）

冻结 20 个任务，覆盖：

- anchored/dynamic；
- explicit/implicit；
- flip/stable/name-collision；
- 至少 5 个 state clusters；
- v6 中 action-target 与 monitoring-reference 分离。

模型：Qwen、GLM。方法：Exact CTA、Binding Drift strongest、M1、M2。

先只评 compiler，不运行自由 actor。指标：

- event type/order/reference-edge；
- derived reference mode；
- bound-ID；
- selector AST schema validity；
- selector execution equivalence；
- parse/API failure。

Smoke 只允许修 schema、解析和明显 prompt 歧义。不得看完整 v7 测试结果后迭代 prompt。

### Phase C：冻结主运行（条件 P0）

仅当 M2 smoke 满足以下条件才运行 v7：

- schema validity >=95%；
- selector equivalence >=95%；
- derived mode accuracy 不低于 CTA；
- 两个模型方向一致；
- API/parse failure <=5%。

主数据：v7 240。优先新跑 M2 和 Binding Drift strongest；Generic、CTA、Lifecycle 复用完整且 provenance 一致的历史输出。若模型端点或参数变化导致不可比，做 matched rerun，并把历史结果改为 supporting replication。

### Phase D：transfer 与组合边界（条件 P0）

按优先级运行：

1. human rewrites 50；
2. v6 multi-referent 40；
3. unseen domains 80。

只有主运行显示 M2 改善 CTA 错误时才扩展。若 M2 与 CTA 持平，优先保留 CTA，停止额外 API 消耗。

### Phase E：Atomic/Concurrency（P0，零 API）

至少 100 个确定性序列，均含 authorize 后并发变化：

- delete；
- action precondition invalidation；
- version increment；
- ID alias/name collision；
- unrelated entity update；
- legal no-change control。

比较 validity-only、capability-only、capability+version、atomic transaction。报告 stale write、wrong write、false block 和 successful legal write，不把该实验混同为 LLM 语义准确率。

### Phase F：外部边界（P1）

不再以获得正向 TRI 为目标扩模板。现有 ToolSandbox/AppWorld/tau3 审计已经足以支持 coverage blind spot。仅在主文需要一个端到端例子且不影响 P0 时，运行 AppWorld 16-task case study。

## 8. 主要指标与统计

### 正确性和机制

- authorized-target accuracy；
- final database-state success；
- selector execution equivalence；
- conditional TRI；
- Preserve/Flip unauthorized rebind；
- Reevaluate/Flip premature lock；
- dynamic-old；
- stable masking；
- pre-binding order error（与 TRI 分开）。

### 后果和效用

- wrong-entity write；
- stale write；
- collateral modification；
- invalid attempt；
- false block；
- completion；
- unnecessary reject；
- clarification rate（仅在实现 clarification 时）。

### 成本

- calls/task；
- input/output tokens；
- latency；
- tool calls；
- cost/task 和 cost/success；
- deterministic gate latency；
- persistent-state bytes。

### 统计规则

- 以 template/state/writer/scenario cluster 为重采样单位；
- cluster bootstrap 10,000 次，报告 paired effect 和 95% CI；
- McNemar 仅作配对二元结果的次要检验；
- API/parse/timeout 按 intention-to-treat 计失败，另报 transport-complete sensitivity；
- 不把同一 state cluster 的多行当独立样本；
- 预先冻结 primary endpoint：`authorized-target accuracy`；
- `conditional TRI` 和 `wrong writes` 为关键安全终点；
- 多个 exploratory slices 明确标注，不用未经校正的 p 值制造主张。

## 9. 运行公平性与溯源

1. 运行前冻结 dataset、prompt、controller、evaluator 的 SHA-256 和 Git commit；
2. 方法间固定模型版本、provider、temperature、thinking、token budget、tool schema、timeout 和 retry policy；
3. 新方法不能获得 Generic/CTA 看不到的 gold ID、gold mode、criterion 或 direction；
4. oracle selector 与 learned compiler 必须分表；
5. 保存逐任务 prompt、结构化 IR、工具轨迹、DB diff、token、latency、错误码和 retry；
6. smoke、debug、frozen primary、post-primary exploratory 分目录；
7. 官方实现和 author adaptation 分开命名；
8. 表格由脚本从 JSONL 生成，不手工录数；
9. 旧结果只有在模型版本、运行参数和 evaluator provenance 可核对时才进入 matched 主表；
10. 冻结后只允许修 transport，不允许按结果改任务、prompt 或指标。

## 10. Go/No-Go 决策

### M2 进入论文主方法需同时满足

1. Phase A 全部通过；
2. selector equivalence >=95%；
3. v7 authorized-target accuracy 不比 CTA 低超过 2 points；
4. conditional TRI 不高于 CTA；
5. human rewrites 或 v6 至少一项对 CTA 有稳定改善；
6. parse/API failure <=5%；
7. 两个模型方向一致；
8. 新增成本完整报告。

### 立即回退 CTA 的条件

- Event Graph mode/reference-edge 不优于 CTA；
- selector AST 编译不稳定；
- 改善只来自更多拒绝或 oracle 信息；
- multi-referent 不如已有 role-indexed baseline；
- 两模型效果方向冲突；
- 7 月 23 日前未得到可信 smoke 结果。

回退不是实验失败：它支持“简单 commitment compilation 已接近受控设置上限，新复杂度未提供稳定增益”，并保护论文现有主张。

## 11. 请求预算

不再预授权 1,500--2,500 次请求。采用分段预算：

- Stage 0：零 API；
- Stage 1：20 tasks x 4 methods x 2 models = 最多 160 个 compiler 请求；
- Stage 2：若通过，只运行必要的 v7 新方法/强基线；每增加一个 method-model 矩阵需单独确认；
- Stage 3：transfer 每次只解锁一个数据集；
- 硬停止条件：出现系统性 parse/transport 错误、两模型方向冲突或 M2 不优于 CTA。

理想新增预算控制在 600--1,200 次模型请求；只有主结果明确需要 matched rerun 时才允许超过该范围。

## 12. 八日执行与论文推进

### Day 1，7 月 20 日

- 冻结投稿主张、primary endpoint 和回退条件；
- 完成 Event Graph、selector AST、capability/version gate 的零 API接口；
- 开始摘要定稿；
- 核对主文 7 页正文边界和引用起始页。

### Day 2，7 月 21 日

- 完成 v3/v7/v6 oracle/property tests 与 100 个并发序列；
- 提交摘要，不等待新方法结果；
- 完成 Binding Drift 官方仓库可运行性审计；
- 冻结 20-task smoke manifest 和 hashes。

### Day 3，7 月 22 日

- 运行 20-task smoke；
- 作 M2 Go/No-Go；
- 同时开始将主文压到 7 页正文，不把写作推迟到最后一天。

### Day 4，7 月 23 日

- 若 Go：冻结并启动必要 v7 矩阵；
- 若 No-Go：停止 M2 API，锁定 CTA 主线；
- 完成主结果表、方法图和 external-boundary 表述草稿。

### Day 5，7 月 24 日

- 完成 v7 分析、error decomposition、cluster bootstrap、成本和 provenance；
- 仅在 v7 支持时解锁 human rewrites 或 v6；
- 主文应已有完整 7 页版本。

### Day 6，7 月 25 日

- 完成最多一个 transfer 数据集；
- 锁定所有主实验数字；
- 更新 supplement、limitations、reproducibility checklist 和匿名化检查。

### Day 7，7 月 26 日

- 不再启动高风险新实验；
- 独立 reviewer pass：主张-证据、统计单位、相关工作、引用真实性、图表可读性；
- clean-room artifact test 和 LaTeX 编译。

### Day 8，7 月 27 日

- 冻结 PDF；
- 检查 7 页正文/9 页总长、字体、匿名性、引用、补充材料链接和表格一致性；
- 完成提交表单，保留至少 24 小时缓冲。

### 7 月 28 日只作缓冲

仅处理提交系统、格式或致命事实错误，不再改方法、不再增加实验主张。

## 13. 论文结构建议

七页正文优先级：

1. Introduction：问题、反例、贡献和边界；
2. Definition：pre-binding error 与 post-binding TRI 的严格区分；
3. Method：CTA 主线；M2 只有通过 Go/No-Go 才替换或扩展；
4. Setup：受控设计、cluster、模型、primary endpoint；
5. Results：v3/v7、SQLite consequence、human rewrite；
6. Analysis：对称控制、表示消融、组合失败；
7. External boundary + limitations + conclusion。

主文必须保留：TRI 定义、最强主结果及 clustered CI、实际 wrong-write 证据、human/OOD 证据、外部 benchmark 零 opportunity 边界和限制。完整 prompts、所有切片、长表、并发序列和额外 trace 放 supplement。

## 14. 当前立即执行项

1. 实现并测试零 API Event Graph/Selector/Capability/Atomic Gate；
2. 生成 Phase A 机器可读报告；
3. 审计 Binding Drift 的 commit、依赖、任务映射与可复现性；
4. 冻结 20-task smoke manifest，但在 Phase A 通过前不调用 API；
5. 并行开始摘要与七页正文压缩。
