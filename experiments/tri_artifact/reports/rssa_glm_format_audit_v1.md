# Post-Hoc GLM R-SSA Format Audit

Status: **post-hoc; does not replace the prospective 0/20 strict-schema ITT result**.

| Diagnostic | Count |
|---|---:|
| Markdown-fenced outputs | 20/20 |
| Valid after removing one outer fence | 20/20 |
| Correct refresh count | 20/20 |
| Correct action-binding epoch | 20/20 |
| Correct producer edge | 20/20 |
| Correct binding inventory | 8/20 |
| Correct composition roles | 4/4 |
| Format-only structural failures | 8/20 |
| Semantic structure failures after unwrap | 12/20 |

The audit removes only one outer Markdown fence. It does not repair generated IR. GLM
grounding, Free execution, and Enforced execution were not called after strict parser
failure and therefore remain unmeasured.
