# Call- and Base-Payload-Matched Decision Visibility

**Evidence status:** post-primary.

Call- and base-payload-matched decision-visibility test; the visible condition adds the compiled block, and deterministic enforcement reuses that actor call.

State-cluster bootstrap: 10,000 replicates, seed 20260725.

## Pro/zai-org/GLM-5.1

Rows: 80; state clusters: 40.

| Outcome | Changed PairAcc | E2E | Preserve conditional substitution |
|---|---:|---:|---:|
| history_only | 30.0% (12/40), 95% CI [17.5, 45.0] | 65.0% (52/80), 95% CI [58.8, 72.5] | 50.0% (12/24), 95% CI [30.0, 70.6] |
| decision_visible | 60.0% (24/40), 95% CI [45.0, 75.0] | 80.0% (64/80), 95% CI [72.5, 87.5] | 0.0% (0/24), 95% CI [0.0, 0.0] |
| decision_enforced | 60.0% (24/40), 95% CI [45.0, 75.0] | 80.0% (64/80), 95% CI [72.5, 87.5] | 0.0% (0/24), 95% CI [0.0, 0.0] |

Compiler mode accuracy: 80.0% (64/80), 95% CI [72.5, 87.5].
Preserve binding accuracy: 60.0% (24/40), 95% CI [45.0, 75.0].
Joint mode/binding accuracy: 80.0% (64/80), 95% CI [72.5, 87.5].

Shadow actor disagreement: 12/80 both-parsed tasks; 0 unavailable; cluster interval 15.0% (12/80), 95% CI [8.8, 22.5].
Enforcement changes: 0; repairs: 0; harms: 0; other wrong-to-wrong changes: 0.
Enforcement repair rate: 0.0% (0/80), 95% CI [0.0, 0.0]; harm rate: 0.0% (0/80), 95% CI [0.0, 0.0].
Failures: 0 API calls; 0 parse/schema calls; 0 incomplete tasks.
Calls: 240/240 logical; 240 HTTP attempts; 0 retries.

| Paired contrast | Metric | Difference (right-left) | 95% CI |
|---|---|---:|---:|
| history_only -> decision_visible | changed_pairacc | 30.0 pp | [17.5, 45.0] |
| history_only -> decision_visible | preserve_conditional_substitution | -50.0 pp | [-70.6, -30.0] |
| history_only -> decision_visible | e2e | 15.0 pp | [8.7, 22.5] |
| decision_visible -> decision_enforced | changed_pairacc | 0.0 pp | [0.0, 0.0] |
| decision_visible -> decision_enforced | preserve_conditional_substitution | 0.0 pp | [0.0, 0.0] |
| decision_visible -> decision_enforced | e2e | 0.0 pp | [0.0, 0.0] |

## Qwen/Qwen3.5-122B-A10B

Rows: 80; state clusters: 40.

| Outcome | Changed PairAcc | E2E | Preserve conditional substitution |
|---|---:|---:|---:|
| history_only | 30.0% (12/40), 95% CI [15.0, 45.0] | 65.0% (52/80), 95% CI [57.5, 72.5] | 57.1% (16/28), 95% CI [38.5, 75.0] |
| decision_visible | 50.0% (20/40), 95% CI [35.0, 65.0] | 73.8% (59/80), 95% CI [65.0, 82.5] | 14.3% (4/28), 95% CI [3.3, 28.6] |
| decision_enforced | 42.5% (17/40), 95% CI [27.5, 57.5] | 68.8% (55/80), 95% CI [60.0, 77.5] | 0.0% (0/28), 95% CI [0.0, 0.0] |

Compiler mode accuracy: 76.2% (61/80), 95% CI [68.8, 83.8].
Preserve binding accuracy: 70.0% (28/40), 95% CI [55.0, 85.0].
Joint mode/binding accuracy: 70.0% (56/80), 95% CI [61.3, 78.8].

Shadow actor disagreement: 21/80 both-parsed tasks; 0 unavailable; cluster interval 26.2% (21/80), 95% CI [16.2, 36.2].
Enforcement changes: 16; repairs: 4; harms: 8; other wrong-to-wrong changes: 4.
Enforcement repair rate: 5.0% (4/80), 95% CI [1.2, 10.0]; harm rate: 10.0% (8/80), 95% CI [3.8, 16.2].
Failures: 0 API calls; 0 parse/schema calls; 0 incomplete tasks.
Calls: 240/240 logical; 240 HTTP attempts; 0 retries.

| Paired contrast | Metric | Difference (right-left) | 95% CI |
|---|---|---:|---:|
| history_only -> decision_visible | changed_pairacc | 20.0 pp | [2.5, 37.5] |
| history_only -> decision_visible | preserve_conditional_substitution | -42.9 pp | [-61.5, -24.2] |
| history_only -> decision_visible | e2e | 8.8 pp | [0.0, 17.5] |
| decision_visible -> decision_enforced | changed_pairacc | -7.5 pp | [-22.5, 7.5] |
| decision_visible -> decision_enforced | preserve_conditional_substitution | -14.3 pp | [-28.6, -3.3] |
| decision_visible -> decision_enforced | e2e | -5.0 pp | [-13.7, 3.7] |

Negative, null, mixed, API-failure, and enforcement-harm outcomes remain in this report.
The conditional substitution denominator requires a correct shared Preserve compiler mode and bound ID; ITT PairAcc and E2E retain all observed task failures.
