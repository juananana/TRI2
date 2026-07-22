# AppWorld TRI Two-Application Boundary Results

## Scope

The custom case study uses AppWorld 0.1.3.post1 databases and native APIs for two
independent selector clusters: Todoist earliest-due tasks and Simple Note alphabetical
titles. Each cluster crosses Preserve/Reevaluate, Stable/Flip, and two paraphrases.
The 16 task definitions, synchronization operators, sidecar binding instrument, and
evaluators are custom. These are not AppWorld leaderboard results. The Simple Note
cluster was added after the Todoist result and is reported as a post-primary extension.

## Results by Application and Model

| Cluster | Model/controller | Rows | Strict success | Correct write | Auditable binding | Conditional TRI | Wrong writes |
|---|---|---:|---:|---:|---:|---:|---:|
| simple-note-alphabetical-first | Pro/zai-org/GLM-5.1 / full-history | 8 | 4/8 | 8/8 | 4/8 | 0/4 | 0 |
| simple-note-alphabetical-first | Qwen/Qwen3.5-122B-A10B / full-history | 8 | 6/8 | 7/8 | 6/8 | 0/6 | 1 |
| todoist-earliest-due | Pro/zai-org/GLM-5.1 / full-history | 8 | 8/8 | 8/8 | 8/8 | 0/8 | 0 |
| todoist-earliest-due | Qwen/Qwen3.5-122B-A10B / full-history | 8 | 6/8 | 8/8 | 6/8 | 0/6 | 0 |

## Combined Boundary

Across 2 clusters and 32 trajectories, strict
success is 24/32 and authorized-target
writes are 31/32. A correct,
correctly timed initial binding is observable in 24
trajectories; conditional TRI is 0/24. The Preserve/Flip slice contains
0/4 unauthorized rebindings after such a binding.

There is one real wrong-entity database write. Qwen searches the correct Simple Note A,
synchronizes without recording a commitment, searches again, binds new winner B, and
writes B. The matched Stable trajectory has the same delayed-binding order but writes A
because the winner does not change. This is a selector-sensitive tool-order failure, not
post-binding drift, and is excluded from the conditional TRI numerator by the frozen rule.

## Interpretation

No post-binding TRI was observed after a correct, correctly timed binding. One Qwen Simple Note trajectory made a real wrong-entity write, but it refreshed and rebound before the sidecar recorded an initial commitment, so it is a delayed-binding/tool-order error outside the conditional TRI denominator. The study is a custom AppWorld-backed boundary case study, not a leaderboard or prevalence result.
The sidecar is scientifically useful because it prevents final-target errors from being
misclassified as TRI, but its omission in 8/32 trajectories also shows that explicit
binding instrumentation changes the autonomous workflow. The external result therefore
bounds universality; the controlled benchmark remains the positive mechanism diagnosis.
