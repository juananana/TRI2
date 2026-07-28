# Convention-Told Natural-History Control

Evidence status: **post-primary replication/audit**.

Convention-told minus Plain-history changed PairAcc, separately by model.

Bootstrap: 10,000 state-cluster draws; seed 20260728.

## Pro/MiniMaxAI/MiniMax-M2.5

Rows: 80; changed pairs: 40.

| Condition | Changed PairAcc | E2E | Preserve | Reevaluate |
|---|---:|---:|---:|---:|
| plain_history | 37.5% (15/40), [22.5, 52.5] | 66.2% (53/80), [57.5, 75.0] | 37.5% (15/40), [22.5, 52.5] | 95.0% (38/40), [87.5, 100.0] |
| convention_told | 62.5% (25/40), [47.5, 77.5] | 77.5% (62/80), [67.5, 86.2] | 62.5% (25/40), [47.5, 77.5] | 92.5% (37/40), [82.5, 100.0] |

| Contrast | Estimate | 95% CI |
|---|---:|---:|
| Convention - Plain changed_pairacc | 25.0 pp | [12.5, 37.5] |
| Convention - Plain e2e | 11.3 pp | [3.7, 18.8] |

Failures: 0 API; 0 parse/schema; 0 incomplete task rows.
Calls: 160/160 logical; 160 HTTP attempts; 0 retries.

## Pro/zai-org/GLM-5.1

Rows: 80; changed pairs: 40.

| Condition | Changed PairAcc | E2E | Preserve | Reevaluate |
|---|---:|---:|---:|---:|
| plain_history | 15.0% (6/40), [5.0, 27.5] | 52.5% (42/80), [45.0, 60.0] | 15.0% (6/40), [5.0, 27.5] | 90.0% (36/40), [80.0, 97.5] |
| convention_told | 25.0% (10/40), [12.5, 40.0] | 61.3% (49/80), [53.8, 68.8] | 27.5% (11/40), [15.0, 42.5] | 95.0% (38/40), [87.5, 100.0] |

| Contrast | Estimate | 95% CI |
|---|---:|---:|
| Convention - Plain changed_pairacc | 10.0 pp | [2.5, 20.0] |
| Convention - Plain e2e | 8.8 pp | [3.7, 15.0] |

Failures: 0 API; 1 parse/schema; 1 incomplete task rows.
Calls: 160/160 logical; 160 HTTP attempts; 0 retries.

## Qwen/Qwen3.5-122B-A10B

Rows: 80; changed pairs: 40.

| Condition | Changed PairAcc | E2E | Preserve | Reevaluate |
|---|---:|---:|---:|---:|
| plain_history | 10.0% (4/40), [2.5, 20.0] | 28.7% (23/80), [18.8, 38.8] | 12.5% (5/40), [2.5, 22.5] | 45.0% (18/40), [30.0, 60.0] |
| convention_told | 5.0% (2/40), [0.0, 12.5] | 22.5% (18/80), [13.8, 32.5] | 7.5% (3/40), [0.0, 17.5] | 37.5% (15/40), [22.5, 52.5] |

| Contrast | Estimate | 95% CI |
|---|---:|---:|
| Convention - Plain changed_pairacc | -5.0 pp | [-12.5, 0.0] |
| Convention - Plain e2e | -6.2 pp | [-13.8, 1.3] |

Failures: 0 API; 0 parse/schema; 0 incomplete task rows.
Calls: 160/160 logical; 160 HTTP attempts; 0 retries.

## deepseek-ai/DeepSeek-V4-Pro

Rows: 80; changed pairs: 40.

| Condition | Changed PairAcc | E2E | Preserve | Reevaluate |
|---|---:|---:|---:|---:|
| plain_history | 5.0% (2/40), [0.0, 12.5] | 52.5% (42/80), [50.0, 56.2] | 17.5% (7/40), [7.5, 30.0] | 87.5% (35/40), [77.5, 97.5] |
| convention_told | 12.5% (5/40), [2.5, 22.5] | 56.2% (45/80), [51.2, 61.3] | 12.5% (5/40), [2.5, 22.5] | 100.0% (40/40), [100.0, 100.0] |

| Contrast | Estimate | 95% CI |
|---|---:|---:|
| Convention - Plain changed_pairacc | 7.5 pp | [-5.0, 20.0] |
| Convention - Plain e2e | 3.7 pp | [-2.5, 10.0] |

Failures: 0 API; 0 parse/schema; 0 incomplete task rows.
Calls: 160/160 logical; 160 HTTP attempts; 0 retries.

## Boundaries

- Authored frozen gold; not independent-human or open-language evidence.
- No structured ID, reference-mode record, compiler decision, or separately scored initial binding.
- Refreshed-winner and old-target errors are unconditional and are not called conditional TRI.
