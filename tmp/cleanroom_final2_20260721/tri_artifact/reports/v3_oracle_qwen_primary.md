# TRI-v3 Oracle Component Decomposition

Tasks: 160; preserve tasks: 80.

| Component condition | Accuracy |
|---|---:|
| Learned mode + learned ID + free actor | 96.9 |
| Learned mode + learned ID + gate | 98.1 |
| Oracle mode + learned ID + gate | 98.1 |
| Learned mode + oracle ID + gate | 98.1 |
| Oracle mode + oracle ID + gate | 98.1 |

Mode accuracy: 100.0%.
Bound-ID accuracy on preserve tasks: 100.0%.

Oracle interventions replace only mode and/or pre-refresh bound ID. Reevaluate branches retain the observed lifecycle-free actor output.
