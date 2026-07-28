# Revision Matched Audit: full_diagnostic

**Evidence status:** post-primary; protocol frozen before own calls.

Matched actor evidence only. Human rewrites retain authored task semantics; source-grounded contrasts are controlled interventions, not native benchmark prevalence or open-language proof.

## Pro/MiniMaxAI/MiniMax-M2.5

Rows/clusters: 160/80; cluster sizes: {2: 80}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 43.8% (14/32), CI [28.1, 62.5] | 85.9% (110/128), CI [80.5, 91.3] | 56.2% (18/32), CI [38.9, 73.1] | 35.8% (19/53), CI [23.4, 49.1] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 14.1% (18/128), CI [8.7, 19.5] |
| decision_visible | 78.1% (25/32), CI [62.5, 90.6] | 94.5% (121/128), CI [90.5, 97.8] | 75.0% (24/32), CI [59.3, 89.7] | 5.7% (3/53), CI [0.0, 12.7] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 5.5% (7/128), CI [2.2, 9.5] |
| decision_enforced | 84.4% (27/32), CI [71.9, 96.9] | 96.1% (123/128), CI [92.6, 99.2] | 81.2% (26/32), CI [66.7, 93.8] | 0.0% (0/53), CI [0.0, 0.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 3.9% (5/128), CI [0.8, 7.4] |

### Source slices

- Matched Timing Diagnostic: History PairAcc 43.8% (14/32), CI [28.1, 62.5]; Visible PairAcc 78.1% (25/32), CI [62.5, 90.6].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.34375, 'ci95_cluster': [0.11111111111111105, 0.5833333333333333]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.0859375, 'ci95_cluster': [0.04132231404958675, 0.1328125]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 4/0.
Logical calls completed/planned: 480/480; HTTP attempts: 480.

## Pro/zai-org/GLM-5.1

Rows/clusters: 160/80; cluster sizes: {2: 80}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 25.0% (8/32), CI [9.4, 40.6] | 79.7% (102/128), CI [73.8, 85.6] | 34.4% (11/32), CI [18.4, 51.6] | 50.0% (24/48), CI [36.0, 64.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 18.0% (23/128), CI [12.3, 23.6] |
| decision_visible | 78.1% (25/32), CI [62.5, 90.6] | 93.8% (120/128), CI [89.5, 97.6] | 65.6% (21/32), CI [48.4, 82.1] | 0.0% (0/48), CI [0.0, 0.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 5.5% (7/128), CI [2.2, 9.4] |
| decision_enforced | 78.1% (25/32), CI [62.5, 90.6] | 93.8% (120/128), CI [89.5, 97.6] | 78.1% (25/32), CI [62.9, 92.0] | 0.0% (0/48), CI [0.0, 0.0] | 0.0% (0/64), CI [0.0, 0.0] | NA (0/0) | 5.5% (7/128), CI [2.2, 9.4] |

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
| history_only | 15.6% (5/32), CI [3.1, 28.1] | 78.1% (100/128), CI [72.4, 84.0] | 65.6% (21/32), CI [48.4, 81.5] | 53.6% (30/56), CI [40.4, 66.7] | 1.9% (1/53), CI [0.0, 6.2] | NA (0/0) | 20.3% (26/128), CI [14.5, 26.0] |
| decision_visible | 40.6% (13/32), CI [25.0, 59.4] | 82.8% (106/128), CI [76.9, 88.5] | 78.1% (25/32), CI [63.0, 91.4] | 25.0% (14/56), CI [14.0, 36.5] | 0.0% (0/53), CI [0.0, 0.0] | NA (0/0) | 13.3% (17/128), CI [8.1, 18.5] |
| decision_enforced | 75.0% (24/32), CI [59.4, 90.6] | 88.3% (113/128), CI [82.5, 93.4] | 87.5% (28/32), CI [75.0, 97.1] | 0.0% (0/56), CI [0.0, 0.0] | 0.0% (0/53), CI [0.0, 0.0] | NA (0/0) | 6.2% (8/128), CI [2.4, 10.4] |

### Source slices

- Matched Timing Diagnostic: History PairAcc 15.6% (5/32), CI [3.1, 28.1]; Visible PairAcc 40.6% (13/32), CI [25.0, 59.4].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.25, 'ci95_cluster': [0.0625, 0.4615384615384615]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.046875, 'ci95_cluster': [0.0, 0.09375]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 18/8.
Logical calls completed/planned: 480/480; HTTP attempts: 480.

## deepseek-ai/DeepSeek-V4-Pro

Rows/clusters: 160/80; cluster sizes: {2: 80}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 34.4% (11/32), CI [18.8, 50.0] | 83.6% (107/128), CI [77.9, 89.2] | 50.0% (16/32), CI [32.3, 67.6] | 50.8% (30/59), CI [38.3, 63.3] | 0.0% (0/54), CI [0.0, 0.0] | NA (0/0) | 16.4% (21/128), CI [10.8, 22.1] |
| decision_visible | 78.1% (25/32), CI [62.5, 90.6] | 90.6% (116/128), CI [84.7, 95.5] | 84.4% (27/32), CI [70.6, 96.4] | 1.7% (1/59), CI [0.0, 5.5] | 0.0% (0/54), CI [0.0, 0.0] | NA (0/0) | 3.1% (4/128), CI [0.8, 6.3] |
| decision_enforced | 81.2% (26/32), CI [65.6, 93.8] | 91.4% (117/128), CI [86.3, 96.0] | 87.5% (28/32), CI [75.0, 97.1] | 0.0% (0/59), CI [0.0, 0.0] | 0.0% (0/54), CI [0.0, 0.0] | NA (0/0) | 4.7% (6/128), CI [1.6, 8.5] |

### Source slices

- Matched Timing Diagnostic: History PairAcc 34.4% (11/32), CI [18.8, 50.0]; Visible PairAcc 78.1% (25/32), CI [62.5, 90.6].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.4375, 'ci95_cluster': [0.16666666666666669, 0.7142857142857142]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.0703125, 'ci95_cluster': [0.0, 0.13636363636363646]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 5/3.
Logical calls completed/planned: 480/480; HTTP attempts: 480.

Negative, null, mixed, parse-failure, transport-failure, and enforcement-harm outcomes are retained.
