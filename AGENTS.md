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

## Fit-First Use of External Material

- Before using anything supplied to the project--including writing templates, example papers,
  reviewer suggestions, checklists, figures, prompts, or experimental recipes--first judge
  whether it fits TRI's contribution type, current evidence, claim boundaries, venue, and
  submission stage.
- Record or state the fit decision when it affects the manuscript: adopt, adapt, or reject, with
  a brief reason. Do not mechanically apply generic top-conference advice merely because it is
  presented as a standard pattern.
- For introduction advice in particular, TRI may use a clear funnel from the practical referent
  problem to the state--authorization distinction, evidence, and bounded contributions. It must
  not be forced into an algorithm-paper template built around an allegedly exhaustive taxonomy,
  a manufactured ``triple challenge,'' a multi-module novelty story, or SOTA-style claims.
- Prefer structures appropriate to a problem-definition and controlled-diagnostic paper: define
  the concrete failure, distinguish it from the closest neighboring problem, explain why the
  distinction is identifiable, summarize the diagnostic evidence and adverse boundaries, and
  state contributions at their actual evidentiary strength.

## Paper Writing And Page Budget

These rules apply to every edit of the main paper, supplement, abstract, figure, table, and
rebuttal-facing explanation.

### Scope and Closure

- The main paper is a diagnostic/evaluation paper. Describe CTA, Lifecycle, gates, and rules as
  controller probes or operational realizations, not as a general runtime architecture or the
  paper's unique algorithmic contribution.
- Keep one visible argument chain in the main text: authorization contrast and identifiability
  requirement -> matched diagnostic -> controlled conditional behavior -> executed consequence
  -> implementation and external boundaries. Do not require a reviewer to infer a missing link
  from the supplement.
- Every abstract claim, contribution bullet, table caption, discussion claim, and conclusion
  sentence must have the same scope and an identifiable supporting result. Remove a claim when
  its necessary evidence is only planned, only post-hoc, or only described informally.
- State the closest-neighbor boundary early: TRI does not claim to discover post-binding drift;
  it evaluates whether a re-resolution was authorized. Do not recover novelty through broader or
  more dramatic wording.
- Preserve unfavorable evidence in the main-text logic: Rule v2, full-history baseline, external
  nulls, and negative composition results narrow the claim rather than becoming footnotes.

### Conceptual Figure Roles

- Figure 1 is the problem-definition figure: it introduces unauthorized re-resolution with a
  concrete shared-refresh example. Do not force it to carry the later scoring or controller audit.
- Figure 2 is the diagnostic-workflow figure: it connects the shared transition, matched
  Preserve/Reevaluate pair, same probe interface, PairAcc, conditional substitution, and executed
  state diff. It is not a controller architecture or a claim about an internal model mechanism.
- Figure 2 must show what is fixed within a pair, that the old target remains action-valid, and
  which slice each readout measures. It must not expose gold information as controller input or
  contain model results, percentages, confidence intervals, or a preferred implementation.
- When both Figure 2 and the claim-to-evidence table remain in the main text, keep the diagnostic
  figure compact enough that the body still occupies at most seven pages excluding references.
- Adapt Figure 1's palette and semantic icon language, but do not copy decorative clouds, cartoon
  agents, or redundant prose into the method figure. Preserve solid/dashed and textual redundancy
  so the two referent paths remain distinguishable in grayscale.

### Page Budget and Main/Supplement Split

- The AAAI main body is at most **7 pages excluding references**. The current target is a
  9-page PDF with 7 body pages and 2 reference pages. Any edit that risks moving references past
  page 8 must be offset by a deletion or compression in the body.
- The main paper must retain the definition/minimal pair, closest-neighbor boundary, primary and
  v7 evidence, identifiability controls, write consequence, strongest baseline and adverse
  external result, and limitations. These are not supplement-only material.
