# Event Graph Oracle and Atomic Gate Report

## Oracle datasets

| Dataset | Tasks | Mode | Selector initial | Selector final | Authorized target | Capability binding |
|---|---:|---:|---:|---:|---:|---:|
| temporal_referent_v3_language_clusters.jsonl | 160 | 160/160 | 160/160 | 160/160 | 160/160 | 160/160 |
| temporal_referent_v7_core_replication.jsonl | 240 | 240/240 | 240/240 | 240/240 | 240/240 | 240/240 |
| temporal_referent_v6_role_heldout.jsonl | 40 | 40/40 | 40/40 | 40/40 | 40/40 | 40/40 |

## Atomic gate

- Deterministic sequences: 120
- Legal writes: 40
- False blocks: 0
- Wrong writes: 0
- Status counts: `{"missing_target": 40, "stale_version": 40, "written": 40}`

This is a zero-API implementation check. It does not measure learned compiler accuracy.
