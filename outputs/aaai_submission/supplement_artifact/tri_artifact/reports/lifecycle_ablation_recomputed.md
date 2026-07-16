# Lifecycle Representation Ablation

## Overall

| Representation | Binding | n | Accuracy |
|---|---|---:|---:|
| binding_time_only | anchored | 15 | 0.0 |
| binding_time_only | dynamic | 15 | 100.0 |
| bound_id_only | anchored | 15 | 80.0 |
| bound_id_only | dynamic | 15 | 0.0 |
| bound_name_only | anchored | 15 | 20.0 |
| bound_name_only | dynamic | 15 | 60.0 |
| full_lifecycle_ledger | anchored | 15 | 100.0 |
| full_lifecycle_ledger | dynamic | 15 | 100.0 |
| latest_state_selector | anchored | 15 | 0.0 |
| latest_state_selector | dynamic | 15 | 100.0 |
| time_plus_id | anchored | 15 | 80.0 |
| time_plus_id | dynamic | 15 | 100.0 |

## By Scenario

| Representation | Scenario | Binding | n | Accuracy |
|---|---|---|---:|---:|
| binding_time_only | action_invalid | anchored | 3 | 0.0 |
| binding_time_only | action_invalid | dynamic | 3 | 100.0 |
| binding_time_only | delayed_binding | anchored | 3 | 0.0 |
| binding_time_only | delayed_binding | dynamic | 3 | 100.0 |
| binding_time_only | multi_refresh_flip | anchored | 3 | 0.0 |
| binding_time_only | multi_refresh_flip | dynamic | 3 | 100.0 |
| binding_time_only | name_collision | anchored | 3 | 0.0 |
| binding_time_only | name_collision | dynamic | 3 | 100.0 |
| binding_time_only | rename_and_flip | anchored | 3 | 0.0 |
| binding_time_only | rename_and_flip | dynamic | 3 | 100.0 |
| bound_id_only | action_invalid | anchored | 3 | 0.0 |
| bound_id_only | action_invalid | dynamic | 3 | 0.0 |
| bound_id_only | delayed_binding | anchored | 3 | 100.0 |
| bound_id_only | delayed_binding | dynamic | 3 | 0.0 |
| bound_id_only | multi_refresh_flip | anchored | 3 | 100.0 |
| bound_id_only | multi_refresh_flip | dynamic | 3 | 0.0 |
| bound_id_only | name_collision | anchored | 3 | 100.0 |
| bound_id_only | name_collision | dynamic | 3 | 0.0 |
| bound_id_only | rename_and_flip | anchored | 3 | 100.0 |
| bound_id_only | rename_and_flip | dynamic | 3 | 0.0 |
| bound_name_only | action_invalid | anchored | 3 | 0.0 |
| bound_name_only | action_invalid | dynamic | 3 | 0.0 |
| bound_name_only | delayed_binding | anchored | 3 | 0.0 |
| bound_name_only | delayed_binding | dynamic | 3 | 100.0 |
| bound_name_only | multi_refresh_flip | anchored | 3 | 100.0 |
| bound_name_only | multi_refresh_flip | dynamic | 3 | 0.0 |
| bound_name_only | name_collision | anchored | 3 | 0.0 |
| bound_name_only | name_collision | dynamic | 3 | 100.0 |
| bound_name_only | rename_and_flip | anchored | 3 | 0.0 |
| bound_name_only | rename_and_flip | dynamic | 3 | 100.0 |
| full_lifecycle_ledger | action_invalid | anchored | 3 | 100.0 |
| full_lifecycle_ledger | action_invalid | dynamic | 3 | 100.0 |
| full_lifecycle_ledger | delayed_binding | anchored | 3 | 100.0 |
| full_lifecycle_ledger | delayed_binding | dynamic | 3 | 100.0 |
| full_lifecycle_ledger | multi_refresh_flip | anchored | 3 | 100.0 |
| full_lifecycle_ledger | multi_refresh_flip | dynamic | 3 | 100.0 |
| full_lifecycle_ledger | name_collision | anchored | 3 | 100.0 |
| full_lifecycle_ledger | name_collision | dynamic | 3 | 100.0 |
| full_lifecycle_ledger | rename_and_flip | anchored | 3 | 100.0 |
| full_lifecycle_ledger | rename_and_flip | dynamic | 3 | 100.0 |
| latest_state_selector | action_invalid | anchored | 3 | 0.0 |
| latest_state_selector | action_invalid | dynamic | 3 | 100.0 |
| latest_state_selector | delayed_binding | anchored | 3 | 0.0 |
| latest_state_selector | delayed_binding | dynamic | 3 | 100.0 |
| latest_state_selector | multi_refresh_flip | anchored | 3 | 0.0 |
| latest_state_selector | multi_refresh_flip | dynamic | 3 | 100.0 |
| latest_state_selector | name_collision | anchored | 3 | 0.0 |
| latest_state_selector | name_collision | dynamic | 3 | 100.0 |
| latest_state_selector | rename_and_flip | anchored | 3 | 0.0 |
| latest_state_selector | rename_and_flip | dynamic | 3 | 100.0 |
| time_plus_id | action_invalid | anchored | 3 | 0.0 |
| time_plus_id | action_invalid | dynamic | 3 | 100.0 |
| time_plus_id | delayed_binding | anchored | 3 | 100.0 |
| time_plus_id | delayed_binding | dynamic | 3 | 100.0 |
| time_plus_id | multi_refresh_flip | anchored | 3 | 100.0 |
| time_plus_id | multi_refresh_flip | dynamic | 3 | 100.0 |
| time_plus_id | name_collision | anchored | 3 | 100.0 |
| time_plus_id | name_collision | dynamic | 3 | 100.0 |
| time_plus_id | rename_and_flip | anchored | 3 | 100.0 |
| time_plus_id | rename_and_flip | dynamic | 3 | 100.0 |
