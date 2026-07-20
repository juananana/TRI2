# TRI-v6 Matched Scalar-vs-Role Addendum

This post-freeze addendum compares the existing role-indexed controller against a matched
scalar lifecycle controller with the same actor, action schema, preserve/invalidity gate,
mutation boundary, and call policy. The remaining treatment difference is the compiler
record: one scalar action-target record versus role-indexed action and monitoring records.

## Qwen matched held-out

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scalar lifecycle | 35/40 | 35/40 | 3 | 0 | 2 | 54 | 0 |
| Role-indexed lifecycle | 39/40 | 39/40 | 0 | 0 | 1 | 60 | 0 |

Role-indexed minus scalar: +10.0 points, template-cluster 95% CI [+2.5, +20.0].
Discordant pairs: 5 role-only and 1 scalar-only; exact McNemar p=0.21875.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Scalar lifecycle | 20/20 | 15/20 | 17/20 | 18/20 |
| Role-indexed lifecycle | 20/20 | 19/20 | 20/20 | 19/20 |

## GLM matched held-out, conservative ITT

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scalar lifecycle | 40/40 | 40/40 | 0 | 0 | 0 | 61 | 0 |
| Role-indexed lifecycle | 37/40 | 37/40 | 0 | 0 | 3 | 60 | 3 |

Role-indexed minus scalar: -7.5 points, template-cluster 95% CI [-15.0, +0.0].
Discordant pairs: 0 role-only and 3 scalar-only; exact McNemar p=0.25.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Scalar lifecycle | 20/20 | 20/20 | 20/20 | 20/20 |
| Role-indexed lifecycle | 20/20 | 17/20 | 20/20 | 17/20 |

## GLM matched held-out, transport-recovered sensitivity

| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Scalar lifecycle | 40/40 | 40/40 | 0 | 0 | 0 | 61 | 0 |
| Role-indexed lifecycle | 40/40 | 40/40 | 0 | 0 | 0 | 60 | 0 |

Role-indexed minus scalar: +0.0 points, template-cluster 95% CI [+0.0, +0.0].
Discordant pairs: 0 role-only and 0 scalar-only; exact McNemar p=1.

| Controller | Anchored | Dynamic | Explicit | Implicit |
|---|---:|---:|---:|---:|
| Scalar lifecycle | 20/20 | 20/20 | 20/20 | 20/20 |
| Role-indexed lifecycle | 20/20 | 20/20 | 20/20 | 20/20 |

The GLM ITT comparison includes transport-contaminated role-indexed rows from the original
concurrent run. The transport-recovered comparison replaces only automatically selected
failed rows with serial retries and is reported as an availability sensitivity analysis.
