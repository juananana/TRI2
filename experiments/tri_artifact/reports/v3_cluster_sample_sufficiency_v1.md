# TRI-v3 Primary Sample Sufficiency Audit

This is a retrospective precision and stability analysis, not post-hoc power.
Each draw samples complete independent clusters without replacement and retains all tasks
inside each selected cluster. The full-sample confidence interval instead uses paired
paired cluster bootstrap with replacement.

| Model | Full delta | Cluster-bootstrap 95% CI | Clusters | Tasks |
|---|---:|---:|---:|---:|
| Qwen3.5 | 33.8 | [18.7, 49.4] | 20 | 160 |
| GLM-5.1 | 28.1 | [18.1, 38.1] | 20 | 160 |

| Model | Sampled clusters | Tasks | Positive draws | >=10-point draws | Median delta | 95% subsample interval |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | 5 | 40 | 98.9% | 96.8% | 32.5 | [5.0, 62.5] |
| Qwen3.5 | 10 | 80 | 100.0% | 99.9% | 33.8 | [17.5, 50.0] |
| Qwen3.5 | 15 | 120 | 100.0% | 100.0% | 34.2 | [24.2, 43.3] |
| Qwen3.5 | 20 | 160 | 100.0% | 100.0% | 33.8 | [33.8, 33.8] |
| GLM-5.1 | 5 | 40 | 100.0% | 99.0% | 27.5 | [10.0, 45.0] |
| GLM-5.1 | 10 | 80 | 100.0% | 100.0% | 27.5 | [17.5, 38.8] |
| GLM-5.1 | 15 | 120 | 100.0% | 100.0% | 28.3 | [22.5, 34.2] |
| GLM-5.1 | 20 | 160 | 100.0% | 100.0% | 28.1 | [28.1, 28.1] |

The curve diagnoses effective cluster-level information rather than treating templated
rows as independent observations. It does not establish natural-world
prevalence or replace evaluation on externally sourced TRI opportunities.
