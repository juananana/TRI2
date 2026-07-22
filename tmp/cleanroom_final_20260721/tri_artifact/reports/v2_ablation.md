# TRI-v2 Representation Ablation

Tasks: 246

## Overall

| Representation | n | Accuracy | 95% CI |
|---|---:|---:|---:|
| binding_time_only | 246 | 58.1 | [51.9, 64.1] |
| bound_id_only | 246 | 41.9 | [35.9, 48.1] |
| bound_name_only | 246 | 58.9 | [52.7, 64.9] |
| latest_state | 246 | 64.6 | [58.5, 70.3] |
| schema_lifecycle | 246 | 100.0 | [98.5, 100.0] |
| time_plus_id | 246 | 74.0 | [68.2, 79.1] |

## By Task Type

| Representation | Task type | Binding | n | Accuracy |
|---|---|---|---:|---:|
| binding_time_only | collection | anchored | 7 | 0.0 |
| binding_time_only | collection | dynamic | 7 | 100.0 |
| binding_time_only | conditional | conditional | 56 | 85.7 |
| binding_time_only | nested | anchored | 8 | 0.0 |
| binding_time_only | nested | dynamic | 8 | 100.0 |
| binding_time_only | scalar | anchored | 80 | 0.0 |
| binding_time_only | scalar | dynamic | 80 | 100.0 |
| bound_id_only | collection | anchored | 7 | 100.0 |
| bound_id_only | collection | dynamic | 7 | 0.0 |
| bound_id_only | conditional | conditional | 56 | 42.9 |
| bound_id_only | nested | anchored | 8 | 100.0 |
| bound_id_only | nested | dynamic | 8 | 0.0 |
| bound_id_only | scalar | anchored | 80 | 60.0 |
| bound_id_only | scalar | dynamic | 80 | 20.0 |
| bound_name_only | collection | anchored | 7 | 0.0 |
| bound_name_only | collection | dynamic | 7 | 100.0 |
| bound_name_only | conditional | conditional | 56 | 85.7 |
| bound_name_only | nested | anchored | 8 | 0.0 |
| bound_name_only | nested | dynamic | 8 | 100.0 |
| bound_name_only | scalar | anchored | 80 | 37.5 |
| bound_name_only | scalar | dynamic | 80 | 65.0 |
| latest_state | collection | anchored | 7 | 0.0 |
| latest_state | collection | dynamic | 7 | 100.0 |
| latest_state | conditional | conditional | 56 | 85.7 |
| latest_state | nested | anchored | 8 | 0.0 |
| latest_state | nested | dynamic | 8 | 100.0 |
| latest_state | scalar | anchored | 80 | 20.0 |
| latest_state | scalar | dynamic | 80 | 100.0 |
| schema_lifecycle | collection | anchored | 7 | 100.0 |
| schema_lifecycle | collection | dynamic | 7 | 100.0 |
| schema_lifecycle | conditional | conditional | 56 | 100.0 |
| schema_lifecycle | nested | anchored | 8 | 100.0 |
| schema_lifecycle | nested | dynamic | 8 | 100.0 |
| schema_lifecycle | scalar | anchored | 80 | 100.0 |
| schema_lifecycle | scalar | dynamic | 80 | 100.0 |
| time_plus_id | collection | anchored | 7 | 100.0 |
| time_plus_id | collection | dynamic | 7 | 100.0 |
| time_plus_id | conditional | conditional | 56 | 42.9 |
| time_plus_id | nested | anchored | 8 | 100.0 |
| time_plus_id | nested | dynamic | 8 | 100.0 |
| time_plus_id | scalar | anchored | 80 | 60.0 |
| time_plus_id | scalar | dynamic | 80 | 100.0 |

## Error Counts

| Representation | Error type | Count |
|---|---|---:|
| binding_time_only | alias_collision | 16 |
| binding_time_only | collection_mismatch | 7 |
| binding_time_only | invalid_but_processed | 32 |
| binding_time_only | nested_mismatch | 8 |
| binding_time_only | other | 40 |
| bound_id_only | invalid_but_processed | 32 |
| bound_id_only | other | 32 |
| bound_id_only | premature_binding | 79 |
| bound_name_only | invalid_but_processed | 14 |
| bound_name_only | other | 8 |
| bound_name_only | premature_binding | 28 |
| bound_name_only | temporal_rebinding | 51 |
| latest_state | other | 8 |
| latest_state | temporal_rebinding | 79 |
| time_plus_id | invalid_but_processed | 32 |
| time_plus_id | other | 32 |
