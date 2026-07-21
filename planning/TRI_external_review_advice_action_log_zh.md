# 外部评审建议提取与落实记录

更新时间：2026-07-21（收尾核验）

## 总体判断

评审意见的核心判断可信：论文当前是“证据完整但新颖性和外部有效性可能引发分裂”的 borderline 稿件。最有效的改进不是增加复杂方法或更多同质合成任务，而是强化 transition authorization 的理论辨识度、统一指标分母、提升人类稳健性、正面比较 Binding Drift，并建立从受控诊断到真实工具 substrate 的外部桥梁。

## P0：已落实

| 建议 | 判断 | 已执行修改 |
|---|---|---|
| 将核心变量改写为 post-binding transition authorization | 高价值 | 正文先定义 `U(q)` 未解析查询、`B(e)` 已绑定承诺和授权转移 `Gamma`；lifecycle tuple 降为一种实现 |
| 增加显式状态机和世界更新不推出目标变化的不变量 | 高价值 | 正文加入 `S_t != S_{t+1}` 不推出 `C_t != C_{t+1}`；formalization report 同步状态机 |
| 主打机制发现 + 诊断盲区，不主打 memory/controller | 高价值 | 论文贡献和正式进展报告均按 problem/diagnostic/evidence/minimal intervention 排序 |
| 统一所有 accuracy 和条件分母 | 高价值 | 主表改名 E2E；supplement v7 表统一报告 E2E、initial binding、conditional TRI、wrong writes、Stable controls |
| 用人类多数票和高共识子集重算 | 已有结果被低估 | 将 46 条 determinate majority 和 35 条 unanimous-gold 结果提升到正文；不需要重跑模型 |
| Preserve/Reevaluate 作为核心，Reject 降级 | 高价值 | 正文明确 Reject 只有 55% majority-gold、25% unanimity，是规范性 action policy |
| 与 Binding Drift 做逐维区别 | 必须 | 正文区分 lock、oracle reverify、learned self/cross reverify 与 TRI deferred query；不再把源码审计包装成 LLM 复现 |
| 外部 benchmark audit 加 checklist 和分层 | 高价值 | ToolSandbox 审计加入六项 checklist、strict/near/excluded 三层和单人审计限制；生成脚本同步 |
| 补 benchmark-compatible 外部正例 | 最高价值 | 对已有冻结 24-task ToolSandbox-compatible pilot 做 post-hoc 严格条件审计：GLM Generic 3/6 TRI、Stable 0/2；Qwen Lifecycle 2/6，gate replay 0/6 |
| 不过度宣称因果/内部机制 | 必须 | 将“main performance mechanism”改为“gain primarily associated with”；使用 behavioral/controller-level diagnosis |
| 复杂方法负结果不能完全隐藏 | 合理 | 正文继续保留 gate 增益小、复杂 M1/M2 不稳定的简要结论；详细表留 supplement |
| 用二维问题地图区分 Binding Drift 与 TRI | 高价值 | 正文明确“初始绑定正确性”和“刷新后重选授权”是正交轴；supplement 加入 2x2 矩阵 |
| 排除单一 schema/template 主导 | 高价值且零 API | 新增 v7 leave-one-domain/template-out 分析；三模型所有剔除差值均保持为正 |
| 将强后置提示解释为 practical re-resolution | 合理 | 正文和 supplement 明确其是最近邻近似，不冒充官方 Binding Drift self/cross 复现 |

## 新外部正例的严格边界

新结果使用 ToolSandbox 原生 reminder 数据库和 native search/modify 工具，但任务语义和同步事件是自定义干预。严格机会要求：

1. Preserve + Flip；
2. 编译出的初始 ID 等于冻结 manifest 的初始目标；
3. 旧目标刷新后仍存在；
4. 刷新后赢家是不同的稳定 ID；
5. 轨迹没有 protocol error；
6. 最终写入刷新后赢家才计 unauthorized rebinding。

该任务清单在模型运行前冻结，但严格条件审计是在已有输出后新增，因此必须标记 `post-hoc strict audit`。它能证明 TRI 不只存在于作者的 JSON/SQLite 标签环境，但不能证明官方 ToolSandbox 分布中的 prevalence，也不能作为 confirmatory 外部效应量。

## 本轮两份新增建议的裁决

### 已采纳并补入论文

- 用“初始绑定正确性 x 状态变化后重选授权”的二维矩阵定位 Binding Drift 与 TRI；
- 将现有 one-shot aware baseline 明确解释为 post-refresh re-resolution 风格的强近似，而不是官方 self/cross reverify；
- 新增逐领域、逐模板家族剔除敏感性。Qwen、GLM、DeepSeek 的所有剔除差值均为正；
- 在正式进展报告中明确 CTA 不负责修复错误初始绑定，也不宣称是更强的通用 Binding Drift defense；
- 继续保留 Qwen 与后置强提示总体持平、多指称不稳定、外部自然闭环为 null 等边界。

