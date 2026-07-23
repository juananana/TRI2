# TRI AAAI-27 External GPT PDF Review

Status: internal decision record; not empirical evidence.

## Review conditions

- Reviewer: an external ChatGPT session with no prior review supplied.
- Materials transmitted: anonymous main-paper PDF, supplementary-material PDF, and
  reproducibility-checklist PDF only.
- Excluded: TeX, code, artifact ZIP, internal plans, claim provenance, author identity, and the
  independent Codex-agent review.
- Requested format: strict AAAI-27 Phase-1 review in Chinese with evidence-stage distinctions,
  score, confidence, verdict, and separate existing-evidence versus new-evidence recommendations.

## Verdict

- Overall: **5/10 (borderline, leaning Weak Reject)**.
- Confidence: **4/5**.
- Phase-1 prediction: **leaning not to advance, but close to the boundary**.

The reviewer considered the diagnostic variable clear and useful and the experimental discipline
above average. The score was capped by narrow novelty relative to Binding Drift,
controlled-interface dependence, and null public/lower-intervention evidence. It estimated that an
area chair who values benchmark identifiability could assign 6, whereas a reviewer emphasizing
external occurrence or method novelty could assign 4.

## Evidence-stage reading

| Status | Reviewer's reading |
|---|---|
| Primary/frozen | v3 160-task inventory; Qwen Lifecycle-Gated minus Generic is the primary pre-specified estimand; GLM is same-inventory replication |
| Frozen secondary | v3 CTA/Lifecycle-free/component probes and 40-task model-facing SQLite execution checks |
| Post-primary replication/audit | v7 new-schema/state runs, DeepSeek, identifiability reanalysis, full-history baseline, repeats, rewrites, composition, external audits, and Binding Drift adaptation |
| Post-hoc | Rule v2, strict audit of the 24-task ToolSandbox pilot, selected qualitative cases, and failure-driven analyses |
| Planned/unverified | Natural-traffic prevalence, general multi-step composition, and artifact execution not available to this PDF-only reviewer |

The reviewer credited the disclosure but warned that dense mixing of phases could make the body of
confirmatory evidence appear broader than it is.

## Strongest contributions

1. Matched Preserve/Reevaluate members share state, selector, and action while requiring opposite
   targets, excluding both Always-Lock and Always-Reevaluate more cleanly than one-sided scoring.
2. Correct initial binding, conditional substitution, final target, and executed write are kept as
   separate estimands; pre-binding tool-order failures are not relabeled as TRI.
3. Negative evidence is retained: external `0/24` and `0/28`, zero substitution in the frozen
   96-task extension, adverse composition, and post-hoc Rule v2 near CTA.
4. SQLite replay links wrong target choice to wrong-entity mutation rather than stopping at text
   classification.
5. Cluster bootstrap, ITT handling, and denominator reporting are broadly appropriate.
6. The paper avoids prevalence, universal-failure, and uniquely necessary CTA claims.

## Major concerns

1. **External validity and practical importance.** The strongest positive results are controlled,
   while public strict opportunities and lower-intervention substitutions are null. The evidence
   cannot distinguish public-benchmark undercoverage from amplification by the controlled interface.
2. **Narrow increment over Binding Drift.** The matched deferred-resolution contrast is real, but
   may be judged as a contrast-set extension of a known post-binding drift problem rather than a
   new general agent problem or strong theory contribution.
3. **Controller/interface conditionality.** CTA/Lifecycle can deterministically execute an already
   compiled decision while Generic permits model-mediated re-inference. Full-history controls help,
   but Qwen CTA nearly ties the aware baseline and external nulls remain.
4. **Construct validity outside the dynamic core.** Dynamic agreement is strong, anchored
   actionable agreement moderate, and anchored Reject agreement weak. The primary E2E estimate
   includes 32 author-specified Reject items; actionable-core results deserve interpretive priority.
5. **Potential numerical inconsistencies.** The reviewer observed a `Q-Gen 0` PairAcc label in the
   compact main figure versus the source-supported `3/32 = 9.4%`, and two Qwen bootstrap intervals
   (`[18.1, 50.0]` versus `[18.7, 49.4]`) generated with different Monte Carlo seeds. These were
   flagged for source-level audit rather than accepted without verification.
6. **Method reliability is scoped.** Qwen v7 CTA/Gated PairAcc remains low, non-core errors persist,
   and scalar Lifecycle loses to Generic in one composition test. Zero core substitution does not
   imply task success or general safety.

## Dimension scores

| Dimension | Score |
|---|---:|
| Technical reliability | 7/10 |
| Experimental rigor | 7/10 |
| Construct validity | 5/10 |
| External validity | 3/10 |
| Reproducibility from the PDFs alone | 6/10 |

The reproducibility score is PDF-only: the external reviewer did not receive or execute the
artifact and therefore could not verify its tests or reconstruction scripts.

## Recommendations using existing evidence

1. Correct any figure/interval inconsistency from the machine-readable reports.
2. Keep the primary identity as a controlled policy-identifiability diagnostic, not a general
   CTA/Lifecycle method paper.
3. Give actionable-core results interpretive priority while retaining the pre-specified E2E result.
4. Keep evidence phases visible and avoid implying external preregistration.
5. Preserve external nulls and adverse composition in the main argument.
6. State that temporal parsing, referential control, and controller serialization are not fully
   separated by current evidence.
7. Keep the Binding Drift boundary focused on the new variable and identifiable conclusion.
8. Ensure checklist statements agree with the actual final submission package.

## Recommendations requiring new evidence

- A prospectively frozen positive result in a truly low-intervention, independently sourced
  workflow.
- Independently authored natural-language tasks, especially anchored actionable cases.
- Independent double annotation or executable recall validation of the public-suite opportunity audit.
- Frozen Rule/CTA evaluation on wholly new vocabulary, templates, and domains.
- Replication across different planning, memory, and execution architectures.
- Confirmatory multi-target, multi-role, or multi-refresh evidence if a broader method claim is kept.

These are future evidence needs. They are not current results and are not authorized new runs under
the submission experiment gate.

## Internal disposition

The external review independently converges with the Codex-agent review on the 5/10 risk profile:
the paper is technically careful, but its acceptance probability depends on whether reviewers value
policy-identifying evaluation without external positive incidence. Its unique actionable discovery
was the numerical-presentation audit. The compact figure label was a genuine hard-coded stale value;
the bootstrap intervals came from separate seeds and should not both be presented as the same
primary interval. Both are repaired from source or clarified in the supplement.
