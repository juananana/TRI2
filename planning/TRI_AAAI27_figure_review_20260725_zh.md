# TRI 主文图形审查与定稿方案（2026-07-25）

性质：内部设计记录。每张主文图只回答一个 review-critical question。

## 最终三图

1. Figure 1：Observed execution trace。
   - 回答：正确初始 ID 的后续替换是否真的成为 wrong-entity write。
   - 保留“full run 后选作说明”的 caption；不作为频率证据。
   - 删除长指令框，改为 S0--refresh--S1 与 Generic/CTA 两条执行轨迹。

2. Figure 2：Changed-winner policy space。
   - 回答：为什么单侧 Preserve 或 Reevaluate 分数不能识别 selective policy。
   - 坐标是两种方向的准确率；模型由颜色和形状共同编码；Rule* 明示 post-hoc。
   - 不使用任意 80% 阴影，不恢复机制图。

3. Figure 3：Shared-eligibility consequence path。
   - 回答：在两控制器都正确绑定的相同任务上，substitution 如何传导为 wrong write。
   - 三模型共享尺度；Generic/CTA 使用同一 eligible denominator。
   - 显示 outside-core wrong writes，避免暗示 CTA 没有其他错误。

## 合规要求

- 主文嵌入后的 figure text 至少 9pt；线宽至少 0.5pt。
- 使用 Helvetica、嵌入字体、PDF 矢量输出。
- 颜色之外再用圆/方标记和直接标签，保证灰度与色觉可读性。
- caption 写出 evidence status、条件分母和负面边界。

## 参考过的公开论文图形组织

- AgentBoard, NeurIPS 2024：共享尺度小多图与指标验证。
- AgentHarm, ICLR 2025：按相同模型顺序对齐总体与条件指标。
- CToolEval, ACL Findings 2024：原始点、分布和汇总统计的联合呈现。
- ShoppingBench, AAAI Proceedings：核验了环图/雷达图；这两种形式不适合 TRI 的条件分母，
  因而未采用。

