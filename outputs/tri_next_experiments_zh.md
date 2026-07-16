# TRI 下一轮实验计划与 AAAI 缺口

## 当前可以写进论文的结果

1. **主效应很强**：GLM-5.1 在 state-overwrite-once 控制器下，anchored+flip 只有 3.0% 正确，97.0% 漂移到刷新后新对象。
2. **机制特异性强**：同一控制器 dynamic+flip 是 100% 正确，说明不是一般动态环境失败。
3. **跨改写成立**：p0/p1/p3/p4 均 0% 正确；最显式 p2 也只有 20% 正确。
4. **未见领域成立**：heldout anchored+flip 20/20 失败。
5. **方法有效**：compile-then-act 在 13 个 anchored+flip 样本上 100% 正确。
6. **跨模型 pilot**：Qwen、DeepSeek、MiniMax 在 p0 小样本上均复现 state-overwrite 漂移；dynamic-flip 对照正确。
7. **实体失效边界**：anchored-removed 条件下，safe ledger 和 compile-then-act 能返回 invalid，不是盲目保持旧 ID。
8. **自然记忆强基线**：natural memory 在简单 p0 样本上也能修复 anchored-flip/removed，因此论文应诚实承认它是强 baseline。

## 还不能直接投 AAAI 的地方

1. Qwen、DeepSeek、MiniMax 还只是 p0 pilot，需要完整扩展矩阵。
2. compile-then-act 需要补 dynamic+flip，确认不会过度冻结动态指称。
3. natural memory 需要在压缩、噪声、预算限制和多实体任务上比较，不能只用简单 p0。
4. entity invalidation 需要扩展到 renamed、invalid_action 等条件。
5. 最好接入一个真实 agent framework 或模拟常见 summarizing controller。

## 推荐下一批实验

### E1 完整多模型主效应

模型：

- GLM-5.1
- Qwen3.5-397B
- DeepSeek-V4-Pro
- MiniMax-M2.5

条件：

- state_overwrite_once
- anchored+flip
- dynamic+flip
- dev + heldout
- all paraphrases

当前 p0 pilot 已证明不是单模型特性；下一步目标是证明跨改写、跨领域稳定。

### E2 方法完整性

模式：

- state_overwrite_once
- natural_language_memory
- oracle_ledger
- compile_then_act

条件：

- anchored+flip
- dynamic+flip

目标：证明 typed ledger 在更强压力下优于普通记忆摘要，并且不会把 dynamic 错误冻结。

### E3 失效实体

新增 update：

- `removed`: 预绑定实体刷新后消失；
- `invalid_action`: 预绑定实体仍存在但动作不合法；
- `renamed`: 实体 ID 稳定但名称变化。

目标：避免 ledger 被审稿人批评为“盲目保持旧对象”。

### E4 外部迁移

选项：

- 改造 AppWorld 风格 API；
- 改造 ToolSandbox 风格状态工具；
- 自建一个真实数据库/API sandbox。

目标：把合成机制迁移到更像真实工具环境的设置。

## 论文定位建议

不要写成：

> LLM agents fail in dynamic environments.

应该写成：

> Dynamic environments require agents to decide which references should update and which should remain bound. Current state-overwrite controllers can update observations correctly while still corrupting pre-bound user targets.

这个定位更窄、更新、更容易防撞题。
