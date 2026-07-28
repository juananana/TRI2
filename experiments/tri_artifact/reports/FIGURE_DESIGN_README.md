# TRI 论文高密度可视化图表设计说明

## 概述

为了提升论文的视觉呈现质量和信息密度，我重新设计并生成了以下5个高质量的综合性图表。这些图表将多个维度的实验结果整合在一起，大幅提高了单张图的信息密度，同时保持清晰易读。

---

## 新生成的图表

### 1. **tri_comprehensive_analysis.pdf** - 综合消融分析图（5个子面板）

**用途**: 主要实验结果的全面展示

**包含面板**:
- **Panel A: PairAcc提升对比**
  - 展示History Only → Decision Visible → Decision Enforced的性能提升
  - 使用分组柱状图对比Qwen和GLM两个模型
  - 添加提升箭头标注，直观显示改进幅度
  - 数值标注在柱子上方，粗体显示关键结果

- **Panel B: 条件替换率分析**
  - 对比History Only vs Decision Visible的替换率
  - 包含95%置信区间误差棒
  - 显示戏剧性的下降（例如50% → 0%）
  - 用百分点标注强调改进

- **Panel C: 强制执行效果（Enforcement）**
  - 使用发散条形图展示Repairs vs Harms
  - 正向（绿色）表示修复，负向（红色）表示损害
  - 清晰展示混合效果

- **Panel D: 准确率分解**
  - 折线图展示Preserve vs Reevaluate在不同条件下的表现
  - 虚线表示Preserve，实线表示Reevaluate
  - 展示决策可见性对两个维度的不同影响

- **Panel E: 综合指标热图**
  - 6种指标 × 6种条件的完整矩阵
  - 颜色编码性能（绿色=好，黄色=中等，红色=差）
  - 每个单元格标注精确数值
  - 快速识别最佳配置

**建议使用位置**: 论文Results部分的第一个综合图，或作为双栏图横跨整页

---

### 2. **tri_new_schema_comprehensive.pdf** - 新Schema复制结果（4个子面板）

**用途**: 展示跨Schema泛化能力和错误类型分析

**包含面板**:
- **Panel A: 错误写入对比（带准确率）**
  - 主坐标轴：Wrong-entity writes（柱状图）
  - 次坐标轴：End-to-End准确率（折线图）
  - 显示Generic的高错误率 vs CTA的低错误率
  - 同时展示准确率的对应关系

- **Panel B: 替换级联可视化**
  - 堆叠横向条形图
  - 显示"替换/总数"比例
  - Generic vs CTA的直接对比
  - 颜色区分替换（红色）和正确（绿色/灰色）

- **Panel C: 准确率-替换率权衡散点图**
  - X轴：替换率，Y轴：准确率
  - 理想区域标注（高准确率+低替换率）
  - 箭头连接同一模型的Generic → CTA改进轨迹
  - 清晰展示trade-off关系

- **Panel D: 错误类型分解**
  - 堆叠柱状图
  - 区分"错误目标"vs"无效尝试"
  - 对比Generic和CTA的错误分布差异

**建议使用位置**: Results部分关于Schema Transfer的实验结果

---

### 3. **tri_policy_identifiability_comprehensive.pdf** - 策略可识别性（4个子面板）

**用途**: 解释为什么需要Matched Pairs评估

**包含面板**:
- **Panel A: Stable-Only评估**
  - 所有策略都得100分
  - 警告标注："无法区分策略"
  - 黄色高亮显示问题

- **Panel B: Preserve-Only评估**
  - Lock策略100分，Reevaluate 0分
  - 显示单侧偏好
  - 橙色警告

- **Panel C: Reevaluate-Only评估**
  - Reevaluate 100分，Lock 0分
  - 相反的单侧偏好
  - 橙色警告

- **Panel D: Matched Pairs评估**
  - 只有Selective策略100分
  - 其他策略0分
  - 绿色成功标注："完全区分所有策略"
  - 证明Matched Pairs的必要性

**建议使用位置**: Methods或Results开头，解释评估方法的优越性

---

### 4. **tri_temporal_flow_comprehensive.pdf** - 时间流程图（2个面板）

**用途**: 核心概念的可视化解释

**包含面板**:
- **Panel A: PRESERVE流程**
  - 时间线展示：Observe → Bind A → Refresh → Write A
  - 状态盒子显示S₀和S₁
  - 授权决策高亮：B(A)（绑定A）
  - 绿色成功标注："正确写入A"
  - 事件标记用圆圈和颜色编码

- **Panel B: REEVALUATE流程**
  - 时间线展示：Observe → Refresh → Bind B → Write B
  - 相同的状态转换，不同的绑定时机
  - 授权决策高亮：U(q)→B(B)（延迟解析后绑定B）
  - 绿色成功标注："正确写入B"

**设计亮点**:
- 清晰的时间轴
- 颜色编码事件类型
- 状态转换可视化
- 授权边界明确标注

**建议使用位置**: Introduction或Methods的核心概念解释图

---

### 5. **tri_controller_architectures.pdf** - 控制器架构对比（3个面板）

