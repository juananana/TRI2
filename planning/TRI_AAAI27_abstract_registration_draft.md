# AAAI-27 Abstract Registration Draft

**Status:** submitted to OpenReview on 2026-07-22 (Asia/Shanghai). This record is a decision log,
not empirical evidence. The registered title and abstract are the submission-system source of
truth; do not make a material change before the full-paper deadline.

## Title

Temporal Referent Integrity: A Controlled Diagnostic of Referential Resolution Timing in Tool-Using Agents

## Short Title

Temporal Referent Integrity in Tool-Using Agents

## Registered TL;DR

Matched Preserve/Reevaluate pairs distinguish legitimate deferred resolution from discourse-inconsistent post-binding substitution, exposing a controlled evaluation gap in tool-using agents.

## Abstract

Refreshing external state does not by itself authorize a tool-using agent to change the entity denoted by an earlier reference. Prior work documents post-binding target drift, but evaluations that do not control resolution timing cannot distinguish cases in which a target is resolved before an update and should be preserved from cases in which its resolution is intentionally deferred until afterward. We formalize this instruction-conditioned distinction as temporal referent integrity (TRI) and introduce matched Preserve/Reevaluate tasks that hold the states, selector, action, and transition fixed while requiring opposite targets. Identifying discourse-inconsistent substitution requires an observable correct initial binding; establishing its consequence additionally requires a target-level mutation outcome. In a frozen primary diagnostic and frozen post-primary replications covering three model families, Always-Lock and Always-Reevaluate both pass Stable controls but fail changed-winner pairs, while Generic controllers often replace a correctly bound, still-valid target with the refreshed selector winner. Deterministic SQLite replay turns these observed substitutions into wrong-entity writes. Compile-then-act reduces this specific behavior, but the evidence does not identify a unique implementation. Audits of three pinned public agent benchmarks find no strict native opportunities under our checklist, and lower-intervention external agents do not reproduce the controlled failure. TRI therefore identifies a controlled benchmark-identifiability gap and controller-conditional behavior, not natural prevalence or universal agent failure.

## Full-Paper Chronology Clarification

The registered abstract above remains the submission-system record. The manuscript makes one
non-material chronology clarification, replacing ``a frozen primary diagnostic and frozen
post-primary replications'' with:

> In a pre-specified v3 controller comparison, followed by a post-primary diagnostic reanalysis
> and frozen v7 replications across three model families, ...

This does not change the paper's problem, methods, results, or scope. It prevents the registered
wording from being read as a claim that PairAcc, identifiability, or selection regret was the
original v3 primary estimand.

## Keywords

- LLM agents
- tool use
- entity binding
- stateful agents
- agent memory
- diagnostic evaluation
- AI safety and reliability

## Suggested Subject Areas

Registered topics:

1. Primary: `ML: Evaluation, Benchmarking, Datasets & Analysis`.
2. Secondary: `MAS: LLM-based Agents & Agentic Systems`.
3. Secondary: `MAS: Tool Use, Orchestration & Multi-Agent Coordination for LLMs`.
4. Secondary: `NLP: Semantics, Textual Inference & Discourse`.

## One-Sentence Summary

We show that authorization contrasts are needed to distinguish a legitimate deferred selector evaluation from an unauthorized replacement of an already resolved action target.

## Contribution Summary

1. Authorization-controlled evaluation requirements and a matched Preserve/Reevaluate diagnostic.
2. Frozen v3/v7 controller-conditional substitutions and wrong-entity SQLite consequences.
3. Identifiability controls, implementation probes, human validation, and public-suite coverage/null boundaries that constrain interpretation.

## Registration Checklist

- Confirm final author order, affiliations, conflicts, and email addresses with all authors.
- Confirm that the title in the submission system exactly matches the LaTeX title.
- Recheck every abstract number against `reports/current_claim_provenance.md`.
- Do not mention Event Graph/M2 as the main method; the 20-task Go/No-Go rejected promotion.
- Do not describe external null results as prevalence evidence.
- Do not call Binding Drift deterministic reverify a learned baseline; it reads a gold target.
- Do not claim CTA is uniquely necessary or an algorithmic contribution; the post-hoc strengthened deterministic rule is competitive and must be disclosed in the full paper.
- Before final PDF submission, compare the registered OpenReview title and abstract with the
  manuscript. Do not make a material abstract rewrite merely to match this candidate text.
