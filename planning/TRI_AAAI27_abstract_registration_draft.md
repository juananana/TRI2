# AAAI-27 Abstract Registration Draft

## Title

Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents

## Short Title

Temporal Referent Integrity in Tool-Using Agents

## Abstract

Refreshing external state does not by itself authorize a tool-using agent to change the entity denoted by an earlier reference. We formalize this post-binding problem as temporal referent integrity (TRI), separating world-state updates from referent-transition authorization. We construct controlled Preserve/Reevaluate contrasts that hold the initial state, refreshed state, selector, and action fixed while varying when the target is resolved. On a frozen 160-task diagnostic, a Generic Structured Ledger reaches 64.4%/71.9% with Qwen3.5/GLM-5.1, whereas pre-refresh Compile-then-act reaches 95.0%/96.2%; unconditional locking and reevaluation each reach 60.0% and fail complementary cases. A disclosed post-hoc benchmark-aware rule reaches 92.5%, narrowing the algorithmic claim to executable authorization rather than method complexity. In a separately frozen 240-task replication, Generic frequently substitutes the refreshed selector winner after a correct initial binding, while an explicit pre-refresh commitment policy exhibits no such conditional drift; replay converts these substitutions into wrong-entity SQLite writes. Human judgments support the Preserve/Reevaluate distinction, while audits of public agent benchmarks find few native opportunities to measure it. These results establish TRI as a controlled, model- and controller-conditional diagnosis and support executable transition authorization as a simple design principle, not a prevalence or general-safety claim.

## Keywords

- LLM agents
- tool use
- entity binding
- stateful agents
- agent memory
- diagnostic evaluation
- AI safety and reliability

## Suggested Subject Areas

Use the closest available AAAI-27 categories, in this order:

1. Natural Language Processing: language models / agents.
2. AI and the Web or intelligent agents: tool-using and interactive agents.
3. Evaluation and analysis of AI systems.
4. AI safety, reliability, or trustworthy AI, only as a secondary area; the paper is not a broad safety guarantee.

## One-Sentence Summary

We show that a state refresh can make an LLM agent silently replace a correctly bound action target, and that compiling the user's target commitment before refresh sharply reduces this error in controlled settings.

## Contribution Summary

1. Formal definition of post-binding referent-transition authorization.
2. Frozen Stable/Flip and Preserve/Reevaluate diagnostics with cluster-aware statistics.
3. Independent 240-task replication and wrong-entity SQLite consequences.
4. Component and deterministic-rule analyses showing that executable transition authorization, rather than gating alone or method complexity, explains most of the controlled gain.
5. Human-language validation and public-benchmark opportunity audits that bound external validity.

## Registration Checklist

- Confirm final author order, affiliations, conflicts, and email addresses with all authors.
- Confirm that the title in the submission system exactly matches the LaTeX title.
- Recheck every abstract number against `reports/current_claim_provenance.md`.
- Do not mention Event Graph/M2 as the main method; the 20-task Go/No-Go rejected promotion.
- Do not describe external null results as prevalence evidence.
- Do not call Binding Drift deterministic reverify a learned baseline; it reads a gold target.
- Do not claim CTA is uniquely necessary or an algorithmic contribution; the post-hoc strengthened deterministic rule is competitive and must be disclosed in the full paper.
- Submit the abstract before 2026-07-22 19:59 Beijing time, preferably by noon.
