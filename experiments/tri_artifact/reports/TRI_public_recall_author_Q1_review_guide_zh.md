# Public Recall 作者复核 Q1 操作说明

本轮复核的身份是 `Q1`（作者 QA），不是独立标注者 A1--A3。完成 Q1 后，复核者不能再
作为 A1、A2 或 A3。Q1 的结果只能检查模型预标签，不能进入独立人类多数票，也不能解锁
prevalence、recall、human agreement 或“自然正例为零”的论文主张。

协调者须在复核前建立私有 `private_role_registry.json`。每个自然人只生成一个稳定的、
至少 128 位随机 participant token；同一人如被误分配到两个角色，必须复用该 token，因而
会被重叠检查拒绝。表中只保存 SHA-256，不保存姓名、联系方式或原始令牌。协调者须确认
Q1、A1、A2、A3 对应四个不同自然人及四个不同哈希。另由 Q1 填写私有
`Q1_reviewer_provenance.json`，确认 699 行均由
本人阅读 source evidence、模型建议仅作提示。二者都留在 `human_studies/`，不进入匿名包。

## 使用文件

- 自包含复核表：`reports/public_recall_model_prelabels_partial_v1_author_qa_template.csv`
- 完整机器可读队列：`reports/public_recall_model_prelabels_partial_v1_author_qa_queue.jsonl`
- 运行与失败边界：`reports/TRI_public_recall_model_prelabels_failure_diagnostic_addendum.md`

CSV 已按 `review_priority` 排序。优先级 0 包含缺模型票、最终 strict 标签不一致或任一
rubric 字段不一致的单位。`source_evidence_json` 是唯一允许使用的事实来源；
`model_labels_json` 仅用于定位分歧。不要查看 private annotation key、sampling role、control
gold 或 source-unit identity 后再作答。

## 每行填写规则

八个 `author_qa_feature_*` 字段只能填 `yes`、`no` 或 `partial`。缺失事件不能推断为存在。
只有八个字段全部为 `yes` 时，`author_qa_strict_eligible` 才能填 `true`，且
`author_qa_primary_exclusion_reason` 必须填 `NONE`。否则 strict 必须为 `false`，并从一个
非 `yes` 的 rubric 字段中选择 primary exclusion reason。`author_qa_confidence` 填 1--5，
`author_qa_notes` 简要引用 source evidence。缺失模型票不是 negative vote。

若要生成完整 Q1 报告，699 行必须全部填写。可以先完成 priority 0，但部分 CSV 不能通过
正式 ingestion。

## 推荐的七批复核流程

`human_studies/public_recall_Q0_model_drafts_v1.csv` 是三模型面板生成的非人工预审表。
其中 `q0_*` 字段只用于定位优先复核项，不能复制后直接声明为 Q1 判断，也不能进入
A1--A3 多数票。Q1 必须回到七批文件中的 `source_evidence_json` 独立核对。

先把 699 行按现有优先级顺序拆成 100/100/100/100/100/100/99 七批：

```bash
PYTHONPATH=. python3 scripts/prepare_public_recall_author_Q1_batches.py prepare
```

输出位于 `human_studies/public_recall_author_Q1_batches_v1/`。每行复核完成后，将
`qa_review_status` 从 `pending_human_Q1_review` 改为 `human_Q1_reviewed`。模型标签只是定位
分歧的建议；`model_suggestion_*` 是三模型逐字段多数建议，平票写为 `review_required`。
八个人工字段、strict、排除原因、置信度和 notes 必须由 Q1 阅读 source evidence 后填写，
不能直接把建议列复制为人类判断。

全部七批完成后合并。合并器会拒绝未复核行、缺字段、重复/缺失 ID，以及对 source
evidence、模型标签或排序字段的改动：

```bash
PYTHONPATH=. python3 scripts/prepare_public_recall_author_Q1_batches.py merge \
  --manifest human_studies/public_recall_author_Q1_batches_v1/manifest.json \
  --input-dir human_studies/public_recall_author_Q1_batches_v1 \
  --output human_studies/public_recall_author_Q1_reviewed_v1.csv \
  --reviewer-provenance human_studies/Q1_reviewer_provenance.json \
  --private-role-registry human_studies/private_role_registry.json
```

合并器同时生成 `public_recall_author_Q1_reviewed_v1.manifest.json`，锁定合并 CSV、七个已
复核批次、原模板、队列、Q1 provenance 和私有角色表。直接制作一个 699 行 CSV 不能通过
后续 ingestion。`prepare` 默认拒绝覆盖非空目录；只有确认要清空并重建工作批次时才使用
`--force`。该选项只清理本版本的 batch CSV 和 manifest；目录中出现其他文件时仍会拒绝。

## 完成后的验证命令

从 `experiments/tri_artifact/` 运行：

```bash
PYTHONPATH=. python3 scripts/ingest_public_recall_author_qa.py \
  --queue reports/public_recall_model_prelabels_partial_v1_author_qa_queue.jsonl \
  --qa-csv human_studies/public_recall_author_Q1_reviewed_v1.csv \
  --review-manifest human_studies/public_recall_author_Q1_reviewed_v1.manifest.json \
  --reviewed-batches-dir human_studies/public_recall_author_Q1_batches_v1 \
  --private-role-registry human_studies/private_role_registry.json \
  --template reports/public_recall_model_prelabels_partial_v1_author_qa_template.csv \
  --batch-manifest human_studies/public_recall_author_Q1_batches_v1/manifest.json \
  --reviewer-provenance human_studies/Q1_reviewer_provenance.json \
  --output reports/public_recall_author_Q1_v1.json
```

成功输出仍会明确标记 `author QA of model-assisted labels; not independent-human evidence`、
`human_gate_unlocked=false` 和 `prevalence_or_recall_claim_allowed=false`。
