# TRI 外部证据补强与克制化叙事审计

> 日期：2026-07-24  
> 状态：Track A 已完成且无严格原生阳性；另行冻结的 STATE-Bench/AgentDojo source-anchored Track B 已完成，得到单仓库有限阳性  
> 目标：补强外部成立性，同时保持 TRI 为受控 evaluation/diagnostic contribution

## 0. 2026-07-24 执行更新

- 已按冻结协议扫描 API-Bank test 528 units、BFCL multi-turn 800 variants/200 clusters 和
  ToolTalk 50 dialogues；结果为 **0 strict native opportunities**。
- 确定性检索保留 BFCL 57 和 ToolTalk 23 个 source-anchored candidate clusters。该 80 条
  inventory 只授权候选标注，不满足 Track B 的完整 matched contrast 构造门槛。
- 初始 smoke 的 8 个 pair 在受限沙箱内全部发生 DNS `URLError`。协议允许的 transport-only
  repair 增加了只重试 transport/HTTP/timeout failure 的恢复路径，并保留原始失败行；修复后
  8/8 最新行通过 schema gate，full run 随即按原 inventory/prompt 启动。
- full run 曾在 84/160 unique pairs 时中断，随后仅补齐原先缺失的 76 pair，并按未变的
  inventory、prompt、runner 和停止规则达到 160/160。最终 168 raw attempts 保留 8 条早期
  sandbox-DNS 失败；latest-pair view 有 145 条 exact-schema 有效行和 15 条失败/无效行。
- 65 个候选具有两条有效模型标签，24 个发生模型分歧。strict-positive 并集/交集均为 0，
  因而协议不触发 strict-positive source verification；较宽的 source-eligible 并集/交集为
  25/1。这是可错的模型候选标注，不是独立复核、原生 opportunity、行为结果或 prevalence。
- `external_public_annotation_partial_v1.{json,md}` 保留为中断时的 failure-accounting 检查点，
  已由 `external_public_annotation_v1.{json,md}` 取代，不应引用为最终结果。
- 零 API 结构结果已进入 supplement、experiment registry 和 claim provenance；摘要、标题和
  主贡献没有升级为 external validation、natural prevalence 或 benchmark-wide undercoverage。
- 续跑严格使用已记录 hash 的 transport-repair runner，只补齐 76 个 missing pairs；未重试
  parse/schema failures，也未按已见输出调整候选、prompt、模型、解码或结果解释。
- 另行冻结的 source-anchored matched transfer 使用 STATE-Bench 和 AgentDojo 各 10 个工作流
  簇，形成 80 个任务、320 个模型--条件行。零 API 源工具检查为 80/80；full run 为
  306/320 valid，保留 14 个 GLM parse failures，且没有 transport/source-execution failure。
- 正确初始选择后的 Preserve/Changed 中，Qwen ordinary history 在 AgentDojo 为 2/7
  refreshed-winner substitutions，对应 Stable 为 0/7；STATE-Bench 全部对应切片为 0，GLM
  AgentDojo 也为 0。因此只能写成单一来源、单一模型/接口的 limited bridge evidence。
- execution record 没有稳定优势：shared-initial rows 上 GLM 为 52/59（ordinary 57/59），
  Qwen 为 63/65（ordinary 62/65）。该负面结果已进入正文、supplement、registry 和 provenance。

## 1. 当前缺口的准确表述

现有证据已经支持：在作者构造的单刷新标量诊断及其新 schema 复制中，部分测试控制器会在正确初始绑定后，把仍有效的旧目标替换为刷新后的 selector winner；该替换可被确定性重放为 wrong-entity write。

现有证据尚未支持：

1. 严格 TRI opportunity 在自然工具请求或真实流量中的发生率；
2. 受控 substitution 在多个外部来源、模型和接口中的稳定复现；
3. CTA、显式字段、特定序列化或 pre-refresh compilation 的唯一必要性；
4. 一般工具安全、所有模型的普遍失败或开放语言泛化。

当前外部证据不只是“样本少”，而是分布不平衡：一个 24-task ToolSandbox-compatible pilot 提供小规模、post-hoc 阳性；更低干预的 96-task ToolSandbox-style、custom AppWorld 和 sidecar-removal 条件均为零。新实验必须排除“作者生成器/控制接口造成现象”的替代解释，而不是单纯增加同分布任务数量。

## 2. 必须分开的三类外部证据

