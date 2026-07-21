# Public-Benchmark TRI Coverage Checklist

Feature audit of each benchmark's closest released natural near-match, not a claim that every task in the benchmark has the marked feature. 'Partial' means the trace has a related structure but not the strict same-role controlled condition.

| Strict feature | ToolSandbox | AppWorld | tau3-bench |
|---|---|---|---|
| Stable ID | yes | yes | no |
| Observed prior binding | yes | yes | partial |
| Independent transition | no | no | yes |
| Competing same-role entity | no | partial | no |
| Changed winner | no | partial | no |
| Old remains actionable | yes | yes | no |
| Later mutation | yes | yes | no |
| Scorable authorized target | yes | yes | partial |

## Evidence

### ToolSandbox

Closest case: `update_contact_relationship_with_relationship_twice_multiple_user_turn`. 129 semantic families; 0 strict; 1 TRI-like.

- Stable ID (yes): mutation gold exposes person_id.
- Observed prior binding (yes): search_contacts precedes mutation.
- Independent transition (no): first mutation is the requested agent action, not exogenous.
- Competing same-role entity (no): reviewed case introduces no competing friend.
- Changed winner (no): no replacement selector winner or Flip control.
- Old remains actionable (yes): same person_ids are legally changed back.
- Later mutation (yes): second modify_contact mutation targets the prior IDs.
- Scorable authorized target (yes): official mutation gold exposes target person_ids.

Source: `reports/official_toolsandbox_tri_prevalence_audit.json`.

### AppWorld

Closest case: `generator family 8ce6779`. 244 generator families; 0 strict; 1 TRI-like family.

- Stable ID (yes): Todoist task IDs persist across assignment and comment.
- Observed prior binding (yes): correct assignment operations expose 16 bound IDs.
- Independent transition (no): assignment is agent-induced; no scheduled external refresh.
- Competing same-role entity (partial): other tasks exist, but no controlled competing-winner intervention.
- Changed winner (partial): old tasks leave assigned-to-me selector; no measured replacement winner.
- Old remains actionable (yes): the same IDs accept later comments.
- Later mutation (yes): 16 comments follow correct assignments.
- Scorable authorized target (yes): official expected task IDs permit same-ID scoring.

Source: `reports/appworld_public_trace_tri_audit.json`.

### tau3-bench

Closest case: `8 telecom overdue-payment/resume-line definitions`. 2,449 tasks; 0 strict; 8 dual-control near-matches.

- Stable ID (no): user-side mutation carries no bill/line stable ID.
- Observed prior binding (partial): agent identifies a bill, but no scored same-role commitment.
- Independent transition (yes): user pays through a user-side tool.
- Competing same-role entity (no): no competing bill or line selector candidate.
- Changed winner (no): no same-role selector flip.
- Old remains actionable (no): subsequent action targets a different role: line, not bill.
- Later mutation (no): resume_line is not a later mutation of the bound bill.
- Scorable authorized target (partial): actions are scored, but not a same-role referent transition.

Source: `reports/official_tau3_native_tri_audit.json`.

Missing strict opportunities can make a benchmark unable to measure TRI. It does not imply that TRI is common in deployed traffic or absent from agents.
