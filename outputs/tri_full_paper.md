# Temporal Referent Integrity in Tool-Using LLM Agents

## Abstract

Tool-using language agents often operate in environments that change while a task is being executed. Existing evaluations ask whether agents can update their beliefs when observations change. We study a complementary question: when should an agent **not** update the referent of a user's target description? We introduce **temporal referent integrity** (TRI), the requirement that an agent distinguish references that bind to an entity before an observation update from references that should be evaluated after the update. We construct paired tasks that cross binding time (anchored vs. dynamic) with environmental update (selector-flipping, stable, and removed-entity updates). In a state-overwrite controller, which retains the original natural-language goal and the latest observation but not the previously bound entity, three model families show a strong paired contrast: they drift on anchored-flip tasks while remaining largely correct on dynamic-flip controls. GLM-5.1 drifts in 97.0% of 33 valid anchored-flip cases and succeeds in 100% of 21 dynamic-flip cases; Qwen3.5 obtains 0.0% anchored-flip accuracy and 100.0% dynamic-flip accuracy over 15 all-paraphrase development tasks per condition; MiniMax-M2.5 obtains 0.0% and 93.3%, respectively. A DeepSeek-V4-Pro pilot shows the same qualitative pattern but the endpoint was unstable in longer runs. Typed temporal reference ledgers, natural-language memory in simple cases, and automatic compile-then-act controllers repair the failure: GLM-5.1 compiles and acts correctly on 30/30 anchored/dynamic flip tasks, with smaller Qwen3.5 and MiniMax-M2.5 pilots also succeeding. These results suggest that reliable tool agents need goal representations that record binding time and entity identity, not only updated observations and re-evaluable natural-language instructions.

## 1. Introduction

Consider two instructions to a tool-using agent:

1. "First identify the currently highest-severity incident. After refreshing, escalate that same incident."
2. "Refresh first. Then identify the currently highest-severity incident and escalate it."

The two instructions contain similar words but impose different temporal semantics. The first binds an entity before the refresh. The second intentionally evaluates the referring expression after the refresh. If a refresh changes which incident has the highest severity, a reliable agent must preserve the first target but update the second.

This distinction is easy to lose in LLM-agent controllers. Many agents carry a natural-language goal forward while updating their environment state. If the controller later sees only the latest state and the original goal, a phrase such as "the currently highest-severity incident" can be re-evaluated in the wrong state. The agent may confidently act on the new incident, even though the user had already bound the old one.

We call this failure **referent drift** and study the broader property of **temporal referent integrity**. TRI is not simply memory retention, dynamic-environment adaptation, or referential ambiguity. The central question is not "did the world change?" but "should this referring expression be re-bound after the world changes?"

This paper makes four contributions:

1. We define temporal referent integrity for tool-using agents.
2. We introduce a paired benchmark that isolates binding time from environmental change.
3. We show that a state-overwrite controller produces a mechanism-specific failure: anchored references drift after refresh, while dynamic references remain correct.
4. We propose a typed temporal reference ledger and a compile-then-act controller, and report compiler-level accuracy separately from final action accuracy.

## 2. Problem Definition

Let `s0` be the initial observation, `s1` a later observation after a refresh, and `r` a referring expression in the user's instruction.

An **anchored** reference binds before the update:

```text
target = bind(r, s0)
```

A **dynamic** reference binds after the update:

```text
target = bind(r, s1)
```

Temporal referent integrity requires the agent to preserve this binding-time distinction even when:

```text
bind(r, s0) != bind(r, s1)
```

This creates a natural 2 x 2 experimental design:

| Binding | Update | Correct behavior |
|---|---|---|
| Anchored | Flip | preserve pre-refresh entity |
| Anchored | Stable | preserve same entity |
| Dynamic | Flip | select post-refresh entity |
| Dynamic | Stable | select same entity |

The `anchored + flip` condition is the critical counterexample. It is where a state-overwrite controller has the strongest temptation to re-evaluate the target description against the new state.

### Sufficient Controller State

