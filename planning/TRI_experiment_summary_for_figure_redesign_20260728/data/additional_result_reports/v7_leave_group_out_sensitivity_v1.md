# V7 Leave-Group-Out Sensitivity

Each row recomputes the matched CTA-minus-Generic difference after excluding one complete
domain or one complete template family. No model calls or task filtering were added.

| Model | Full delta | Leave-one-domain-out range | Leave-one-template-out range |
|---|---:|---:|---:|
| Qwen3.5 | 23.3 | [18.5, 25.5] | [20.4, 26.3] |
| GLM-5.1 | 24.2 | [23.1, 25.9] | [20.8, 26.1] |
| DeepSeek | 17.5 | [15.7, 22.2] | [14.2, 19.6] |

All leave-group-out differences remain positive. The matched advantage is therefore not
explained by any single domain or template family, although this sensitivity does not turn
templated tasks into independent natural-world observations.
