# Model-Assisted Public Recall Triage

**Decision:** MODEL-ASSISTED TRIAGE ONLY / NOT INDEPENDENT CALIBRATION.

Natural records triaged: 72.
Injected controls: 60.
Natural candidate strict opportunities: 0.

## Suite Summary

| Suite | Natural records | Highest | High | Candidate strict |
|---|---:|---:|---:|---:|
| ToolSandbox | 10 | 1 | 0 | 0 |
| AppWorld | 10 | 1 | 9 | 0 |
| tau3-bench | 4 | 1 | 1 | 0 |
| API-Bank | 6 | 0 | 6 | 0 |
| BFCL | 21 | 0 | 20 | 0 |
| ToolTalk | 21 | 0 | 21 | 0 |

## Injected Controls

- Strict-positive controls recovered: 30/30.
- One-feature-missing controls excluded: 30/30.

## Human Review Queue

| Record | Suite | Case | Priority | Candidate strict | Missing or partial features |
|---|---|---|---|---:|---|
| `closest-toolsandbox` | ToolSandbox | `update_contact_relationship_with_relationship_twice_multiple_user_turn` | highest | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `closest-appworld` | AppWorld | `generator family 8ce6779` | highest | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `closest-tau3bench` | tau3-bench | `8 telecom overdue-payment/resume-line definitions` | highest | False | stable_entity_id, observable_pre_refresh_binding, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `appworld-ipfuncall_gpt4o_test_normal-8ce6779_2-1` | AppWorld | `ipfuncall_gpt4o_test_normal::8ce6779_2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable |
| `appworld-ipfuncall_gpt4turbo_test_normal-8ce6779_1-2` | AppWorld | `ipfuncall_gpt4turbo_test_normal::8ce6779_1` | high | False | observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable |
| `appworld-ipfuncall_gpt4turbo_test_normal-8ce6779_2-3` | AppWorld | `ipfuncall_gpt4turbo_test_normal::8ce6779_2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-ipfuncall_gpt4turbo_test_normal-8ce6779_3-4` | AppWorld | `ipfuncall_gpt4turbo_test_normal::8ce6779_3` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-react_gpt4o_test_normal-8ce6779_1-5` | AppWorld | `react_gpt4o_test_normal::8ce6779_1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-react_gpt4o_test_normal-8ce6779_2-6` | AppWorld | `react_gpt4o_test_normal::8ce6779_2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-react_gpt4o_test_normal-8ce6779_3-7` | AppWorld | `react_gpt4o_test_normal::8ce6779_3` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-react_gpt4turbo_test_normal-8ce6779_2-8` | AppWorld | `react_gpt4turbo_test_normal::8ce6779_2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `appworld-react_gpt4turbo_test_normal-8ce6779_3-9` | AppWorld | `react_gpt4turbo_test_normal::8ce6779_3` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner |
| `tau3-telecom` | tau3-bench | `telecom` | high | False | stable_entity_id, observable_pre_refresh_binding, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-1-response:0` | API-Bank | `level-1-response:0` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-1-response:1` | API-Bank | `level-1-response:1` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-1-response:2` | API-Bank | `level-1-response:2` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-1-response:3` | API-Bank | `level-1-response:3` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-3:0` | API-Bank | `level-3:0` | high | False | observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-apibank-level-3:2` | API-Bank | `level-3:2` | high | False | observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_0` | BFCL | `multi_turn_base_0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_1` | BFCL | `multi_turn_base_1` | high | False | stable_entity_id, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_100` | BFCL | `multi_turn_base_100` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_101` | BFCL | `multi_turn_base_101` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_102` | BFCL | `multi_turn_base_102` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_103` | BFCL | `multi_turn_base_103` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_104` | BFCL | `multi_turn_base_104` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_106` | BFCL | `multi_turn_base_106` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_107` | BFCL | `multi_turn_base_107` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_108` | BFCL | `multi_turn_base_108` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_109` | BFCL | `multi_turn_base_109` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_110` | BFCL | `multi_turn_base_110` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_13` | BFCL | `multi_turn_base_13` | high | False | observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_24` | BFCL | `multi_turn_base_24` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_26` | BFCL | `multi_turn_base_26` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_29` | BFCL | `multi_turn_base_29` | high | False | stable_entity_id, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_3` | BFCL | `multi_turn_base_3` | high | False | stable_entity_id, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_5` | BFCL | `multi_turn_base_5` | high | False | stable_entity_id, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_55` | BFCL | `multi_turn_base_55` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-bfcl-multi_turn_base_60` | BFCL | `multi_turn_base_60` | high | False | independent_post_binding_transition, changed_selector_winner, old_entity_remains_actionable, evaluable_authorized_target |
| `external-tooltalk-AccountTools-Alarm-Calendar-AddAlarm-0` | ToolTalk | `AccountTools-Alarm-Calendar-AddAlarm-0` | high | False | observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-AccountTools-Alarm-Email-GetAccountInformati-0` | ToolTalk | `AccountTools-Alarm-Email-GetAccountInformati-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-AccountTools-Alarm-Messages-FindAlarm-0` | ToolTalk | `AccountTools-Alarm-Messages-FindAlarm-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-AccountTools-Alarm-Weather-DeleteAccount-2` | ToolTalk | `AccountTools-Alarm-Weather-DeleteAccount-2` | high | False | stable_entity_id, observable_pre_refresh_binding, independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Alarm-Messages-Reminder-GetReminder-2` | ToolTalk | `Alarm-Messages-Reminder-GetReminder-2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Email-Reminder-GetReminder-1` | ToolTalk | `Calendar-Email-Reminder-GetReminder-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Email-Reminder-SendEmail-2` | ToolTalk | `Calendar-Email-Reminder-SendEmail-2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Messages-Reminder-AddReminder-1` | ToolTalk | `Calendar-Messages-Reminder-AddReminder-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Messages-Reminder-ModifyEvent-0` | ToolTalk | `Calendar-Messages-Reminder-ModifyEvent-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Messages-Reminder-QueryCalendar-2` | ToolTalk | `Calendar-Messages-Reminder-QueryCalendar-2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Messages-Weather-DeleteEvent-0` | ToolTalk | `Calendar-Messages-Weather-DeleteEvent-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-CompleteReminder-1` | ToolTalk | `Calendar-Reminder-Weather-CompleteReminder-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-CreateEvent-1` | ToolTalk | `Calendar-Reminder-Weather-CreateEvent-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-DeleteEvent-0` | ToolTalk | `Calendar-Reminder-Weather-DeleteEvent-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-DeleteReminder-1` | ToolTalk | `Calendar-Reminder-Weather-DeleteReminder-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-ModifyEvent-1` | ToolTalk | `Calendar-Reminder-Weather-ModifyEvent-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Calendar-Reminder-Weather-QueryCalendar-0` | ToolTalk | `Calendar-Reminder-Weather-QueryCalendar-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Email-Messages-Reminder-DeleteReminder-1` | ToolTalk | `Email-Messages-Reminder-DeleteReminder-1` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Email-Messages-Reminder-SendEmail-2` | ToolTalk | `Email-Messages-Reminder-SendEmail-2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Email-Reminder-Weather-CompleteReminder-2` | ToolTalk | `Email-Reminder-Weather-CompleteReminder-2` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |
| `external-tooltalk-Email-Reminder-Weather-DeleteReminder-0` | ToolTalk | `Email-Reminder-Weather-DeleteReminder-0` | high | False | independent_post_binding_transition, competing_same_role_entity, changed_selector_winner, old_entity_remains_actionable, later_target_mutation, evaluable_authorized_target |

## Boundary

These candidate labels are produced from existing frozen audits and structured source excerpts. They can prioritize human review and probe whether the deterministic audit missed obvious near cases, but they cannot be reported as independent human recall calibration or as a new public benchmark result.
