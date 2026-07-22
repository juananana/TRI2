# TRI-v7 Temperature-Zero Repeat Stability

Frozen decision: **MIXED**.

Repeat 1 is the matching subset of the original 240-task run. Repeats 2 and 3 are new
complete calls. All denominators retain API and parse failures under intention-to-treat.

| Model | Controller | Repeat | Accuracy | Initial anchored | Conditional TRI | Stable errors | API / parse | Requests / retries | Tokens | Latency s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic | 1 | 22/40 (55.0%) | 16/20 | 5/10 | 1/8 | 0 / 0 | 80 / 0 | NA | 132.3 |
| Qwen3.5 | generic | 2 | 23/40 (57.5%) | 17/20 | 5/11 | 1/8 | 0 / 0 | 80 / 0 | 43567 | 182.1 |
| Qwen3.5 | generic | 3 | 22/40 (55.0%) | 18/20 | 7/11 | 1/8 | 0 / 0 | 80 / 0 | 43552 | 145.5 |
| Qwen3.5 | cta | 1 | 32/40 (80.0%) | 16/20 | 0/10 | 2/8 | 0 / 0 | 80 / 0 | NA | 109.2 |
| Qwen3.5 | cta | 2 | 28/40 (70.0%) | 15/20 | 0/9 | 2/8 | 0 / 0 | 80 / 0 | 37526 | 143.7 |
| Qwen3.5 | cta | 3 | 31/40 (77.5%) | 16/20 | 0/10 | 2/8 | 0 / 0 | 80 / 0 | 37544 | 120.3 |
| GLM-5.1 | generic | 1 | 28/40 (70.0%) | 20/20 | 4/12 | 1/8 | 0 / 0 | 80 / 0 | NA | 285.6 |
| GLM-5.1 | generic | 2 | 31/40 (77.5%) | 20/20 | 5/12 | 0/8 | 0 / 0 | 80 / 0 | 42012 | 230.6 |
| GLM-5.1 | generic | 3 | 30/40 (75.0%) | 20/20 | 6/12 | 1/8 | 0 / 0 | 80 / 0 | 41952 | 232.7 |
| GLM-5.1 | cta | 1 | 40/40 (100.0%) | 20/20 | 0/12 | 0/8 | 0 / 0 | 80 / 0 | NA | 155.1 |
| GLM-5.1 | cta | 2 | 39/40 (97.5%) | 20/20 | 0/12 | 0/8 | 0 / 0 | 80 / 0 | 33721 | 173.6 |
| GLM-5.1 | cta | 3 | 40/40 (100.0%) | 20/20 | 0/12 | 0/8 | 0 / 0 | 80 / 0 | 33818 | 174.7 |

| Model | CTA-Generic r1 | r2 | r3 | Generic target unanimity | CTA target unanimity |
|---|---:|---:|---:|---:|---:|
| Qwen3.5 | +25.0 | +12.5 | +22.5 | 28/40 (70.0%) | 29/40 (72.5%) |
| GLM-5.1 | +30.0 | +20.0 | +25.0 | 34/40 (85.0%) | 39/40 (97.5%) |

New repeat-2/3 calls: 320 task-controller executions, 640 requests, 0 retries, 313692 tokens, and 1403.3 client seconds.
Historical repeat-1 token usage was not captured and is shown as NA.

Decision flags:

- Any nonpositive CTA delta: `False`.
- Any CTA conditional drift: `False`.
- Accuracy range over 10 points: `False`.
- Target unanimity below 90%: `True`.

A MIXED decision means the method direction is preserved but endpoint-level target outputs
are not deterministic enough to call the runs fully stable. It is not a reversal of the
controlled effect and does not establish natural-world prevalence.
