# TRI 论文实验结果图 - 最终版本

## 📊 推荐使用的图表（已生成）

### 🎯 主要结果图

#### 1. **tri_main_results.pdf** (47KB) ⭐⭐⭐⭐⭐
**推荐用于**: Results部分的主要实验结果

**包含3个面板**:
- **Panel A**: Controller Improvement（斜率图）
  - 清晰展示Generic→CTA的性能提升
  - 使用连线展示每个模型的改进轨迹
  - Qwen: 9.4% → 93.8%, GLM: 21.9% → 96.9%

- **Panel B**: Preserve vs Reevaluate（分组柱状图）
  - 对比两个关键维度的准确率
  - Preserve是挑战（红棕色），Reevaluate相对容易（青色）
  - 清晰显示CTA在Preserve上的巨大改进

- **Panel C**: Changed-Winner PairAcc（热图矩阵）
  - 紧凑的2×2矩阵展示核心指标
  - 颜色编码：红→黄→绿（0-100%）
  - 一目了然看出CTA的优势

**配色**: 
- 主色：深青色 #2A7B7E（CTA/解决方案）
- 对比色：陶土红 #C96D5A（Generic/问题）
- 中性色：深灰 #3D4852（基线）

**优势**:
- ✅ 信息密度高但不拥挤
- ✅ 3种可视化方式展示同一发现的不同角度
- ✅ 配色协调，符合顶会审美
- ✅ 字号符合AAAI规范（9-10pt）

---

#### 2. **tri_policy_comparison.pdf** (51KB) ⭐⭐⭐⭐⭐
**推荐用于**: Methods或Results开头，解释评估方法的优越性

**包含2个面板**:
- **Panel A**: One-Sided Evaluation Problem
  - 展示单侧评估的问题：Always-Lock和Always-Reevaluate都能在各自的测试上得高分
  - 红色高亮区域标注"⚠ 单侧评估偏向极端策略"
  - 清晰说明为什么现有评估方法不够

- **Panel B**: Matched Pairs Solution
  - 展示配对评估如何区分策略
  - 只有CTA和选择性策略能得高分，极端策略得0分
  - 绿色高亮区域标注"✓ 配对评估能区分选择性策略"

**设计亮点**:
- 对比式布局（问题 vs 解决方案）
- 使用视觉标注（警告⚠ vs 成功✓）
- 颜色区域引导视线到关键信息

---

#### 3. **tri_results_clean.pdf** (52KB) ⭐⭐⭐⭐
**推荐用于**: Results部分，ablation分析

**包含3个面板**:
- **Panel A**: Decision Visibility Impact（改进对比）
  - Before/After柱状图 + 改进箭头
  - 数值标注增益（+20pp, +30pp）

- **Panel B**: Substitution Elimination（瀑布图风格）
  - 戏剧性展示替换率的下降
  - 从57%/50%降到14%/0%
  - 使用重叠柱状图 + 下降标注

- **Panel C**: Cross-Model Consistency（散点图）
  - 展示改进在不同模型间的一致性
  - 对角线参考线
  - 改进区域阴影标注

---

#### 4. **tri_schema_transfer_clean.pdf** (47KB) ⭐⭐⭐⭐
**推荐用于**: Results部分，Schema transfer实验

**包含2个面板**:
- **Panel A**: Substitution Cascade（堆叠横向条形图）
  - 清晰展示Generic的替换问题：43/72, 38/80, 59/79
  - CTA完美：0/71, 0/70, 0/70
  - 颜色区分：红色=替换，青色=正确

- **Panel B**: Accuracy Trade-off Space（散点图 + 箭头）
  - 二维空间：准确率 vs 替换率
  - 理想区域标注（高准确率+零替换）
  - 改进轨迹箭头（Generic→CTA）

---

## 🎨 设计特点

### 配色方案（3色系统）
```
主色：深青色 #2A7B7E  - CTA、解决方案、成功
对比色：陶土红 #C96D5A - Generic、问题、挑战
中性色：深灰色 #3D4852 - 基线、参考
```

**为什么选择这个配色**：
- ✅ 受Nature/Science期刊启发的专业配色
- ✅ 色彩和谐，区分度高
- ✅ 黑白打印友好（明度对比足够）
- ✅ 符合学术审美（不花哨，不俗气）

### 字号规范（AAAI标准）
- 正文字号：9pt
- 轴标签：9pt，加粗
- 刻度标签：8pt
- 图例：8pt
- 标题：10pt，加粗
- 面板标记（A, B, C）：12pt，加粗

### 视觉层次
1. **清晰的网格线**（浅灰色，透明度30%）
2. **去除不必要的边框**（顶部和右侧spine）
3. **适当的留白**（wspace=0.32-0.38）
4. **一致的边框样式**（白色边框，linewidth=1.2）

---

## 📐 与原图对比