TRI can be viewed as a sufficient-state requirement for agent controllers. A controller state that contains only the latest observation and the original natural-language goal is not sufficient for anchored references. A sufficient referent state should include:

```text
z = (r, binding_time, bound_entity_id, selector, validity_condition, provenance)
```

Here `r` is the original referring expression, `binding_time` records whether the referent has already bound, `bound_entity_id` stores the stable identity when binding is pre-refresh, `selector` records how dynamic references should be evaluated, `validity_condition` determines whether the bound entity remains actionable, and `provenance` records the observation that licensed the binding.

This framing turns the failure from a generic "the model forgot" error into a representation claim: latest-state summaries can be insufficient even when the latest observation is perfectly accurate.

## 3. Benchmark

We generate deterministic tasks over structured mini-domains. Each task contains:

- a user instruction;
- an initial state with stable entity IDs;
- a refreshed state;
- an oracle target ID;
- a fixed action schema.

Domains include incidents, meetings, support tickets, repository branches, shipments, experiment runs, invoices, devices, patient cases, and datasets. Selectors cover numeric maxima, queue position, Boolean selection, default branch, active run, urgent case, and assignment status.

We use five paraphrase families. Four are natural anchored/dynamic formulations; one is a highly explicit binding paraphrase. This lets us test whether stronger wording reduces drift.

Scoring is exact string matching over entity IDs. No LLM judge is used.

## 4. Agent Modes

We compare several controller modes.

**Direct semantic resolution.** The model sees both states and resolves the target in one turn. This tests whether the language model can understand the temporal semantics when state management is not involved.

**Full transcript interactive.** The model performs a refresh and then acts while retaining the full transcript. This tests whether a full-context controller avoids drift.

**State-overwrite controller.** After refresh, the controller retains only the original instruction and the refreshed state. This simulates agents whose working state is updated to the latest observation without persisting bound entity identities.

**State-overwrite-once controller.** A single-call version of the same representation: the model receives only the original instruction and current refreshed state. This isolates the representation failure without an unnecessary refresh call.

**Typed temporal reference ledger.** The controller carries:

```json
{
  "binding_time": "pre_refresh | post_refresh",
  "selector": "...",
  "bound_target_id": "entity id or null",
  "validity_condition": "entity still exists and action remains legal"
}
```

**Natural memory.** The model summarizes the initial instruction and state into a free-form note, then acts using only the note and refreshed state.

**Compressed memory.** A stricter summary controller prohibits entity IDs, exact names, and exact numeric values. This simulates low-budget state compression that retains the task description but drops identity-bearing details.

**Compile-then-act prototype.** The model first compiles the instruction and initial state into a ledger, then acts using only the ledger and refreshed state.

**Stateful tool controllers.** We also instantiate the tasks as a small tool environment with `observe`, `refresh`, and `process` tools. The controller first observes the pre-refresh state, calls `refresh`, receives the new tool observation, and then calls `process(target_id)`. We evaluate four controller memory policies in this actual tool loop: latest-state-only, full-history, lossy summary, and compile-then-act.

## 5. Results

### 5.1 Main Mechanism Result

The state-overwrite representation creates a sharp failure on anchored references and not dynamic references.

| Model | Mode | Condition | n | Accuracy | Drift Rate |
|---|---|---|---:|---:|---:|
| GLM-5.1 | state-overwrite-once | anchored + flip | 33 | 3.0% | 97.0% |
| GLM-5.1 | state-overwrite-once | dynamic + flip | 21 | 100.0% | 0.0% |
| Qwen3.5 | state-overwrite-once | anchored + flip | 15 | 0.0% | 73.3% |
| Qwen3.5 | state-overwrite-once | dynamic + flip | 15 | 100.0% | 0.0% |
| MiniMax-M2.5 | state-overwrite-once | anchored + flip | 15 | 0.0% | 100.0% |
| MiniMax-M2.5 | state-overwrite-once | dynamic + flip | 15 | 93.3% | 0.0% |
| DeepSeek-V4-Pro | state-overwrite-once | anchored + flip | 3 | 0.0% | 100.0% |
| DeepSeek-V4-Pro | state-overwrite-once | dynamic + flip | 3 | 100.0% | 0.0% |

