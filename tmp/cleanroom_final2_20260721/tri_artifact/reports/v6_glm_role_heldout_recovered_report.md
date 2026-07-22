# TRI-v6 Role-Indexed Held-Out Validation

Post-hoc held-out validation on 40 compositional tasks from four unseen schemas.
Historical Compile-then-act predictions are replayed through the same SQLite mutation evaluator.

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Historical Compile-then-act | 40/40 | 40/40 | 0 | 0 | 0 | 80 | 0 |
| Role-indexed lifecycle | 40/40 | 40/40 | 0 | 0 | 0 | 60 | 0 |

Role-indexed minus historical CTA: +0.0 points, template-cluster 95% CI [+0.0, +0.0].
Discordant pairs: 0 role-only and 0 CTA-only; exact McNemar p=1.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Historical Compile-then-act | 20/20 | 20/20 | 20/20 | 20/20 |
| Role-indexed lifecycle | 20/20 | 20/20 | 20/20 | 20/20 |
