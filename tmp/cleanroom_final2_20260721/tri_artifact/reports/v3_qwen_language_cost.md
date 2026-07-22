# TRI-v3 Logged Inference Cost

Latency is client-observed wall time. API request counts include retries; token usage is unavailable in the frozen runner and is therefore not estimated.

| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 80 | 1.00 | 80 | 2.84 | 2.64 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 80 | 2.00 | 160 | 2.71 | 2.50 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 80 | 2.00 | 160 | 3.63 | 3.60 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 80 | 2.00 | 160 | 3.69 | 3.66 | 0 | 0 |
