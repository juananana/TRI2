# Temporal Referent Integrity 小规模验证报告

日期：2026-07-15/16

## 结论

建议 **Conditional Go**，继续发展为 AAAI 投稿方向，但论文表述需要从“LLM 本身不会处理动态指称”优化为：

> 许多工具型 Agent 控制器会把目标保存为可重新解释的自然语言描述，并在环境刷新后只保留最新状态。这种 `state-overwrite` 表示会系统性破坏已在刷新前绑定的实体身份；显式的 temporal reference ledger 可以修复该问题，同时不阻止动态指称在刷新后重新求值。

这比原始版本更稳，因为我们发现强模型在完整 transcript 条件下可以做对；真正值得研究的是 **Agent 状态表示/目标编译方式**，不是简单的模型语义能力缺陷。

## 实验设计

任务结构为 2 x 2 配对：

- `anchored + flip`：用户要求先绑定当前对象，刷新后仍操作同一实体；刷新会改变哪个实体满足描述。
- `anchored + stable`：同样先绑定，但刷新不改变目标。
- `dynamic + flip`：用户要求刷新后再选目标；刷新会改变目标。
- `dynamic + stable`：刷新后再选，但目标不变。

测试模式：

- `direct`：模型同时看到刷新前后状态，只做语义解析。
- `interactive`：完整多轮 transcript 保留刷新前状态。
- `state_overwrite`：模拟常见 Agent 控制器，只保留自然语言目标和刷新后的当前状态。
- `ledger`：使用结构化 temporal reference ledger，显式保存 `binding_time` 和 `bound_target_id`。

## 核心结果

| 模型 | 模式 | Split | Anchored+Flip | Anchored+Stable | Dynamic+Flip | Dynamic+Stable |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | direct | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | interactive | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | state_overwrite | dev | 0/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | ledger | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| Qwen3.5-397B | state_overwrite | dev partial | 0/3 | 3/3 | 3/3 | 3/3 |
| Qwen3.5-397B | ledger | dev partial | 3/3 | 3/3 | 3/3 | 3/3 |
| GLM-5.1 | state_overwrite | heldout | 0/2 | 2/2 | 2/2 | 2/2 |
| GLM-5.1 | ledger | heldout | 2/2 | 2/2 | 2/2 | 2/2 |

错误类型也很干净：

- GLM state-overwrite 的 6 个 anchored+flip 错误全部漂移到刷新后的新目标。
- Qwen state-overwrite 的 3 个 anchored+flip 错误全部漂移到刷新后的新目标。
- dynamic 条件保持正确，说明不是“不适应环境变化”，而是错误地把已绑定目标重新求值。
- stable 条件保持正确，说明不是普通两轮执行失败。

## 研究价值判断

### 正面信号

- 机制特异性强：只打 anchored+flip，不打 dynamic/stable。
- 跨模型出现：GLM 与 Qwen 均复现 state-overwrite 漂移。
- 未见领域复现：invoice/device heldout 在 GLM 上完全复现。
- 方法头寸清晰：ledger 从 0% 修到 100%，且不伤 dynamic。
- 能与动态环境 benchmark 区分：我们的变量不是“世界变了”，而是“目标指称何时绑定”。

### 主要风险

- 目前样本量仍小，不能直接写成最终实验。
- 完整 transcript baseline 全对，论文不能声称所有 Agent 都会失败。
- 需要证明真实或主流 Agent 框架确实存在 state-overwrite/summarized-state 控制器。
- ledger 当前使用 oracle binding，需要下一步实现真正的 compiler：从自然语言和初始状态自动产生 ledger。
- Qwen 结果是 partial smoke，正式实验需要完整补齐。

## 优化后的论文问题

推荐题目：

**Temporal Referent Integrity in Tool-Using LLM Agents**

核心贡献可以写成：

1. 定义 temporal referent integrity：Agent 应区分刷新前绑定的 de re 目标和刷新后求值的 de dicto 目标。
2. 提出一个 paired benchmark，控制 binding time、environment update、state overwrite、stable control。
3. 证明 state-overwrite 目标表示会导致系统性 referent drift。
4. 提出 typed temporal reference ledger 作为最小修复机制。
5. 将问题与动态环境、记忆更新、一般指称歧义区分开。

## 下一步实验

正式推进前建议补：

1. 完整 6 域 x 3 paraphrase x 4 条件 x 4 模型。
2. 至少 2 个真实/开源 Agent controller：完整 transcript、latest-state summary、memory summary、ledger。
3. 自动 compiler：从自然语言产生 `{binding_time, selector, bound_entity_id, validity_condition}`。
4. 失效实体条件：被绑定实体在刷新后消失/不可操作时，应请求澄清或重新选择。
5. 外部迁移：改造 ToolSandbox/AppWorld 或一个真实 API sandbox。

当前状态：**值得正式立项，但还需要 1-2 天补完整实验才能写成 AAAI 主会级别的强稿。**

