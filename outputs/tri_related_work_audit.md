# Related Work Audit for Temporal Referent Integrity

Date: 2026-07-16

## Positioning Claim

The paper should not be positioned as a generic "dynamic environment" benchmark or a generic "referential ambiguity" benchmark. Its specific contribution is:

> In tool-using agents, a target can be semantically bound before an observation update, but a controller that stores only the latest observation and the original natural-language goal may re-evaluate the referring expression after the update, causing referent drift.

## Adjacent Areas

### Stateful Tool-Use Benchmarks

- ToolSandbox studies stateful tool use, tool execution, and insufficient information settings. It is adjacent because it evaluates tool-using agents in controlled environments, but it does not isolate temporal binding of referring expressions as the experimental factor.
- AppWorld evaluates agents over app-like APIs and workflows. It provides an external migration target, but the proposed benchmark is narrower and mechanistic.

Useful links:

- ToolSandbox: https://arxiv.org/abs/2408.04682
- AppWorld: https://arxiv.org/abs/2407.18901

### Dynamic and Evolving Agent Environments

Recent dynamic-environment benchmarks study whether agents adapt to changing worlds, updated rules, evolving tasks, or multi-agent perturbations. The closest framing risk is that reviewers may say this is "just another dynamic environment failure." The paper should explicitly distinguish:

- dynamic-environment robustness: can the agent update beliefs when the world changes?
- temporal referent integrity: should the agent update the referent at all?

In our tasks, dynamic references should update and anchored references should not. The agent must decide the binding time, not merely react to change.

Useful links:

- ClawArena: https://arxiv.org/abs/2604.04202
- EvoArena: https://arxiv.org/abs/2606.13681

### Referential Ambiguity and Grounded Reference

Work on referential ambiguity typically asks whether models resolve ambiguous descriptions, use context, or ask clarifying questions. Our setting is different because the reference can be unambiguous at the time it is uttered. The failure occurs when the agent controller later reinterprets a previously bound description against a new state.

Useful query target:

- Referential Ambiguity in LLMs: https://arxiv.org/abs/2509.16107

### Memory and Belief State

Belief-state and memory work asks how agents should summarize trajectories. TRI can be framed as a specific missing field in belief state: not just "what is true now," but "which entity was bound by the user's goal, and at what binding time." The cleanest method contribution is therefore a typed temporal reference ledger, not a generic memory summary.

## Recommended Related-Work Wording

"Prior work on dynamic agent benchmarks evaluates whether agents can adapt to changing observations. We ask a complementary question: when should an agent refuse to adapt a referring expression? An anchored instruction such as 'select the current default branch, refresh, then run checks on that same branch' requires preserving a pre-refresh entity identity, whereas 'refresh, then select the current default branch' requires re-evaluation. Existing benchmarks do not make this binding-time distinction a controlled experimental variable."

## Collision Risk

Current collision risk is moderate, not high. The broad ingredients exist:

- dynamic environments;
- stateful tool use;
- reference resolution;
- memory summaries.

The specific paired-factor design appears distinct:

- anchored vs dynamic binding;
- flip vs stable updates;
- full transcript vs state-overwrite controller;
- typed ledger repair.

The paper should avoid claiming "first dynamic environment benchmark" or "first referential ambiguity benchmark." It should claim a new failure mode and evaluation factor in agent state management.

