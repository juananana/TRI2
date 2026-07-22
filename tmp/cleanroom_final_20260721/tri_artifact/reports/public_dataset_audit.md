# Public Stateful-Agent Dataset Audit

**Audit date:** 2026-07-20

This is a dataset-selection record, not an empirical result. It records whether a public
benchmark can independently validate TRI without replacing the frozen TRI-v3 diagnostic.

## Decision Summary

| Candidate | Public code/data | Stateful mutable world | Stable IDs and state evaluator | TRI fit | Decision |
|---|---|---:|---:|---:|---|
| ToolSandbox | Yes: [GitHub](https://github.com/apple/ToolSandbox), paper [arXiv:2408.04682](https://arxiv.org/abs/2408.04682) | Yes | Partial: milestone and trajectory evaluation, but no TRI-specific gold | High adaptation fit | Use as the first external pilot |
| AppWorld | Yes: [GitHub](https://github.com/StonyBrookNLP/appworld), paper [arXiv:2407.18901](https://arxiv.org/abs/2407.18901) | Yes: 9 apps, 457 APIs, 100+ tables | Strong: task worlds and database-state unit tests with collateral checks | High validity, higher engineering cost | Best external case study if a custom transition can be frozen |
| tau-bench / tau2-bench / current tau3-bench | Yes: [GitHub](https://github.com/sierra-research/tau2-bench), [tau-bench paper](https://arxiv.org/abs/2406.12045), [tau2 paper](https://arxiv.org/abs/2506.07982) | Yes; tau2 adds dual control and user tools | Strong task/action evaluation, but no TRI-specific referent gold | High conceptual fit, moderate adaptation cost | Use as a second external case study or future validation |
| WebArena / BrowserGym / OSWorld | Public | Stateful browser or desktop sessions | Final task success, but entity-level mutation attribution is difficult | Low to moderate | Do not prioritize for this paper |
| Static coreference, API-call, or tool-selection sets | Usually public | No controlled post-binding state transition | No final database mutation evaluator | Low | Not suitable as TRI evidence |

## What Can and Cannot Be Claimed

The public benchmarks are suitable for **external instantiation**, not for replacing TRI-v3's
minimal-pair gold. Their released tasks generally do not guarantee the exact event sequence

```text
correct binding in S0 -> refresh or user-side mutation -> final action on a referent
```

Therefore, a valid external experiment must freeze a small TRI-adapted subset and release the
adaptation protocol, transition operator, target identity mapping, and evaluator. Running an
unmodified leaderboard score and calling it TRI evidence would be invalid.

## Candidate Details

### ToolSandbox

The official repository describes stateful tool execution, implicit tool dependencies, an
on-policy user simulator, and milestone/final trajectory evaluation. It is the lowest-risk
extension because the environment already exposes intermediate tool state and the current
project has a 24-task ToolSandbox-based pilot. The official scenarios should be audited first;
only scenarios with stable entity IDs, a read/refresh operation, and a mutation with a visible
wrong-target consequence should enter a TRI-adapted subset.

### AppWorld

The official repository describes a controllable world with nine day-to-day apps, 457 APIs,
more than 100 database tables, task-specific initial worlds, and database-state unit tests that
also check collateral damage. Train/dev worlds expose setup and evaluation information, while
test worlds preserve evaluation-only access. This makes AppWorld the strongest external validity
candidate. The difficulty is that an ordinary AppWorld task is not automatically a TRI task;
the study must add a frozen mid-trajectory transition or use a custom task world, without
leaking its solution or changing the public evaluator semantics.

### tau-bench, tau2-bench, and tau3-bench

The current public repository has moved from tau2-bench to a tau3-bench release and includes
airline, retail, telecom, mock, and banking-knowledge domains. The tau2 paper is especially
relevant because it introduces dual-control settings in which the user and agent can both
affect the shared environment. This is conceptually close to TRI, but the default benchmark
asks for customer-service policy adherence and task completion, not explicit Preserve versus
Reevaluate referential gold. A TRI adaptation should use user-side state changes after an
initial entity is mentioned, then score the final action ID and any resulting database diff.

## Recommended Experimental Order

1. Keep the existing TRI-v3 controlled benchmark as the primary phenomenon diagnosis.
2. Freeze an 80--120 task ToolSandbox-adapted external subset with autonomous tool choice and
   explicit trace decomposition. Cross Preserve/Reevaluate language with Stable/Flip world
   transitions rather than evaluating changed-versus-unchanged state alone; report it as
   external validity, including negative outcomes. The complete pre-registration draft is
   `reports/TRI_public_external_validation_protocol.md`. Each task should be a single user
   message followed by a logged stateful tool trajectory; see
   `reports/TRI_single_user_turn_trajectory_protocol.md`.
3. If the environment is stable, add an 8--16 task AppWorld case study with a custom frozen
   transition and database-diff evaluator.
4. Treat tau3-bench as a second independent validation only after confirming that its user-side
   transition can be inserted before the final mutation without changing the benchmark's task
   objective.

The first candidate is the most practical; AppWorld is the strongest but most expensive; tau3
is the most conceptually aligned with dual control. None should be described as an unmodified
TRI benchmark unless the released task metadata already contains the required transition and
referent semantics.

## Completed Audits and Case Study

- Official ToolSandbox at commit `165848b`: 129 semantic families, 1,032 augmented
  tool-presentation instances, 0 strict native TRI opportunities, 1 TRI-like natural trace.
- Official AppWorld `0.1.3.post1`: installation verified on all 147 train/dev tasks; downloaded
  release contains 732 task instances from 244 generator families, 0 strict externally scheduled
  TRI opportunities, and 1 natural TRI-like Todoist family.
- Released AppWorld trace audit: 42 trajectories across 14 configurations for family `8ce6779`;
  16/16 correct target operations retain the same task ID for the later comment, with 0
  post-binding substitutions. Most failures are pre-binding omissions.
- Official tau3-bench at commit `cf71a807`: 2,449 airline/retail/telecom tasks and 10,832 released
  GPT-4.1/GPT-4.1-mini/Claude 3.7/o4-mini trajectories. Strict native TRI opportunities are 0.
  Eight telecom payment tasks are natural dual-control near-matches but move from a bill to an
  associated line, not the same referential role.
- Custom AppWorld study: 8 frozen Todoist tasks plus a separately frozen post-primary 8-task
  Simple Note extension, two full-history models, 31/32 authorized final writes, 24 auditable
  correctly timed bindings, and 0/24 conditional TRI. The sole wrong write follows delayed
  binding after synchronization and is not counted as post-binding drift.

These results strengthen construct realism while weakening any universal or prevalence reading.
The controlled TRI-v3/v7 experiments remain the positive failure diagnosis.
