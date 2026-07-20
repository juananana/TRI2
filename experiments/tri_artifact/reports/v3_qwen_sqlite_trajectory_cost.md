# TRI-v3 Logged Inference Cost

Latency is client-observed wall time. API request counts include retries; token usage is unavailable in the frozen runner and is therefore not estimated.

| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | anchored | 20 | 2.00 | 40 | 6.43 | 7.48 | 0 | 0 |
| Qwen3.5 | sqlite_generic_structured_ledger | dynamic | 20 | 2.00 | 40 | 5.39 | 5.96 | 0 | 0 |
| Qwen3.5 | sqlite_lifecycle_gated | anchored | 20 | 1.00 | 20 | 3.89 | 3.69 | 0 | 0 |
| Qwen3.5 | sqlite_lifecycle_gated | dynamic | 20 | 2.00 | 40 | 3.30 | 3.29 | 0 | 0 |
