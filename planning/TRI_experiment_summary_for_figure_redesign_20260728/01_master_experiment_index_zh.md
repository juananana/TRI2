# TRI 全实验主索引

## A. 受控主证据、可识别性与组件

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| A1 | v3 package comparison | 160 tasks；20 template clusters；Qwen primary、GLM replication；Generic vs Lifecycle-Gated | Qwen 64.4%→98.1%，差 +33.8pp [18.1,50.0]；GLM 71.9%→100%，+28.1pp [18.1,38.1] | `primary/frozen`；估计整套 controller package，不是组件因果分解 |
| A2 | v3 component addenda | 同一 v3 inventory；validity-only、mode-only、untyped plan、Historical CTA、Lifecycle-free | Qwen/GLM：Generic 64.4/71.9；mode-only 75.0/75.0；untyped 81.2/70.6；CTA 95.0/96.2；Lifecycle-free 96.9/98.1；Gated 98.1/100 | post-primary；支持“可执行 timing decision”，不支持唯一字段/架构 |
| A3 | crossed domain×template sensitivity | 完整 8×20 primary inventory；domain/template/two-way bootstrap | 最宽依赖区间在 Qwen、GLM 仍高于 0 | zero-API sensitivity；不增加自然样本独立性 |
| A4 | PairAcc / policy identifiability | v3/v7 matched Preserve–Reevaluate；Always-Lock/Always-Reevaluate controls | 两个极端均通过 Stable，但 v3 changed PairAcc 0/32、v7 0/80；Generic 也只有 v3 3/32、7/32 | 证明对称 PairAcc 的识别作用；Aggregate 不是形式识别指标 |
| A5 | evaluation-selection regret | 5 个冻结候选集×4 proxy regimes | 15 个 Stable-only/单侧 maximizer set 都包含 0-PairAcc 策略；最大 worst-case regret 100pp；修正后 Aggregate 在 5/5 候选集选到 PairAcc 最优 | zero-API；worst-case tie 不是实际开发者选择预测 |
| A6 | v7 core replication | 240 tasks；10 新 schemas；40 state clusters；Qwen/GLM/DeepSeek；Generic vs CTA | Generic E2E 47.5/70.0/73.8%，CTA 70.8/94.2/91.2%；changed PairAcc 7/15/17→31/66/64；conditional substitution 43/72、38/80、59/79→均 0 | post-primary frozen replication；受控 interface，不是自然 prevalence |
| A7 | v7 shared eligibility | Generic 与 CTA 同时正确初始绑定的同任务分母 | Qwen 41/66→0/66；GLM 30/70→0/70；DeepSeek 50/69→0/69 | 排除 controller-specific denominator selection；0/N 不是总体风险为零 |
| A8 | matched full-history baselines | v7 240 tasks×3 模型；ordinary history、final-step-aware history、CTA | E2E：Qwen 63.3/69.6/70.8；GLM 67.1/80.8/94.2；DeepSeek 68.8/75.8/91.2 | 强基线；history 无单独 pre-refresh ID，replacement 不能称 conditional TRI |
| A9 | Binding Drift author adaptation | v7 240 GLM rows；Entity Lock、self-reverify、CTA、Rule* | Preserve/Reevaluate：Lock 120/40；self-reverify 39/116；CTA 110/116；Rule* 110/110 | author adaptation，不是官方或信息匹配 comparison |

