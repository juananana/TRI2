# Referential-Core and Reject-Policy Sensitivity

This post-primary sensitivity uses unchanged frozen TRI-v3 runs. The actionable
referential core excludes the 32 anchored remove/invalidate items whose benchmark
target is the author-specified `INVALID_BOUND_ENTITY` execution outcome.

| Run | Actionable referential core | Author-specified reject policy |
|---|---:|---:|
| Qwen Generic | 95/128 (74.2%) | 8/32 (25.0%) |
| Qwen Generic + validity gate | 95/128 (74.2%) | 9/32 (28.1%) |
| Qwen Untyped plan | 106/128 (82.8%) | 24/32 (75.0%) |
| Qwen Historical CTA | 126/128 (98.4%) | 26/32 (81.2%) |
| Qwen Lifecycle-free | 123/128 (96.1%) | 32/32 (100.0%) |
| Qwen Lifecycle-Gated | 125/128 (97.7%) | 32/32 (100.0%) |
| GLM Generic | 93/128 (72.7%) | 22/32 (68.8%) |
| GLM Generic + validity gate | 93/128 (72.7%) | 24/32 (75.0%) |
| GLM Untyped plan | 107/128 (83.6%) | 6/32 (18.8%) |
| GLM Historical CTA | 127/128 (99.2%) | 27/32 (84.4%) |
| GLM Lifecycle-free | 125/128 (97.7%) | 32/32 (100.0%) |
| GLM Lifecycle-Gated | 128/128 (100.0%) | 32/32 (100.0%) |

## Paired template-cluster sensitivity

```json
{
  "Qwen_Gated_minus_Generic_actionable_core": {
    "difference": 0.234375,
    "cluster_95_interval": [
      0.11267605633802817,
      0.38392857142857145
    ],
    "n": 128,
    "n_clusters": 20,
    "samples": 10000,
    "seed": 20260718
  },
  "Qwen_Gated_minus_Generic_reject_policy": {
    "difference": 0.75,
    "cluster_95_interval": [
      0.5757575757575758,
      0.9259259259259259
    ],
    "n": 32,
    "n_clusters": 10,
    "samples": 10000,
    "seed": 20260718
  },
  "Qwen_Gated_minus_Historical_CTA_actionable_core": {
    "difference": -0.0078125,
    "cluster_95_interval": [
      -0.04929577464788732,
      0.03076923076923077
    ],
    "n": 128,
    "n_clusters": 20,
    "samples": 10000,
    "seed": 20260718
  },
  "Qwen_Gated_minus_Historical_CTA_reject_policy": {
    "difference": 0.1875,
    "cluster_95_interval": [
      0.038461538461538464,
      0.3235294117647059
    ],
    "n": 32,
    "n_clusters": 10,
    "samples": 10000,
    "seed": 20260718
  },
  "GLM_Gated_minus_Generic_actionable_core": {
    "difference": 0.2734375,
    "cluster_95_interval": [
      0.1693548387096774,
      0.3983739837398374
    ],
    "n": 128,
    "n_clusters": 20,
    "samples": 10000,
    "seed": 20260718
  },
  "GLM_Gated_minus_Generic_reject_policy": {
    "difference": 0.3125,
    "cluster_95_interval": [
      0.13333333333333333,
      0.4838709677419355
    ],
    "n": 32,
    "n_clusters": 10,
    "samples": 10000,
    "seed": 20260718
  },
  "GLM_Gated_minus_Historical_CTA_actionable_core": {
    "difference": 0.0078125,
    "cluster_95_interval": [
      0.0,
      0.02564102564102564
    ],
    "n": 128,
    "n_clusters": 20,
    "samples": 10000,
    "seed": 20260718
  },
  "GLM_Gated_minus_Historical_CTA_reject_policy": {
    "difference": 0.15625,
    "cluster_95_interval": [
      0.03333333333333333,
      0.29411764705882354
    ],
    "n": 32,
    "n_clusters": 10,
    "samples": 10000,
    "seed": 20260718
  }
}
```

The split does not redefine benchmark gold or replace the pre-specified total
accuracy. It prevents the normative invalid-target policy from being interpreted
as if it had the same human support as Preserve/Reevaluate referential judgments.