The contrast is the important signal. The same controller can use the refreshed state correctly when the instruction is dynamic, but it incorrectly re-binds anchored descriptions after the refresh.

### 5.2 Paraphrase Robustness

For GLM-5.1 under state-overwrite-once:

| Paraphrase | Anchored + Flip Accuracy | Drift Rate |
|---|---:|---:|
| p0 | 0.0% | 100.0% |
| p1 | 0.0% | 100.0% |
| p2 | 20.0% | 80.0% |
| p3 | 0.0% | 100.0% |
| p4 | 0.0% | 100.0% |

The highly explicit p2 paraphrase helps slightly, but does not solve the state-representation problem. The other paraphrases drift almost perfectly.

### 5.3 Held-Out Domains

On held-out domains (invoice, device, patient case, dataset), GLM-5.1 under state-overwrite-once fails on 20/20 anchored-flip tasks. Most failures select the post-refresh entity. Dynamic held-out controls were partially run because of API timeouts; among valid responses, dynamic-flip accuracy was 6/6.

### 5.4 Stateful Tool Controller Replication

To address the concern that TRI is only an artifact of manually constructed JSON prompts, we implement a small stateful tool environment with `observe`, `refresh`, and `process` tools. Each run produces an actual tool trace: the controller observes the initial state, calls `refresh`, receives a refreshed observation, and then calls `process` on a target ID. We then vary the controller's carried state.

| Model | Tool Controller | Condition | n | Accuracy | Drift |
|---|---|---|---:|---:|---:|
| GLM-5.1 | latest-state | anchored + flip | 14 | 21.4% | 64.3% |
| GLM-5.1 | latest-state | dynamic + flip | 15 | 100.0% | 0.0% |
| GLM-5.1 | full-history | anchored + flip | 3 | 100.0% | 0.0% |
| GLM-5.1 | full-history | dynamic + flip | 3 | 100.0% | 0.0% |
| GLM-5.1 | lossy-summary | anchored + flip | 3 | 66.7% | 33.3% |
| GLM-5.1 | lossy-summary | dynamic + flip | 3 | 100.0% | 0.0% |
| GLM-5.1 | tool compile-then-act | anchored + flip | 3 | 100.0% | 0.0% |
| GLM-5.1 | tool compile-then-act | dynamic + flip | 3 | 100.0% | 0.0% |

This tool-loop result mirrors the text-controller finding. In the latest-state controller, all p0 anchored-flip tasks drift to the post-refresh target, and the all-paraphrase expansion remains unreliable: among valid anchored-flip responses, accuracy is 21.4% and drift is 64.3%, while the same controller is correct on 15/15 dynamic-flip tasks. Full-history and compile-then-act controllers repair the p0 failure. The lossy-summary controller partially fails, again showing that automatic summaries can preserve temporal wording while dropping executable identity.

### 5.5 Repair by Memory and Temporal Reference Ledgers

Several representations can repair the failure when they preserve the pre-refresh identity. This is important: the paper does not claim that natural language memory is always useless. Instead, the claim is that state overwrite is unsafe, and typed reference records make the relevant state explicit and checkable.

| Model | Mode | Condition | n | Accuracy |
|---|---|---|---:|---:|
| GLM-5.1 | compile-then-act | anchored + flip | 15 | 100.0% |
| GLM-5.1 | compile-then-act | dynamic + flip | 15 | 100.0% |
| Qwen3.5 | compile-then-act | anchored + flip | 9 | 100.0% |
| Qwen3.5 | compile-then-act | dynamic + flip | 6 | 100.0% |
| MiniMax-M2.5 | compile-then-act | anchored + flip | 6 | 100.0% |
| MiniMax-M2.5 | compile-then-act | dynamic + flip | 6 | 100.0% |
| GLM-5.1 | natural memory | anchored + flip | 3 | 100.0% |
| GLM-5.1 | compressed memory | anchored + flip | 3 | 0.0% |
| GLM-5.1 | compressed memory | dynamic + flip | 3 | 100.0% |
| Qwen3.5 | oracle ledger | anchored + flip | 3 | 100.0% |
| Qwen3.5 | oracle ledger | dynamic + flip | 3 | 100.0% |