## B. Matched-call decision visibility

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| B1 | 40-pair call/base-payload-matched ablation | 80 rows/model；History-only、Decision-visible、Decision-enforced | Qwen PairAcc 12/40→20/40，subst. 16/28→4/28；enforcement repairs 4、harms 8。GLM 12/40→24/40，subst. 12/24→0；enforcement 不改变 target | post-primary；visibility 有益，hard enforcement 非普遍有益 |
| B2 | full-diagnostic matched-call audit | 160 rows/model；32 actionable changed pairs、128 actionable rows、32 Reject rows | Qwen PairAcc 5/32→13/32，E2E 100/128→106/128；GLM 8/32→25/32，102/128→120/128 | frozen before calls；Reject 分母单列 |
| B3 | decision-block stratification | 9 inventories、760 records；compiler correctness strata | initial ID、selector、actor copies 均 760/760 完全相同；correct-compiler strata 收益大，错误 compiler 可传播伤害 | zero-API post-treatment association；不能作 mediation/组件因果图 |
| B4 | human-rewrite matched-call | 50 rewrites；48 determinate majorities；40 actionable；仅 3 complete changed pairs | Qwen actionable E2E 30/40→30/40（0pp）；GLM 31/40→39/40（+20pp [8.6,32.5]） | one-volunteer authored-semantics transfer；PairAcc n=3 仅 sensitivity |
| B5 | three-source matched-call | 30 changed pairs；STATE-Bench、AgentDojo、ToolSandbox 各 10；3 模型 | PairAcc Qwen 12→13/30、GLM 11→20/30、DeepSeek 19→22/30；仅 GLM E2E +18.3pp [8.3,30.0] 排除 0 | source-derived controlled contrast；不是 native benchmark score |
| B6 | Rule* source-grounded transfer | 冻结 Rule* 直接应用 60 source-derived rows | 15/60 exact targets、2/30 PairAcc | post-hoc rule 的冻结外推；显示模板/解析 transfer 边界 |
| B7 | model-authored linguistic stress | 24 workflow specs→48 model-authored rows；两 model judges；Qwen/GLM controllers | Generic 24/48、0/24 PairAcc；CTA 36/48、12/24；但 judges 共同接受仅 11/48 且无完整 pair | 结果对 open-language transfer 不可判定；保留 transport-normalizer repair |

## C. 执行后果与错误归因

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| C1 | 40-task model-facing SQLite | 冻结 tool loop；Qwen/GLM；完整 query→refresh→mutation→final diff | Generic：Qwen correct 27/40、strict TRI writes 8、fallback writes 5；GLM 26/40、6、2、reject 6；Stable writes 均 0/4 | secondary frozen execution；实际模型 tool mutation，不是自然 prevalence |
| C2 | v7 deterministic SQLite replay | 冻结 v7 target outputs 全量确定性执行 | Generic 43/38/59 core substitutions 全部成为 wrong-entity writes；CTA core=0，但仍有 8/14/17 non-core wrong writes | zero-API consequence check；不是新 behavioral replication |
| C3 | full-history deterministic replay | 3 模型×ordinary/aware history，1,440 episodes | wrong writes ordinary→aware：Qwen 87→70、GLM 79→46、DeepSeek 75→57 | history 无 observable pre-binding，不能把所有 wrong write 叫 TRI |

## D. 人类构念与人工改写

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| D1 | blind human construct validation | 3 annotators×100 randomized original/rewrite items | majority–gold 86%；94 determinate 中 91.5%；unanimity 72%；κ/α=.708/.709。Dynamic 98%，anchored actionable 86.7%，Reject 55% | 支持 scalar core；Reject/fallback 语义支持弱 |
| D2 | human-rewrite model replication | 50 volunteer rewrites；4 controllers×2 models | benchmark gold：Qwen Generic/CTA 60/90%，GLM 74/98%；CTA 与 Gated/Lifecycle-free 差异区间不排除 0 | transfer 到 authored-task rewrites，不是独立自然请求 |
| D3 | six-form human follow-up | 6×12 items；目标每 item 5 valid labels；31 submissions | 仅 11/31 通过 frozen gate；无 item 有 5 labels；eligible referent/execution agreement 38.6/25.8%；all-primary changed PairAcc 3/18 仅 sensitivity | failed frozen eligibility gate；不能强化 construct claim |

## E. 规则、稳定性和组合性

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| E1 | deterministic Rule v2 | v3、50 rewrites、v7 | 148/160（92.5%）、48/50（96%）、220/240（91.7%） | 明确 post-hoc、benchmark-aware；限制算法新颖性 |
| E2 | Rule*-hard residual audit | 20 个 v7 Rule* error rows；无完整 pairs | timing reminder/CTA row accuracy：Qwen 13/13、GLM 20/20、DeepSeek 18/16（不同可用行） | post-hoc selection；不能画 PairAcc 或 confirmatory superiority |
| E3 | multi-refresh / role composition | v5 scalar stress + v6 scalar-vs-role addendum | scalar lifecycle 不自动组合；role indexing 有希望但无稳定跨模型优势 | negative/mixed compositional boundary |
| E4 | method-upgrade Go/No-Go | 20-task Event Graph M1 / Executable Selector M2 smoke | Qwen M1/M2 9/20、15/20；GLM 20/20、18/20；未达双模型冻结门槛 | exploratory No-Go；不能画成新主方法 |
| E5 | repeat/subsample robustness | v7 40-task frozen repeat subset；leave-group-out；cluster subsampling | CTA−Generic 六个 model-repeat cells 均正，CTA conditional subst. 均 0；但逐任务三轮一致率 Qwen 70/72.5%、GLM 85/97.5% | direction stable、endpoint non-deterministic；结论 `Mixed` |
| E6 | trigger/order 与 Rule*--model overlap | v3 authored leave-template-out；31 条 human-majority changed rewrites；9 个冻结 model/controller 输出 | trigger-only v3 71.2%/AUC .724，但 rewrite 48.4%/AUC .121；加 event order 后 rewrite 仍 48.4%/AUC .555，低于 61.3% majority baseline；错误 pair 中 Rule* 可解比例依模型/控制器为 28.6%--77.9% | post-hoc、zero-API；反对稳定浅层 trigger 解释，但不是独立 holdout 或机制证明 |

