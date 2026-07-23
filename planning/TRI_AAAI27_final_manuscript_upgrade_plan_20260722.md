# TRI AAAI-27 Final Manuscript Upgrade Plan

Status: active submission plan and internal decision record; not empirical evidence.

## Objective

Raise the paper from a collection of controlled agent results to a closed evaluation argument:

> Tool-agent evaluation cannot identify selective referential updating unless it distinguishes a
> referent already resolved before refresh from a selector intentionally left unresolved until
> afterward, observes the initial binding when claiming post-binding substitution, and observes
> the mutation target when claiming a wrong-entity consequence.

The paper remains a problem-definition, controlled-diagnostic, and design-principle contribution.
It will not become a general runtime architecture paper, a prevalence study, or a claim that CTA,
Lifecycle, an explicit field, or a particular serialization is uniquely necessary.

## Frozen submission identity

- Registered title: `Temporal Referent Integrity: A Controlled Diagnostic of Referential
  Resolution Timing in Tool-Using Agents`
- Primary topic: `ML: Evaluation, Benchmarking, Datasets & Analysis`
- Main contribution: policy-identifying evaluation of instruction-conditioned resolution timing.
- Empirical scope: frozen v3 primary; frozen post-primary v7 replications; deterministic SQLite
  consequences; human construct validation; non-unique controller/rule probes; scoped public-suite
  coverage and lower-intervention nulls.
- No new model/API experiment is planned. A new run requires the existing experiment gate and a
  verified fatal review concern.

## Argument chain

1. **Semantic state at refresh.** The instruction leaves the action-target reference either as a
   bound commitment `B(e0)` or as an unresolved query `U(q)`.
2. **Evaluation identifiability.** Stable or one-sided tasks cannot distinguish Always-Lock from
   Always-Reevaluate. Matched changed-winner Preserve/Reevaluate pairs can.
3. **Controlled behavior.** Tested Generic controllers sometimes substitute the refreshed winner
   after a correct observable initial binding; other target errors remain separate.
4. **Executed consequence.** Deterministic target-level replay maps the identified substitutions
   to wrong-entity writes while retaining all non-core errors.
5. **Implementation boundary.** CTA, typed Lifecycle state, and a post-hoc deterministic rule are
   non-unique realizations of an executable discourse-sensitive decision.
6. **External boundary.** Three pinned public suites lack strict native opportunities under the
   checklist, and lower-intervention external agents are null. This establishes undercoverage and
   limits external claims; it does not estimate prevalence.

## Work packages and acceptance checks

### WP1: Identity and formal core

- Synchronize the registered title and abstract across main paper, supplement, and submission
  decision records.
- Define refresh-boundary status as `B(e0)` versus `U(q)`; do not describe the Reevaluate member as
  a transition away from an already bound referent.
- Define the authorized target separately from action validity/fallback.
- Retain the implementation-independent transition-authorization principle for genuine changes to
  an existing bound commitment.

Acceptance: the minimal pair, equations, contribution bullets, abstract, and conclusion use the
same semantic object and do not imply that a particular explicit variable is necessary.

### WP2: Policy-identifying evaluation

- Make observational equivalence on Stable tasks and complementary failure on one-sided tasks the
  main evaluation result.
- Keep changed-winner PairAcc, conditional substitution, initial binding, and executed writes as
  distinct estimands.
- Replace method-centered headings with intervention/probe language.

Acceptance: a skeptical reader can reconstruct why aggregate, Stable-only, Preserve-only, and
Reevaluate-only scores are insufficient without consulting the supplement.

### WP3: Empirical closure

- Keep v3 primary status and v7 post-primary replication status adjacent to their results.
- Move the information-matched full-history and TRI-aware baselines close to the Generic/CTA
  comparison; state the Qwen tie and denominator difference.
- Keep Rule v2, external nulls, composition failures, rejection, invalid attempts, utility, and
  non-core writes visible.

Acceptance: every positive claim has its strongest fair baseline and strongest relevant negative
result nearby; no denominator or evidence-status reconstruction is required.

### WP4: Evidence boundary and closest neighbor

- Present Binding Drift as covering the shared correct-binding-then-replacement phenomenon.
- State TRI's increment as the matched resolved-versus-deferred timing variable and the evaluation
  conditions needed to distinguish legitimate deferred resolution from substitution.
- Scope public-suite results to three pinned versions and the documented checklist; do not imply an
  independent recall audit.

Acceptance: title, abstract, contributions, related work, discussion, and conclusion all make the
same novelty and external-validity claim.

### WP5: Submission validation

- Regenerate source-derived tables/figures and run the main-paper evidence audit.
- Compile main paper, supplement, and checklist.
- Confirm 7 content pages plus at most 2 reference pages; inspect figures/tables for legibility and
  overlap.
- Run artifact tests, `git diff --check`, anonymous-package scans, and clean-room smoke tests.

Acceptance: all commands pass; PDFs are readable; claims agree with provenance; no private or
identifying material enters the submission archives.

## Stop conditions

Stop changing the scientific story when WP1--WP4 are satisfied. Further work is limited to factual,
reproducibility, anonymity, page-budget, or presentation defects. Do not reopen Event Graph,
R-SSA, rule tuning, opportunistic external pilots, or LLM-only language holdouts for this submission.
