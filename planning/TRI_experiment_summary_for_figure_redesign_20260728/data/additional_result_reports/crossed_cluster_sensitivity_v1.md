# TRI-v3 Crossed-Dependence Statistical Sensitivity Audit

**Evidence status:** `post-primary replication/audit`; zero API. This analysis was
designed after observing the primary result. It does not replace the primary confidence
interval and does not provide multiplicity-adjusted confirmatory inference.

Seed: `20260725`. Bootstrap draws per method and model: `10,000`.

| Model (source-run status) | Generic | Lifecycle-Gated | Delta | Dependence assumption | 95% interval | Width |
|---|---:|---:|---:|---|---:|---:|
| Qwen3.5 (primary/frozen) | 103/160 | 157/160 | 33.8% | Language-template cluster | [18.1%, 49.4%] | 31.2% |
| Qwen3.5 (primary/frozen) | 103/160 | 157/160 | 33.8% | Domain cluster | [30.6%, 36.9%] | 6.2% |
| Qwen3.5 (primary/frozen) | 103/160 | 157/160 | 33.8% | Two-way pigeonhole | [16.2%, 50.6%] | 34.4% |
| GLM-5.1 (post-primary replication/audit) | 115/160 | 160/160 | 28.1% | Language-template cluster | [18.1%, 38.1%] | 20.0% |
| GLM-5.1 (post-primary replication/audit) | 115/160 | 160/160 | 28.1% | Domain cluster | [24.4%, 32.5%] | 8.1% |
| GLM-5.1 (post-primary replication/audit) | 115/160 | 160/160 | 28.1% | Two-way pigeonhole | [16.2%, 40.0%] | 23.8% |

## Widest intervals

- Qwen3.5: Two-way pigeonhole, [16.2%, 50.6%], width 34.4%.
- GLM-5.1: Two-way pigeonhole, [16.2%, 40.0%], width 23.8%.

The widest interval overall is Qwen3.5 under Two-way pigeonhole resampling: [16.2%, 50.6%] (width 34.4%).

All rows use the same complete 8 x 20 crossed inventory after exact task-ID, full
task-metadata, and cross-model inventory checks. This sensitivity addresses
dependence on authored generator axes. It does not establish natural-world prevalence
or isolate a controller component effect.