### 已有证据覆盖，无需重复调用模型

- 等调用/等思考控制：Generic 为两次调用，untyped pre-refresh plan、mode-only、post-refresh aware 和 CTA 已形成控制链；
- 编译器拆解：已有 mode、bound ID、selector/schema、actor/gate 阶段报告；
- oracle 与 learned 分离：oracle executor 和 Binding Drift gold reverify 均未进入 learned 主表；
- 去模板线索：已有 50 条独立人工改写、隐含表达、human-majority 与 unanimous-gold 重算；
- 聚类统计：主结果使用 10,000 次 cluster bootstrap，本轮再增加 leave-group-out；
- benchmark-compatible 正例：已有 ToolSandbox 原生数据库/API substrate 的冻结 24-task pilot 严格审计。

### 暂不采纳或不能据此宣称完成

- 不把 Always-Lock 直接改名为官方 Entity Lock；它只能称 matched policy analogue；
- 不把 aware one-shot 改名为官方 Binding Drift self/cross reverify；输入接口和原始任务目标不同；
- 不在没有冻结协议的情况下扩出 80--120 个外部任务追求正结果，现有 96-task null 必须保留；
- 不复现 Binding Drift 的四万次完整 sweep，也不以总准确率全面胜过它作为论文目标；
- 不依据二手建议直接加入尚未核验元数据的最新论文引用；相关表述先限制在已核验的 EvoArena、公开 benchmark 和 Binding Drift。

## P1：仍值得做，但需要新资源

### 1. Binding Drift practical reverify 适配

当前已复现官方确定性 25/25 断言，并确认 oracle reverify 读取 gold target。官方完整源码已确认在 `external_sources/binding-drift/`，commit 为 `0e040e0954b18d4621a6f9b16f6e6e9591c822e1`。硅基流动 OpenAI-compatible author adaptation 已完成 20-task 对称 smoke：Lock 为 Preserve 10/10、Reevaluate 0/10；GLM self-reverify 为 0/10、10/10；Qwen reverify 主要出现 14/20 selector-grounding errors；冻结 CTA 为 Qwen 12/20、GLM 17/20。

下一步只建议扩展 GLM verifier 到完整 160 条 core opportunity；Qwen 的 smoke 已被 selector grounding 主导，直接扩量信息增益低。扩展仍必须单独冻结并明确数据出境范围，不得把适配版称为官方结果。

### 2. 国际 frontier model 小切片

价值高于重复随机种子，但不是当前核心结论前提。建议 40--80 条核心配对，只跑 ordinary full history、final reminder、CTA。需要稳定可审计的 GPT/Claude/Gemini 接口和单独预算；不能用无法固定版本的 relay 结果进入主表。

### 3. 公开 benchmark 审计第二复核者

现有 per-scenario JSON、排除理由和候选 ID 已足以供复核，但没有第二标注者一致率。若能安排一名不了解作者标签的人复核所有 near-match 和随机 20% excluded 样本，可报告 strict/near 分类一致率。不能事后虚构双人审计。

### 4. 外部切片的 confirmatory 扩展

当前 24-task ToolSandbox pilot 只有六个 selector clusters，严格审计 post-hoc。更强版本应先冻结 2 个应用或 benchmark、20--30 个状态簇、Preserve/Reevaluate x Stable/Flip，并预注册条件分母。由于现有 96-task 后续扩展为 null，不能为了得到正结果不断改 prompt 或挑模型。

## P2：截止前不优先

- 再增加 200--500 个同质合成任务；
- 继续升级 Event Graph 或复杂 selector；
- 大规模随机种子笛卡尔积；
- 再增加一个同谱系普通模型；
- 把 null 外部结果删除或只展示正例。

这些工作不能直接解决 novelty 或外部有效性，且容易稀释论文主线。

## 对投稿判断的影响

本轮修改显著改善了两个最危险问题：

1. 理论上不再像“特殊 entity lock”，而是显式的目标转换授权状态机；
2. 实证上已有 benchmark-compatible 原生数据库/API substrate 的严格正例，不再只有合成诊断和外部 null。

但结果仍需克制：外部正例来自 post-hoc 小切片，方法优势不跨控制器稳定；Qwen Generic 为 0/6，Qwen Lifecycle-free 反而出现 2/6。论文仍应定位为 model/controller-conditional diagnosis，而不是普遍安全缺陷。

## 本轮收尾核验

- 相关新增与审计测试：`133 passed`；仅有 holidays 库的兼容性 warning。
- 主文保持 8 页（7 页正文 + 1 页参考文献）；补充材料加入二维问题地图和 leave-group-out 后仍为 9 页。
- `git diff --check` 通过；未发现把 96-task 低干预 null 外推为全部外部条件 null 的残留表述。
- 未宣称 Binding Drift 的 learned self/cross re-verification 已完成公平复跑；当前仅报告官方确定性断言审计和可比性边界。
