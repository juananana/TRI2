# TRI AAAI-27 八天动态投稿计划

更新日期：2026-07-20（Asia/Shanghai）

## 1. 截止日期

- 摘要截止：2026-07-21 23:59 UTC-12，北京时间 2026-07-22 19:59。
- 全文截止：2026-07-28 23:59 UTC-12，北京时间 2026-07-29 19:59。
- 补充材料与代码：2026-07-31 23:59 UTC-12，北京时间 2026-08-01 19:59。
- 内部目标：7 月 27 日冻结主文，7 月 28 日只处理提交系统和致命事实错误。

## 2. 当前投稿决策

论文主线固定为：

> 状态刷新更新了世界知识，但不自动授权 Agent 改变已经绑定的操作目标。普通结构化状态仍可能发生 post-binding drift；刷新前目标承诺编译显著减少该错误，而执行 gate 只能保护正确编译的承诺。

方法定位：

- 标量主方法：Exact Compile-then-act，即“刷新前目标承诺编译”。
- 可审计系统扩展：typed Lifecycle + deterministic gate。
- 组合扩展：Role-Indexed Lifecycle。
- Event Graph 与 Executable Selector：20-task smoke 未通过双模型 Go/No-Go，只作探索性负面消融，不升级为主方法。
- 论文类型：phenomenon + diagnostic benchmark + authorization mechanism + benchmark blind spot。
- 不宣称：真实流量高频、所有 LLM 普遍存在、gate 提供通用写安全。

## 3. 投稿必须保住的证据

1. v3 160-task 主实验：Generic 64.4/71.9%，CTA 95.0/96.2%。
2. Always-Lock 与 Always-Reevaluate 均为 60%，错误互补。
3. v7 240-task 独立复制：Generic conditional core drift 43/72、38/80；CTA/Gated 为 0。
4. 81 次 conditional drift 全部可重放为 wrong-entity SQLite writes。
5. 人工语义：Fleiss kappa 0.708，majority-gold 86%。
6. 50 条独立英文改写：CTA 90/98%，Generic 60/74%。
7. 外部证据：公开基准几乎不提供原生严格 TRI opportunity；冻结 ToolSandbox-compatible pilot 的 post-hoc 严格审计发现 GLM Generic 3/6 条件 TRI，而低干预 ToolSandbox/AppWorld full-history Agent 为 null。
8. 组合边界：scalar lifecycle 不稳定；role indexing 能改善 Qwen，但 GLM 上与简单方法持平。

## 4. 动态调整规则

以下规则高于原实验愿望清单：

1. 不再为把 M2 做成正结果而改 prompt 或扩大任务。
2. DeepSeek 第三模型已完成冻结 v7 全量：Generic/CTA 73.8/91.2，conditional drift 59/79 对 0/70；作为 post-primary robustness replication 报告。
3. 不再扩大 AppWorld、ToolSandbox 或 tau3 模板；现有零 opportunity/null 结果已经支持 coverage blind spot。
4. 新 API 实验必须回答一个会改变主文结论的问题，并先通过小 smoke。
5. 7 月 24 日后原则上不启动新模型实验；只允许 transport repair 或致命审稿问题验证。
6. 主文任何新增主张必须有 raw run、report script 和 claim provenance。
7. 若师姐认为方法新颖性不足，优先重构叙事为“发现评测盲区与授权机制诊断”，不仓促发明新控制器。
8. 若主文超过 7 页，优先删除探索性方法和次要外部细节，不删除定义、v3/v7、SQLite、人类证据和限制。

## 5. 每日计划

### Day 1：7 月 20 日晚，锁定故事并形成评估材料

交付物：

- 完成 20-task 论文级最小闭环与 Go/No-Go；
- 完成给师姐的论文总结文档；
- 完成八天投稿计划；
- 主文正式编译为 7 页正文、8 页总计；
- 更新方法升级计划和 Binding Drift 审计；
- 更新 claim provenance 与补充材料中的探索性方法状态；
- 运行代码测试、LaTeX 编译、密钥扫描。

退出条件：明早能用一份文档解释“问题、方法、结果、边界、投稿风险”。

### Day 2：7 月 21 日，师姐评估与摘要定稿

上午：

- 将总结文档、8 页 PDF、主结果表发给师姐；
- 请师姐重点判断：题目是否清楚、主张是否过窄、AAAI novelty 是否足够、DeepSeek 全量结果放正文还是 supplement。

下午至晚上：

