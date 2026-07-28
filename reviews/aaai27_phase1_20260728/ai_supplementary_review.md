# AI Supplementary Review（匿名稿事实与技术核查）

核查范围：已完整阅读主文 8 页、补充材料 32 页及 Reproducibility Checklist 2 页，并逐页检查 PDF 版面；仅用对应 `.tex` 作为位置辅助。未读取其他 reviewer 文件，未查询外部资料。本文不含总体评分或接收建议。

标记中的“主文”“补充”“主文+补充”表示证据来源；补充材料不能倒推为主文独立可见的支持。

## 核心定义、形式化与度量

1. **No issue found【主文+补充】**：TRI 的核心故事内部一致：`bound(e0)` 表示刷新前已承诺的身份，`deferred(q)` 表示刷新后才求值；动作有效性 `Va` 与指称身份被分开，Remove/Invalidate 另列 fallback-policy slice。引用：主文第 2-3 页，式 (1)-(3)；补充第 1 节（第 1 页）、表 2（第 3 页）。

2. **No issue found【补充支持】**：主文“两行充分且最小”的简短 claim 在补充中给出完整论证，且明确只适用于确定性、exact-target 的 `{Always-Lock, Always-Reevaluate, Selective}` 三策略类，并非任意随机控制器下界。该限定足以支撑文中的受限 observation。引用：主文第 3 页 “Restricted identifiability observation”；补充第 1.3 节（第 4 页）。

3. **Clarification needed【主文+补充】**：`Selective` 在证明中实质上被定义为 oracle 行为 `Preserve→e, Reevaluate→e'`，因此“identifies selective authorization”应读作区分这三个预设策略输出，而不是从两题识别一般控制器的内部机制。读者很容易把 “Identifies? Yes” 外推为更强结果。引用：主文表 1（第 3 页）；补充第 1.3 节 Observation/Argument（第 4 页）。

4. **No issue found【主文+补充】**：PairAcc 定义为完整配对的共正确率；式 (4) 的上下界与边际不决定联合分布的叙述正确。ITT 把 API/parse/missing 输出计错，changed-winner、Stable 与 invalidity slice 的分母也在补充中分开。引用：主文式 (4)（第 3 页）；补充第 1.3 节（第 4 页）、表 15-16（第 11-12 页）。

5. **No issue found【补充】**：论文没有提出渐近时间/空间复杂度 claim；仅报告请求数和延迟。160 题上 Generic 为 320 requests/model，Lifecycle-Gated 为 240，符合表 5 的 2-call 与 1-or-2-call 流程；作者也没有把网络延迟称为受控系统 benchmark。引用：补充表 5（第 6 页）、第 9 节（第 27-28 页）。

## 控制器与接口逻辑

6. **Confirmed issue【主文+补充】**：primary Generic vs Lifecycle-Gated 同时改变表示、执行 gate 和调用数，不能识别 timing field 或某单一组件的因果效应。补充 component ladder 显示 mode-only、validity gate、untyped plan、CTA、Lifecycle-free 各自表现不同，进一步确认它只能是 package contrast。引用：主文第 4 页 “Controller Probes”、第 5 页 “Primary Package Comparison”；补充表 5、9（第 6、9 页）及第 3.2 节（第 11 页）。

7. **Confirmed issue【主文+补充】**：matched-call Decision-visible 仍是 `mode + bound ID + selector restatement` 的复合 intervention；History-only 与 visible actor 都已收到 `initial_selected_id`。它检验的是正确初始选择已显式供应后的表示/显著性效应，不能证明端到端 grounding，也不能分离三个字段。引用：主文第 5 页 “Matched-Call Decision Visibility”、第 7 页 Limitations；补充第 2.3 节（第 7 页）、表 22（第 15 页）。

8. **Likely issue【补充】**：Decision-visible actor 的 system prompt 明说“若 compiler_decision 存在则 follow it”，所以改进也可由更强指令服从/显著性产生，而非建立了持久的 referential control state。760/760 的 initial ID 和 selector 内容相同只能排除新增事实信息，不能排除 framing。引用：补充第 2.3 节 prompt（第 7 页）、“Decision-block stratification”（第 15 页）。

9. **No issue found【补充】**：Lifecycle-Gated 的控制流在 scalar case 内自洽：Preserve 先校验 bound ID 的动作有效性，有效则直接输出，无效按编译 fallback；Reevaluate/未决分支交给 actor。作者也明确 Action-Validity Stress Test 的 guard 字段不属于 scalar 主诊断。引用：补充第 2 节及表 4（第 5-6 页）。

10. **Likely issue【主文+补充】**：authored inventory 的条件可由事件顺序和有限词表直接判别。post-hoc Rule* 在 authored 160/50/240 集达到 92.5%/96.0%/91.7%，但在 source-derived 仅 15/60、2/30 PairAcc；因此 CTA/Lifecycle 的高分可能部分来自模板 cue 与格式化中间监督，而非开放语言下的普遍指称能力。引用：主文第 6 页 “Representation and rule boundaries”；补充表 10-12（第 9-10 页）。

## 数字、图表与实验蕴涵

