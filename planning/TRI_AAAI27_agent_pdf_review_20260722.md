# TRI AAAI-27 Independent PDF Review

Status: internal decision record; not empirical evidence.

## Review conditions

- Reviewer: independent Codex subagent.
- Materials: anonymous main-paper PDF, supplementary-material PDF, and reproducibility-checklist
  PDF only.
- Excluded: TeX, code, artifact, planning records, claim provenance, and earlier reviews.
- No files were edited by the reviewer.

## Verdict and scores

| Dimension | Score |
|---|---:|
| Significance | 6/10 |
| Novelty | 5/10 |
| Technical soundness | 7/10 |
| Empirical rigor | 8/10 |
| Clarity | 7/10 |
| Reproducibility | 8/10 |
| Overall | **5/10** |
| Confidence | **4/5** |

Predicted Phase-1 verdict: **Borderline / Weak Reject**. The reviewer did not identify a fatal
technical error. The predicted rejection risk comes from uncertain incremental novelty relative
to Binding Drift and uncertain external importance, not from weak experimental care.

## Strongest contributions identified by the reviewer

1. The matched Preserve/Reevaluate changed-winner design makes the target-update policy
   identifiable and rejects both Always-Lock and Always-Reevaluate.
2. Correct observable initial binding, conditional substitution, and SQLite target-level replay
   form an unusually complete attribution chain from target choice to wrong-entity write.
3. Evidence status and unfavorable evidence are disclosed: Rule v2 is post-hoc, the Binding Drift
   adaptation is an interface audit, and the external and compositional negative results remain
   visible.
4. Clustered inference, ITT treatment, denominator separation, and shared-eligible analyses are
   careful.
5. The PDF-level reproducibility description is substantially stronger than average, although the
   reviewer did not execute the artifact.

## Main concerns

### P0/P1 scientific risks

1. **External importance remains unestablished.** The controlled diagnostic is positive, while
   three pinned public suites contain no strict native opportunity under the checklist and the
   lower-intervention studies are null. The evidence cannot distinguish benchmark undercoverage
   from controlled-interface amplification.
2. **The increment over Binding Drift is narrow.** TRI adds the symmetric bound-versus-deferred
   timing contrast and policy-identifying gold, but post-binding drift itself is prior work and the
   formal non-identifiability observation is elementary.
3. **Temporal parsing remains an active account.** Post-hoc Rule v2 scores strongly, so the paper
   must explain that temporal parsing is an upstream realization while the contribution is the
   matched evaluation needed to distinguish selective updating from unconditional policies.
4. **Evidence phases are numerous.** The v3 primary result should remain visibly separate from v7
   replication/audit, post-hoc interpretation, and descriptive coverage results. Internal frozen
   protocols must not be presented as equivalent to external preregistration.
5. **Controller comparisons are not a clean single-factor causal intervention.** CTA changes the
   error structure and can weaken initial binding; it supports a controller probe/realization
   claim, not general controller superiority.

### Secondary limitations

- Human validation is small; rewrites come from one volunteer, and anchored/reject agreement is
  materially weaker than the scalar dynamic contrast.
- Template and workflow diversity is limited despite appropriate cluster analyses.
- The seven-page main paper is dense, and the `Core/all writes` distinction requires careful
  explanation.
- API model revisions are not immutable; raw-output replay is more reproducible than fresh calls.
- The reviewer requested an ethics/exemption sentence if required by the applicable institutional
  policy; no policy claim should be invented without author confirmation.

## Reviewer questions retained for author audit

1. What evidence establishes practical priority when strict public opportunities and
   lower-intervention substitutions are null?
2. Could the strict opportunity checklist miss real referential-integrity errors, and is there an
   independent recall audit?
3. How does the paper distinguish its evaluation contribution from event-order parsing?
4. Why does CTA sometimes reduce v7 initial binding relative to Generic?
5. Should CTA/Gated be read as successful methods or diagnostic probes?
6. What independently verifiable chronology supports the internally frozen protocols?
7. How does the single rewrite author and weaker anchored agreement limit construct validity?
8. What is the minimum implementation-independent executable requirement for a deployed system?

## Prioritized recommendations and disposition

| Recommendation | Disposition for this submission |
|---|---|
| Center the paper on policy-identifying evaluation | Already implemented; preserve |
| Reduce version-by-version narration to primary, replication, strongest alternatives, boundaries | Largely implemented; do not re-expand |
| Explain why temporal parsing does not replace the evaluation claim | Accept as a targeted discussion edit |
| Make the Binding Drift scientific-question boundary explicit | Already implemented in the closest-neighbor table and prose |
| Make external nulls part of the conclusion | Accept as a targeted conclusion edit |
| Add independently authored prospective linguistic holdout | Reject for this submission: planned/unverified and violates the current experiment gate |
| Add a new low-intervention nonzero external run | Reject absent a verified fatal concern and frozen protocol |
| Add an independent public-suite recall audit | Valuable future work, but currently unavailable and must not be implied |

## Score-change conditions from the reviewer

- **6/10:** a simpler main-paper identity centered on policy-identifying evaluation; clear
  Binding Drift and temporal-parsing boundaries; CTA consistently framed as a probe; external
  nulls treated as a conclusion; artifact reconstructs the headline results.
- **7/10:** additionally, a prospectively frozen independently authored holdout not explained by a
  simple rule, or a prospectively specified nonzero low-intervention external replication with an
  independent opportunity audit.
- **4/10 or lower:** artifact reconstruction failure, untrustworthy chronology, unacknowledged
  prior symmetric timing contrast, denominator exclusion, or hiding Rule v2/external/compositional
  negative results.

## Internal decision

The review independently converges with the post-restructure skeptical pass. The current evidence
can plausibly support a 6 when the reviewer values evaluation identifiability; wording alone cannot
make a 7 reliable. The safe remaining changes are to sharpen the temporal-parsing logic and the
two interpretations of the external nulls, then preserve the frozen scientific story.
