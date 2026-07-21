# AAAI-27 Abstract Registration Draft

## Title

Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents

## Short Title

Temporal Referent Integrity in Tool-Using Agents

## Abstract

Refreshing external state does not by itself authorize a tool-using agent to change the entity denoted by an earlier reference. We formalize this post-binding problem as temporal referent integrity (TRI), separating belief updates from referent transitions. On a frozen 160-task diagnostic, a Generic Structured Ledger reaches 64.4%/71.9% with Qwen3.5-122B/GLM-5.1, whereas pre-refresh Compile-then-act reaches 95.0%/96.2%. Always-Lock and Always-Reevaluate each reach 60.0% and fail opposite modes. In a separately frozen 240-task replication, conditional on correct initial binding, Generic drifts on 43/72 and 38/80 opportunities; Compile-then-act and Lifecycle-Gated drift on none, and all 81 Generic drifts replay as wrong-entity SQLite writes. A post-primary DeepSeek replication finds 59/79 versus 0/70 Generic/Compile-then-act drifts. A typed Lifecycle reaches 98.1%/100.0% on the primary set, but its gate adds only 1.2--1.9 points over a matched free actor. Three blind annotators obtain Fleiss' kappa=.708 and 86% majority-gold agreement on 100 original/rewrite items. Native public benchmark opportunities are rare; a post-hoc strict audit of a frozen ToolSandbox-compatible intervention finds 3/6 GLM Generic violations, while lower-intervention external loops are null. TRI is therefore a controlled, model- and controller-conditional mechanism diagnosis, not a prevalence or safety claim.

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
4. Mechanism decomposition showing that pre-refresh commitment compilation, rather than gating alone, explains most of the gain.
5. Human-language validation and public-benchmark opportunity audits that bound external validity.

## Registration Checklist

- Confirm final author order, affiliations, conflicts, and email addresses with all authors.
- Confirm that the title in the submission system exactly matches the LaTeX title.
- Recheck every abstract number against `reports/current_claim_provenance.md`.
- Do not mention Event Graph/M2 as the main method; the 20-task Go/No-Go rejected promotion.
- Do not describe external null results as prevalence evidence.
- Do not call Binding Drift deterministic reverify a learned baseline; it reads a gold target.
- Submit the abstract before 2026-07-22 19:59 Beijing time, preferably by noon.
