# TRI-v3 Logged Inference Cost

Latency is client-observed wall time. API request counts include retries; token usage is unavailable in the frozen runner and is therefore not estimated.

| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | anchored | 40 | 1.00 | 40 | 5.54 | 3.44 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dynamic | 40 | 2.00 | 80 | 3.04 | 2.94 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | anchored | 40 | 2.00 | 80 | 3.98 | 3.64 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | dynamic | 40 | 2.00 | 80 | 3.95 | 3.97 | 0 | 0 |
