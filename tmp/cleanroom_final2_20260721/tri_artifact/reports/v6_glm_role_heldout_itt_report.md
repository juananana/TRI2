# TRI-v6 Role-Indexed Held-Out Validation

Post-hoc held-out validation on 40 compositional tasks from four unseen schemas.
Historical Compile-then-act predictions are replayed through the same SQLite mutation evaluator.

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Historical Compile-then-act | 36/40 | 37/40 | 0 | 0 | 3 | 80 | 4 |
| Role-indexed lifecycle | 37/40 | 37/40 | 0 | 0 | 3 | 60 | 3 |

Role-indexed minus historical CTA: +2.5 points, template-cluster 95% CI [-10.0, +15.0].
Discordant pairs: 4 role-only and 3 CTA-only; exact McNemar p=1.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Historical Compile-then-act | 18/20 | 18/20 | 18/20 | 18/20 |
| Role-indexed lifecycle | 20/20 | 17/20 | 20/20 | 17/20 |
