# Model Results on Human-Validated TRI Subsets

Original human items: 50; determinate majorities: 46; majority supports benchmark gold: 42; unanimous support: 35.

| Run | Human-majority accuracy | Majority-gold subset | Unanimous-gold subset |
|---|---:|---:|---:|
| qwen_generic | 32/46 (69.6%) | 76.2% (n=42) | 85.7% (n=35) |
| qwen_cta | 42/46 (91.3%) | 97.6% (n=42) | 100.0% (n=35) |
| qwen_free | 40/46 (87.0%) | 95.2% (n=42) | 94.3% (n=35) |
| qwen_gated | 41/46 (89.1%) | 97.6% (n=42) | 97.1% (n=35) |
| glm_generic | 34/46 (73.9%) | 81.0% (n=42) | 88.6% (n=35) |
| glm_cta | 41/46 (89.1%) | 97.6% (n=42) | 97.1% (n=35) |
| glm_free | 42/46 (91.3%) | 100.0% (n=42) | 100.0% (n=35) |
| glm_gated | 42/46 (91.3%) | 100.0% (n=42) | 100.0% (n=35) |

## Paired comparisons

Template-cluster bootstrap is primary for this sensitivity; task-level exact
McNemar is retained as a secondary descriptive analysis.

```json
{
  "qwen_gated_vs_generic_human_majority": {
    "difference": 0.1956521739130435,
    "cluster_95_interval": [
      0.05,
      0.36363636363636365
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260718,
    "secondary_task_level_mcnemar": {
      "generic_only": 1,
      "treatment_only": 10,
      "exact_mcnemar_p": 0.01171875
    }
  },
  "glm_gated_vs_generic_human_majority": {
    "difference": 0.17391304347826086,
    "cluster_95_interval": [
      0.06818181818181818,
      0.3157894736842105
    ],
    "n_clusters": 18,
    "samples": 10000,
    "seed": 20260718,
    "secondary_task_level_mcnemar": {
      "generic_only": 0,
      "treatment_only": 8,
      "exact_mcnemar_p": 0.0078125
    }
  }
}
```
