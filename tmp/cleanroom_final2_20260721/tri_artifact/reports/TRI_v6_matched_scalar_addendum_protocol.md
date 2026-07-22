# TRI-v6 Matched Scalar-versus-Role Addendum

Frozen on 2026-07-17 after the independent Round-3 review and before any scalar-lifecycle model
call on TRI-v6. Role-indexed TRI-v6 outputs already exist and are not changed or rerun. This is a
post-hoc mechanism addendum, not part of the original confirmatory experiment.

## Question

Does role indexing improve multi-referent composition when the actor, action schema, mutation
boundary, preserve gate, model, inference parameters, and realized call policy are held fixed?

## Fixed comparison

- Data: `data/temporal_referent_v6_role_heldout.jsonl`, SHA-256
  `ecf8f19a55ebfa31b9c8414a14ade7a19f264149923819643936aff071613105`.
- Scalar controller: existing `run_lifecycle` in `tri/run_v5_stress.py`.
- Role-indexed controller: existing `run_role_indexed` in the same file; its prior frozen outputs
  are reused exactly.
- Both use `LIFECYCLE_ACTOR_SYSTEM`, the same final state and action schema, the same deterministic
  preserve/invalidity gate, and one compiler call plus an actor call only for reevaluate branches.
- The intended treatment difference is the compiler record: one unindexed lifecycle record versus
  a role-keyed set whose unique `action_target` is projected at mutation time. Compiler prompts and
  serializations necessarily differ, so this is not a pure single-bit causal effect.

Qwen3.5-122B-A10B and GLM-5.1 run at temperature zero with thinking disabled, 1,200 output tokens,
180-second timeout, one API retry, and the existing four-task v6 smoke set. No prompt or parser
change is permitted after observing a scalar v6 response.

## Metrics and stopping

Continue from smoke if there is at most one API/parse failure. Report all 40 tasks intention-to-
treat: target and final-state accuracy, anchored/dynamic and explicit/implicit slices, wrong writes,
invalid attempts, unnecessary rejection, requests, retries, paired discordances, exact McNemar p,
and 20-template-cluster bootstrap intervals. Any transport recovery is reported separately and
never replaces ITT.

Role indexing supports a mechanism claim only if it improves the matched scalar controller without
increasing wrong writes. A tie or loss is retained and reported.
