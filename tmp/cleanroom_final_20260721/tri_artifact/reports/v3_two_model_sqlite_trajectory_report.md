# TRI-v3 Model-Facing SQLite Trajectories

Episodes: 160

| Model | Controller | n | Resolution | Final state | Final 95% CI | Wrong write | Invalid attempt | Unneeded reject | Collateral | Requests | Retries | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | sqlite_generic_structured_ledger | 40 | 62.5 | 65.0 | [49.5, 77.9] | 20.0 | 0.0 | 15.0 | 8 | 80 | 0 | 0 |
| GLM-5.1 | sqlite_lifecycle_gated | 40 | 100.0 | 100.0 | [91.2, 100.0] | 0.0 | 0.0 | 0.0 | 0 | 60 | 0 | 0 |
| Qwen3.5 | sqlite_generic_structured_ledger | 40 | 67.5 | 67.5 | [52.0, 79.9] | 32.5 | 0.0 | 0.0 | 13 | 80 | 0 | 0 |
| Qwen3.5 | sqlite_lifecycle_gated | 40 | 100.0 | 100.0 | [91.2, 100.0] | 0.0 | 0.0 | 0.0 | 0 | 60 | 0 | 0 |

## Paired Final-State Effects

| Model | A | B | n | Templates | Delta B-A | Cluster 95% CI |
|---|---|---|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | sqlite_lifecycle_gated | 40 | 20 | 32.5 | [15.0, 50.0] |
| GLM-5.1 | sqlite_generic_structured_ledger | sqlite_lifecycle_gated | 40 | 20 | 35.0 | [17.5, 52.5] |