- 根据反馈修改标题、摘要、Introduction 和 contributions；
- 完成投稿系统取号/摘要注册所需标题、作者、关键词、摘要；
- 逐句核对摘要数字与 artifact；
- 冻结“主方法=CTA、组合扩展=role indexing”的方法层级。

转向条件：

- 若师姐接受当前定位：停止新方法开发，进入证据与写作加固。
- 若认为 novelty 不够：优先加强 formal distinction、benchmark blind spot 和 consequence，不默认追加模型。
- 若发现致命缺失基线：当天定义最小适配和完成上限，未通过 smoke 即停止。

### Day 3：7 月 22 日，摘要提交与主文证据审计

- 在北京时间 19:59 前完成摘要提交；最好中午前提交初版。
- 对主文每个数字执行 claim-to-artifact 核对。
- 检查 v3 primary、post-primary v7、human rewrites、external audits 的标签是否清楚。
- 把 20-task M1/M2 No-Go 放补充材料或内部决策日志，不放主结果表。
- 完成 related-work primary-source 审核，特别是 Binding Drift、Entity Binding Failures、LedgerAgent、Bounded Autonomy。

退出条件：主文不存在“数字无来源”“oracle 当 learned baseline”“null 外部结果写成 prevalence”问题。

### Day 4：7 月 23 日，统计与错误分析定稿

- 重新生成全部主表和图，禁止手工录数；
- 核对 cluster bootstrap 单位、paired delta、ITT 与 transport-complete sensitivity；
- 压缩错误分类为审稿人能复核的三层：初始绑定、post-binding transition、执行/selector；
- 检查 SQLite wrong-write 结论是否都限定到 action-valid core；
- 完成主文 Results 和 Discussion 的一次结构性重写。

退出条件：Results 能在两分钟内回答“现象是否存在、CTA 为什么有效、哪里无效”。

### Day 5：7 月 24 日，补充材料与 artifact

- 将完整 prompts、方法接口、20-task No-Go、Binding Drift 审计、额外切片移入 supplement；
- 修复 artifact README、依赖说明、测试命令和运行入口；
- 生成匿名 artifact 清单，排除 API key、private XLSX、annotation key、环境和外部大仓库；
- clean-room 解压并运行核心测试与报告生成。

退出条件：一个不了解项目的人能按 README 复现确定性结果和主要表格。

### Day 6：7 月 25 日，内部审稿与反驳预演

- 以 AAAI reviewer 视角写一次完整 review；
- 检查四类高风险质疑：合成性、外部有效性、方法新颖性、基线公平性；
- 每个质疑在正文或限制中有直接回答；
- 核对标题、摘要、贡献、结论是否使用同一强度的主张；
- 完成 reproducibility checklist。

退出条件：没有靠 supplement 才能判断核心结论的关键证据。

### Day 7：7 月 26 日，冻结实验与语言精修

- 原则上停止新实验；
- 冻结所有主表数字、图、数据 hash 和 Git commit；
- 精修摘要、Introduction、Related Work、Limitations、Conclusion；
- 检查英文术语统一：binding、commitment、referent transition、validity、wrong write；
- 检查匿名性、引用真实性、图表字体和 PDF 元数据。

退出条件：正文 7 页、总页数不超过 9，LaTeX 无 undefined citation/reference。

### Day 8：7 月 27 日，提交包冻结

- 生成最终 PDF、supplement PDF、匿名代码包；
- 对照提交系统逐项填写；
- 两次独立数字核对；
- 上传并下载回检 PDF；
- 保留 7 月 28 日及 UTC-12 时区余量处理系统问题。

退出条件：除提交系统问题和致命事实错误外，不再修改方法或新增主张。

## 6. 今晚完成情况与剩余动作

已完成：

- 20-task 双模型主比较、消融与自动 Go/No-Go；
- M2 No-Go，CTA/role-indexing 定位冻结；
- 主文 7 页正文、8 页总计；
- Binding Drift 官方离线 harness 25/25 断言复现及可比性审计；
- 零 API Event Graph/Selector/Atomic Gate oracle tests；
- API key 未写入仓库或输出。
- DeepSeek 第三模型 240-task 全量已完成：Generic 73.8%，CTA 91.2%；conditional core drift 为 59/79 对 0/70，配对 CI [10.8,23.3]，0 API/parse error。

今晚剩余：

- 将第三模型 full replication 与 SQLite replay 同步到正文、supplement 和 claim provenance；
- 修复子集报告中的 cluster 数说明并复跑相关测试；
- 重新执行匿名与密钥扫描；
- 创建并推送新的安全 GitHub 快照，输出明早可直接发送的文件清单。
