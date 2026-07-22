# TRI-v6 Role-Indexed Held-Out Validation

Post-hoc held-out validation on 40 compositional tasks from four unseen schemas.
Historical Compile-then-act predictions are replayed through the same SQLite mutation evaluator.

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Historical Compile-then-act | 33/40 | 38/40 | 0 | 5 | 2 | 80 | 0 |
| Role-indexed lifecycle | 39/40 | 39/40 | 0 | 0 | 1 | 60 | 0 |

Role-indexed minus historical CTA: +15.0 points, template-cluster 95% CI [+0.0, +30.0].
Discordant pairs: 7 role-only and 1 CTA-only; exact McNemar p=0.0703125.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Historical Compile-then-act | 13/20 | 20/20 | 15/20 | 18/20 |
| Role-indexed lifecycle | 20/20 | 19/20 | 20/20 | 19/20 |
