# Always-Lock and Always-Reevaluate Policy Controls

These are deterministic policy extremes, not reproductions of any named prompting method or agent architecture.

| Slice | n | Always lock + validity | Always reevaluate |
|---|---:|---:|---:|
| Overall | 160 | 96/160 (60.0%) | 96/160 (60.0%) |
| Anchored | 80 | 80/80 (100.0%) | 16/80 (20.0%) |
| Dynamic | 80 | 16/80 (20.0%) | 80/80 (100.0%) |

Always lock and always reevaluate are complementary: each solves one reference mode and fails the changed-winner cases in the other. Their identical aggregate accuracy therefore does not imply behavioral equivalence.
