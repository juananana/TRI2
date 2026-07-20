# TRI-v3 Oracle Component Decomposition

Tasks: 160; preserve tasks: 80.

| Component condition | Accuracy |
|---|---:|
| Learned mode + learned ID + free actor | 98.1 |
| Learned mode + learned ID + gate | 100.0 |
| Oracle mode + learned ID + gate | 100.0 |
| Learned mode + oracle ID + gate | 100.0 |
| Oracle mode + oracle ID + gate | 100.0 |

Mode accuracy: 100.0%.
Bound-ID accuracy on preserve tasks: 100.0%.

Oracle interventions replace only mode and/or pre-refresh bound ID. Reevaluate branches retain the observed lifecycle-free actor output.
