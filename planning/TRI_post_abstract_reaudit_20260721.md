# TRI Post-Abstract Re-Audit

Date: 2026-07-21 (Asia/Shanghai)

## Current judgment

The paper is strongest as a problem-definition, controlled-diagnostic, and executable-control
principle paper. The main remaining acceptance risks are external/natural-language validity and
method depth, not the number of models or synthetic tasks.

The full-v7 Binding Drift author adaptation is retained only as an interface audit. It is not an
information-matched baseline because it receives the instruction and refreshed candidates but
neither the initial state nor the resolved old ID. The matched full-history and Generic-ledger
conditions are the valid performance controls.

## Only decision-changing new experiment

Run a prospective blind linguistic holdout only if genuinely new human-authored language can be
collected before the experiment freeze. The experiment tests whether the strong post-hoc rule v2
merely captures inspected vocabulary and whether unchanged CTA provides additional semantic
generalization.

Minimum design:

1. Freeze rule v2 code, CTA prompt, endpoints, metrics, exclusions, and analysis before collection.
2. Recruit at least six independent English-proficient writers, none of whom saw TRI templates,
   rule failures, Preserve/Reevaluate terminology, or model outputs.
3. Each writer produces ten instructions from neutral scenario cards, for at least 60 instructions
   spanning both intended timing orders and at least six domains.
4. Obtain writer intent after instruction submission, then have three separate blind annotators
   choose the intended target. Primary evaluation uses determinate writer intent with at least
   two-of-three annotator agreement; all-item/Clarify sensitivity remains visible.
5. Evaluate frozen rule v2 and frozen CTA without prompt or vocabulary changes. A matched
   full-history condition is optional only if API budget and time remain after human validation.
6. Cluster intervals resample writers and scenario families; do not treat multiple instructions
   from one writer as independent.

Interpretation rules:

- If CTA exceeds rule v2 by at least 10 points and the writer/scenario-cluster interval excludes
  zero while human agreement remains strong, the paper gains evidence for semantic compilation
  beyond the benchmark-aware rule.
- If rule v2 is within 5 points of CTA, retain the paper as a problem/diagnostic contribution and
  make no learned-method generalization claim.
- If both methods fall substantially or human intent is ambiguous, narrow the construct and
  emphasize clarification rather than deterministic authorization recovery.
- Every outcome is retained; no rule or prompt revision is allowed after holdout inspection.

## Go / No-Go

**Go** only if all writers and annotators can be recruited immediately, collection can finish with
time for blind validation, and no author response enters the primary analysis.

**No-Go** if the set would be generated from existing TRI templates, authored by the paper authors,
created only by another LLM, contain fewer than six independent writers, or finish too late for a
clean freeze. In those cases the result would not repair the generalization concern.

### Decision recorded on 2026-07-21

**NO-GO for the current submission.** The required independent writers and annotators cannot be
recruited reliably within the remaining submission window. No author-written substitute, reduced
convenience sample, or LLM-only paraphrase set will be used as evidence of open-language
generalization. The paper retains the existing human-rewrite evidence for CTA and explicitly
labels rule v2 as post-hoc and non-generalizing. Experiments are frozen except for repair of a
verified artifact defect or factual inconsistency.

## Experiments not recommended before submission

- another model from the same endpoint;
- more v3/v7 templated rows;
- a larger ToolSandbox/AppWorld custom intervention after existing null results;
- further prompt tuning of CTA, Lifecycle, or rule v2;
- another complex runtime/controller method;
- expanding the information-mismatched Binding Drift adaptation.

## Remaining non-experimental priorities

1. Primary-source verification of every 2025--2026 related-work citation and metadata entry.
2. Final claim-to-artifact number audit after all paper edits.
3. Rebuild and clean-room test the anonymous artifact.
4. Re-audit the reproducibility checklist against the final text.
5. Run one final skeptical review focused on synthetic construct validity, Binding Drift overlap,
   rule-v2 post-hoc status, and page-limit compliance.

## Completion record (2026-07-21)

- Primary-source metadata audit completed in
  `planning/TRI_related_work_primary_source_audit_20260721.md`; the tau3 entry was corrected to a
  software release and Binding Drift re-verifiers are described as LLM-based, not learned.
- Main-text number audit completed in
  `planning/TRI_final_claim_to_artifact_audit_20260721.md`; no empirical-number discrepancy found.
- Skeptical AAAI review completed in
  `planning/TRI_AAAI_skeptical_review_20260721.md`; judgment remains Borderline/Weak Reject.
- OpenReview abstract updated to disclose the post-hoc 92.5% benchmark-aware rule.
- Main PDF is 7 content pages plus 2 reference pages; supplement is 15 pages; checklist is 2 pages.
- Full scientific tests and clean-room artifact tests passed; final secret, identity, private-file,
  local-path, and whitespace scans passed.
