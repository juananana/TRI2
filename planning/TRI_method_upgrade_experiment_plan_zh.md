# TRI 方法升级与完整补实验计划

## 1. 目标

验证新方法 `Proof-Carrying Referential Capability Controller` 是否相对 Exact CTA：

1. 更准确编译自然语言中的事件顺序、指称来源和 selector；
2. 在正确绑定后保持零或更低 TRI；
3. 减少 CTA 仍存在的 dynamic-old、selector、invalid-policy 和多指称错误；
4. 不依赖大量拒绝或 clarification 获得表面安全；
5. 在并发状态变化下阻止 stale/wrong writes；
6. 额外 API、token、延迟和状态成本可接受。

若新方法不能在 CTA 已经很强的设置上增加准确率、组合泛化或形式化保证，论文保留 CTA，定位为 phenomenon/benchmark/authorization paper。

## 2. 已有可直接复用实验

### 主受控结果

- TRI-v3：160 tasks，20 template clusters，8 domains，Qwen/GLM。
- Generic：64.4/71.9%；Exact CTA：95.0/96.2%；Lifecycle-Gated：98.1/100.0%。
- Always-Lock 与 Always-Reevaluate：各 60%，错误模式互补。
- Generic + reference mode：75/75%，证明 mode 字段有用但不充分。
- Untyped pre-refresh plan：81.2/70.6%，证明仅提前规划不充分。

### 独立复现

- TRI-v7：240 tasks，40 state clusters。
- Generic core drift：Qwen 43/72，GLM 38/80。
- CTA core drift：0/71、0/70。
- CTA 仍有 dynamic-old、selector、invalid-attempt 和 rejection 错误，可作为新方法优化目标。

### 实际写入

- v3 SQLite：Generic Qwen/GLM wrong writes 13/8；Lifecycle-Gated 0/0。
- v7 replay：81 次 Generic core drift 全部成为 wrong writes。
- 现有 SQLite 输出可重放，不必重复调用模型。

### 自然语言与人类语义

- 100 条、3 annotators：Fleiss kappa 0.708，majority-gold 86%。
- 50 条独立 human rewrites：CTA Qwen/GLM 90/98%，Generic 60/74%。
- 不新增人工标注；现有结果用于 human-language OOD。

### 泛化与压力

- 80 unseen-domain tasks。
- 40 conditional-policy tasks。
- v5 multi-refresh negative stress。
- v6 scalar/role-indexed multi-referent held-out。
- ToolSandbox、AppWorld、tau3 opportunity audits 与普通 full-history Agent 边界结果。

## 3. 新方法版本

### M0：Exact CTA

现有最强简单基线。刷新前编译 binding time、ID、selector。

### M1：Event Graph CTA

编译：

```json
{
  "events": [
    {"id": "E1", "type": "SELECT"},
    {"id": "E2", "type": "REFRESH"},
    {"id": "E3", "type": "ACT", "referent": "E1"}
  ],
  "order": ["E1", "E2", "E3"]
}
```

Mode 由事件图确定性推出，不由模型直接输出标签。

### M2：Event Graph + Executable Selector

Selector 编译为受限 AST/relational query。程序执行 selector，禁止 actor 自由重解释。

### M3：Referential Capability

绑定后生成：entity ID、action scope、binding epoch、source event、release condition、fallback。
World refresh 只能更新 belief，不能修改 capability。

### M4：Proof Validator + Clarify

Compiler 输出 evidence span、event edge、confidence。Verifier 检查证据、事件顺序、schema、selector 和 fallback。低置信度输出 Clarify。

### M5：Atomic Capability Gate

同一事务检查 capability、entity ID、version、action validity 并写入。使用 compare-and-swap/version predicate 阻止 TOCTOU。

主方法为 M5。M1--M4 只用于组件消融。

## 4. 对比方法

### 必须比较

1. Ordinary full-history function-calling Agent：已有 AppWorld 结果。
2. Generic Structured Ledger：已有。
3. Exact CTA：已有，最重要强基线。
4. Lifecycle-free：已有。
5. Lifecycle-Gated：已有。
6. Always-Lock + validity：已有。
7. Always-Reevaluate：已有。

### 公开邻近工作

1. Binding Drift `Entity Lock`：复现官方仓库 `shashank-indukuri/binding-drift`。
2. Binding Drift `Independent Re-verification`：必须在其 workflow benchmark 和 TRI matched tasks 上分别报告。
3. LedgerAgent：若官方代码可用，运行官方实现；否则按论文 prompt/schema 重实现，并标记 `author reimplementation`。
4. Bounded Autonomy typed action contract：比较 execution-time contract 是否能阻止 action-valid wrong target；无官方代码时只做透明重实现。
5. Entity Binding Failures confidence/clarification：比较初始绑定 confidence gate；强调其研究初始 binding，不是 post-binding transition。
6. ReAct/full-history：作为普通 Agent，不作为新颖强方法。

