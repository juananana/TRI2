# TRI-v3 Model-Facing SQLite Trajectory Protocol

Frozen before any API call on this subset.

## Scope

This experiment tests whether the target-resolution difference survives an actual stateful
database trajectory rather than prediction-only mutation replay. It is intentionally small and
controlled. It is not an external benchmark and does not claim that the model autonomously
plans every tool call.

For each episode, the controller runtime executes:

1. `query_entities` against an in-memory SQLite database;
2. a model compiler call using the returned rows;
3. `refresh_database`, which replaces rows with the task's refreshed state;
4. a model actor call when the controller cannot resolve the target deterministically;
5. `mutate_entity`, which enforces action preconditions and performs a real SQL `UPDATE`.

The original user instruction requires the refresh, so query and refresh are controller-
orchestrated. The model is responsible for compiling target state and, where applicable,
selecting the mutation target from the refreshed tool result.

## Frozen tasks

- File: `data/temporal_referent_v3_sqlite_trajectory.jsonl`
- SHA-256: `43b5613ef64fe2a3fc578e9d07686d044fb6efa7fd7bf07f609967da920f47e8`
- 40 tasks;
- 20 language-template clusters;
- 20 anchored and 20 dynamic references;
- eight tasks for each of flip, stable, remove, invalidate, and name-collision updates;
- all eight original domains, five tasks per domain.

Balanced smoke subset:

- File: `data/temporal_referent_v3_sqlite_trajectory_smoke.jsonl`
- SHA-256: `d6cd70bfe6645e3968b0d4a45d43f53445c0cc431bfcae2d7f04214b25e167eb`
- eight tasks, one per domain, two per language style, four per binding mode, covering all
  five update types.

Frozen runner:

- File: `tri/run_v3_sqlite_trajectories.py`
- SHA-256: `bfdf5655e29b1321f6fd64bc46d7cd7fa70edf84e84b10f56ed8898d1a268a4d`

## Controllers

- Generic Structured Ledger: stores identity, snapshot, selector, action, and action
  preconditions, but no reference mode or invalidity policy.
- Lifecycle-Gated Controller: compiles reference mode, bound identity, selector, and invalidity
  policy. Preserved targets are resolved by the deterministic action-validity gate; dynamic
  targets use the actor.

The prompt semantics and inference configuration match the frozen TRI-v3 runs. No prompt may be
changed after inspecting model output from this trajectory subset.

## Models and run gate

Qwen3.5-122B-A10B runs first at temperature zero with thinking disabled. Proceed from a balanced
eight-task smoke subset to all 40 tasks only if each controller has at most one API/parse failure.
GLM replication is optional and occurs only if the Qwen trajectory result is informative.

## Metrics

- correct target resolution;
- final database state success;
- wrong-target attempt;
- wrong-entity write;
- invalid-target attempt blocked by preconditions;
- unnecessary rejection;
- collateral modifications;
- API failures, request count, retries, and wall-clock latency;
- complete tool trace for every episode.

API failures are never interpreted as model behavior. The larger 160/80-task mutation replay
remains a consequence analysis; this 40-task trajectory is the model-facing execution check.
