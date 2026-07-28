# AI 补充核查：主文阶段（仅 8 页主文）

范围：本文件仅依据 `paper/AnonymousSubmission2027.pdf` 全部 8 页；尚未读取补充材料或 reproducibility checklist。以下不含总体评分或接收建议。

## 核心故事与形式化

1. **No issue found（主文支持）**：核心 estimand 清楚区分 `bound(e0)` 与 `deferred(qr)`，并把世界状态、指称控制状态和动作有效性分开；可执行核心的目标函数与 Preserve/Reevaluate 的语义一致。引用：第 2 页 “Temporal Referent Integrity and Evaluation Identifiability”，式 (1)-(2)；第 3 页式 (3)。

2. **Clarification needed（主文限定）**：“两行充分且最小”的可识别性结论只在 `{Always-Lock, Always-Reevaluate, Selective}`、确定性、精确目标这一受限策略类中成立，但 `Selective` 的函数类在主文没有形式定义；若允许按任务内容记忆、随机策略或其他混合策略，两行不能一般性识别“选择性重解析能力”。作者已写出部分限定，但标题式措辞仍容易被读成一般 identifiability 定理。引用：第 3 页 “Restricted identifiability observation”，表 1，式 (4)。

3. **No issue found（主文支持）**：PairAcc 的定义、Fréchet 型上下界及“边际不能决定联合正确率”的叙述数学上相容；Always-Lock/Always-Reevaluate 在 changed-winner 配对上均为 0 的例子也与定义一致。引用：第 3 页式 (4) 与表 1；第 4 页图 2、“Policy Discrimination”。

4. **Clarification needed（需补充材料）**：主文称 Preserve/Reevaluate 配对共享 `S0,S1,q,a`，仅语言表达改变承诺时点；但主文没有给出完整模板、生成约束和配对审计，尚不能排除条件可由表层措辞直接识别，或不同条件含额外提示。Rule* 在 authored inventory 达 92.5% 且 source-derived 仅 2/30 PairAcc，正说明“时点语义”与“模板事件顺序线索”可能混杂。引用：第 3 页 “Diagnostic Construction”；第 4 页 “Controller Probes”；第 6 页 “Representation and rule boundaries”。

## 算法、接口与实验解释

5. **Confirmed issue（主文可确认的解释边界）**：Decision-visible 干预是 predicted mode、bound ID、selector restatement 的复合 block，并且在 actor 前已经供应 initial ID，因此其增益不能归因于单个字段，也不能证明系统端到端学会了初始 grounding。主文已诚实承认这一点，但摘要/结论中的“explicit timing block improves”应始终按复合、post-binding 干预理解。引用：第 4 页 “Controller Probes”；第 5 页 “Matched-Call Decision Visibility”；第 7 页 “Limitations”与“Conclusion”。

6. **Confirmed issue（主文可确认的因果限制）**：primary Generic vs Lifecycle-Gated 同时改变控制器结构和调用次数，是 package-level、call-asymmetric 对比，不能识别 timing field 的独立效应。主文明确披露，后续 matched-call 对比仅缓解其中一部分。引用：第 4 页 “Controller Probes”；第 5 页 “Primary Package Comparison”；第 7 页 “Limitations”。

7. **Likely issue（主文限定）**：conditional substitution 只纳入初始 ID 正确、刷新完成、winner 改变且旧目标仍有效的后处理子集。该指标适合定位“正确绑定后的替换”，但控制器若改变进入该子集的概率，shared-eligible 比较可能产生选择效应；不能把 41/66、30/70、50/69 解释为总体错误率或一般安全率。图注已声明其为 conditional diagnostic endpoint。引用：第 3 页 “Observable substitution”；第 5 页 “Conditional Target Substitution”与图 3。

8. **No issue found（主文数值一致）**：摘要的 shared-eligible substitution 数字 41/66、30/70、50/69 与第 5 页正文及图 3 一致，CTA 均为 0；matched-call authored PairAcc 的 Qwen 5/32→13/32、GLM 8/32→25/32 也在第 1、5 页一致。引用：第 1 页摘要与 Introduction；第 5 页图 3、“Matched-Call Decision Visibility”。

9. **No issue found（主文数值一致）**：SQLite 40-task 分解与图 4 对齐：Qwen 27 correct + 8 strict TRI writes + 5 fallback writes = 40；GLM 26 + 6 + 2 + 6 rejects = 40。Stable 0/4、Changed 8/8 和 6/8 与正文、图注一致。引用：第 5 页 “Executed Target Consequences”；第 6 页图 4。