| 证据类型 | 数据来源 | 能支持的结论 | 不能支持的结论 |
|---|---|---|---|
| 严格原生机会审计 | 未经 TRI 团队改写的公开任务或轨迹 | 外部语料中存在/未发现符合 checklist 的机会 | 模型在该机会中必然失败；自然发生率（除非召回率经校准） |
| Source-anchored contrast set | 外部任务、工具 schema 和环境，加冻结的 matched transition/intervention | 诊断可迁移到外部任务基底和 API | 原生 benchmark 阳性；自然请求或真实流量发生率 |
| AI 生成或 AI 改写任务 | 强模型生成的指令、状态或轨迹 | 额外语言/组合压力测试 | 独立人类证据、自然请求、外部 prevalence |

论文不得把后三者合并写成“external positive data”。

## 3. Track A：AI 辅助的外部原生机会审计

### 3.1 研究问题

在独立发布的多轮工具任务或轨迹中，是否存在可观察的严格 TRI opportunity：刷新前已经解析到稳定 ID，中间发生状态更新，旧目标仍存在且动作有效，刷新后同一 selector 的 winner 改变，随后又发生同角色实体写操作？

该 Track 首先测试 **opportunity coverage**，不是控制器失败率。

### 3.2 优先数据源

1. **BFCL V3/V4 multi-turn**：官方材料提供 multi-turn/multi-step function calling 和 state-based evaluation，适合检查稳定 ID、服务状态与连续工具调用。  
   Source: <https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard>
2. **ToolTalk**：28 个工具、7 个插件和完整模拟实现，强调会改变外部世界的多步工具使用。  
   Source: <https://arxiv.org/abs/2311.10775>
3. **API-Bank evaluation set**：314 个手工标注的工具对话和 753 次 API 调用，可用于寻找自然多轮 referential timing motif。  
   Source: <https://aclanthology.org/2023.emnlp-main.187/>
4. **AgentDojo**：97 个任务、四类可变环境和确定性 state/utility 检查；适合筛选可执行写操作与稳定实体。  
   Source: <https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html>
5. **WebLINX**：约 100K interactions、2,300 个 expert demonstrations、150 多个真实网站；适合检查自然语言中的“先选定—页面变化—继续操作”模式，但通常缺少可复现数据库状态和稳定 ID，因此不能单独建立 strict wrong-write denominator。  
   Source: <https://mcgill-nlp.github.io/weblinx/>

**STATE-Bench** 可作为第二阶段 source-anchored 环境：它提供 450 个 stateful enterprise tasks、task-local database、工具和确定性状态断言，但官方明确披露任务由 LLM 合成，因此不能作为自然语言或真实流量证据。  
Source: <https://github.com/microsoft/STATE-Bench>

### 3.3 冻结标注 schema

每个语料单位必须保留来源版本、原始文本/轨迹和以下字段：

```yaml
source_dataset: string
source_version: string
unit_id: string
authorship_provenance: human | llm | mixed | unknown
prior_selector_query: true | false | unclear
observable_initial_id: true | false | unclear
binding_before_update: true | false | unclear
update_type: exogenous | sync | user | agent_induced | none | unclear
old_target_present_after_update: true | false | unclear
old_target_action_valid_after_update: true | false | unclear
distinct_refreshed_winner: true | false | unclear
same_referential_role: true | false | unclear
later_entity_mutation: true | false | unclear
instruction_timing: preserve | reevaluate | ambiguous | absent
target_level_outcome_observable: true | false | unclear
strict_native_opportunity: true | false
evidence_turns_or_steps: [string]
exclusion_reason: string
```

只有所有必要字段均为 `true` 且 timing 不为 `ambiguous/absent` 时，才进入严格 opportunity 分母。只出现 “same/it/that item” 或一般页面变化不能自动判为 TRI。

### 3.4 AI 标注流程

1. 冻结数据版本、完整 inventory hash、标注 prompt、模型、endpoint、temperature、max tokens、失败政策和停止规则。
2. 两个不同模型家族独立做高召回筛选；候选取并集，不以多数票提前删样本。
3. 对可机检字段执行确定性 verifier：事件顺序、稳定 ID、同角色、更新前后 winner 和最终 mutation。
4. 所有 AI 阳性、所有模型分歧样本及每个语料的分层随机阴性样本进入盲审。
5. 若没有独立人工盲审，只能称为 `LLM-assisted candidate discovery / author-verified descriptive audit`；不得报告独立 recall、自然 prevalence 或 independent human evidence。
6. 保存全部 AI 输出、解析失败和被排除候选，不得只保留阳性。

### 3.5 最低报告项

- 每个数据源的总单位数与逐级 funnel；
- 双模型候选数、交集/并集、分歧数；
- 严格阳性及 near-match 的完整 source IDs；
- 全部排除原因；
- 人工/作者复核精度和阴性抽查结果；
- 若没有召回校准，明确写 `count under this retrieval procedure`，不写 prevalence。

## 4. Track B：外部 source-anchored matched contrast

### 4.1 研究问题

