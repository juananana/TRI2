# TRI AppWorld Simple Note Addendum Protocol

**Status:** frozen before Simple Note model calls; post-primary external extension.

The addendum introduces a second AppWorld application and selector cluster after the Todoist
case study had been analyzed. It uses the same official AppWorld `0.1.3.post1` train task world
`82e2fac_1` only as a database/API substrate. Task instructions, synchronization, sidecar binding
instrumentation, and evaluation are custom and must not be described as an AppWorld leaderboard
result.

The eight tasks cross Preserve/Reevaluate, Stable/Flip, and two paraphrases. Initially, controlled
notes A (`BRAVO`) and C (`CHARLIE`) are tagged `tri-experiment`; A is first alphabetically. Sync
adds B. Stable uses title `DELTA`, leaving A first; Flip uses `ALPHA`, making B first. Preserve gold
is A in both transitions. Reevaluate gold is A in Stable and B in Flip. All notes remain editable.

The Agent autonomously chooses among AppWorld-backed search, sync, and append tools plus a sidecar
`record_binding(note_id)`. The evaluator uses stable note IDs and compares post-sync and final
database contents. Primary metrics are correct timed binding, conditional TRI, Stable error,
wrong-entity write, and collateral modification. A wrong write without a correct, pre-action
binding is reported but excluded from the conditional TRI numerator.

Because this is one additional selector cluster with two paraphrases, rows are not treated as
independent samples and no row-level confidence interval is reported.
