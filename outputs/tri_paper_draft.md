# Temporal Referent Integrity in Tool-Using LLM Agents

## Abstract

Tool-using language agents increasingly operate in environments whose state changes during task execution. Existing evaluations study whether agents can update beliefs under environmental change, but they rarely ask whether an agent preserves the identity of an entity that was already selected before such change. We study **temporal referent integrity**: the requirement that agents distinguish references that bind before an observation update from references that should be evaluated after the update. We construct paired tasks that isolate four conditions: anchored references with changing selectors, anchored stable controls, dynamic references with changing selectors, and dynamic stable controls. A small pilot shows a sharp architecture-dependent failure. When a controller overwrites its state with the latest observation while retaining only the original natural-language goal, GLM-5.1 and Qwen3.5 systematically drift from the pre-refresh entity to the post-refresh entity on anchored-changing tasks, while remaining correct on dynamic and stable controls. Preserving a typed temporal reference ledger restores performance in the same tasks. These findings suggest that reliable agents need goal representations that record binding time and entity identity, not only updated observations and re-evaluable textual goals.

## 1. Introduction

Users often describe targets relative to the current environment:

> First identify the currently highest-severity incident. After refreshing, escalate that same incident.

This instruction is not equivalent to:

> Refresh first, then escalate the currently highest-severity incident.

The first instruction binds an entity before refresh; the second intentionally evaluates the description after refresh. A reliable agent must preserve this distinction. If the agent stores the goal only as a textual description and then replaces its world state with the latest observation, the phrase "currently highest-severity incident" can be reinterpreted against the wrong state.

We call this failure **referent drift**. It is especially easy to miss because the tool outputs are correct, the environment update is legitimate, and the model may understand the instruction in a direct semantic setting. The failure arises from the interface between natural-language goals and agent state management.

## 2. Problem Definition

Let an instruction contain a referring expression `r`, an initial observation `s0`, and an updated observation `s1`.

- An **anchored** reference binds at `s0`; the correct target is `bind(r, s0)`.
- A **dynamic** reference binds at `s1`; the correct target is `bind(r, s1)`.

Temporal referent integrity requires the agent to select:

```text
target = bind(r, s0)  for anchored references
target = bind(r, s1)  for dynamic references
```

even when `bind(r, s0) != bind(r, s1)`.

The critical counterexample is the `flip` condition, where the refreshed state changes which entity satisfies the selector.

## 3. Benchmark

Each task has four matched conditions:

| Condition | Binding time | Refresh changes selector? | Expected behavior |
|---|---|---:|---|
| Anchored + Flip | before refresh | yes | keep original entity |
| Anchored + Stable | before refresh | no | keep original entity |
| Dynamic + Flip | after refresh | yes | choose new entity |
| Dynamic + Stable | after refresh | no | choose same entity |

Pilot domains include incidents, meetings, support tickets, repository branches, invoices, and devices. The hidden oracle is deterministic and uses entity IDs, so scoring does not require an LLM judge.

## 4. Agent Modes

We compare four controller modes:

- **Direct semantic resolution**: the model sees both states and directly resolves the target.
- **Full transcript interactive**: the model retains the full conversation and both observations.
- **State-overwrite controller**: after refresh, the controller retains the original instruction and latest state, but not the bound entity.
- **Temporal reference ledger**: the controller stores a typed ledger containing `binding_time`, `selector`, and `bound_target_id`.

The state-overwrite controller is the failure-inducing representation. The ledger is the minimal repair.

## 5. Pilot Results

| Model | Mode | Split | Anchored+Flip | Anchored+Stable | Dynamic+Flip | Dynamic+Stable |
|---|---|---|---:|---:|---:|---:|
| GLM-5.1 | direct | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | full transcript | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | state-overwrite | dev | 0/4 | 4/4 | 4/4 | 4/4 |
| GLM-5.1 | ledger | dev | 4/4 | 4/4 | 4/4 | 4/4 |
| Qwen3.5 | state-overwrite | dev partial | 0/3 | 3/3 | 3/3 | 3/3 |
| Qwen3.5 | ledger | dev partial | 3/3 | 3/3 | 3/3 | 3/3 |
| GLM-5.1 | state-overwrite | heldout | 0/2 | 2/2 | 2/2 | 2/2 |
| GLM-5.1 | ledger | heldout | 2/2 | 2/2 | 2/2 | 2/2 |

All state-overwrite failures select the post-refresh target. This supports a specific referent-drift mechanism rather than random execution error.

## 6. Method: Typed Temporal Reference Ledger

The ledger stores:

```json
{
  "binding_time": "pre_refresh | post_refresh",
  "selector": "natural language selector or structured predicate",
  "bound_target_id": "entity id when binding_time=pre_refresh",
  "validity_condition": "entity still exists and action remains legal"
}
```

The next method step is to replace the oracle ledger with a compiler that produces this representation from the user instruction and initial observation.

## 7. Related Work Positioning

Dynamic-agent benchmarks such as ProEvolve, ClawArena, and EvoArena study changing environments, belief revision, memory evolution, and robustness to updates. Our focus is narrower: whether a target reference should be bound before or after an update, and whether the bound entity identity survives a state update.

ToolSandbox includes stateful tool use and insufficient-information tasks, but it does not isolate temporal binding of referring expressions as the experimental variable.

Work on referential ambiguity studies whether LLMs resolve ambiguous references or ask clarification questions. Our setting differs because the reference can be semantically clear, but the agent controller can still lose the binding when its observation state is overwritten.

## 8. Current Limitations

- The pilot is small and should be expanded before submission.
- Qwen results are partial because of API latency.
- The current ledger experiment uses oracle binding; a real compiler is required.
- Full transcript agents can solve the pilot, so the paper must target controller-state representations rather than raw LLM ability.
- A stronger paper should test real agent frameworks that summarize or overwrite state.

## 9. Submission Plan

The paper is promising if the next experiments show:

1. State-overwrite drift persists across at least four model families.
2. The effect holds across paraphrases and more domains.
3. Real agent controllers or summarizing memory modules exhibit the same failure.
4. An automatic temporal-reference compiler recovers most failures without over-binding dynamic references.

