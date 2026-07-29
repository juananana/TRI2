# TRI Public-Recall Model-Prelabel Failure Diagnostic Addendum

**Status:** post-run, model-assisted author-QA diagnostic; disclosed as a failed-gate study
boundary, not an independent-human, prevalence, recall, agreement, or natural-zero endpoint.

**Freeze time:** 2026-07-29 after the three full run files closed and after the frozen formal
`699/699 complete` gate failed. This addendum does not amend the pre-call protocol, whose SHA-256
remains `89daec1a96d34b750080dfd056ad51c51ff25590136e836cc95fc213dd557d91`.

## Frozen run outcomes

| Labeler / model | Rows | Complete | Incomplete | HTTP attempts | Retries | Run SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| M1 / Qwen | 699 | 699 | 0 | 699 | 0 | `8cde5b60f49d786d1f1c0d91fb3270ba61edfb168634f832573de97c162c09f3` |
| M2 / GLM | 699 | 695 | 4 | 699 | 0 | `34d47ee9b4ad7a5984dc9a1595cffb854576466e3244680ebecbfb79a04e593d` |
| M3 / DeepSeek | 699 | 685 | 14 | 699 | 0 | `dd1c8cc0dcef311deb1f7de0d37ca52b7580c8ae32a2f9300bcc94f05f523935` |

All 18 failures followed a retained transport-success response but failed strict parsing or schema
validation. They are not logically rerun. The formal reporter rejects the matrix because M2 and M3
are incomplete. Across the three runs, 2,097 HTTP attempts used 2,941,998 reported tokens
(2,474,758 prompt and 467,240 completion tokens); reported prompt-cache hits total 352,512 tokens.

## Failure-aware author-QA queue

The post-run reporter validates all three 699-row frozen inventories, then admits only parsed labels
to the diagnostic queue. Missing labels remain missing and never become negative votes. Affected
units have no provisional majority or unanimity value and receive priority zero.

- 681 units have complete three-model panels; 18 have at least one missing model label.
- Queue priorities are 517 priority-zero, 18 provisional-positive, 91 low-confidence, and 73
  remaining unanimous-negative units.
- Among complete panels, strict-positive vote counts are 524 with zero votes, 127 with one vote,
  12 with two votes, and 18 with three votes.
- All 30 complete-panel provisional majority positives are injected strict-positive controls.
- Retrieved candidates have 115 complete panels and zero majority positives, with one incomplete
  panel. Random non-candidates have 509 complete panels and zero majority positives, with 14
  incomplete panels. These incomplete natural units prohibit a zero-positive claim even before the
  independent-human gate is considered.

Model-specific diagnostics expose why model labels cannot substitute for human review. Qwen labels
zero natural units positive and classifies all 60 controls correctly. GLM labels zero natural units
positive, recovers 24/30 positive controls, and correctly excludes all 27 available negative
controls. DeepSeek labels 126 natural units positive, recovers 24/30 positive controls, and excludes
29/30 negative controls. The resulting 501 rubric-disagreement rows are author-QA priorities, not a
prevalence estimate.

## Frozen artifacts

- Partial report: `reports/public_recall_model_prelabels_partial_v1.json`, SHA-256
  `958b3f8c82b938465ee8328ed9f4f490ee042ac78bf37fe9e98827871ee9d112`.
- Separate aggregate role-quality report:
  `reports/public_recall_model_prelabels_partial_v1_role_quality.json`, SHA-256
  `dfaff60f18dfd9549edeb02878ff346d227f12268405429b43199c2634e7d2a7`. It records and
  validates the frozen private-key hash; the key itself is excluded from the public artifact.
- Author-QA queue: `reports/public_recall_model_prelabels_partial_v1_author_qa_queue.jsonl`, SHA-256
  `10ce1f60c6053593435e79285f2c253930bc39b00a366f88e256bad6d02b6a36`.
- Author-QA CSV: `reports/public_recall_model_prelabels_partial_v1_author_qa_template.csv`, SHA-256
  `1586b665fee864da63c4d2b568b7e9df8e0553e908ccc5ec1494494efe212fff`.
- Parsed partial returns for M1/M2/M3 have 699/695/685 rows and SHA-256 values
  `317558d52191b9cd99078f3e5e72134c88a54aa9a1bcfab247eb565282b3326f`,
  `6807848677d258c3e9dc8100eb18a2160952a85f9635f8db0924476348972114`, and
  `4b4c74c0203a32524dbbda3329667c60e3208f298f283a698feb71a1b27f1701`.

The author reviewer is labeled Q1 and must not later serve as A1--A3. Completing Q1 can produce an
author-QA report only; it cannot unlock the independent-human public audit or enter its majority.