The compile-then-act controller is especially important because it does not rely on an oracle ledger: the model first produces the temporal ledger from the instruction and initial state, then acts from the ledger and refreshed state. We additionally separate compiler quality from final action quality. For GLM-5.1, binding-time compilation, anchored bound-ID compilation, and final action accuracy are all 100.0% over 15 anchored-flip and 15 dynamic-flip development tasks. Smaller Qwen3.5 and MiniMax-M2.5 compiler pilots also compile binding time correctly and act correctly on all completed tasks (Qwen3.5: 9 anchored, 6 dynamic; MiniMax-M2.5: 6 anchored, 6 dynamic).

The memory baselines clarify the mechanism. A free-form natural note can preserve enough identity information in simple tasks, but a compressed note that drops entity IDs and exact values collapses back to state-overwrite behavior: anchored-flip fails while dynamic-flip remains correct. This supports the interpretation that the key missing variable is not generic memory, but executable identity preservation.

We also test a text-level summary controller: the agent first executes `refresh`, a controller memory module summarizes the transcript, and the next step acts from the generated summary plus the refreshed state. When the summary module is instructed to preserve task-critical entity identity, GLM-5.1 solves anchored-flip and dynamic-flip in 3/3 p0 tasks. A lossy bounded summary that forbids entity IDs is much less reliable over the all-paraphrase development set: anchored-flip accuracy falls to 26.7% (4/15), with 53.3% drift to the post-refresh target and additional invalid-action errors, while dynamic-flip remains high at 93.3% (14/15). This is important because the identity loss is produced by an automatic controller summary, not directly by the benchmark author deleting a field. In a case-study analysis, 100% of anchored lossy summaries contain temporal anchor words such as "initial," "original," or "before," but 0% contain an entity ID; temporal wording alone is therefore not sufficient controller state. The real risk is not summary per se, but summaries that fail to preserve executable identity for pre-bound referents.

### 5.6 Field Ablation

To show that the ledger is not merely "save an ID," we run an oracle representation ablation over all 300 generated tasks. The result separates three requirements: binding time, entity identity, and validity.

| Representation | Anchored+Flip | Anchored+Removed | Dynamic+Flip |
|---|---:|---:|---:|
| raw goal + latest state | 0.0% | 0.0% | 100.0% |
| selector memory | 0.0% | 0.0% | 100.0% |
| binding-time only | 0.0% | 0.0% | 100.0% |
| entity only | 100.0% | 0.0% | 0.0% |
| time + entity | 100.0% | 0.0% | 100.0% |
| full ledger | 100.0% | 100.0% | 100.0% |

The ablation explains why a referent lifecycle representation is needed. Entity identity fixes anchored flips, but fails when the entity is removed. Binding time plus entity fixes dynamic-vs-anchored selection, but still fails validity. The full ledger is the only representation that handles both referent preservation and entity invalidation.

### 5.7 Entity Invalidation

A reasonable concern is that a ledger might blindly preserve an entity that is no longer available. We therefore add a `removed` update in which the pre-refresh entity disappears from the refreshed state. The correct behavior for anchored references is not to act on a different entity, but to report the bound target as invalid.

On p0 development tasks over three domains, `ledger_safe` returns the invalid target in 3/3 cases. `compile-then-act` succeeds in 4/4 valid responses after retrying API failures. Natural-language memory also succeeds in 3/3 valid responses in this small setting. These results show that TRI should be framed as preserving bound identity **with validity checks**, not as always acting on stale IDs.

### 5.8 Boundary Condition: Full Transcript

GLM-5.1 succeeds in direct semantic resolution and full-transcript interactive mode on the initial p0 development set. This is not a weakness of the paper; it sharpens the claim. TRI failure is not an unavoidable limitation of the base model. It is induced by a controller representation that overwrites state without preserving bound referents.

