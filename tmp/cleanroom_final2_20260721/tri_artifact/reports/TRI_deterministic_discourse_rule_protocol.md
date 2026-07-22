# Deterministic Discourse-Rule Baseline Protocol

Frozen: 2026-07-21 before running this baseline on any complete evaluation set.

## Question

Can a benchmark-specific deterministic controller solve TRI by parsing event order,
executing a simple state selector, and storing one ID, without an LLM or gold metadata?

## Allowed Inputs

The controller receives only:

- `instruction`;
- `initial_state`;
- `refreshed_state`;
- `action_schema`.

It must not read `binding`, `style`, `phenomenon`, `update`, `selector`,
`pre_refresh_target`, `post_refresh_target`, `correct_target`, `new_leader`,
`bound_entity_present_after_refresh`, or
`bound_entity_actionable_after_refresh`. Those fields are available only to the
separate evaluator after prediction.

## Frozen Rules

1. Normalize the instruction to lowercase ASCII words.
2. Find the earliest refresh event and earliest target-selection event.
3. Return `preserve` when selection occurs before refresh; return `reevaluate`
   when refresh occurs before selection. Missing or tied events are unresolved.
4. Infer the selector from state structure rather than the dataset `selector`
   field. Filter entities by `action_schema.preconditions`. If one non-schema
   Boolean field identifies a unique true entity, select it. Otherwise identify
   the single varying numeric field outside IDs, labels, owners, and schema
   fields, then apply the instruction's frozen minimum/maximum cue vocabulary.
5. Under `preserve`, resolve the selector in the initial state and store that ID.
   After refresh, execute only that ID if it is present and satisfies the action
   preconditions; otherwise return `INVALID_BOUND_ENTITY`.
6. Under `reevaluate`, resolve the selector in the refreshed state.
7. Ambiguous mode, selector, direction, or target resolution returns an
   unresolved prediction and counts as incorrect under intention-to-treat.

The implementation may not be modified after inspecting complete-set results.
Any failure cases will be reported as observed. Changes would require a new
versioned protocol and cannot replace this result.

## Evaluation Sets

- frozen TRI-v3 language clusters: 160 rows, 20 template clusters;
- independently authored human rewrites: 50 rows;
- frozen TRI-v7 core replication: 240 rows, 40 state clusters.

## Outcomes

- end-to-end authorized-target accuracy;
- mode classification accuracy;
- actionable-core and reject-policy accuracy;
- anchored and dynamic accuracy;
- unresolved mode/selector counts;
- forbidden-field invariance test;
- paired accuracy difference from unchanged CTA runs, with complete-cluster
  bootstrap intervals where matched runs exist.

## Interpretation

- If the rule is within 3 points of CTA on both original and human-rewrite
  sets, CTA is not treated as an algorithmic contribution. The paper is framed
  as problem definition, diagnostic evidence, benchmark gap, and a simple
  repair principle.
- If the rule matches CTA on templates but trails it by at least 8 points on
  human rewrites, the result supports semantic compilation beyond surface
  template rules.
- Intermediate or model-dependent outcomes are reported as mixed and do not
  justify a stronger method claim.