11. **No issue found【主文+补充】**：cross-schema shared-eligible substitution 数字完全一致：Qwen 41/66、GLM 30/70、DeepSeek 50/69，CTA 均 0；Generic→CTA changed PairAcc 为 7→31/80、15→66/80、17→64/80。引用：主文摘要、第 5 页图 3；补充表 25（第 18 页）。

12. **No issue found【主文+补充】**：fixed-replay wrong-write 分解一致。Generic conditional TRI writes 为 43+38+59=140，总 wrong writes 为 44+38+60=142；CTA TRI writes 为 0，总 wrong writes 为 8+14+17=39。引用：主文第 5 页 “Executed Target Consequences”；补充表 24（第 17 页）、图 6（第 18 页）。

13. **No issue found【主文+补充】**：40-task model-facing SQLite 分解守恒：Qwen `27 correct + 8 strict TRI + 5 fallback = 40`；GLM `26 + 6 + 2 + 6 rejects = 40`。Changed/Stable 条件写入为 Qwen 8/8 vs 0/4、GLM 6/8 vs 0/4。引用：主文图 4（第 6 页）；补充图 7（第 21 页）。

14. **Clarification needed【主文+补充】**：240-task fixed executor 只是把冻结 target 映射为 deterministic SQLite write；真正 model-facing mutation loop 只有 40 题。两者都能证明错误 target 会写错实体，但只有后者证明模型实际发出工具调用。引用：主文第 3 页 “Measurements and Denominators”、第 5 页 “Executed Target Consequences”；补充图 6（第 18 页）、第 5 节（第 19-20 页）。

15. **Likely issue【主文+补充】**：conditional substitution 是后处理子集：必须先有正确 initial ID、成功 refresh、changed winner、旧目标仍 present/action-valid。它适合机制定位，但 controller 会影响进入该分母的概率；不同方法 denominator 不同（如 72/71、80/70），因此不能当总体风险率，也不能单独作无偏方法比较。引用：主文第 3 页 “Observable substitution”；补充表 24-25（第 17-18 页）。

16. **No issue found【主文+补充】**：matched-call authored 效应与补充一致：Qwen PairAcc 5/32→13/32、E2E 100/128→106/128；GLM 8/32→25/32、102/128→120/128。source-derived 中只有 GLM E2E 区间排除 0，Qwen 为零效应、DeepSeek 跨零。主文没有把异质性隐藏。引用：主文第 5-7 页、图 5；补充表 21（第 14 页）、表 28-29（第 20-21 页）。

17. **No issue found【补充】**：重复、composition 与失败结果均被保留：两刷新 scalar Lifecycle 低于 Generic；role indexing 只在 Qwen 改进且 GLM 有 transport failure；Event Graph/Executable Selector 未通过 go/no-go；temperature-zero 三次并非逐题确定。引用：补充第 7-8 节（第 26-27 页）。

18. **Likely issue【主文+补充】**：主要置信区间以 authored template/state cluster 为重采样总体，不能产生自然语言或部署流量的抽样外推。补充的 two-way pigeonhole、leave-group-out 和 subsampling 对“观察库存内稳健性”有帮助，但都是 post-primary 且不增加独立自然机会。引用：主文第 3 页 “Measurements and Denominators”；补充第 4-4.1 节（第 13-14 页）、第 8 节 sensitivity（第 27 页）。

19. **Likely issue【主文+补充】**：除 frozen primary 外，大量 post-primary 区间、slice、McNemar 与 oracle 审计没有全局 multiplicity correction；应作为探索性证据，不宜用单个区间排除 0 来暗示确认性发现。作者和 checklist 已明确承认。引用：主文第 3-4 页 “Measurements/Evidence Status”；补充第 4 节（第 13-14 页）；Checklist 第 4.12 项（第 2 页）。

20. **Confirmed issue【补充】**：Model-Authored Linguistic Stress Audit 在看到原 parser 因双连字符把所有行误判为错后，冻结并应用 transport repair，再称“all 48 rows remain in ITT”。保留全部行不等于保留原冻结分析规则；修复后的表 39 是合理的 post-hoc repaired sensitivity，但不应再称原协议意义下的 ITT 结果。引用：补充第 12 节、表 39 及其后 transport-repair 段（第 31 页）。

## 外部效度、人类证据与相关工作

21. **No issue found【主文+补充】**：外部效度 claim 整体克制。source-derived/STATE-Bench/AgentDojo/ToolSandbox 都是 author-adapted contrasts，不是 native benchmark score；public-suite strict opportunity 为 0 也没有被解释为部署 prevalence 为 0。引用：主文第 6-7 页 Discussion/Limitations；补充表 3（第 4 页）、第 6.3-6.5 节（第 24-26 页）。

22. **Confirmed issue【主文+补充】**：public-suite coverage 的自然召回率未独立校准。30 positive/30 one-feature-negative injected controls 只验证 checker code path；model-assisted triage 也不是独立人工审计。因此“六套件未发现 strict native opportunity”只能是该检索流程下的零计数，不能证明真实不存在。引用：主文第 6-7 页；补充第 6.2-6.3 节、图 9（第 22-24 页）。

