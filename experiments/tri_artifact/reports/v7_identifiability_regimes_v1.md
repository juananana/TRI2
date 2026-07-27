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
| v7 | Qwen-Generic | 47.5% (114/240) | 38.3% (46/120) | 56.7% (68/120) | 78.8% (63/80) | 12.5% (10/80) | 8.8% (7/80) | 59.7% (43/72) |
| v7 | Qwen-CTA | 70.8% (170/240) | 86.7% (104/120) | 55.0% (66/120) | 81.2% (65/80) | 87.5% (70/80) | 38.8% (31/80) | 0.0% (0/71) |
| v7 | Qwen-Lifecycle-Gated | 71.2% (171/240) | 79.2% (95/120) | 63.3% (76/120) | 76.2% (61/80) | 80.0% (64/80) | 50.0% (40/80) | 0.0% (0/64) |
| v7 | GLM-Generic | 70.0% (168/240) | 45.0% (54/120) | 95.0% (114/120) | 95.0% (76/80) | 20.0% (16/80) | 18.8% (15/80) | 47.5% (38/80) |
| v7 | GLM-CTA | 94.2% (226/240) | 91.7% (110/120) | 96.7% (116/120) | 100.0% (80/80) | 87.5% (70/80) | 82.5% (66/80) | 0.0% (0/70) |
| v7 | GLM-Lifecycle-Gated | 97.1% (233/240) | 99.2% (119/120) | 95.0% (114/120) | 100.0% (80/80) | 98.8% (79/80) | 91.2% (73/80) | 0.0% (0/79) |
| v7 | DeepSeek-Generic | 73.8% (177/240) | 47.5% (57/120) | 100.0% (120/120) | 100.0% (80/80) | 21.2% (17/80) | 21.2% (17/80) | 74.7% (59/79) |
| v7 | DeepSeek-CTA | 91.2% (219/240) | 90.8% (109/120) | 91.7% (110/120) | 98.8% (79/80) | 87.5% (70/80) | 80.0% (64/80) | 0.0% (0/70) |
| v7 | Always-Lock+validity | 66.7% (160/240) | 100.0% (120/120) | 33.3% (40/120) | 100.0% (80/80) | 100.0% (80/80) | 0.0% (0/80) | NA |
| v7 | Always-Reevaluate | 66.7% (160/240) | 33.3% (40/120) | 100.0% (120/120) | 100.0% (80/80) | 0.0% (0/80) | 0.0% (0/80) | NA |

The audit is descriptive and reuses frozen runs; it does not add model calls. Aggregate accuracy is not an identifiability test: Always-Lock and Always-Reevaluate can be equally accurate overall while failing opposite authorization modes.
