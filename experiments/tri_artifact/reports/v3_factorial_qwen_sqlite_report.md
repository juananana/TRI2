# TRI-v3 Model-Facing SQLite Trajectories

Episodes: 160

| Model | Controller | n | Resolution | Final state | Final 95% CI | Wrong write | Invalid attempt | Unneeded reject | Collateral | Requests | Retries | API err. |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | sqlite_generic_structured_ledger | 40 | 67.5 | 67.5 | [52.0, 79.9] | 32.5 | 0.0 | 0.0 | 13 | 80 | 0 | 0 |
| Qwen3.5 | sqlite_generic_validity_gated | 40 | 67.5 | 67.5 | [52.0, 79.9] | 32.5 | 0.0 | 0.0 | 13 | 80 | 0 | 0 |
| Qwen3.5 | sqlite_lifecycle_free_actor | 40 | 100.0 | 100.0 | [91.2, 100.0] | 0.0 | 0.0 | 0.0 | 0 | 80 | 0 | 0 |
| Qwen3.5 | sqlite_lifecycle_gated | 40 | 100.0 | 100.0 | [91.2, 100.0] | 0.0 | 0.0 | 0.0 | 0 | 60 | 0 | 0 |