23. **Confirmed issue【主文+补充】**：human construct evidence 不能验证完整 gold policy。早期三人样本对 Dynamic 为 98%，但 Anchored Reject 仅 55%；六表 follow-up 未达到每题五个有效标签，合格 referent/execution agreement 仅 38.6%/25.8%，冻结的 κ、α 和 PairAcc endpoint 均不可用。引用：主文第 4 页 “Construct Scope”、第 7 页 Limitations；补充表 34-35（第 28-29 页）。

24. **Clarification needed【补充】**：人类研究没有 formal institutional review 或 exemption determination，recruitment channel、与团队关系、确切报酬与实际用时也未记录；这不推翻去标识化结果，但构成伦理审查与复现背景缺口，需由会议政策判断是否可接受。引用：补充第 10 节 “Blind Human Construct Validation”（第 28 页）。

25. **Clarification needed【主文】**：仅依据投稿内容，相关工作区别是概念层面的：Binding Drift 固定已承诺 referent，TRI 交叉 Preserve/Reevaluate 并新增 opposite-gold PairAcc；runtime ledger/monitor 被定位为实现路径。由于禁止外查，无法核实引用论文内容和 novelty coverage 是否准确或完整。引用：主文第 2 页 “Related Work”。

## 可复现性与 checklist

26. **No issue found【补充】**：补充提供了 literal matched-call prompts、严格 JSON parser、failure-as-error 规则、cluster seed/10,000 draws、model IDs、temperature、thinking、token cap、日期、Python/pytest/OS，并给出 artifact audit 命令；就“从冻结输出重建分析”而言信息较充分。引用：补充第 2.3 节（第 6-7 页）、第 4 节（第 13-14 页）、第 13 节（第 31-32 页）。

27. **Confirmed issue【补充】**：exact API inference 不可严格复现：provider 不提供 inference seed、immutable weight revision 或 serving hardware；temperature zero 的三次逐题一致率也只有 70.0-97.5%。冻结 raw outputs 可复算既有结果，但不能保证重新调用得到同一行为。引用：补充第 8 节 “Temperature-zero repeat stability”（第 27 页）、第 13 节 “Model and environment provenance”（第 32 页）；Checklist 第 4.7-4.8 项（第 2 页）。

28. **Clarification needed【补充】**：本次允许来源不含单独 Code and Data Supplement，故无法独立确认稿中所称 inventories、raw outputs、hash manifests、scripts 与 tests 是否齐全或命令是否实际通过；这里能确认的只是 PDF 对 artifact 内容的声明。引用：补充第 13 节（第 31-32 页）；Checklist 第 3.3、4.3-4.6、4.13 项（第 1-2 页）。

29. **Confirmed issue【Checklist】**：Checklist 第 2.1 对“是否有 theoretical contributions”回答 `NA`，但主文明确提出 restricted identifiability observation，且随后 2.2-2.8 又回答其假设、形式化和 proof。即使作者把它称为 elementary deduction，`NA` 与稿件及后续答案结构不一致，建议改为 `yes`。引用：Checklist 第 2.1-2.4 项（第 1 页）；补充第 1.3 节（第 4 页）。

30. **No issue found【视觉核查】**：主文 8 页、补充 32 页和 checklist 2 页未见文字/公式/表格裁切、重叠、缺图或页码错误；主文图 1-5、补充图 1-9 与表 1-39 均可读。引用：三份 PDF 全页视觉检查。

## 最可能的 reviewer 误读

31. **Clarification needed【主文+补充】**：PairAcc 不是 160/240 rows 的普通 accuracy；主文图 2 三列分母分别为 80、80、32，cross-schema changed PairAcc 分母为 80 pairs。引用：主文图 2（第 4 页）；补充表 16（第 12 页）。

32. **Clarification needed【主文+补充】**：`0 substitutions` 是观察到的条件计数，不是 population risk 为 0，也不是无 wrong writes；CTA 在 cross-schema 仍有 39 个 non-core wrong writes。引用：主文图 3（第 5 页）；补充图 6、表 25（第 18 页）。

33. **Clarification needed【主文+补充】**：Rule* 是看过 authored inventories 失败后写成的 post-hoc benchmark-aware rule；其高 authored 成绩不能作为 held-out generalization，但其 source-derived 失败也不能否定 TRI 定义本身。引用：主文第 4、6 页；补充表 10-12（第 9-10 页）。

34. **Clarification needed【主文+补充】**：Figure 5 的横纵 whisker 是两个单独 cluster-bootstrap 区间，不是 joint confidence region；“both endpoints improve”区域也不是联合显著性判定。引用：主文图 5（第 7 页）；补充表 21、28（第 14、20 页）。

35. **Clarification needed【主文+补充】**：本稿最强支持的是“受控配对诊断能区分互补固定策略，并在特定 controller 中定位正确绑定后的替换”；它不支持 native prevalence、开放语言泛化、唯一必要架构或部署安全率。引用：主文摘要、Discussion、Limitations（第 1、6-7 页）；补充表 3（第 4 页）、图 9（第 23 页）。
