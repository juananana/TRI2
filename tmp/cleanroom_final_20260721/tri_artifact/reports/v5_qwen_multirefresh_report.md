# TRI-v5 Multi-Refresh, Multi-Referent SQLite Stress

Frozen secondary stress test: two refreshes, a monitoring-only referent, an unrelated
tool call, and a real SQLite mutation. It is not pooled with the primary experiment.

| Controller | n | Accuracy | 95% CI | Anchored | Dynamic | Wrong writes | Unneeded reject | Requests | API err. | Parse/internal err. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sqlite_multirefresh_generic | 40 | 80.0 | [65.2, 89.5] | 65.0 | 95.0 | 1 | 4 | 80 | 0 | 0 |
| sqlite_multirefresh_lifecycle | 40 | 70.0 | [54.6, 81.9] | 100.0 | 40.0 | 6 | 6 | 45 | 0 | 1 |

Lifecycle minus generic: -10.0 points, template-cluster 95% CI [-35.0, +12.5].
Discordant pairs: 11 generic-only and 7 lifecycle-only; exact McNemar p=0.480682.

Lifecycle mode accuracy: 25/40; anchored bound-ID accuracy: 20/20.

| Controller | Update slice | Success |
|---|---|---:|
| sqlite_multirefresh_generic | flip | 6/8 |
| sqlite_multirefresh_generic | invalidate | 7/8 |
| sqlite_multirefresh_generic | name_collision | 6/8 |
| sqlite_multirefresh_generic | remove | 5/8 |
| sqlite_multirefresh_generic | stable | 8/8 |
| sqlite_multirefresh_lifecycle | flip | 5/8 |
| sqlite_multirefresh_lifecycle | invalidate | 5/8 |
| sqlite_multirefresh_lifecycle | name_collision | 5/8 |
| sqlite_multirefresh_lifecycle | remove | 5/8 |
| sqlite_multirefresh_lifecycle | stable | 8/8 |

The scalar lifecycle record was designed for one action referent. Failure to separate the
monitoring referent from the action referent is a compositional reference-scope boundary,
not evidence that post-binding temporal authorization is unnecessary.
