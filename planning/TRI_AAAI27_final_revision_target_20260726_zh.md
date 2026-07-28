# TRI AAAI-27 最终修改目标（2026-07-26）

性质：内部决策记录，不是论文证据，不进入匿名提交材料。

## 最终论文定位

将论文稳定定位为：

> 一个识别 selective referent re-resolution 的 matched evaluation diagnostic，以及一套
> 将 initial binding、state update、referent transition 和 executed target 分开的审计条件。

CTA、Lifecycle、Gated 和 deterministic rule 都是该原则的 executable probes，不是论文要
证明唯一正确的 runtime architecture。论文不主张真实流量 prevalence、公共 benchmark
排名已经错误、开放语言泛化或通用组合安全。

## 提交前必须成立

1. 正文 headline 使用 128-task actionable core、changed PairAcc、conditional substitution
   和 matched-call decision visibility；Reject 单列。
2. Cross-Schema 同时报告 conditional TRI 与全 240 行 E2E/total wrong writes，不能把零
   core substitution 写成 general safety。
3. SQLite deterministic replay 称为 fixed-executor consequence audit，不称独立自治验证。
4. 正文明确：当前五个 candidate sets 中 aggregate E2E 都选择 PairAcc-optimal controller；
   PairAcc 的贡献是 paired diagnosis，不是已证明改变所有排行榜。
5. Cross-Schema 只称 schema/state transfer；共享语言模板意味着它不是 open-language evidence。
6. Related Work 同表区分 initial binding、entity memory、temporal reasoning、persistence 与 TRI。
7. primary/frozen、post-primary replication/audit、post-hoc、planned/unverified 在正文和
   Supplement chronology 中一致。
8. 外部 null、post-hoc rule、Qwen enforcement harms、mixed composition 不得删除或弱化。
9. 主文保持 7 页内容加 references；三份 AAAI 官方文件名不变。

## 新实验决策

### GO：仅在独立来源真实可得时运行开放语言 holdout

最低条件：

- 至少两名未参与 TRI 模板设计的任务作者；
- 根据状态、工具和意图从零写指令，不改写原模板；
- 至少 24 个独立 workflow specifications，形成 48 个 opposite-gold rows；
- 覆盖隐式时序、跨轮修正、条件句、插入语和不同 anaphora；
- 收集前冻结 CTA、Rule*、模型、prompt、PairAcc/ITT、失败处理和停止规则；
- Rule* 不得根据 holdout 错误修改；
- 独立 gold 审核与任务作者分离。

若缺少独立作者或 gold 审核，则 NO-GO。LLM 生成或 LLM judge 只能称 model-assisted
stress test，不能替代该证据。

### GO：公共套件 recall calibration 仅在独立复核可得时运行

最低条件：对检索前过滤单元做分层随机抽样、植入隐藏正例校验 parser sensitivity，并由
独立复核者 adjudicate。植入正例只校验检测流程，不能证明自然 opportunity 存在。无独立
复核时，正文继续写“under our checklist; without independent recall calibration”。

### NO-GO：继续增加同模板 API 模型矩阵

已有三模型 Cross-Schema、双模型 matched-call ablation、full-history、CTA/Lifecycle/Gated、
deterministic extremes 和 Rule*。再增加模型或作者模板不会解决当前主要压分项。

### NO-GO：把 mixed composition 包装成方法成功

两刷新 scalar Lifecycle 的负结果必须保留。Role-indexed repair 仅为 post-hoc/held-out
boundary evidence，不能支持通用 multi-referent runtime claim。

## 当前不可由写作解决的风险

1. 没有独立开放语言确认集。
2. 没有严格 native public-benchmark opportunity。
3. 公共检索没有独立 recall calibration。
4. primary package comparison 仍 call-asymmetric；matched ablation 为 post-primary。
5. provider weight revision 和 serving hardware 不可固定。

这些风险决定当前严格评分更接近 5--6，而不是稳定 7。只有前两项中的至少一项获得可信
新增证据，才可能实质提高外部效度与科学重要性评分。

## 结果入口

关键报告和最终图统一生成到
`experiments/tri_artifact/reports/submission_summary/`。该目录保留 external null、post-hoc
和 negative composition evidence，并由 `manifest.json` 记录来源和 SHA-256。
