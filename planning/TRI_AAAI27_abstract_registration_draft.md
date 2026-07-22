# AAAI-27 Abstract Registration Draft

**Status:** current-manuscript candidate, not evidence that the OpenReview registration has been
updated. If an abstract has already been registered, compare it with this text before changing
anything: AAAI warns against substantial abstract changes after registration. Use the registered
abstract as the submission-system source of truth and seek workflow-chair guidance for any
material change.

## Title

Temporal Referent Integrity: A Controlled Diagnostic for Referential Re-resolution in Tool-Using Agents

## Short Title

Temporal Referent Integrity in Tool-Using Agents

## Abstract

Refreshing external state does not by itself license a tool-using agent to change the entity denoted by an earlier reference. Post-binding target drift has been documented; our contribution is an instruction-timing-controlled evaluation variable that distinguishes legitimate deferred resolution from discourse-inconsistent substitution. We formalize this distinction as temporal referent integrity (TRI). Identifying it requires an eligible opportunity, an observable initial binding, and a Preserve/Reevaluate contrast; observing the executed mutation is additionally required to establish a wrong-entity consequence. On frozen v3/v7 diagnostics, Always-Lock and Always-Reevaluate both score 100% on Stable controls but zero changed-winner PairAcc, whereas Generic controllers selectively substitute the refreshed winner after correct binding. In replayed Qwen/GLM v7 outputs, all 43 and 38 eligible substitutions, respectively, become wrong-entity SQLite writes. CTA reduces this specific drift but does not solve all target errors and is not the unique implementation. Public audits find zero strict native opportunities in the three audited suites, and the controlled failure does not reproduce in our lower-intervention external agents. TRI is therefore a controlled, model- and controller-conditional diagnosis of an evaluation gap in these regimes, not a natural prevalence estimate or a universal controller claim. A workflow-grounded task grammar makes the required selector, refresh, and mutation opportunity explicit.

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
