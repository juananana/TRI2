# TRI 论文工作目录

这是当前唯一的论文写作入口。需要编辑、编译或上传到 Overleaf 的文件都放在本目录；实验原始数据和代码不复制到这里，而是统一保存在 `../experiments/tri_artifact/`。

## 当前文件

| 用途 | 文件 |
| --- | --- |
| 主论文源码 | `AnonymousSubmission2027.tex` |
| 主论文 PDF | `AnonymousSubmission2027.pdf`（2026-07-21 成功编译，8 页：7 页正文 + 1 页参考文献） |
| 补充材料源码 | `supplementary_material.tex` |
| 补充材料 PDF | `supplementary_material.pdf` |
| 参考文献 | `aaai2027.bib` |
| AAAI 样式 | `aaai2027.sty`, `aaai2027.bst` |
| 可复现性清单 | `ReproducibilityChecklist.tex` |
| 正式插图 | `Figures/` |

主文和补充材料使用的文件名保持 AAAI 官方模板约定，便于直接复制到 Overleaf。`paper/` 中的样式文件与 `AuthorKit27/` 中的官方样式文件内容一致；前者是当前稿独立编译所需的工作副本，后者是只读参考模板，不要删除或混用两套源码。

当前环境已安装 TeX Live 2026。本轮主文和补充材料均已用 `latexmk` 完整编译；主文为 8 页，正文止于第 7 页，参考文献从第 8 页开始。PDF 仍应在每次实质源码修改后重新编译并检查页数、表格、图和参考文献。

## 证据和复现文件

论文数字的唯一证据源是 `../experiments/tri_artifact/`：

- `data/`：冻结任务数据；
- `runs/`：原始模型运行记录；
- `reports/`：协议、统计报告、表格数据和主张来源映射；
- `human_validation/`：匿名化人工验证数据及分析；
- `tri/`、`scripts/`、`tests/`：评测实现、运行脚本和测试。

不要把报告或 JSONL 复制进 `paper/`。复制会产生两个可能不一致的结果版本；需要查证论文数字时，请从 `reports/current_claim_provenance.md` 开始，再沿其中的路径回到冻结数据和原始 run。

## 编译

在本目录执行：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error AnonymousSubmission2027.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_material.tex
```

## 上传边界

不要把整个仓库或整个 `paper/` 目录直接作为匿名提交包上传。按照 `提交文件说明_请勿整目录上传.md` 选择主文、参考文献、样式文件、插图和补充材料；匿名实验包使用 `../submission/tri_anonymous_artifact_current.zip`。

隐私规则：API key、志愿者身份信息、原始 XLSX、私有答案映射和协调表不得进入论文源码或公开 artifact。