公开实现不可运行时，不伪称官方结果。报告 commit、修改、失败原因和适配边界。

## 5. 研究问题

- RQ1：Event Graph 是否提高 mode、event-order、reference-edge 编译？
- RQ2：Executable Selector 是否减少 selector grounding 和 dynamic-old 错误？
- RQ3：Capability 是否阻止 actor 在 refresh 后改写已授权目标？
- RQ4：Proof Validator 是否在执行前发现错误 contract？
- RQ5：Clarify 是否降低 wrong writes，同时保持可接受 coverage？
- RQ6：Atomic Gate 是否阻止 stale-version/TOCTOU 写入？
- RQ7：方法是否泛化到 human rewrites、unseen domains、multi-refresh、multi-referent？
- RQ8：收益是否值得额外 token、延迟、clarification 和实现复杂度？

## 6. 实验阶段

### Phase A：Oracle Executor，零 API

数据：v3、v4、v7、并发注入集。

输入 gold Event Graph、selector、capability。要求：

- scalar target/final state 100%；
- unauthorized rebind 0；
- injected stale writes 0；
- legal-write false block 接近 0。

未通过则停止模型实验。

### Phase B：Compiler-only

数据：v3 160、human rewrites 50、unseen 80。

比较 M0/M1/M2/M4。指标：

- Event type/order/reference-edge accuracy；
- Preserve/Reevaluate/Conditional accuracy；
- bound-ID accuracy；
- selector AST schema validity；
- selector execution equivalence；
- evidence-span validity；
- guard/fallback accuracy；
- Brier、ECE、risk-coverage、AURC。

### Phase C：Scalar end-to-end

冻结 v7 240 作为主新方法比较。

主表只放：Generic、Exact CTA、Binding Drift strongest、M5。
Lifecycle 与其他组件放消融表。

指标：final state、authorized target、conditional TRI、wrong writes、dynamic-old、stable error、invalid attempt、unneeded reject、collateral modification。

### Phase D：自然语言与 transfer

- Human rewrites 50；
- unseen domains 80；
- implicit/explicit、anchored/dynamic 分层。

目标：新方法必须改善 CTA 的自然语言错误，而非只在模板任务加字段。

### Phase E：组合压力

- v5 multi-refresh；
- v6 multi-referent；
- role-indexed capability；
- ID migration/version change；
- unrelated tool calls；
- selector name collision。

### Phase F：Atomic/Concurrency

至少 100 个确定性事件序列：authorize 后注入 delete、invalidate、version increment、ID alias、competitor update。

比较 validity-only、capability-only、capability+version、atomic transaction。

### Phase G：外部边界

AppWorld Todoist/Simple Note 低干预 selector API。先跑 smoke，再跑 M5。外部 conditional TRI 若仍为 0，如实作为边界，不扩大模板数量追求正向结果。

## 7. 核心指标

### 正确性

- Exact authorized-target accuracy；
- final database-state success；
- compiler field accuracy；
- selector execution equivalence。

### 机制

- conditional TRI rate；
- Preserve/Flip unauthorized rebind；
- Reevaluate/Flip premature lock；
- pre-binding order error；
- Stable masking rate。

### 后果

- wrong-entity write；
- collateral modification；
- stale write；
- invalid attempt；
- false block。

### Utility

- task completion；
- unnecessary reject；
- clarification rate；
- completion after clarification；
- coverage at zero wrong write。

### 成本

- LLM calls/task；
- input/output tokens；
- API cost/task；
- latency/task；
- tool calls；
- gate/transaction latency；
- persistent-state bytes；
- clarification turns；
- cost per successful task；
- cost per prevented wrong write。

## 8. 统计

- 按 template/state/writer/scenario cluster bootstrap，10,000 samples；
- paired effect size 与 95% CI；
- McNemar 次要；
- Stable/Flip paired attribution；
- multiple rows from same cluster 不当独立样本；
- API/parse errors 做 intention-to-treat，并提供 transport-complete sensitivity；
- frozen primary 与 post-primary exploratory 明确分开。

## 9. 最小充分新运行矩阵

### Smoke

- 20 tasks；
- Qwen、GLM；
- Exact CTA、Binding Drift strongest、M2、M5。

### 主运行

- v7 240；
- Qwen、GLM；
- 新跑 Binding Drift strongest、M2、M5；
- Generic、CTA、Lifecycle 复用旧输出。

### 第三模型家族

- 选择与 Qwen、GLM 不同训练谱系且接口稳定的一个模型；候选按可用性为
  DeepSeek、Llama 或 MiniMax；
