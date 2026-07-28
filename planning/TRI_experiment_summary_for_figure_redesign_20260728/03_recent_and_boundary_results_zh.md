# 2026-07-24 后新增/定稿实验补遗

`02_detailed_results_zh.md` 已系统覆盖 v3、v7、组件、SQLite、human、external 和 composition。
本文件补齐投稿冻结前最后完成或重新定稿的 matched-call 与证据边界结果。

## 1. Call/base-payload-matched 40-pair ablation

每个模型 80 rows / 40 changed pairs。History-only 与 Decision-visible actor 调用数和 base
payload 相同；Decision-enforced 是对同一 actor output 的零新调用确定性变换。

| 模型 | 条件 | PairAcc | E2E | Preserve conditional substitution |
|---|---|---:|---:|---:|
| Qwen | History-only | 12/40 | 52/80 | 16/28 |
| Qwen | Decision-visible | 20/40 | 59/80 | 4/28 |
| Qwen | Decision-enforced | 17/40 | 55/80 | 0/28 |
| GLM | History-only | 12/40 | 52/80 | 12/24 |
| GLM | Decision-visible | 24/40 | 64/80 | 0/24 |
| GLM | Decision-enforced | 24/40 | 64/80 | 0/24 |

- Visible−History PairAcc：Qwen +20.0pp [2.5,37.5]；GLM +30.0pp [17.5,45.0]。
- Visible−History E2E：Qwen +8.8pp [0.0,17.5]；GLM +15.0pp [8.7,22.5]。
- Qwen enforcement 改变 16 rows：4 repairs、8 harms、4 wrong→wrong；GLM 改变 0 rows。

适合图表表达的结论是“visibility 与 enforcement 必须分开”：前者两模型方向一致，后者在
Qwen 上可能损害输出。

## 2. Full-diagnostic matched-call confirmation

每模型 160 rows / 80 matched pairs；32 actionable changed pairs、128 actionable rows 和 32
Reject-policy rows 分开报告。所有 960 logical calls 完成，无 API/parse failure。

| 模型 | 端点 | History-only | Decision-visible | 差值与 cluster 95% CI |
|---|---|---:|---:|---:|
| Qwen | changed PairAcc | 5/32 | 13/32 | +25.0pp [6.3,46.2] |
| Qwen | actionable E2E | 100/128 | 106/128 | +4.7pp [0.0,9.4] |
| GLM | changed PairAcc | 8/32 | 25/32 | +53.1pp [28.6,77.8] |
| GLM | actionable E2E | 102/128 | 120/128 | +14.1pp [8.4,20.0] |

Preserve substitution：Qwen 22/28→13/28；GLM 16/25→0/25。Decision-enforced 相对
History-only 的改善更大，但 Qwen 有 18 repairs 与 8 harms，因此不能把 hard gate 画成单向
“安全增益”。

## 3. Decision-block stratification 与接口冗余

- authored、rewrite、source-derived 和 cross-schema 共 760 records；initial ID、selector
  restatement、compiler/history/visible copies 和两 actor copies 均 760/760 exact equal。
- 这说明 intervention 没有加入新的 selector/ID 值，但不能排除 restatement/salience 效应。
- Authored Qwen：compiler mode correct strata 76.6%→86.9%，mode wrong 69.6%→52.2%；
  bound-ID correct 55.7%→74.3%，wrong 40.0%→20.0%。
- Authored GLM：mode correct 78.0%→96.5%；bound-ID correct 52.5%→93.4%。

这些是 post-treatment descriptive strata。可以画“correct vs wrong compiler 的收益异质性”，
但图注必须明确不是 mediation 或单字段 causal attribution。

## 4. Matched-call transfer

### 4.1 Human rewrites

| 模型 | 端点 | History-only | Decision-visible | 差值 |
|---|---|---:|---:|---:|
| Qwen | actionable E2E | 30/40 | 30/40 | 0.0pp [-10.0,9.5] |
| GLM | actionable E2E | 31/40 | 39/40 | +20.0pp [8.6,32.5] |

只有 3 个 complete actionable changed pairs，因此 PairAcc（Qwen 0→1/3；GLM 1→3/3）只能
作为小样本 sensitivity。该数据来自一个志愿者对 authored tasks 的改写，不是 open-language
自然请求验证。

### 4.2 Three-source controlled contrast

| 模型 | PairAcc History→Visible | PairAcc effect | E2E History→Visible | E2E effect |
|---|---:|---:|---:|---:|
| Qwen | 12/30→13/30 | +3.3pp [-11.1,20.0] | 39/60→39/60 | 0.0pp [-6.7,6.7] |
| GLM | 11/30→20/30 | +30.0pp [0.0,55.6] | 37/60→48/60 | +18.3pp [8.3,30.0] |
| DeepSeek | 19/30→22/30 | +10.0pp [-10.0,30.0] | 45/60→47/60 | +3.3pp [-5.0,11.7] |

