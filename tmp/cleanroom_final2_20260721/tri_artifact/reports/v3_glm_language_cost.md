# TRI-v3 Logged Inference Cost

Latency is client-observed wall time. API request counts include retries; token usage is unavailable in the frozen runner and is therefore not estimated.

| Model | Controller | Binding | n | Requests/task | Total requests | Mean latency (s) | Median latency (s) | Retries | API err. |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | factorized_hybrid_compile_then_act | anchored | 80 | 1.00 | 80 | 3.47 | 3.43 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | dynamic | 80 | 2.00 | 160 | 4.28 | 4.15 | 0 | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | anchored | 80 | 2.00 | 160 | 5.18 | 4.93 | 0 | 0 |
| GLM-5.1 | generic_structured_ledger_then_act | dynamic | 80 | 2.00 | 160 | 5.02 | 4.88 | 0 | 0 |
