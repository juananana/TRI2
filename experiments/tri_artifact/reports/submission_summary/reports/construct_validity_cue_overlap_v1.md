# Trigger/Order and Rule--Model Overlap Audit

Evidence status: **post-hoc, zero API**. No new model output is used.

## Trigger and event-order logistic

| Model | v3 leave-template-out acc. | v3 AUC | Human-majority changed rewrites | Acc. | AUC |
|---|---:|---:|---:|---:|---:|
| trigger_only | 71.2% | 0.724 | 31 (12/19) | 48.4% | 0.121 |
| trigger_plus_event_order | 75.0% | 0.695 | 31 (12/19) | 48.4% | 0.555 |

The human-majority rewrite majority-class baseline is 61.3%.

Existing three-annotator agreement on 100 items is Fleiss kappa 0.708 and Krippendorff alpha 0.709.

The cue lexicon and model specification were developed post hoc. Human rewrites adapt authored tasks and do not form an independent open-language holdout.

## Rule* and frozen model-error overlap

`rule-only` means Rule* is correct and the model is wrong. `model-only` is the reverse.

| Model/controller | Unit | Both correct | Rule-only | Model-only | Both wrong | Model errors rule-solvable |
|---|---|---:|---:|---:|---:|---:|
| Qwen / History-only | all_rows (n=240) | 142 | 78 | 10 | 10 | 88.6% |
| Qwen / History-only | changed_rows (n=160) | 72 | 68 | 10 | 10 | 87.2% |
| Qwen / History-only | changed_pairs (n=80) | 3 | 57 | 0 | 20 | 74.0% |
| Qwen / Timing-reminder | all_rows (n=240) | 154 | 66 | 13 | 7 | 90.4% |
| Qwen / Timing-reminder | changed_rows (n=160) | 81 | 59 | 13 | 7 | 89.4% |
| Qwen / Timing-reminder | changed_pairs (n=80) | 13 | 47 | 2 | 18 | 72.3% |
| Qwen / CTA | all_rows (n=240) | 157 | 63 | 13 | 7 | 90.0% |
| Qwen / CTA | changed_rows (n=160) | 92 | 48 | 13 | 7 | 87.3% |
| Qwen / CTA | changed_pairs (n=80) | 23 | 37 | 8 | 12 | 75.5% |
| GLM / History-only | all_rows (n=240) | 151 | 69 | 10 | 10 | 87.3% |
| GLM / History-only | changed_rows (n=160) | 76 | 64 | 10 | 10 | 86.5% |
| GLM / History-only | changed_pairs (n=80) | 6 | 54 | 0 | 20 | 73.0% |
| GLM / Timing-reminder | all_rows (n=240) | 174 | 46 | 20 | 0 | 100.0% |
| GLM / Timing-reminder | changed_rows (n=160) | 100 | 40 | 20 | 0 | 100.0% |
| GLM / Timing-reminder | changed_pairs (n=80) | 32 | 28 | 8 | 12 | 70.0% |
| GLM / CTA | all_rows (n=240) | 206 | 14 | 20 | 0 | 100.0% |
| GLM / CTA | changed_rows (n=160) | 126 | 14 | 20 | 0 | 100.0% |
| GLM / CTA | changed_pairs (n=80) | 56 | 4 | 10 | 10 | 28.6% |
| DeepSeek / History-only | all_rows (n=240) | 150 | 70 | 15 | 5 | 93.3% |
| DeepSeek / History-only | changed_rows (n=160) | 77 | 63 | 15 | 5 | 92.6% |
| DeepSeek / History-only | changed_pairs (n=80) | 7 | 53 | 5 | 15 | 77.9% |
| DeepSeek / Timing-reminder | all_rows (n=240) | 164 | 56 | 18 | 2 | 96.6% |
| DeepSeek / Timing-reminder | changed_rows (n=160) | 94 | 46 | 18 | 2 | 95.8% |
| DeepSeek / Timing-reminder | changed_pairs (n=80) | 26 | 34 | 7 | 13 | 72.3% |
| DeepSeek / CTA | all_rows (n=240) | 203 | 17 | 16 | 4 | 81.0% |
| DeepSeek / CTA | changed_rows (n=160) | 124 | 16 | 16 | 4 | 80.0% |
| DeepSeek / CTA | changed_pairs (n=80) | 50 | 10 | 14 | 6 | 62.5% |

Rule* was developed after authored error inspection. Overlap is descriptive and does not establish a learned mechanism or confirmatory residual superiority.
