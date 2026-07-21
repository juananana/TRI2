# TRI Project Instructions

## Objective

Prepare the AAAI-27 submission on Temporal Referent Integrity (TRI). The paper is a
problem-definition, controlled-diagnostic, and design-principle contribution. Do not turn it
into a broad agent-runtime paper during the submission window.

## Current Main Claim

A world-state update provides evidence about the world but does not by itself authorize changing
an already resolved action referent. Tool-using agents need access to a discourse-sensitive,
executable referent-transition decision. CTA, lifecycle state, and deterministic rules are
implementations of this separation principle.

The evidence supports a controlled, model- and controller-conditional behavioral diagnosis. It
does not establish real-traffic prevalence, universal LLM failure, general tool safety, or the
unique necessity of CTA, an explicit field, or a particular serialization.

## Evidence Status

Always distinguish these categories in prose, tables, and reports:

1. `primary/frozen`: specified before the corresponding full run;
2. `post-primary replication/audit`: completed evidence that was not part of the primary design;
3. `post-hoc`: developed or selected after inspecting relevant outcomes;
4. `planned/unverified`: not evidence and must not be written as a result.

The deterministic discourse rule v2 is explicitly post-hoc and benchmark-aware. Its strong score
narrows algorithmic novelty and cannot support open-language generalization.

## Non-Negotiable Claim Boundaries

- Say that the minimal pair requires authorization information or history, not that a particular
  explicit variable is mathematically necessary.
- Describe `state--authorization confusion` as a behavioral/controller-level diagnosis, never an
  internal model mechanism.
- Do not call the Binding Drift gold-target re-verifier a learned baseline.
- Do not call author adaptations official benchmark or repository results.
- Treat the full-v7 Binding Drift author adaptation as an interface audit, not an
  information-matched CTA baseline: it receives S1 but neither S0 nor the resolved old ID.
- Do not relabel initial binding, selector grounding, tool-order, or protocol errors as TRI.
- Conditional TRI denominators require a correct observable initial binding, a completed refresh,
  a surviving/action-valid old target, and a distinct refreshed winner where applicable.
- Report rejection, invalid attempts, utility, and wrong writes separately. Safety gains obtained
  only by refusing work are not successful task performance.
- Preserve external null results and negative compositional results.

## Experiment Gate

Before any new model/API run:

1. state the claim being tested and the alternative explanation being excluded;
2. freeze the task inventory, prompt, endpoint, metrics, denominator, retry policy, and stopping
   rule in a protocol file;
3. specify which outcomes would strengthen, narrow, or overturn the paper conclusion;
4. run zero-API validation and a bounded smoke test first;
5. retain all attempted rows and count API/parse failures in ITT unless the protocol says otherwise;
6. save raw JSONL, an executable report script, a machine-readable report, and a Markdown report;
7. add the result to `experiments/tri_artifact/reports/current_claim_provenance.md`.

Do not tune prompts or rules on the evaluation set and then describe the result as held out. Do
not start new model experiments after 2026-07-24 except transport repair or validation of a fatal
review concern.

The prospective blind linguistic holdout is NO-GO for the current submission because the required
independent writers and annotators are unavailable. Do not replace them with authors, convenience
samples, or LLM-only paraphrases and call the result independent human evidence.

## Paper Priorities

Main-text evidence must retain: the TRI definition and minimal pair, v3 primary result, v7
replication, complementary Always-Lock/Always-Reevaluate controls, wrong-entity SQLite replay,
human validation, the strong post-hoc rule disclosure, nearest-neighbor distinction, external
coverage/null boundary, and limitations.

Prefer deleting exploratory methods and secondary tables over weakening these items. Keep the
main paper within the AAAI page limit and keep the title, abstract, contributions, results,
discussion, and conclusion at the same claim strength.

## Project Map

- Main paper: `paper/AnonymousSubmission2027.tex`
- Bibliography: `paper/aaai2027.bib`
- Supplement: `paper/supplementary_material.tex`
- Reproducibility checklist: `paper/ReproducibilityChecklist.tex`
- Artifact root: `experiments/tri_artifact/`
- Claim provenance: `experiments/tri_artifact/reports/current_claim_provenance.md`
- Submission plan: `planning/TRI_AAAI27_eight_day_submission_plan_zh.md`
- Abstract registration text: `planning/TRI_AAAI27_abstract_registration_draft.md`

Treat planning documents and internal reviews as decision records, not empirical evidence.

## Validation Commands

Run artifact tests from `experiments/tri_artifact/`:

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/pytest -q tests
```

Build the paper from `paper/`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error AnonymousSubmission2027.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary_material.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error ReproducibilityChecklist.tex
```

Before packaging, run `git diff --check`, scan all archive members for secrets and author identity,
then clean-room extract the anonymous artifact and execute its documented smoke tests.

## Editing Rules

- Preserve user changes and unrelated untracked files.
- Use source-derived tables and scripts; do not hand-copy result numbers when regeneration exists.
- Use primary sources for related-work metadata and record anything not independently checked as
  unverified.
- Keep API keys, private annotation returns, author identities, local environments, and external
  repositories out of submission archives.
- Use ASCII in code and machine-readable artifacts unless existing content requires otherwise.

## Deadlines (Asia/Shanghai)

- Full paper: 2026-07-29 19:59
- Supplement and code: 2026-08-01 19:59
- Internal main-paper freeze: 2026-07-27