- 先跑 20-task smoke，通过后只跑冻结 v7 的 Generic、Exact CTA、
  Binding Drift strongest、M5；
- 不因单个模型的异常结果临时更换任务、prompt 或主指标；
- 同一 API 提供商不等于同一模型家族，但论文同时披露 provider，避免把
  provider diversity 误写成 model diversity。

### OOD

- human rewrites 50；
- unseen 80；
- 新跑 CTA matched rerun仅在接口变化导致不可直接复用时；否则复用。

### Stress

- v6 40；
- concurrency 100，确定性，无 API；
- AppWorld 16，仅 M5 与 ordinary Agent。

预计新增约 1,500--2,500 次模型请求；完整全组件矩阵约 4,000--6,000 次，不推荐。实际 tokens、人民币/美元成本从 API 日志计算，不预估虚假价格。

## 10. 运行公平性与结果溯源

1. 运行前冻结 dataset、prompt、controller、evaluator 的 SHA-256 和 Git commit；
2. 方法间使用相同模型版本、temperature、thinking 设置、token budget、tool schema、
   timeout 和 transport retry policy；
3. 只有方法定义所需字段可以变化；不能给主方法额外 gold ID、gold mode 或 oracle
   selector；
4. Exact CTA 与新方法共用同一 compiler 输入；程序执行部分单独报告 oracle 与
   learned compiler 结果；
5. API/parse/timeout 按 intention-to-treat 计失败；另报 transport-complete sensitivity；
6. 保存逐任务输入、结构化中间状态、工具轨迹、数据库 diff、token、latency 和错误码；
7. 官方实现记录仓库 URL、commit、依赖和最小适配 diff；重实现明确标记
   `author reimplementation`；
8. 主结果只来自冻结运行；调试、smoke、失败重试和 post-hoc 分析分目录保存；
9. temperature 0 仍可能有服务端非确定性，在分层 40-task 子集上重复 3 次，报告
   disagreement rate；
10. 所有表格数字由脚本从原始 JSONL 生成，不手工录入。

## 11. Go/No-Go

继续作为主方法需满足：

1. Oracle executor 100%；
2. selector execution equivalence >=95%；
3. scalar accuracy 不比 CTA 低超过 2 points；
4. conditional TRI 不高于 CTA；
5. human rewrite 或 multi-referent 至少一项稳定提升；
6. clarification rate <20--25%，或 risk-coverage 明显优于 CTA；
7. injected stale writes 0；
8. legal-write false block 接近 0；
9. 成本和 latency 完整报告；
10. 至少两个模型效果方向一致。

降级或放弃新方法条件：

- Event Graph 不优于 CTA；
- selector AST 自然语言编译不稳定；
- capability 只增加字段，不减少错误；
- clarification 靠大量拒绝换安全；
- atomic gate 无新增保护；
- multi-referent 仍不如简单 role-indexed baseline；
- 模型间效果方向冲突。

## 12. 优先级

### P0：投稿主张必需

1. Oracle executor、selector equivalence、atomic concurrency tests；
2. Binding Drift 官方方法复现及 matched TRI 对比；
3. 冻结 v7 上 Exact CTA、Binding Drift strongest、M2、M5；
4. human rewrites、unseen-domain、v6 multi-referent；
5. 完整错误分解、cluster statistics、成本与溯源；
6. 至少 Qwen、GLM 两个家族方向一致。

### P1：最可能增加说服力

1. 第三模型家族冻结主矩阵；
2. 40-task 三次重复，测服务端不确定性；
3. AppWorld 16-task 低干预 case study；
4. LedgerAgent、Bounded Autonomy、Entity Binding Failures 的透明重实现；
5. confidence/clarification risk-coverage 分析。

### P2：有价值但不应抢占 P0

1. 扩更多相似 synthetic domains；
2. 完整 ToolSandbox/AppWorld/tau3 大规模改造；
3. 全组件、全模型、全数据笛卡尔积；
4. 新增第二条 TRI-v4 类政策主线；
5. 为得到正结果而继续扩外部模板任务。

## 13. 九日执行

1. Day 1：实现 Event Graph IR、selector AST、oracle executor、property tests。
2. Day 2：实现 capability、proof validator、atomic gate、concurrency tests。
3. Day 3：复现 Binding Drift；确认其他公开代码可用性。
4. Day 4：20-task smoke；修复 schema，不看主测试结果调 prompt。
5. Day 5：冻结并跑 v7 主矩阵。
6. Day 6：human rewrites、unseen transfer。
7. Day 7：v6 multi-referent、AppWorld、成本审计。
8. Day 8：cluster statistics、消融、图表、claim provenance。
9. Day 9：论文重写、LaTeX 编译、匿名包、严格 reviewer pass。