| 维度 | 原图 | 新图 | 改进 |
|------|------|------|------|
| 配色 | 6-8种颜色 | 3种主色 | ✅ 更协调 |
| 信息密度 | 中等 | 高 | ✅ 每张图包含更多维度 |
| 字号 | 不统一 | 9-10pt | ✅ 符合AAAI规范 |
| 视觉新颖性 | 常规柱状图 | 斜率图、瀑布图、热图矩阵 | ✅ 更有特色 |
| 拥挤程度 | 有的图太密 | 适中 | ✅ 呼吸感更好 |

---

## 📝 LaTeX使用示例

### 主要结果图（双栏）
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Figures/tri_main_results.pdf}
\caption{Main experimental results. (A) Controller improvement: CTA substantially 
outperforms Generic on changed-winner pairs (Qwen: 9.4\%→93.8\%, GLM: 21.9\%→96.9\%). 
(B) Preserve vs reevaluate breakdown shows CTA's strength on the challenging preserve 
dimension. (C) Changed-winner PairAcc matrix provides a compact view of core performance.}
\label{fig:main-results}
\end{figure*}
```

### 策略对比图（双栏）
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Figures/tri_policy_comparison.pdf}
\caption{Policy identifiability comparison. (A) One-sided evaluation fails to 
discriminate: both Always-Lock and Always-Reevaluate achieve high scores on their 
respective test sets. (B) Matched pairs successfully distinguish policies: only 
selective controllers (CTA, Generic with decision visibility) achieve non-zero PairAcc, 
while unconditional policies score 0\%.}
\label{fig:policy-comparison}
\end{figure*}
```

### Schema Transfer图（双栏）
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{Figures/tri_schema_transfer_clean.pdf}
\caption{New schema replication results. (A) Substitution cascade: Generic exhibits 
43/72 (Qwen), 38/80 (GLM), and 59/79 (DeepSeek) wrong-target substitutions after 
correct binding, while CTA shows 0/71, 0/70, and 0/70 respectively. (B) Accuracy-substitution 
trade-off space illustrates the consistent improvement trajectory across all models.}
\label{fig:schema-transfer}
\end{figure*}
```

---

## 🚀 生成新图表

所有图表可通过以下命令重新生成：

```bash
cd experiments/tri_artifact
source venv/bin/activate

# 生成主要结果图和策略对比图（基于真实数据）
python scripts/make_final_results_figures.py

# 生成消融分析图（基于ablation数据）
python scripts/make_refined_results_figures.py
```

---

## 💡 使用建议

### 最小配置（4张图）
1. ✅ tri_first_figure.pdf（保留原图，Introduction）
2. ✅ **tri_main_results.pdf**（新图，主要结果）
3. ✅ **tri_policy_comparison.pdf**（新图，方法解释）
4. ✅ tri_changed_winner_calibration.pdf（保留原图，补充）

### 推荐配置（6张图）
1. tri_first_figure.pdf
2. **tri_policy_comparison.pdf**（Methods）
3. **tri_main_results.pdf**（Results主图）
4. **tri_schema_transfer_clean.pdf**（Results，泛化）
5. **tri_results_clean.pdf**（Results，ablation）
6. tri_authorization_tradeoff.pdf（补充或Appendix）

### 完整配置（8张图）
前6张 + tri_changed_winner_calibration.pdf + tri_component_audit_dotline.pdf

---

## 🎯 关键改进总结

### 1. 配色更优雅
- ❌ 原来：多种颜色，不够协调
- ✅ 现在：3色系统，专业简洁

### 2. 视觉更新颖
- ❌ 原来：传统柱状图、散点图
- ✅ 现在：斜率图、瀑布图、热图矩阵、连接散点图

### 3. 信息密度更合理
- ❌ 原来：有的图太空，有的图太挤
- ✅ 现在：每张图3个面板，密度适中

### 4. 符合规范
- ❌ 原来：字号不统一
- ✅ 现在：严格遵循AAAI字号规范

### 5. 叙事更清晰
- ❌ 原来：图与图之间独立
- ✅ 现在：每张图讲一个完整故事（问题→解决方案）

---

## 📊 图表文件清单

### 新生成的推荐图表
- ✅ tri_main_results.pdf (47KB) - **主要结果，强烈推荐**
- ✅ tri_policy_comparison.pdf (51KB) - **方法优势，强烈推荐**
- ✅ tri_results_clean.pdf (52KB) - **消融分析，推荐**
- ✅ tri_schema_transfer_clean.pdf (47KB) - **泛化实验，推荐**

### 原有值得保留的图表
- ✅ tri_first_figure.pdf (39KB) - Introduction开篇图
- ✅ tri_authorization_tradeoff.pdf (2.8KB) - 简洁散点图
- ✅ tri_changed_winner_calibration.pdf (39KB) - 校准图

---

生成日期：2026-07-26
工具版本：Matplotlib 3.11.1
符合标准：AAAI 2027 Author Kit
