# TRI AAAI-27 术语去合成化与审稿风险控制

## 适配判断

- **采用**：AAAI 对 significance、novelty、soundness、relevance、clarity 和 reproducibility
  的评审维度。这些维度适合 TRI 的问题定义与诊断型贡献。
- **调整后采用**：AAAI-26 主赛道公开 rubric 是当前可核对的最近一届详细主赛道标准；
  AAAI-27 页面和本地 2027 Author Kit 用于确认当前截止时间和格式要求。
- **拒绝**：不把 TRI 改写成算法模块故事，不增加实验，不扩大安全性、普遍性或真实流量发生率主张。

## 审稿人可能的评价

| 评审维度 | 当前术语风险 | 可能的审稿意见 | 修改目标 |
|---|---|---|---|
| Significance | 大量新复合词让一个核心诊断看起来像许多局部指标 | “The paper introduces substantial terminology for a narrow phenomenon.” | 显示一条主链：授权差异 -> 成对诊断 -> 替换 -> 写入后果 -> 边界。 |
| Novelty | 名称数量可能被误读为通过命名制造新意 | “Several terms appear to rename conditions rather than add a new concept.” | 只保留 TRI、PairAcc 和 Preserve/Reevaluate 等正式对象。 |
| Soundness | cohort、endpoint、provenance 被压进一个短语 | “It is difficult to tell whether these results use the same denominator.” | 用从句明确 eligibility；同一段只讨论一个分母。 |
| Clarity | changed-winner、shared-eligible、strict-opportunity 等需反复拆词 | “The presentation is dense and requires repeated backtracking.” | 图内放指标，caption 放分母，正文放证据状态。 |
| Reproducibility | 同一设计出现 matched-call、equal-call、call-matched 等近义写法 | “Condition names are not consistently mapped to the artifact.” | 正式实验名保留一次；正文使用一个规范化称呼。 |
| Scope | source-derived、native-opportunity 可能让作者改造任务看似原生任务 | “The relation to upstream benchmarks is unclear.” | 明写“pairs adapted by the authors from public benchmark states and schemas”。 |

## 规范化术语表

### 保留的正式术语

- Temporal Referent Integrity (TRI)
- Pair accuracy (PairAcc)
- Preserve / Reevaluate
- conditional substitution
- Always-Lock / Always-Reevaluate
- Lifecycle-Gated、History-only、Decision-visible（实验条件名，仅在首次出现时保留完整名）

### 主文显示用语

| 旧写法 | 规范写法 | 说明 |
|---|---|---|
| changed-winner PairAcc | PairAcc when the selector winner changes | 条件展开为从句。 |
| shared-eligible rows | rows eligible under both controllers | 明确是谁共享 eligibility。 |
| strict-opportunity rate | rate among cases meeting the strict eligibility conditions | 不创造新的指标名。 |
| cross-schema tasks | tasks spanning ten schemas | 首次给出实际范围。 |
| model-facing SQLite test | SQLite tool-loop test | 直接说明实验是什么。 |
| matched-call comparison | equal-call comparison | 与实际控制变量一致。 |
| source-derived pairs | pairs adapted from public benchmarks | 明确是作者改造，不是官方 benchmark 结果。 |
| native-opportunity coverage | coverage in native tasks | eligibility 在句中解释。 |
| fallback-policy writes | writes in fallback cases | 避免把 slice 包装成新 policy。 |
| wrong-target writes | writes to the wrong target | 正文用普通短语，图例可保留短标签。 |
| task-model rows | combinations of task and model | 普通表达。 |

## 信息分层规则

1. **图内**：只保留指标、轴、模型和结论性数值。
2. **图注**：定义 cohort、分母、置信区间和 scope。
3. **Results**：报告比较、精确计数和直接边界。
4. **Methods / Supplement**：保留完整 eligibility、实验条件名和 provenance。
5. 同一概念不混用 `matched-call`、`call-matched`、`equal-call`；主文统一为
   `equal-call comparison`，首次出现时映射到正式条件名。

## 不变项

- 所有数值、分母、区间和证据状态不变。
- 不改变 TRI、PairAcc 的定义和公式。
- 不把 post-primary 或 post-hoc 证据升级。
- 不把作者适配的 public-source pairs 写成原 benchmark 结果。
- 不修改 AAAI style、边距、字号或行距。

