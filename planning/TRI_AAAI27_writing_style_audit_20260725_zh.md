# TRI 学术写作风格审查（2026-07-25）

性质：内部编辑记录，不是“AI 检测通过”证明。

## 诊断

原稿没有明显宣传词堆砌。主要问题是过度防御：同一限制在摘要、引言、结果、
Discussion、Limitations 和 Conclusion 重复，且 `not / does not / cannot / rather than`
结构过密，读起来像提前写好的 rebuttal。

任何工具都不能可靠给出所谓“AI 率”，也不能保证避免 desk reject。可执行的目标是让
每句话对应定义、证据、比较或边界，并保留真实写作与实验 provenance。

## 本轮编辑规则

- 标题和已提交摘要不做实质改动。
- 先写观察和分母，再写解释；限制放在其限定的结果附近。
- 固定术语：`resolution timing` 表示语义变量，`referent-transition decision` 表示控制输出。
- 删除模板化铺陈、重复数字和同一免责声明的多次复述。
- 不使用 `novel`、`comprehensive`、`crucially`、`state-of-the-art`、`robust` 等宣传词。
- 负面结果用直接陈述，不把它们藏进 footnote 或只放 Limitations。

## 已改位置

- Introduction：用 transcript/ID 的具体失败替代三段式抽象铺陈；贡献改成“定义、测量、观察”。
- Experimental Setup：把 evidence status 和 primary estimand 合并为一段，删除四次重复。
- Results：拆开 shared-eligible substitution 与 SQLite consequence，压缩重复 primary 数字。
- Discussion/Limitations：合并反复出现的 claim boundary，保留 external null、post-hoc rule、
  mixed composition 和 provider revision 限制。
- Conclusion：改成三句结果闭环，不再罗列一串免责声明。

