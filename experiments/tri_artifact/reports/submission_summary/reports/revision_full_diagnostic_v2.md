# Revision Matched Audit: full_diagnostic

**Evidence status:** post-primary; protocol frozen before own calls.

Matched actor evidence only. Human rewrites retain authored task semantics; source-grounded contrasts are controlled interventions, not native benchmark prevalence or open-language proof.

## Pro/zai-org/GLM-5.1

Rows/clusters: 160/80; cluster sizes: {2: 80}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 25.0% (8/32), CI [9.4, 40.6] | 79.7% (102/128), CI [73.8, 85.6] | 34.4% (11/32), CI [18.4, 51.6] | 64.0% (16/25), CI [44.8, 82.1] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 18.0% (23/128), CI [12.3, 23.6] |
| decision_visible | 78.1% (25/32), CI [62.5, 90.6] | 93.8% (120/128), CI [89.5, 97.6] | 65.6% (21/32), CI [48.4, 82.1] | 0.0% (0/25), CI [0.0, 0.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 5.5% (7/128), CI [2.2, 9.4] |
| decision_enforced | 78.1% (25/32), CI [62.5, 90.6] | 93.8% (120/128), CI [89.5, 97.6] | 78.1% (25/32), CI [62.9, 92.0] | 0.0% (0/25), CI [0.0, 0.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 5.5% (7/128), CI [2.2, 9.4] |

### Source slices

- Matched Timing Diagnostic: History PairAcc 25.0% (8/32), CI [9.4, 40.6]; Visible PairAcc 78.1% (25/32), CI [62.5, 90.6].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.53125, 'ci95_cluster': [0.2857142857142857, 0.7777777777777777]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.140625, 'ci95_cluster': [0.08396946564885499, 0.19999999999999996]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 4/0.
Logical calls completed/planned: 480/480; HTTP attempts: 480.

## Qwen/Qwen3.5-122B-A10B

Rows/clusters: 160/80; cluster sizes: {2: 80}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 15.6% (5/32), CI [3.1, 28.1] | 78.1% (100/128), CI [72.4, 84.0] | 65.6% (21/32), CI [48.4, 81.5] | 78.6% (22/28), CI [62.5, 92.9] | 1.9% (1/53), CI [0.0, 6.2] | NA (0/0) | 20.3% (26/128), CI [14.5, 26.0] |
| decision_visible | 40.6% (13/32), CI [25.0, 59.4] | 82.8% (106/128), CI [76.9, 88.5] | 78.1% (25/32), CI [63.0, 91.4] | 46.4% (13/28), CI [28.0, 65.4] | 0.0% (0/53), CI [0.0, 0.0] | NA (0/0) | 13.3% (17/128), CI [8.1, 18.5] |
| decision_enforced | 75.0% (24/32), CI [59.4, 90.6] | 88.3% (113/128), CI [82.5, 93.4] | 87.5% (28/32), CI [75.0, 97.1] | 0.0% (0/28), CI [0.0, 0.0] | 0.0% (0/53), CI [0.0, 0.0] | NA (0/0) | 6.2% (8/128), CI [2.4, 10.4] |

### Source slices

- Matched Timing Diagnostic: History PairAcc 15.6% (5/32), CI [3.1, 28.1]; Visible PairAcc 40.6% (13/32), CI [25.0, 59.4].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.25, 'ci95_cluster': [0.0625, 0.4615384615384615]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.046875, 'ci95_cluster': [0.0, 0.09375]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 18/8.
Logical calls completed/planned: 480/480; HTTP attempts: 480.

Negative, null, mixed, parse-failure, transport-failure, and enforcement-harm outcomes are retained.

## Report amendment

The v1 report mixed author-specified Reject rows into the Preserve-substitution denominator. V2 requires `actionable_core`; all raw outputs, ITT accuracy, PairAcc, wrong-write, and failure metrics are unchanged. The v1 report remains in the artifact.
