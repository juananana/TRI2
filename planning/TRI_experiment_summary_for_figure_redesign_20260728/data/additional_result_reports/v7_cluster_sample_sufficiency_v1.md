# TRI-v7 Replication Sample Sufficiency Audit

This is a retrospective precision and stability analysis, not post-hoc power.
Each draw samples complete independent clusters without replacement and retains all tasks
inside each selected cluster. The full-sample confidence interval instead uses paired
paired cluster bootstrap with replacement.

| Model | Full delta | Cluster-bootstrap 95% CI | Clusters | Tasks |
|---|---:|---:|---:|---:|
| Qwen3.5 | 23.3 | [16.2, 30.4] | 40 | 240 |
| GLM-5.1 | 24.2 | [19.6, 28.7] | 40 | 240 |
| DeepSeek | 17.5 | [10.8, 23.3] | 40 | 240 |

| Model | Sampled clusters | Tasks | Positive draws | >=10-point draws | Median delta | 95% subsample interval |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | 5 | 30 | 99.2% | 94.3% | 23.3 | [6.7, 43.3] |
| Qwen3.5 | 10 | 60 | 100.0% | 99.0% | 23.3 | [11.7, 35.0] |
| Qwen3.5 | 20 | 120 | 100.0% | 100.0% | 23.3 | [16.7, 30.8] |
| Qwen3.5 | 30 | 180 | 100.0% | 100.0% | 23.3 | [19.4, 27.2] |
| Qwen3.5 | 40 | 240 | 100.0% | 100.0% | 23.3 | [23.3, 23.3] |
| GLM-5.1 | 5 | 30 | 100.0% | 99.7% | 23.3 | [13.3, 36.7] |
| GLM-5.1 | 10 | 60 | 100.0% | 100.0% | 23.3 | [16.7, 31.7] |
| GLM-5.1 | 20 | 120 | 100.0% | 100.0% | 24.2 | [19.2, 29.2] |
| GLM-5.1 | 30 | 180 | 100.0% | 100.0% | 24.4 | [21.7, 26.7] |
| GLM-5.1 | 40 | 240 | 100.0% | 100.0% | 24.2 | [24.2, 24.2] |
| DeepSeek | 5 | 30 | 95.5% | 85.0% | 20.0 | [0.0, 30.0] |
| DeepSeek | 10 | 60 | 99.8% | 92.0% | 18.3 | [6.7, 26.7] |
| DeepSeek | 20 | 120 | 100.0% | 99.4% | 17.5 | [10.8, 23.3] |
| DeepSeek | 30 | 180 | 100.0% | 100.0% | 17.2 | [14.4, 21.7] |
| DeepSeek | 40 | 240 | 100.0% | 100.0% | 17.5 | [17.5, 17.5] |

The curve diagnoses effective cluster-level information rather than treating templated
rows as independent observations. It does not establish natural-world
prevalence or replace evaluation on externally sourced TRI opportunities.