**用途**: 解释不同控制器设计的差异

**包含面板**:
- **Panel A: Generic架构**
  - 线性流程：Instruction → Model Call 1 → Store → Refresh → Model Call 2 → Execute
  - 黄色警告："隐式解析时机"
  - 简单但容易出错

- **Panel B: CTA架构**
  - Compiler显式决策
  - 存储：Mode + Bound ID + Selector
  - Actor接收决策信息
  - 绿色标注："显式编译决策"

- **Panel C: Lifecycle-Gated架构**
  - 最复杂但最可靠
  - 类型化记录：Mode, ID, Selector, Policy
  - 分支执行：Gate（检查有效性）vs Actor（从S₁选择）
  - 双勾标注："类型化 + 确定性门控"

**设计亮点**:
- 流程框图展示数据流
- 颜色编码组件类型
- 分支路径可视化
- 复杂度渐进

**建议使用位置**: Methods部分解释实验设计

---

## 使用建议

### 在LaTeX论文中引用

```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Figures/tri_comprehensive_analysis.pdf}
\caption{Comprehensive ablation analysis showing (A) PairAcc improvements across conditions, 
(B) dramatic reduction in substitution rates with decision visibility, (C) mixed enforcement 
effects, (D) preserve vs reevaluate accuracy breakdown, and (E) full metrics heatmap across 
all model-condition combinations.}
\label{fig:comprehensive}
\end{figure*}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{Figures/tri_temporal_flow_comprehensive.pdf}
\caption{Temporal flow diagrams illustrating (A) PRESERVE: binding before refresh requires 
writing to the old target A, and (B) REEVALUATE: binding after refresh requires writing to 
the new winner B. Same state transition, opposite authorized targets.}
\label{fig:temporal-flow}
\end{figure}
```

### 图表质量优势

1. **信息密度提升**
   - 原图：单一维度，1-2个指标
   - 新图：多面板，5-6个维度，10+个指标

2. **视觉层次清晰**
   - 使用颜色编码区分类别
   - 字体粗细强调关键结果
   - 标注和图例完整

3. **适合期刊要求**
   - 300 DPI高分辨率
   - 矢量PDF格式
   - 颜色和黑白打印均可读

4. **可读性优化**
   - 合理的字号（7-9pt）
   - 充足的留白
   - 明确的轴标签和图例

---

## 与原图的对比

### 原有图表的问题
- `tri_v3_results.pdf`: 只显示一个维度的准确率对比
- `tri_authorization_tradeoff.pdf`: 散点图信息密度低
- `tri_new_schema_consequence_matrix.pdf`: 只有错误矩阵，缺乏上下文

### 新图表的改进
- **多维度整合**: 一张图包含原来3-4张图的信息
- **层次化展示**: 从高层概况到详细分解
- **上下文丰富**: 同时展示准确率、错误率、改进幅度
- **因果关系**: 用箭头、颜色、布局展示变量间关系

---

## 定制和扩展

### 修改数据

所有脚本从JSON文件加载数据，主要数据源：
- `reports/call_matched_authorization_ablation_v2.json`
- `reports/matched_pair_consistency.json`

修改数据后重新运行：
```bash
bash scripts/generate_all_paper_figures.sh
```

### 调整样式

在各脚本顶部的COLORS字典中修改颜色方案：
```python
COLORS = {
    'qwen': '#B64926',     # 橙红色
    'glm': '#126F66',      # 深绿色
    'deepseek': '#7A8793', # 灰色
    ...
}
```

### 添加新面板

在相应脚本中添加新的`plot_xxx`函数，然后在主函数中调用即可。

---

## 技术细节

### 生成环境
- Python 3.14.6
- Matplotlib 3.11.1
- Seaborn 0.13.2
- NumPy 2.5.1

### 文件大小
每个PDF文件约50-200KB，适合论文提交和在线发布。

### 兼容性
- 所有PDF使用标准字体，无需嵌入特殊字体
- 兼容Overleaf、本地LaTeX编译
- 支持IEEE、ACM、AAAI等会议格式

---

## 常见问题

**Q: 图表太大无法放入单栏？**
A: tri_comprehensive_analysis和tri_new_schema_comprehensive设计为双栏图(\figure*)，其他图适合单栏。

**Q: 颜色在黑白打印中不清晰？**
A: 所有图表使用不同的标记形状（圆圈、方块、三角形）和线型（实线、虚线），黑白打印仍可区分。

**Q: 需要更高分辨率？**
A: 修改脚本中的`dpi=300`为`dpi=600`，但文件会变大。

**Q: 如何只生成特定图表？**
A: 单独运行相应脚本：
```bash
python scripts/make_comprehensive_figures.py
```

---

## 下一步建议

1. **在论文中使用这些新图替换旧图**，提升整体质量
2. **根据审稿人意见调整细节**，如颜色、标注、面板布局
3. **考虑制作动画版本**用于演讲展示
4. **准备高分辨率版本**用于海报或补充材料

---

## 联系与反馈

如需进一步定制或有任何问题，请查看脚本代码或联系作者。

生成日期：2026-07-26
