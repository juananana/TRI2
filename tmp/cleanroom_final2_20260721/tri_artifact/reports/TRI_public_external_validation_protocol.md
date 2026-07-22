# TRI Public External Validation Protocol

**Status:** design frozen as a pre-registration draft; no model result is implied by this file.

## Research Question

Does post-binding target substitution occur in a public, stateful tool environment when the
agent's initial binding is correct, and does it depend on whether the user's language authorizes
preservation or reevaluation?

The experiment is not a test of whether a model can always retain an old object or always choose
the newest object. It uses a crossed design so those two trivial policies fail in opposite cells.

## Core 2 x 2 Design

Every task has a pre-refresh state $S_0$, a refreshed state $S_1$, a selector $q$, a target
action, and a mutation evaluator. The state transition is hidden from the model and the human
labelers.

| Reference semantics | Winner stable | Winner flips |
|---|---|---|
| Preserve: select/bind before refresh, then act on it | old ID remains correct; detects overreaction to refresh | old ID remains correct; primary TRI rebinding cell |
| Reevaluate: refresh before selecting, then act | new selector result is correct; detects unnecessary locking | new ID is correct; primary premature-binding cell |

Stable means the world may change, but the selector winner remains the same. Flip means the
selector winner changes while both relevant entities remain present and action-valid. Remove and
Invalidate are secondary safety-policy slices, not part of the human-supported referential-core
estimand.

The current ToolSandbox-adapted inventory is frozen at 96 tasks, 24 per cell, using six selector
clusters and four paraphrases per cluster. This is a clustered diagnostic inventory rather than
96 independent natural-user samples. The exact task IDs, transition operator, initial/refresh
snapshots, and evaluator are frozen before model calls. A later multi-domain extension must be
reported as a separate study, not concatenated into this denominator. The existing 24-task pilot
is retained as a feasibility audit and is not silently merged into the confirmatory inventory.

## Human and LLM Semantic Labels

### Human gold

Use three independent annotators who do not design TRI. Each sees the natural instruction, the
candidate objects in $S_0$ and $S_1$, and the action preconditions, but not the hidden cell label,
task source, or benchmark gold. They return an entity ID, `REJECT`, or `CLARIFY`. Report:

- majority target and determinate-majority rate;
- Fleiss' kappa and nominal Krippendorff's alpha;
- `CLARIFY` and disagreement rates;
- agreement by all four 2 x 2 cells;
- author/scenario-cluster bootstrap intervals.

Low-agreement items remain an ambiguity slice and are not silently converted into model errors.
Reject is analyzed as an action policy, not as unquestioned referential gold.

### Strong LLM judge

A strong independent LLM may label the same items as an auxiliary semantic judge, but it must
not replace human gold. The judge receives a fixed rubric and no benchmark target. We report:

- judge versus human-majority agreement;
- judge confidence/calibration on determinate versus ambiguous items;
- model results scored against human majority and, separately, judge labels.

The judge is useful for scaling and adjudication triage. It cannot be used to define a gold label
that is then presented as human evidence, especially when the tested model family and judge share
training or provider artifacts.

## Agent Conditions

### Primary existence test

Run an ordinary full-history/ReAct-style tool agent with autonomous tool choice. This answers
whether the phenomenon appears in a plausible agent loop rather than only in the project's
Generic Structured Ledger.

### Mechanism controls

Run the same frozen tasks with:

1. Generic Structured Ledger;
2. exact pre-refresh Compile-then-act;
3. Lifecycle-Gated, as a contract/enforcement condition.

All conditions use the same tools, state transitions, model, task order, and output parser. Tool
selection, compiler, referent, and mutation errors are recorded separately.

## Model Sampling

The claim should be tested across model families, not every available LLM. The minimum useful
sample is three families: the existing Qwen and GLM runs plus one independent family such as
DeepSeek or Llama. A smaller model can be added as a capability sensitivity condition, but it
should not replace a third family. All models use the same API protocol, temperature, token cap,
tool descriptions, and retry policy. A small repeated subset at a nonzero temperature may report
stability, but temperature-zero point estimates remain the primary comparison.

The paper must not claim that every LLM has TRI failures. The estimand is the conditional failure
rate for the tested model/controller sample.

## Metrics and Primary Estimands

For each trajectory, record:

1. initial binding accuracy in $S_0$;
2. final authorized-target accuracy;
3. conditional TRI failure, $P(\text{wrong final target}\mid\text{initial binding correct})$;
4. Preserve unauthorized-rebinding rate;
5. Reevaluate premature-lock rate;
6. wrong-target attempt and wrong-entity write rates;
7. invalid attempt, unnecessary rejection, collateral modification;
8. tool-selection error, compiler/parse error, and API error.

The primary existence estimand is the Preserve/Flip conditional unauthorized-rebinding rate of
the ordinary agent, with a cluster-level 95% bootstrap interval. The Reevaluate/Flip cell is the
paired directionality check. Stable cells test whether a method changes targets merely because
an update occurred. Overall accuracy is secondary and must not hide the conditional denominator.

## External Extensions

### AppWorld case study

After ToolSandbox, select 8--16 AppWorld tasks from mail, calendar, shopping, or payment-like
apps only when the public task world exposes stable entity IDs and the official database-state
evaluator can inspect collateral changes. Add a frozen mid-trajectory transition or custom task
world before the final mutation. Release the adaptation protocol and evaluator, but do not expose
test solutions or call the result an unmodified AppWorld leaderboard score.

### tau3-bench case study

Use the public tau3-bench text mode and its dual-control lineage only after confirming that a
user-side tool can change shared state after the agent has established an entity. Preserve the
benchmark's original policy/task objective, add an explicit hidden transition record, and score
the final action ID plus any state diff. This is conceptually strong but has extra user-simulator
noise, so it is a secondary validation.

## Interpretation Rules

- A nonzero conditional failure with correct initial binding and human-majority support confirms
  the phenomenon in the tested public environment.
- Stable/Flip complementarity supports selective authorization rather than an always-old or
  always-new heuristic.
- A zero result does not disprove TRI if the environment lacks a genuine post-binding opportunity;
  report opportunity coverage first.
- Tool/compiler failures are not referent failures and must be reported separately.
- Mixed or negative external results remain valid evidence about the method's boundary.
