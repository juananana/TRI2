# TRI-v3 Logged Inference Cost

Latency is client-observed wall time. API request counts include retries; token usage is unavailable in the frozen runner and is therefore not estimated.

| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | generic_structured_ledger_then_act | conditional | 40 | 2.00 | 80 | 6.06 | 6.17 | 0 | 0 |
| Qwen3.5 | guarded_lifecycle_then_act | conditional | 40 | 1.82 | 73 | 6.87 | 5.08 | 0 | 0 |
