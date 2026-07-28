# TRI 正文结果图设计方案

## 总体结构：四张结果图

正文保留四张结果图。四张图分别回答 identifiability、behavior、consequence、boundary，
不重复展示同一组指标。

| 正文图 | 核心问题 | 推荐图形 | 主数据 |
|---|---|---|---|
| Figure 2 | 评价能否识别选择性重解析？ | 相位图 + 内嵌 PairAcc key | `matched_pairacc_and_marginals.csv` |
| Figure 3 | 正确初始绑定后，CTA 是否同时降低替换并提高 PairAcc？ | 双面板 paired slope + CI | `v7_shared_eligible_pairacc_and_substitution.csv` |
| Figure 4 | 目标替换是否变成 wrong write？ | 分模型/控制器堆叠横条 | `v7_e2e_wrong_writes.csv` |
| Figure 5 | 显式 timing decision 的收益能否迁移？ | 分组效应量 forest plot | `revision_decision_visible_gains.csv` |

若版面必须减少为三张，只合并 Figure 3 与 Figure 4；Figure 2 和 Figure 5 不合并。

## 全局视觉语言

- 原生单栏宽度约 `3.25 in`，不先画双栏大图再缩小。
- 主轴标题 9 pt；次级标签、key、数值 8--8.5 pt；正文图注由 AAAI 模板控制。
- 正文墨色 `#253238`，辅助网格 `#C1CBD0`。
- 控制器颜色：Generic 紫 `#5E379D`；CTA 蓝 `#2F74B8`；Lifecycle 深橙 `#9A4C00`；Rule/固定策略灰 `#59636B`。
- 结果颜色：TRI substitution 使用低饱和珊瑚色，retained/other 使用浅灰；避免鲜艳纯红/纯绿对照。
- 模型图标固定：Qwen 圆、GLM 方、DeepSeek 菱形。所有图注第一次出现时说明。
- 颜色不单独传递语义：同时使用形状、填充/空心、直接文字或线型。
- 数值只在一个位置出现；不在点旁、legend、图注中三次重复。
- 不放装饰性大标题、阴影卡片或无信息背景；空白必须服务于分组或阅读顺序。

## Figure 2：Policy Phase Space

已接入正文：`Figures/fig_resolution_policy_phase_space_singlecolumn.pdf`。

- 坐标展示全部 80 个 Preserve/Reevaluate pairs 的 marginal accuracy。
- 左下 PairAcc key 展示 changed-winner 32-pair 结果。
- 六个 CTA/Lifecycle marginal 点位于很窄的右上范围；使用蓝框 + 橙底边的精确 min--max envelope，避免单栏尺度下叠点。
- 相位区只保留 `R > 50`、`P,R > 50`、`P > 50`；不把右上象限直接命名为 Selective。
- 图的结论由 PairAcc key 给出，而不是由边际点所在象限推断。

## Figure 3：Cross-Schema Controller Transition

推荐尺寸：`3.25 x 3.05 in`。

- 使用两个上下对齐的 paired slope panels，而不是流程框：Panel A 是 conditional substitution rate，Panel B 是 cross-schema PairAcc。
- 横轴仅有 Generic 与 CTA；每条灰线连接同一模型在两个控制器下的成对估计，不表示训练或时间轨迹。
- Qwen/GLM/DeepSeek 分别用圆/方/菱形；Generic 为紫色实心点，CTA 为蓝色空心点。颜色和形状共同编码。
- Panel A 使用 shared-eligible 计数的 Wilson 95% CI，左侧直接写 `41/66`、`30/70`、`50/69`；CTA 的 0 值以三个错开的空心点表达，避免重叠。
- Panel B 使用报告中的 cluster-bootstrap PairAcc CI。两面板共同显示：正确初始绑定条件下 Generic 仍可替换，而 CTA 在同一 cross-schema inventory 上同时提高 PairAcc。
- 图注必须说明 conditional denominator、`0/N` 的范围，且将连线定义为 paired controller contrast。

## Figure 4：Wrong-Write Decomposition

推荐尺寸：`3.25 x 1.95--2.15 in`。

- 每个模型两条水平 bar：Generic、CTA；模型组之间用细虚线分隔。
- bar 长度编码 total wrong writes；内部堆叠 TRI substitution writes 与 other wrong writes。
- 珊瑚段写白色计数，灰段在段外写黑色计数；CTA 的 `0 TRI` 用空心短标记或文字，不画人为可见的零宽色块。
- controller 总数放进 y label，例如 `Generic (44)`，不在 bar 末端再次重复 total。
- 共用 `0--65` 横轴；不使用百分比或双轴。
- 图注强调 fixed-executor consistency check，不把所有 wrong writes 都归类为 TRI，也不把 CTA 写成综合安全性结果。

## Figure 5：Decision Visibility and Transfer

推荐尺寸：`3.25 x 2.70--2.95 in`。

- 两个并列 forest panels：changed PairAcc effect、actionable E2E effect，共用 audit/model 行。
- 三个 audit groups：authored diagnostic、human rewrite、source-grounded contrast；组间使用细虚线，不使用大色块。
- 零效应线使用深灰；点和 95% CI 使用同一色，模型通过圆/方/菱形区分。
- 右侧只写 `estimate [CI]`；不在点旁重复 denominator。
- human-rewrite PairAcc 的 `n=3 pairs` 必须在组标题或脚注式标签中出现，防止宽 CI 被误读为强证据。
- Qwen source-grounded null、DeepSeek CI 跨零、GLM positive 必须同时保留，不做 pooled universal-effect 点。
- 这张图承担 claim boundary，因此颜色最克制：单一蓝灰色系 + 模型形状即可，不沿用 Figure 3/4 的 outcome colors。

## 不进入正文的图

- Enforcement repairs/harms：作为 supplement figure 或 Figure 5 的补充，不再占正文独立 figure。
- Source-specific AgentDojo/STATE-Bench/ToolSandbox fingerprints：放 supplement；正文只保留 source-grounded 总体异质性。
- Component audit、Rule* residual、完整 controller matrix：放 supplement，避免主文重复证明同一机制边界。

## 每张图的验收清单

1. 在最终单栏尺寸下检查，不在放大预览下判断文字大小。
2. 任意两个文字、点、误差条、ribbon、bar label 不重叠。
3. 图标、形状、颜色在图内或图注首次定义。
4. 灰度下仍能恢复主要比较。
5. 分母、证据状态和 post-hoc 标记与正文一致。
6. PDF 不含 Type 3 字体；位图版本至少 300 dpi。
7. 编译后仍为 7 页正文 + 参考文献，且 figure 在首次讨论附近。