- Put exhaustive component matrices, full intervals, protocol mechanics, raw examples, secondary
  transfer results, and exploratory method variants in the supplement. Do not move a result out
  of the main text merely because it weakens the preferred interpretation.
- Each main-text figure or table must answer one review-critical question. Prefer a compact
  evidence-boundary table or explanatory figure to decorative architecture diagrams or repeated
  metric tables. Captions must name both the result and its scope.

### Experiment Selection and Reporting

- Add an experiment only when it tests a named claim, excludes a concrete alternative
  explanation, or repairs a review-critical validity risk. Do not add models, templates, schemas,
  or ablations merely to increase count.
- Before presenting a result, distinguish end-to-end success, initial binding, conditional TRI,
  tool order, rejection, invalid attempt, wrong write, and API/parse failure. Do not merge their
  denominators or relabel non-TRI errors as TRI.
- Report the strongest fair baseline and the strongest negative result near the corresponding
  positive result. A table must make the comparison and denominator clear without requiring a
  reader to reconstruct it from prose.
- Treat LLM-assisted authoring, reviewing, extraction, or paraphrasing as engineering assistance,
  not independent human evidence. Anonymous reporting may omit contributor names, but it must
  retain private provenance and must not conceal material assistance or invent independence.

### Clear, Human Academic Prose

- Write direct, concrete academic prose. Start with the claim or observation, then give the
  evidence and boundary. Prefer short, specific sentences over stacked abstractions or long lists
  of qualifications.
- Avoid generic AI-style framing such as repeated ``we propose'', ``novel'', ``comprehensive'',
  ``crucially'', or inflated claims of safety, generality, and first discovery. Do not manufacture
  a personal voice, rhetorical suspense, or certainty unsupported by the data.
- Use a concrete workflow example when introducing an abstract distinction; explain technical
  terms at first use; use the same names for the same estimands throughout. Avoid synonym churn,
  redundant restatement, dense percentage dumps in the abstract, and headings that merely restate
  the section title.
- Keep caveats adjacent to the claim they qualify. State limitations plainly once in the relevant
  result/discussion and summarize them in Limitations; do not repeat defensive disclaimers in
  every paragraph.
- Before finalizing text, read it as a skeptical reviewer: it should sound like an accountable
  research argument, not a generated sales pitch. Delete filler, unsupported intensifiers, and
  sentences that do not advance the definition, evidence, comparison, or boundary.

### Required Final Pass

After a substantive paper edit: compile the main paper and supplement, confirm that the main PDF
remains 7 body pages plus references, inspect figures/tables for legibility and non-overlap, run
`git diff --check`, and verify that no title/abstract/contribution claim exceeds the evidence
status recorded in claim provenance.

### Anonymous Artifact Packaging Cadence

- `paper/supplementary_material.pdf` is the supplementary-material document. The separate
  `submission/tri_anonymous_artifact_current.zip` is the anonymous reproducibility artifact
  containing code, data, frozen runs, report scripts, paper sources, and figure sources.
- Do not rebuild the ZIP after every manuscript or figure edit. While the paper is still moving,
  update the source, tests, required-member assertions, and provenance records, but treat the
  existing ZIP only as a checkpoint.
- Rebuild the submission ZIP once after the main paper, supplement, checklist, figures, and audit
  reports are frozen, then perform the clean-room extraction, archived test run, manifest check,
  and secret/identity/private-data scan. Rebuild earlier only for an explicit packaging checkpoint
  or a packaging-specific failure.
- Because the full-paper deadline is 2026-07-29 and the supplement/code deadline is 2026-08-01,
  begin final artifact reconciliation on the afternoon of 2026-07-29. Until then, prioritize the
  manuscript logic, evidence consistency, and final PDF presentation over repeatedly compressing
  an immediately stale archive.

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

## Repository Authorization

- The user authorizes routine, reversible read and write operations throughout this repository.
- Do not ask again before edits within this repository.
- Continue to preserve unrelated changes and exclude private human-study material from commits.
