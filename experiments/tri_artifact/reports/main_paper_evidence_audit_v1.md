# Main-Paper Evidence Audit

**Status:** zero-API audit rebuilt from frozen outputs and source reports.

| Check | Pass |
|---|---:|
| all table2 rows match frozen sources | yes |
| shared qwen claim present | yes |
| shared glm claim present | yes |
| shared deepseek claim present | yes |
| qwen primary claim present | yes |
| glm primary claim present | yes |
| human agreement claim present | yes |
| coverage scope present | yes |
| generic core writes equal conditional substitutions | yes |
| cta core writes zero but all wrong reported | yes |

| Model/controller | PairAcc | Conditional substitution | Core writes | All wrong writes | Shared G/CTA |
|---|---:|---:|---:|---:|---:|
| Qwen3.5 / Generic | 7/80 | 43/72 | 43 | 44 | 41/0 of 66 |
| Qwen3.5 / CTA | 31/80 | 0/71 | 0 | 8 | 41/0 of 66 |
| GLM-5.1 / Generic | 15/80 | 38/80 | 38 | 38 | 30/0 of 70 |
| GLM-5.1 / CTA | 66/80 | 0/70 | 0 | 14 | 30/0 of 70 |
| DeepSeek / Generic | 17/80 | 59/79 | 59 | 60 | 50/0 of 69 |
| DeepSeek / CTA | 64/80 | 0/70 | 0 | 17 | 50/0 of 69 |

- The audit checks numerical and provenance consistency, not natural prevalence.
- Human and public-suite classifications retain the limitations stated in the paper.
- Provider inference cannot be reproduced exactly because immutable serving revisions are unavailable.