当任务语言、工具 schema、数据库和 mutation API 来自独立 benchmark，仅加入冻结的状态 transition 和 Preserve/Reevaluate 最小对时，受控 substitution 是否仍出现？

该 Track 排除“仅由 TRI 自有 schema/生成器造成”的解释，但不能证明 native benchmark 或真实流量本来包含这些机会。

### 4.2 Go/No-Go 门槛

只有 Track A 或零 API 结构审计找到以下资源时才进入模型运行：

- 至少 8 个独立 workflow clusters；
- 至少 2 个外部 benchmark/environment；
- 每个 cluster 均有稳定 ID、可复现状态、同角色 selector 和目标级 mutation；
- 能构造 Preserve/Reevaluate × Stable/Changed 的完整四格；
- 不需要加入 TRI、CTA、commitment、authorization 等术语才能让普通 agent 执行；
- automatic gold、state diff 和 strict conditional denominator 全部通过零 API tests。

不满足即 **No-Go**，不能用 AI 生成的新任务填补并称为外部数据。

### 4.3 冻结实验设计

- 主接口：benchmark 原生或最接近原生的 ordinary full-history agent；
- 对比接口：仅在明确 claim 需要时加入一个控制器 probe；
- 主估计量：matched changed-winner PairAcc；
- 条件替换分母：正确可观察初始绑定、refresh 完成、旧目标仍存在且动作有效、distinct refreshed winner、后续 mutation 已尝试；
- 单独报告：initial binding、tool order、API/parse failure、invalid attempt、rejection、utility、wrong write；
- 全部尝试按 ITT 保留；不因 prompt/tool-order 失败删除行；
- smoke 后不得根据结果改 prompt、筛任务或新增规则。

### 4.4 结果解释

- 跨至少两个外部基底的阳性：支持“受控行为可迁移到外部 task/tool substrates”；不支持自然 prevalence。
- 只有一个基底或 post-hoc slice 阳性：作为小规模 bridge evidence。
- 干净零结果：进一步把行为诊断限定在当前受控 controller interface；必须保留。
- AI 标注或 AI 改写本身不构成模型行为阳性。

## 5. 正文克制化修改清单

2026-07-24 已在 `paper/AnonymousSubmission2027.tex` 做以下窄幅修改：

1. 将 “This distinction is easy to lose in LLM controllers” 改为测试接口可观察的 `can be lost in model-mediated controllers`；
2. 将 “Reliable tool use therefore needs ...” 改为 `These cases motivate ...`；
3. 从贡献项删除 Aggregate 与 Stable/单侧 proxy 的并列失败表述，并明确 Aggregate 在五个已测试候选集中均选择 PairAcc 最优候选；
4. 将 public-suite 结论限定为三个 pinned versions；
5. 将 shared-eligible 的 “excludes denominator selection” 收紧为只在这些 matched tasks 内 `addresses` 该解释；
6. 将实现结论从“需要 explicit decision”改为控制器需要能够访问 discourse-sensitive executable decision；
7. 删除 Generic 的内部机制式措辞，改为可观察的 binding-to-mutation propagation 描述；
8. 将结论中的 wrong-write 主张限定为 controlled replay 中 observed substitutions 的后果。
9. 将 v7 CTA 与 Lifecycle-Gated 的零 substitution 分开报告，并补齐 CTA 分母，避免把观测零值
   读成无条件保证；
10. 将 post-hoc rule 的解释收紧为“高诊断准确率不要求唯一学习算法”，不再把它写成已识别的
    成功机制；
11. 在正文外部边界中披露 API-Bank、BFCL、ToolTalk 的结构扫描与双模型标注均未产生 strict
    positive，并保留无独立 recall calibration 的限制。

若 Track A/B 尚未完成，标题、摘要和贡献中不得加入 `external validation`、`naturalistic prevalence`、`real-world failure` 或 `benchmark-wide undercoverage`。完成后也只能按上节对应证据类型升级措辞。

## 6. 建议决策

1. **立即可做且风险最低**：离线下载并结构化扫描 BFCL multi-turn、ToolTalk 和 API-Bank；先运行零 API parser/field-availability audit。
2. **仅在结构门槛通过后**：冻结双模型 AI annotation protocol，做 candidate discovery；不先承诺一定有阳性。
3. **最高价值但更重**：从 AgentDojo/ToolTalk/BFCL 中形成至少两个基底的 source-anchored matched contrast；这才可能增强行为外部成立性。
4. **不建议**：让强模型直接生成更多 TRI 指令并称为外部阳性；这只增加同类合成证据。
5. 当前日期已到实验截止边界。任何新模型/API run 必须先通过项目 Experiment Gate，并写明何种结果会 strengthen、narrow 或 overturn 论文结论。
