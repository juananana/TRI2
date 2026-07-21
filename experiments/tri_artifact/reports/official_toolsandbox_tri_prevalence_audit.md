# Official ToolSandbox TRI Prevalence Audit

## Scope and Frozen Definition

- Upstream: `https://github.com/apple/ToolSandbox.git`
- Pinned commit: `165848b9a78cead7ca7fe7c89c688b58e6501219`
- Package version: `0.0.1`
- Semantic scenario families audited: **129**
- Official tool-presentation instances: **1032**

The denominator is the semantic scenario family count. Distraction tools and scrambled tool
metadata do not create new referential semantics and therefore are not treated as independent
prevalence observations.

A strict native TRI opportunity must contain: (1) an entity selection/binding, (2) an
independent later world or user-side state transition, (3) a subsequent mutation whose
referent can either be preserved or reevaluated, (4) stable IDs, and (5) an evaluator that
can expose a wrong-target consequence. A merely stateful task or initial disambiguation task
does not qualify.

We applied the following auditable checklist to every semantic scenario family before assigning a
strict label:

1. **Prior binding:** a concrete same-role entity is selected before the later transition;
2. **Independent transition:** a later user, environment, or tool event changes relevant state;
3. **Competing referent:** the selector can have a different same-role winner afterward;
4. **Stable identity:** old and candidate entities have stable IDs across the transition;
5. **Action opportunity:** a later mutation can legally target either entity;
6. **Scorable consequence:** the evaluator exposes which entity was mutated.

We report three tiers: `strict opportunity` requires all six checks; `near-match` satisfies the
referential persistence structure but misses at least one of independent transition, competing
winner, or scorable substitution; all other cases are excluded with a recorded primary reason.
This is a single author-coded metadata audit, not an independently replicated annotation study.
The JSON artifact retains every scenario, check-relevant field, and exclusion reason for re-review.

## Result

- Strict native TRI opportunities: **0/129**
- Broader TRI-like natural traces: **1/129**

The unmodified official suite contains no strict exogenous-refresh/selector-flip TRI task.
Consequently, an unmodified ToolSandbox leaderboard run cannot estimate TRI failure
prevalence. This is a coverage result, not evidence that TRI never occurs in deployed agents.

One official scenario is a genuine natural-language near match:

- `update_contact_relationship_with_relationship_twice_multiple_user_turn`: The agent searches for all friends, changes those stable person IDs to enemies, and later resolves 'them' to change the same IDs back to friends. This is post-binding reference persistence across an action-induced state change, but it has no exogenous refresh, competing entity, or selector flip.
  Official task: Ask User B to update the all friends in (User A's) contact book as (User A's) enemy. After User B did so, ask User B to update them back to (User A's) friends. You do not have more information.

It supports the discourse-side premise that an established group reference can survive
a selector-relevant state change. It cannot test unauthorized substitution because no
competing friend is introduced, and it provides neither Stable/Flip nor
Preserve/Reevaluate controls.

## Exclusion Accounting

| Classification | Scenario families |
|---|---:|
| `excluded_no_entity_mutation` | 86 |
| `excluded_no_intervening_transition` | 17 |
| `excluded_no_prior_entity_selection` | 8 |
| `excluded_no_stable_mutation_id` | 17 |
| `tri_like_post_binding_preservation` | 1 |

## Scientific Interpretation

1. The official audit does not validate a positive model failure rate because the suite
   has zero strict opportunities.
2. The official near-match independently demonstrates that post-binding reference
   persistence is a natural task pattern rather than a phrase invented only for TRI.
3. The project's 96-task ToolSandbox adaptation must remain labeled a custom adaptation.
   Its null full-history result is a model/controller boundary, not an official score.
4. A small AppWorld adaptation is justified only as a preregistered custom case study with
   frozen transitions and database-diff evaluation; it cannot be called an unmodified
   AppWorld benchmark result.

The complete per-scenario evidence, tools, milestones, ID fields, and exclusion reasons
are stored in `official_toolsandbox_tri_prevalence_audit.json`.
