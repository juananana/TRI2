# TRI Human Construct Validation

中文用户友好入口：`人工验证操作手册_中文.md`。正式标注只发送
`最终分行版_标注者1.xlsx`、`最终分行版_标注者2.xlsx`、
`最终分行版_标注者3.xlsx`，每位标注者各收到一个文件。旧的 JSON 版工作簿仅作历史保留，
不要发送给正式标注者。最终分行版按对象 ID 逐行展示完整属性，并隐藏实验条件和标准答案。
正式参与者使用中文列名表；任务文本仍保留英文以避免引入翻译混淆。

This package validates whether people independently recover the benchmark's post-binding target
semantics. Model-generated judgments do not count as human annotations.

## Roles

- One paraphrase author who did not design TRI rewrites 50 instructions.
- Three different annotators, also uninvolved in TRI design, label all 100 randomized items.
- The paraphrase author must not be one of the three annotators.
- Annotators must not see `annotation_key_private.csv`, TRI terminology, source task IDs,
  condition metadata, text-variant labels, or each other's answers. Participant forms use opaque
  item IDs; all experimental metadata stays only in the private key.

Record anonymous participant IDs and basic English proficiency, but do not collect names or other
unnecessary personal information. Obtain informed consent for research use before annotation.

## Step 1: Independent natural rewrites

Give only `paraphrase_authoring.csv` to the paraphrase author. For each row, rewrite the original
instruction as something a real user might say while preserving its operational meaning.

- Do not add `preserve`, `reevaluate`, `binding`, `TRI`, or benchmark labels.
- Do not add target IDs or reveal which target is correct.
- Avoid mechanical synonym replacement; change sentence structure where natural.
- If the source is genuinely unclear, note that in `author_notes` rather than silently resolving it.

After all 50 `rewrite_instruction` cells are complete, run:

```bash
python3 scripts/make_human_validation_packet.py --compile
```

This creates three differently randomized annotation forms and a private answer key.

## Step 2: Blind semantic annotation

Give one `最终分行版_标注者N.xlsx` file to each annotator. These files contain only opaque item IDs
and task information. For every row, inspect the instruction, initial
state, refreshed state, and action preconditions. Enter exactly one response:

- an entity ID from `candidate_ids`;
- `REJECT` when no entity should be acted on;
- `CLARIFY` when the instruction does not determine a sufficiently clear action.

Confidence is optional on a 1--5 scale. Annotators may not consult the private key or discuss
items while labeling.

## Step 3: Analysis

After all forms are complete, the analysis script accepts either normalized CSV files or the
Chinese-column XLSX returns directly:

```bash
python3 scripts/analyze_human_validation.py \
  --forms human_validation/annotator_1.csv \
          human_validation/annotator_2.csv \
          human_validation/annotator_3.csv \
  --key human_validation/annotation_key_private.csv \
  --output human_validation/analysis.json \
  --markdown-output human_validation/analysis.md
```

The report includes majority-gold accuracy, exact response agreement, semantic-label Fleiss'
kappa and nominal Krippendorff's alpha, clarification, consensus-only sensitivity, annotator
audits, and explicit, implicit, original, rewrite, anchored, dynamic, and update slices. It
handles three-way ties as no majority rather than selecting an arbitrary answer. Low-agreement
items must not be silently retained as determinate errors.
