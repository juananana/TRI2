# 指标、分母与不可混用规则

| 指标 | 分母 | 回答的问题 | 不能代表什么 |
|---|---|---|---|
| E2E exact target / final state | 全部 ITT rows；API/parse/missing 为失败 | 整体任务是否完成 | 不能单独定位 TRI；会混合 binding、tool order、Reject 等错误 |
| Initial binding accuracy | 有 observable pre-refresh binding 的 rows | 刷新前是否正确解析目标 | 正确 binding 不保证后续保持，也不适用于无 sidecar history |
| Changed-winner PairAcc | 同一 changed state cluster 的 Preserve 与 Reevaluate 两条都正确 | 是否同时排除 Always-Lock 与 Always-Reevaluate | 不是单条任务 accuracy；不同 pair 数不能无权重 pooling |
| Stable accuracy / PairAcc | selector winner 刷新前后不变 | 是否对 refresh 过度反应 | 不能识别 selective policy；两个无条件极端都可能满分 |
| Conditional substitution | 正确 observable initial binding + refresh complete + old target survives/action-valid + winner changes | 已正确绑定后是否未授权改成 refreshed winner | 不是总体成功率；0/N 不排除上游和非-core wrong writes |
| Shared-eligible substitution | Generic 与 CTA 在同一任务都满足正确初始绑定 | 排除 controller-specific denominator selection | 仍然是条件分母，不能和 E2E 直接比较高度 |
| Wrong-entity write | 实际或 deterministic executor 将 action 写到非授权 ID | 错 target 是否产生执行后果 | 所有 wrong write 不都是 TRI；需分 core/fallback/non-core |
| Reject / invalid attempt | author-specified invalid-target slice 或 tool rejection | fallback policy 与执行可行性 | 人类语义支持弱于 actionable referential core |
| Repair / harm | task-matched transformation 前后由 wrong→right / right→wrong | enforcement 的净变化组成 | repairs−harms 不是 actor visibility effect；enforcement 是 post-processing |
| Human majority–gold | 按 study 的 item 与有效 annotator 规则 | 人类是否恢复 benchmark gold | failed-gate、不等 rater 数或 post-hoc relaxed slices 不可合并 |

## 统计口径

- v3 主要以 20 个 language-template clusters bootstrap。
- v7 主要以 40 个 state clusters bootstrap。
- matched-call full diagnostic 以 80 matched clusters；source-derived 以 30 pairs；rewrite 有
  43 clusters，但只有 3 complete actionable changed pairs。
- 区间通常为 10,000 次 cluster bootstrap；图中必须说明 effect CI 还是 condition CI。
- “区间触及 0”与“区间排除 0”严格区分；不要用星号替代实际 interval。

## 证据状态视觉规则

| 状态 | 允许的图中措辞 | 禁止的措辞 |
|---|---|---|
| primary/frozen | primary package effect | component mechanism proven |
| post-primary replication/audit | replicated/audited under frozen own protocol | primary、independent natural prevalence |
| post-hoc | post-hoc rule/residual audit | held-out method superiority |
| failed frozen gate | descriptive failure/boundary | human validation result |
| planned/unverified | planned only | result、trend、expected gain |