## F. 外部覆盖与边界

| ID | 实验族 | 设计/规模 | 核心结果 | 状态与边界 |
|---|---|---|---|---|
| F1 | 24-task ToolSandbox-compatible pilot | custom intervention；post-hoc strict opportunity audit | GLM Generic 3/6 eligible Flip substitutions、Stable 0/2；其他 model/controller 方向不一致，Gated 仍有 wrong writes | 小规模 post-hoc bridge；非官方 ToolSandbox |
| F2 | 96-task ToolSandbox-style extension | Qwen/GLM ordinary history 和 matched Generic；四 paper-facing conditions | conditional substitutions 0/70、0/73、0/64、0/87 | 反对 universality；wrong writes 仍存在但来自上游/流程错误 |
| F3 | Qwen state-observed sensitivity | 96 rows、73 opportunities、6 wrong writes、13 prohibited-schema/process errors | conditional substitution 0/73 | unmatched exploratory interface；不与四条件合并 |
| F4 | pinned public-suite coverage | ToolSandbox 129 families、AppWorld 244、τ3 2,449 tasks + traces | checklist 下 strict native opportunities 均 0 | descriptive zero-API；无 recall calibration、非 prevalence |
| F5 | additional public structural audit | API-Bank 528、BFCL 800 variants/200 clusters、ToolTalk 50 dialogues | strict native 0；检索出 80 heuristic source-anchored candidates | author-built retrieval audit；语义 absence 不能转成 positive |
| F6 | external candidate annotation | 80 candidates×2 model families；168 attempts；145 valid latest pairs | strict-positive union/intersection 0/0；source-eligible 25/1 | model-assisted，不是 independent review |
| F7 | model-assisted recall triage | 72 natural candidates + 60 injected controls | natural strict 0/72；positive controls 30/30；hard negatives 30/30 | 只验证实现和候选 triage，不校准 natural recall |
| F8 | injected checklist sensitivity | 6 suites×5 positive+5 hard negative=60 | 30/30 positives recovered；30/30 hard negatives excluded | implementation check，不证明 public-suite coverage 完整 |
| F9 | source-anchored external transfer | 20 clusters、80 author-adapted tasks；STATE-Bench/AgentDojo；2 models×2 interfaces | 2/64 Preserve/Changed substitutions，均为 Qwen ordinary-history AgentDojo 2/7；matched Stable 0/7；STATE-Bench 和其他 cells 为 0 | limited single-repository bridge；14 parse failures ITT 保留 |
| F10 | custom AppWorld / low-intervention addenda | custom two-app study + 无 explicit sidecar/术语 addendum | correct timely bindings 中 0/24；低干预 0/28，Preserve/Flip 0/6；wrong writes 属于 pre-binding/tool-order | 冻结低干预环境未阳性复现 controlled failure |

## G. 计划但未验证（不能画成结果）

- 独立 public-suite opportunity recall audit。
- 12 名独立 writers + 3 名 blind annotators 的 controlled-language holdout。
- Convention-told 对照（普通自然 history vs 明示自然语言 convention；等调用、无结构化 ID）。
- 去除 resolver-produced initial ID 的 end-to-end decision-block decomposition full matrix。
- 独立 natural-request elicitation 与 dialogue-aware verifier。

这些项目只能在研究路线图中用虚线或“planned”标识，不能与 completed evidence 共用结果色标。
其中独立人类 holdout 在本次投稿前为 NO-GO；不得用作者便利样本或 LLM 改写替代后称为
independent human evidence。Convention-told 已冻结协议，但尚未运行，不能写成结果。