10. **Clarification needed（需补充材料）**：固定 executor 将选中 target 应用于 refreshed state，只验证 target-to-write 一致性，不是 model-facing 工具使用证据；真正 model-facing SQLite 仅 40 题。主文区分了两者，但“at scale”可能被误读为 240 题均经过模型工具循环。引用：第 3 页 “Measurements and Denominators”；第 5 页 “Executed Target Consequences”。

11. **Likely issue（主文限定）**：主文报告多组 post-primary bootstrap 区间和 McNemar 辅助检验，但未定义 multiplicity-adjusted confirmatory family；因此除 frozen primary estimand 外，区间不宜作确认性显著性证据。主文已将其标为 descriptive/post-primary。引用：第 3 页 “Measurements and Denominators”；第 4 页 “Evidence Status”；第 5 页 matched-call 结果。

12. **Clarification needed（需补充材料）**：cluster bootstrap 的 cluster 定义称随 state 或 workflow 变化，但主文未逐实验说明重采样单位、重复数、seed、区间算法及小 cluster 数情形；图 5 的横纵区间也不是联合置信域。引用：第 3 页 “Measurements and Denominators”；第 7 页图 5。

## 证据范围、替代解释与可复现性

13. **Confirmed issue（主文可确认的外推边界）**：authored cross-schema 仍保留 authored language templates；source-derived tasks 也保留 author-supplied timing contrasts；public-suite retrieval 未校准自然召回率，且未找到 strict native opportunity。因此实验支持“受控诊断能区分策略及暴露替换错误”，不支持该错误在真实 benchmark/部署中的 prevalence。引用：第 6 页 “External Coverage and Composition”；第 7 页 “Limitations”。

14. **Likely issue（替代解释）**：CTA/Decision-visible 的收益可由更直接的事件顺序提示、额外中间推理监督或格式约束解释，而不必是持久“referential control state”的机制性改进。Rule* authored 高分但迁移差、oracle 分解显示 unseen-schema 主要损失来自 bound-ID grounding，均支持此替代解释。引用：第 6 页 “Representation and rule boundaries”；第 6-7 页 “Discussion/Limitations”。

15. **Clarification needed（人类构念效度）**：早期 convenience sample 对 dynamic identity 的一致率高，但 action-invalid fallback 仅 55%；另一个 frozen follow-up 未通过 eligibility gate，保留标签的一致率仅 38.6%。因此人类证据不能普遍验证全部构念，尤其不能固定 Reject/Clarify/reselection 的唯一 gold。引用：第 4 页 “Construct Scope”；第 7 页 “Limitations”。

16. **No issue found（主文对 claim 的约束）**：正文没有把 source-derived null、public-suite 无 native case 或 human mixed evidence 隐去，且明确把 open-language generalization、native prevalence、single-refresh scalar scope 留作未决；结论基本没有超出这些限定。引用：第 1 页摘要；第 6 页 “Discussion”；第 7 页 “Limitations/Conclusion”。

17. **Clarification needed（相关工作，仅稿内可核）**：主文对 Entity Binding、Binding Drift、temporal-agent benchmarks、runtime ledgers/monitors 的区别主要是概念性陈述，没有提供逐项实验维度对照；在不查外部文献的前提下，无法核实 novelty distinction 是否完整。引用：第 2 页 “Related Work”。

18. **Clarification needed（复现性，待补充核验）**：主文声称匿名 artifact 含 frozen inventories、prompts、raw outputs、reports、hashes 与 error taxonomy，但正文未给出模型 endpoint/revision、完整参数、parser、失败处理和数据生成细节。尤其 provider weights 无 immutable revision IDs，限制严格复现。引用：第 4 页 “Evidence Status”；第 7 页 “Limitations”。

## 主文阶段易误读点

- **Clarification needed**：PairAcc 是 changed-winner pair 的 joint correctness，不是全体任务 accuracy；图 2 三列分母分别为 80、80、32。引用：第 4 页图 2。
- **Clarification needed**：conditional substitution 的 41/66 等是 shared-eligible 条件比例，不是 240-task 总体失败率。引用：第 5 页图 3。
- **Clarification needed**：240-task fixed-executor replay 与 40-task model-facing SQLite loop 是两类不同证据。引用：第 3 页 “Measurements and Denominators”；第 5 页 “Executed Target Consequences”。
- **Clarification needed**：Figure 5 的两个 95% 区间是分离的边际区间，不是联合置信域；只有 source/GLM 的 E2E 区间排除 0。引用：第 6 页 “Source-derived pairs”；第 7 页图 5。
