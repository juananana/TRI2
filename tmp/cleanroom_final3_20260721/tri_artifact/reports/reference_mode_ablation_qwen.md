# Generic + reference_mode ablation

This is a frozen 160-task paired comparison. The treatment adds only an explicit
`reference_mode` field to the Generic Structured Ledger; it adds no guard, fallback,
invalidity policy, or deterministic gate.

| Generic | Generic + mode | Tasks | Clusters | Delta | Cluster 95% CI |
|---:|---:|---:|---:|---:|---:|
| 64.4% | 75.0% | 160 | 20 | 10.6% | [5.0%, 16.9%] |

| Binding | Generic | Generic + mode |
|---|---:|---:|
| anchored | 33.8% | 50.0% |
| dynamic | 95.0% | 100.0% |

API errors: Generic=0; Generic+mode=0.

Interpretation is conditional: this comparison identifies the contribution of explicit
mode classification, not the superiority of Lifecycle-Gated or the validity policy.
