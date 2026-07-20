# Generic + reference_mode ablation

This is a frozen 160-task paired comparison. The treatment adds only an explicit
`reference_mode` field to the Generic Structured Ledger; it adds no guard, fallback,
invalidity policy, or deterministic gate.

| Generic | Generic + mode | Tasks | Clusters | Delta | Cluster 95% CI |
|---:|---:|---:|---:|---:|---:|
| 71.9% | 75.0% | 160 | 20 | 3.1% | [-2.5%, 9.4%] |

| Binding | Generic | Generic + mode |
|---|---:|---:|
| anchored | 56.2% | 52.5% |
| dynamic | 87.5% | 97.5% |

API errors: Generic=0; Generic+mode=0.

Interpretation is conditional: this comparison identifies the contribution of explicit
mode classification, not the superiority of Lifecycle-Gated or the validity policy.
