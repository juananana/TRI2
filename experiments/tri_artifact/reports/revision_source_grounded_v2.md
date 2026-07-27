# Revision Matched Audit: source_grounded

**Evidence status:** post-primary; protocol frozen before own calls.

Matched actor evidence only. Human rewrites retain authored task semantics; source-grounded contrasts are controlled interventions, not native benchmark prevalence or open-language proof.

## Pro/zai-org/GLM-5.1

Rows/clusters: 60/30; cluster sizes: {2: 30}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 36.7% (11/30), CI [20.0, 53.3] | 61.7% (37/60), CI [50.0, 73.3] | NA (0/0) | 33.3% (10/30), CI [16.7, 50.0] | 6.7% (2/30), CI [0.0, 16.7] | NA (0/0) | 26.7% (16/60), CI [16.7, 38.3] |
| decision_visible | 66.7% (20/30), CI [50.0, 83.3] | 80.0% (48/60), CI [68.3, 90.0] | NA (0/0) | 3.3% (1/30), CI [0.0, 10.0] | 10.0% (3/30), CI [0.0, 23.3] | NA (0/0) | 8.3% (5/60), CI [1.7, 15.0] |
| decision_enforced | 73.3% (22/30), CI [56.7, 90.0] | 86.7% (52/60), CI [78.3, 95.0] | NA (0/0) | 0.0% (0/30), CI [0.0, 0.0] | 10.0% (3/30), CI [0.0, 23.3] | NA (0/0) | 6.7% (4/60), CI [1.7, 13.3] |

### Source slices

- AgentDojo: History PairAcc 40.0% (4/10), CI [10.0, 70.0]; Visible PairAcc 40.0% (4/10), CI [10.0, 70.0].
- STATE-Bench: History PairAcc 50.0% (5/10), CI [20.0, 80.0]; Visible PairAcc 100.0% (10/10), CI [100.0, 100.0].
- ToolSandbox: History PairAcc 20.0% (2/10), CI [0.0, 50.0]; Visible PairAcc 60.0% (6/10), CI [30.0, 90.0].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.3, 'ci95_cluster': [0.0, 0.5555555555555556]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.18333333333333335, 'ci95_cluster': [0.08333333333333326, 0.29999999999999993]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 4/0.
Logical calls completed/planned: 180/180; HTTP attempts: 180.

## Qwen/Qwen3.5-122B-A10B

Rows/clusters: 60/30; cluster sizes: {2: 30}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 40.0% (12/30), CI [23.3, 56.7] | 65.0% (39/60), CI [53.3, 76.7] | NA (0/0) | 26.9% (7/26), CI [11.1, 45.8] | 16.7% (4/24), CI [3.8, 33.3] | NA (0/0) | 26.7% (16/60), CI [18.3, 35.0] |
| decision_visible | 43.3% (13/30), CI [26.7, 60.0] | 65.0% (39/60), CI [51.7, 76.7] | NA (0/0) | 26.9% (7/26), CI [11.1, 45.8] | 12.5% (3/24), CI [0.0, 27.3] | NA (0/0) | 28.3% (17/60), CI [18.3, 40.0] |
| decision_enforced | 56.7% (17/30), CI [40.0, 73.3] | 71.7% (43/60), CI [58.3, 83.3] | NA (0/0) | 0.0% (0/26), CI [0.0, 0.0] | 12.5% (3/24), CI [0.0, 27.3] | NA (0/0) | 25.0% (15/60), CI [13.3, 38.3] |

### Source slices

- AgentDojo: History PairAcc 40.0% (4/10), CI [10.0, 70.0]; Visible PairAcc 50.0% (5/10), CI [20.0, 80.0].
- STATE-Bench: History PairAcc 80.0% (8/10), CI [50.0, 100.0]; Visible PairAcc 80.0% (8/10), CI [50.0, 100.0].
- ToolSandbox: History PairAcc 0.0% (0/10), CI [0.0, 0.0]; Visible PairAcc 0.0% (0/10), CI [0.0, 0.0].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.033333333333333326, 'ci95_cluster': [-0.11111111111111116, 0.19999999999999996]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.0, 'ci95_cluster': [-0.06666666666666665, 0.06666666666666665]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 9/5.
Logical calls completed/planned: 180/180; HTTP attempts: 180.

## deepseek-ai/DeepSeek-V4-Pro

Rows/clusters: 60/30; cluster sizes: {2: 30}.

| Condition | Changed PairAcc | Actionable E2E | Reject slice | Preserve substitution | Reevaluate lock | Human majority | Wrong writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| history_only | 63.3% (19/30), CI [46.7, 80.0] | 75.0% (45/60), CI [61.7, 86.7] | NA (0/0) | 22.2% (6/27), CI [7.4, 38.5] | 0.0% (0/23), CI [0.0, 0.0] | NA (0/0) | 18.3% (11/60), CI [8.3, 30.0] |
| decision_visible | 73.3% (22/30), CI [56.7, 90.0] | 78.3% (47/60), CI [65.0, 91.7] | NA (0/0) | 7.4% (2/27), CI [0.0, 18.5] | 0.0% (0/23), CI [0.0, 0.0] | NA (0/0) | 15.0% (9/60), CI [3.3, 28.3] |
| decision_enforced | 66.7% (20/30), CI [50.0, 83.3] | 78.3% (47/60), CI [66.7, 90.0] | NA (0/0) | 0.0% (0/27), CI [0.0, 0.0] | 0.0% (0/23), CI [0.0, 0.0] | NA (0/0) | 21.7% (13/60), CI [10.0, 33.3] |

### Source slices

- AgentDojo: History PairAcc 60.0% (6/10), CI [30.0, 90.0]; Visible PairAcc 70.0% (7/10), CI [40.0, 100.0].
- STATE-Bench: History PairAcc 100.0% (10/10), CI [100.0, 100.0]; Visible PairAcc 90.0% (9/10), CI [70.0, 100.0].
- ToolSandbox: History PairAcc 30.0% (3/10), CI [0.0, 60.0]; Visible PairAcc 60.0% (6/10), CI [30.0, 90.0].

Visible-minus-history changed PairAcc: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.09999999999999998, 'ci95_cluster': [-0.09999999999999998, 0.30000000000000004]}.
Visible-minus-history actionable E2E: {'left': 'history_only', 'right': 'decision_visible', 'difference': 0.033333333333333326, 'ci95_cluster': [-0.050000000000000044, 0.1166666666666667]}.
Failures: {'incomplete_tasks': 0, 'compiler': 0, 'history_actor': 0, 'visible_actor': 0}; enforcement repairs/harms: 4/4.
Logical calls completed/planned: 180/180; HTTP attempts: 180.

Negative, null, mixed, parse-failure, transport-failure, and enforcement-harm outcomes are retained.

## Report amendment

The v1 report mixed author-specified Reject rows into the Preserve-substitution denominator. V2 requires `actionable_core`; all raw outputs, ITT accuracy, PairAcc, wrong-write, and failure metrics are unchanged. The v1 report remains in the artifact.