该结果最重要的是模型异质性与 source 异质性，而不是 pooled gain。GLM 的 STATE-Bench
PairAcc 5/10→10/10，AgentDojo 4/10→4/10，ToolSandbox 2/10→6/10；Qwen ToolSandbox
两条件均 0/10；DeepSeek STATE-Bench 从 10/10 降为 9/10。

## 5. 六表人类 follow-up：failed gate

- 31 complete submissions，只有 11 通过 frozen eligibility；forms A--F 的 valid labels 为
  1/2/1/1/3/3，目标是每 form 5。
- 无 item 有 5 个 valid labels，预注册的 fixed-rater κ、α 和 18-pair endpoint 不可计算。
- eligible label-level referent/execution agreement 为 51/132（38.6%）与 34/132（25.8%）。
- all-primary sensitivity：referent majority 27/72、execution 19/72、changed PairAcc 3/18；
  不能作为 evidence。

图表上只能作为“失败的数据质量/招募 gate”，不能与前一个三 annotator study 合并平均。

## 6. Model-authored linguistic stress

- 24 new workflow schemas、48 actionable rows、24 opposite-gold pairs。
- Qwen/GLM Generic 均 24/48、0/24 PairAcc；CTA 均 36/48、12/24 PairAcc；Generic Preserve
  substitution 24/24 和 20/24，CTA 为 0/12。
- 两 model judges 共同接受仅 11/48 rows，且没有完整 opposite-gold pair。
- 初版 normalizer 因 ID 中多连字符产生 invalid all-zero report；零请求 exact-ID transport
  repair 后得到上述结果，旧报告保留。

因此这是“模型替代独立 writers/annotators 失败”的构念边界，不是 open-language positive。

## 6.1 Trigger/order 与 Rule*--model overlap：zero-API post-hoc 审计

- Trigger-only logistic 在 v3 leave-template-out 上为 71.2%、AUC .724；到 31 条
  human-majority changed rewrites 后为 48.4%、AUC .121。
- 加入手写 event-order 特征后，v3 为 75.0%、AUC .695；rewrite 仍为 48.4%，AUC
  升至 .555，但准确率低于 61.3% majority-class baseline。
- 现有三标注者构念复核保留 Fleiss κ=.708、Krippendorff α=.709；rewrite 仍来自
  authored-task 改写，不能称 independent holdout。
- 在 80 个 changed pairs 上，模型错误中 Rule* 可解的比例为：Qwen
  History/Reminder/CTA 74.0/72.3/75.5%，GLM 73.0/70.0/28.6%，DeepSeek
  77.9/72.3/62.5%。这是 benchmark-aware Rule* 的描述性 overlap，不是机制归因。

图表上可以把“authored 内部可预测、rewrite 不 transfer”画成构念边界；Rule* overlap
应与主模型结果分面，并显式标注 post-hoc。

## 7. Public audit 与 source-anchored bridge

- Injected controls：30/30 strict positives recovered，30/30 hard negatives excluded。
- Natural candidate triage：0/72 strict；只是候选级 model-assisted triage。
- API-Bank/BFCL/ToolTalk 结构扫描：strict 0，保留 80 heuristic candidates。
- 双模型候选标注：145 valid latest pairs；strict-positive union/intersection 0/0；较宽
  source-eligible union/intersection 25/1。
- Source-anchored model transfer：20 clusters、80 author-adapted tasks；14 parse failures ITT；
  2/64 Preserve/Changed substitutions，均为 Qwen ordinary-history AgentDojo 2/7，Stable 0/7；
  STATE-Bench 和其他 cells 为 0。

组合解释：公共覆盖结果是“当前 checklist 下没有 strict native positive”，source-anchored
结果是“一个 repository/model/interface 切片出现有限 bridge evidence”。二者都不能转化为
真实发生率。

## 8. 投稿前构念效度收口

- 独立人类 holdout 因独立 writers/annotators 和冻结 eligibility gate 不满足，本次投稿
  明确 NO-GO；不降低门槛，也不用 LLM-only/作者便利样本替代。
- Convention-told 已冻结 equal-call 方案：Plain-history vs 明示自然语言 convention，均为
  单次 actor call，且不提供结构化 ID、reference mode、compiler block 或 gold。
- 该对照尚未调用模型，状态为 planned/unverified；即使以后结果为正，也只能支持 authored
  inventory 上自然语言 convention 有帮助，不能修复独立人类 gold、open-language 或 prevalence。
