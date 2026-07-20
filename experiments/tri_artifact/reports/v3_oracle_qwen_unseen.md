# TRI-v3 Oracle Component Decomposition

Tasks: 80; preserve tasks: 40.

| Component condition | Accuracy |
|---|---:|
| Learned mode + learned ID + free actor | 87.5 |
| Learned mode + learned ID + gate | 82.5 |
| Oracle mode + learned ID + gate | 82.5 |
| Learned mode + oracle ID + gate | 97.5 |
| Oracle mode + oracle ID + gate | 97.5 |

Mode accuracy: 100.0%.
Bound-ID accuracy on preserve tasks: 52.5%.

Oracle interventions replace only mode and/or pre-refresh bound ID. Reevaluate branches retain the observed lifecycle-free actor output.
