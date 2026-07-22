# Public-Suite TRI Coverage Funnel

**Status:** post-primary/descriptive; zero API; not an independent recall audit.

This report summarizes existing official ToolSandbox, AppWorld, and tau3-bench audits. It makes their exclusion paths visible but does not establish candidate retrieval recall, inter-annotator agreement, or coverage outside the pinned versions.

## ToolSandbox

Unit: semantic scenario families.

| Stage | Count |
|---|---:|
| audited families | 129 |
| after entity-mutation exclusion | 43 |
| after independent-transition exclusion | 26 |
| after prior-selection exclusion | 18 |
| TRI-like after stable-ID exclusion | 1 |
| strict native opportunities | 0 |

Near-match count: 1.

These are sequential classification buckets from the source audit, not independently measured marginal feature prevalences.

## AppWorld

Unit: generator families and released trajectories.

| Stage | Count |
|---|---:|
| audited generator families | 244 |
| TRI-like generator families | 1 |
| strict exogenous opportunities | 0 |
| released trajectories in near-match family | 42 |
| observable post-binding operations | 16 |
| observed post-binding substitutions | 0 |

Near-match count: 1.

The released-trace rows describe an action-induced preservation near-match, not an exogenous selector-flip TRI denominator.

## tau3-bench

Unit: core task definitions.

| Stage | Count |
|---|---:|
| audited tasks | 2449 |
| tasks with user-evaluation mutation | 2250 |
| tasks with stable ID in user mutation | 0 |
| metadata strict candidates | 0 |
| strict native opportunities | 0 |

Near-match count: 8.

The listed near-matches use different bill and line roles, so they do not provide a same-role target-transition comparison.

## Interpretation

The funnel supports a scoped coverage statement for three pinned benchmark versions. It does not estimate deployed prevalence and does not replace the planned independent candidate-recall and double-review audit.
