# TRI Revision Summary

## Main structural changes

- Reframed TRI as a controlled evaluation-identifiability diagnostic for resolution timing, not a
  prevalence study or a Lifecycle-Gated architecture claim.
- Separated the 128-row actionable referential core from the 32-row author-specified Reject slice.
- Reordered the main evidence around matched opposite-gold diagnosis, substitution and wrong-write
  consequences, equal-call confirmation, controller and rule attribution, source-derived contrasts,
  and language and structural boundary tests.
- Replaced internal `v3`, `v7`, and `Flip` labels in the main text and figures with reader-facing
  experiment names. Internal inventory IDs remain only where needed for artifact provenance.
- Kept primary/frozen, post-primary, post-hoc, and planned/unverified status explicit.

## Added or promoted evidence

- Full-diagnostic equal-call confirmation (post-primary; frozen before own calls):
  - Qwen changed PairAcc: 5/32 to 13/32; actionable E2E: 100/128 to 106/128.
  - GLM changed PairAcc: 8/32 to 25/32; actionable E2E: 102/128 to 120/128.
  - Actionable Preserve substitution: 22/28 to 13/28 and 16/25 to 0/25.
  - Qwen offline enforcement retains 18 repairs and 8 harms.
- Equal-call transfer on 50 existing volunteer rewrites:
  - Qwen actionable E2E is unchanged at 30/40.
  - GLM improves from 31/40 to 39/40.
  - Only three actionable changed pairs are complete; the result is described as model-dependent,
    not open-language validation.
- Frozen post-hoc rule transfer to 30 source-derived pairs: 15/60 target accuracy and 2/30 PairAcc.
- Injected public-audit implementation check: 30/30 known positives scored correctly and 30/30
  one-condition-missing negatives excluded. This checks the deterministic checklist implementation,
  not semantic retrieval recall in natural workflows.
- Source-derived matched-call contrast on 30 changed pairs across three substrates:
  - Qwen PairAcc is 12/30 to 13/30 and actionable E2E remains 39/60.
  - GLM PairAcc is 11/30 to 20/30 and actionable E2E is 37/60 to 48/60.
  - DeepSeek PairAcc is 19/30 to 22/30 and actionable E2E is 45/60 to 47/60.
  - Only the GLM E2E interval excludes zero; all source/model null and adverse slices are retained.
- Concurrent Binding Drift boundary and baseline adaptation:
  - Added the public preprint citation and a formal task-space boundary: its primary carry slot
    corresponds to TRI Preserve, while changed Reevaluate falls outside the fixed-carry assumption.
  - On all 240 actionable Cross-Schema rows, Entity Lock scores 120/120 Preserve and 40/120
    Reevaluate; GLM self-reverification scores 39/120 and 116/120; frozen CTA scores 110/120 and
    116/120. The adaptation is post-primary and not information-matched to CTA.
- Rule*-hard residual audit (post-hoc, zero API):
  - Twenty rows remain after removing Rule*-correct rows, but no complete matched pair remains.
  - Timing-reminder/CTA row accuracy is 13/13 Qwen, 20/20 GLM, and 18/16 DeepSeek, providing no
    residual CTA advantage.

## Corrections and downgraded claims

- Corrected the v2 substitution reports so Reject rows do not enter actionable Preserve
  denominators; v1 reports remain archived.
- Distinguished all wrong-target writes (44/38/60 for Generic) from the conditional TRI subsets
  (43/38/59).
- Restricted human construct support to the scalar Preserve/Reevaluate core; Reject/Clarify/reselect
  remains a separate, weakly supported policy judgment.
- Explicitly states that Rule* is competitive on authored inventories, hard enforcement is mixed,
  and public-suite zero opportunities do not prove systematic benchmark undercoverage.
- The source-derived rule failure does not establish learned-controller superiority.
- Demoted the restricted identifiability proposition to a benchmark-design observation.
- Replaced `source-grounded transfer` with `source-derived controlled contrast` and reduced
  Lifecycle-specific method language.

## Execution note

- The first Qwen source-derived process stopped after a valid 51/60-row prefix. Append-only
  recovery validated the frozen prefix and completed the missing suffix without rerunning old rows;
  all three models now contain 60/60 complete rows.

## Still requiring new evidence

- No new independent people were recruited. The paper therefore does not claim independent open
  language validation or independently calibrated public-suite recall.
- Source-derived contrasts are controlled interventions over source states and schemas, not native
  benchmark tasks or frequency estimates.
- The current working manuscript is 11 pages and still requires final AAAI page compression.
