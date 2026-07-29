# Revision Matched Audit: human_rewrite

**Evidence status:** post-primary; protocol frozen before own calls.

Matched actor evidence only. Human rewrites retain authored task semantics; source-grounded contrasts are controlled interventions, not native benchmark prevalence or open-language proof.

## Pro/zai-org/GLM-5.1

Rows/clusters: 50/43; cluster sizes: {1: 36, 2: 7}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 33.3% (1/3), CI [0.0, 100.0] | 77.5% (31/40), CI [64.4, 89.5] | 40.0% (4/10), CI [10.0, 71.4] | 90.0% (9/10), CI [66.7, 100.0] | 0.0% (0/20), CI [0.0, 0.0] | 68.8% (33/48), CI [56.0, 80.9] | 22.5% (9/40), CI [10.5, 35.6] |
| decision_visible | 100.0% (3/3), CI [100.0, 100.0] | 97.5% (39/40), CI [91.7, 100.0] | 80.0% (8/10), CI [50.0, 100.0] | 0.0% (0/10), CI [0.0, 0.0] | 0.0% (0/20), CI [0.0, 0.0] | 85.4% (41/48), CI [74.5, 94.2] | 0.0% (0/40), CI [0.0, 0.0] |
| decision_enforced | 100.0% (3/3), CI [100.0, 100.0] | 100.0% (40/40), CI [100.0, 100.0] | 90.0% (9/10), CI [66.7, 100.0] | 0.0% (0/10), CI [0.0, 0.0] | 0.0% (0/20), CI [0.0, 0.0] | 89.6% (43/48), CI [80.0, 97.8] | 0.0% (0/40), CI [0.0, 0.0] |

### Source slices

- independent human rewrite of authored task: History PairAcc 33.3% (1/3), CI [0.0, 100.0]; Visible PairAcc 100.0% (3/3), CI [100.0, 100.0].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.6666666666666666, 'ci95_cluster': [0.0, 1.0]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.19999999999999996, 'ci95_cluster': [0.08571428571428574, 0.32499999999999996]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 2/0.
Logical calls completed/planned: 150/150; HTTP attempts: 150.

## Qwen/Qwen3.5-122B-A10B

Rows/clusters: 50/43; cluster sizes: {1: 36, 2: 7}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 0.0% (0/3), CI [0.0, 0.0] | 75.0% (30/40), CI [62.2, 87.2] | 80.0% (8/10), CI [50.0, 100.0] | 90.0% (9/10), CI [66.7, 100.0] | 0.0% (0/13), CI [0.0, 0.0] | 70.8% (34/48), CI [58.8, 82.6] | 22.5% (9/40), CI [10.8, 35.0] |
| decision_visible | 33.3% (1/3), CI [0.0, 100.0] | 75.0% (30/40), CI [61.7, 87.8] | 100.0% (10/10), CI [100.0, 100.0] | 80.0% (8/10), CI [50.0, 100.0] | 0.0% (0/13), CI [0.0, 0.0] | 72.9% (35/48), CI [60.8, 84.4] | 20.0% (8/40), CI [8.6, 32.5] |
| decision_enforced | 66.7% (2/3), CI [0.0, 100.0] | 82.5% (33/40), CI [70.0, 93.0] | 100.0% (10/10), CI [100.0, 100.0] | 0.0% (0/10), CI [0.0, 0.0] | 0.0% (0/13), CI [0.0, 0.0] | 81.2% (39/48), CI [70.2, 91.5] | 7.5% (3/40), CI [0.0, 16.2] |

### Source slices

- independent human rewrite of authored task: History PairAcc 0.0% (0/3), CI [0.0, 0.0]; Visible PairAcc 33.3% (1/3), CI [0.0, 100.0].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.3333333333333333, 'ci95_cluster': [0.0, 1.0]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.0, 'ci95_cluster': [-0.10000000000000009, 0.09523809523809523]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 8/5.
Logical calls completed/planned: 150/150; HTTP attempts: 150.

Negative, null, mixed, parse-failure, transport-failure, and enforcement-harm outcomes are retained.

## Report amendments

V2 restricted Preserve-substitution eligibility to the actionable core. V3 additionally repairs the changed-PairAcc difference interval: the earlier reporter merged repeated bootstrap draws by their original pair ID and dropped merged four-or-more-row groups. V3 directly resamples eligible pairs with replacement. Point estimates, denominators, raw outputs, tasks, gold labels, and failure accounting are unchanged.
