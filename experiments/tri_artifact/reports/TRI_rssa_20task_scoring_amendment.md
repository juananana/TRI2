# R-SSA 20-Task Smoke: Alpha-Renaming Scoring Amendment

Recorded: 2026-07-22, after the prospective model calls and before final paper use.

## Evaluation bug

The frozen protocol requires producer-edge, role, epoch, and binding-inventory accuracy. The first
implementation incorrectly compared generated SSA variable names against oracle variable names:

- `producer_edge_correct` required `ACT.target_from == "r_action@0"`;
- `binding_inventory_correct` compared `(name, role, epoch)` tuples;
- `role_correct` also depended on oracle variable names.

SSA variable names are alpha-renamable. For example, `r_action@1` can be a valid single-assignment
name whose ACT edge correctly consumes the sole `action_target` producer. Treating that spelling
as an incorrect edge conflates identifier choice with dataflow semantics and is not the estimand
specified by the protocol.

## Corrected scoring

- `producer_edge_correct`: the parsed ACT consumes the unique `action_target` producer. The static
  validator already rejects unknown, monitoring-role, or ambiguous producers.
- `binding_inventory_correct`: compare the multiset of `(role, epoch)` pairs, ignoring alpha-
  renamable names.
- `role_correct`: compare the multiset of roles, ignoring names and epochs.
- `action_binding_epoch_correct`: remains a separate exact epoch comparison.
- `refresh_count_correct` and all end-to-end outcomes are unchanged.

The final analyzer recomputes these fields from each retained raw `compiled_ir`; it does not trust
the preliminary per-row score fields. GLM rows that failed the preregistered strict JSON parser
remain schema failures with no compiled IR. No model response, prompt, task, parser, or execution
outcome is changed.

This amendment is a correctness repair, not a relaxed-parser analysis. Both the original raw row
fields and the corrected final report remain available for audit.
