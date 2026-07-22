# Evaluation-Regime Identifiability Audit

Show which evaluation regimes identify selective authorization and which hide it.

## Regime definitions

- `preserve_only`: All anchored rows, including stable and changed-winner rows.
- `reevaluate_only`: All dynamic rows, including stable and changed-winner rows.
- `stable_only`: State updates with an unchanged selector winner.
- `changed_winner_only`: Anchored, action-valid rows whose selector winner changes.
- `conditional_changed_winner`: Changed-winner rows with correct observable initial binding and an action-valid old target; the numerator counts substitution to the refreshed winner.
- `pairacc`: Both members of a matched Preserve/Reevaluate pair correct under the same state transition.

## Results

| Dataset | Controller | Aggregate | Preserve-only | Reevaluate-only | Stable-only | Changed-only | PairAcc | Conditional substitution |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v3 | Qwen-Generic | 64.4% (103/160) | 33.8% (27/80) | 95.0% (76/80) | 100.0% (32/32) | 9.4% (3/32) | 9.4% (3/32) | 90.6% (29/32) |
| v3 | Qwen-CTA | 95.0% (152/160) | 91.2% (73/80) | 98.8% (79/80) | 100.0% (32/32) | 96.9% (31/32) | 93.8% (30/32) | 0.0% (0/32) |
| v3 | Qwen-Lifecycle-free | 96.9% (155/160) | 97.5% (78/80) | 96.2% (77/80) | 100.0% (32/32) | 93.8% (30/32) | 93.8% (30/32) | 0.0% (0/32) |
| v3 | GLM-Generic | 71.9% (115/160) | 56.2% (45/80) | 87.5% (70/80) | 100.0% (32/32) | 21.9% (7/32) | 21.9% (7/32) | 31.2% (10/32) |
| v3 | GLM-CTA | 96.2% (154/160) | 92.5% (74/80) | 100.0% (80/80) | 100.0% (32/32) | 96.9% (31/32) | 96.9% (31/32) | 0.0% (0/32) |
| v3 | GLM-Lifecycle-free | 98.1% (157/160) | 96.2% (77/80) | 100.0% (80/80) | 100.0% (32/32) | 90.6% (29/32) | 90.6% (29/32) | 0.0% (0/32) |
| v3 | Always-Lock+validity | 60.0% (96/160) | 100.0% (80/80) | 20.0% (16/80) | 100.0% (32/32) | 100.0% (32/32) | 0.0% (0/32) | NA |
| v3 | Always-Reevaluate | 60.0% (96/160) | 20.0% (16/80) | 100.0% (80/80) | 100.0% (32/32) | 0.0% (0/32) | 0.0% (0/32) | NA |

The audit is descriptive and reuses frozen runs; it does not add model calls. Aggregate accuracy is not an identifiability test: Always-Lock and Always-Reevaluate can be equally accurate overall while failing opposite authorization modes.
