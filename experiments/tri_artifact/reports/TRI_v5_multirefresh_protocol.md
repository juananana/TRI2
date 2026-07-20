# TRI-v5 Multi-Refresh SQLite Stress Protocol

Frozen on 2026-07-17 before any model call on TRI-v5.

## Purpose

Test whether post-binding target state survives a longer controlled trajectory without adding a
new controller. This is a secondary stress test, not a new benchmark main line.

Each episode executes:

1. query initial SQLite state;
2. compile generic or lifecycle state;
3. refresh to an intermediate state;
4. inspect a selector winner used only as a monitoring referent;
5. execute an unrelated `count_entities` tool call;
6. refresh to the final state;
7. choose a mutation target;
8. execute a real SQL mutation with action preconditions.

Anchored instructions establish the action target before either refresh. Dynamic instructions
explicitly defer action-target selection until after the second refresh. The monitoring referent
must not overwrite the action referent.

## Frozen Data

- Full: `data/temporal_referent_v5_multirefresh_sqlite.jsonl`
  - SHA-256 `b6b6632f35cdf65e85b712363f5049495c9cd286b43357b1e70650d38a3d64bd`
  - 40 tasks, 20 anchored and 20 dynamic;
  - 20 language-template clusters;
  - eight each of flip, stable, remove, invalidate, and name collision.
- Smoke: `data/temporal_referent_v5_multirefresh_sqlite_smoke.jsonl`
  - SHA-256 `f4d85a2a1a132038dc60281b2f64ff39bf84d9191b73ee89e54d91f7cf1be54c`
  - eight tasks, four per binding mode, covering all five update types.
- Generator: `f052a1e29d4e98b9a1356286f020ab13089d5be69c1d111bad5fa0466c2d5d9e`
- Runner: `a975f57d8aed7a5b24cc5e1dfe552d0556018902f2c5acf287e2bbcd5c456887`

## Controllers and Gate

- Generic Structured Ledger plus free final actor.
- Lifecycle compiler plus hybrid lifecycle gate. Preserve branches are resolved at the mutation
  boundary; dynamic branches use the same lifecycle actor as TRI-v3.

This test is not used to estimate the separate 2x2 effects; those are measured in the dedicated
factorial addendum. It asks whether the existing full method remains useful when the trajectory
contains multiple observations and a distractor referent.

## Inference and Stop Conditions

Qwen3.5-122B-A10B, temperature zero, thinking disabled, 1,200 output-token cap. Run the eight-task
smoke first. Stop if either controller has more than one API/parse failure or if traces omit either
refresh, the count call, or the mutation. Prompts and task data remain fixed after smoke inspection.

## Metrics and Interpretation

- final-state accuracy;
- anchored and dynamic accuracy;
- wrong-entity writes, invalid attempts, and unnecessary rejection;
- API requests, retries, and complete tool traces.

If lifecycle performance falls materially from one-refresh SQLite, the paper will limit the
method to controlled one-refresh settings and report the stress result as a boundary. If generic
and lifecycle are indistinguishable, no multi-refresh advantage will be claimed.