## 6. Analysis

### Why the Failure Is Not Generic Dynamic-Environment Error

Dynamic references require using the refreshed state, and the state-overwrite controller does so correctly. The failure appears when the refreshed state should **not** change the referent.

### Why the Failure Is Not Ordinary Memory Loss

The missing item is not merely "history." The agent needs a typed record of:

- whether the referring expression has already bound;
- which entity ID it bound to;
- whether the entity remains valid for the action.

A generic natural-language memory summary may or may not preserve the bound entity. In our simple p0 tasks it succeeds, which makes it a strong baseline. However, compressed memory without entity IDs fails like state overwrite. Typed ledgers remain useful because they expose binding time, entity identity, and validity conditions as fields that can be tested and enforced.

### Why the Failure Is Not Referential Ambiguity

At the time of binding, the target can be perfectly clear. The ambiguity is introduced by the controller after the environment changes.

## 7. Method: Temporal Reference Compiler

We propose a temporal reference compiler that transforms user goals into structured referent records.

The compiler has three stages:

1. **Binding-time inference:** decide whether the expression binds before or after a future observation update.
2. **Selector grounding:** map the expression to a selector over the current or future state.
3. **Identity persistence:** if binding time is pre-refresh, store the entity ID rather than the textual description alone.

At action time, the controller applies:

```text
if binding_time == pre_refresh:
    act on bound_target_id
else:
    evaluate selector on refreshed_state
```

This simple logic explains both the failure and the repair.

## 8. Related Work

Stateful tool-use benchmarks such as ToolSandbox and app-like benchmarks such as AppWorld evaluate whether agents can use tools over changing state and avoid hallucinating under insufficient information. Our work is narrower: it isolates when a referring expression should be bound relative to an observation update. ToolSandbox: https://arxiv.org/abs/2408.04682. AppWorld: https://arxiv.org/abs/2407.18901.

Dynamic-environment benchmarks such as ClawArena and EvoArena evaluate robustness under changing environments, evolving tasks, and multi-agent perturbations. TRI differs because both adapting and refusing to adapt can be correct depending on binding time. ClawArena: https://arxiv.org/abs/2604.04202. EvoArena: https://arxiv.org/abs/2606.13681.

Referential ambiguity work studies whether models resolve ambiguous references or ask for clarification. TRI can fail even when the initial reference is unambiguous: the controller later reinterprets the description against a new state.

Memory and belief-state methods are also adjacent. TRI suggests a specific required field in agent belief state: bound entity identity and binding time.

## 9. Limitations

The current evidence is strong enough to justify continuing the paper, but not yet a final AAAI submission.

First, the all-paraphrase paired development matrix is now complete for GLM-5.1, Qwen3.5, and MiniMax-M2.5, but DeepSeek-V4-Pro remains a small pilot because the SiliconFlow endpoint was unstable in longer runs. Second, natural-language memory is a strong baseline on simple tasks; our compressed-memory and lossy-summary results are first stress tests, and future work should test noisy, budget-limited, and multi-entity summaries. Third, the compile-then-act controller has a complete GLM-5.1 development matrix and smaller Qwen3.5/MiniMax-M2.5 pilots, but not yet a full cross-model compiler matrix. Fourth, we now include a local stateful tool loop, but external ToolSandbox/AppWorld-style framework replication remains future work. Fifth, entity invalidation has only been tested on small p0 samples; richer invalidation cases such as renamed entities, merge/split, repeated refresh, and action-specific invalidity remain to be added.

## 10. Conclusion

Temporal referent integrity exposes a subtle but consequential gap in tool-using LLM agents. Agents must not only update their beliefs when the world changes; they must also know which parts of the user's goal should remain fixed. A state-overwrite controller can systematically drift from a pre-refresh entity to a post-refresh entity, even while handling dynamic references correctly. Typed temporal reference ledgers and compile-then-act controllers provide a simple and effective repair. This positions TRI as a promising research direction for reliable agent state management.
