# Reviewer B Preliminary Assessment (Main Text Only)

## Scope

This preliminary assessment is based only on all eight pages of `paper/AnonymousSubmission2027.pdf`. I have not consulted the supplementary material, reproducibility checklist, code/data artifact, source files, prior reviews, or project history.

## Summary and provisional judgment

The paper introduces Temporal Referent Integrity (TRI), a matched diagnostic for whether a tool-using agent preserves an entity that was committed before a state refresh while reevaluating a selector that was intentionally deferred until after refresh. Preserve/Reevaluate pair members share the state transition, selector, action, and schema but have opposite correct targets when the selector winner changes. The paper proposes changed-winner PairAcc, conditional target substitution after a correct initial binding, and target-level execution traces. It evaluates deterministic policy extremes, several controller packages/representations, three model backends, a 40-task model-facing SQLite subset, human rewrites/labels, source-derived states and schemas, and limited external/compositional audits.

The central diagnostic idea is clear and potentially useful. In particular, the matched design exposes why stable-only or one-sided accuracy cannot distinguish Always-Lock, Always-Reevaluate, and selective policies (pp. 2-3, Table 1, Eq. 4), and the paper follows a target-selection error into model-issued database writes (pp. 5-6, Fig. 4). The manuscript also does an unusually good job of labeling post-primary and post-hoc evidence and stating that conditional substitution is not a prevalence or safety-rate estimate.

My provisional decision is borderline reject. The diagnostic itself is technically plausible and carefully motivated, but the positive controller evidence is still mostly an authored-expression result. The primary comparison is explicitly call-asymmetric and package-level, while the fairer matched-call comparison exposes a composite block after an initial ID has already been supplied (pp. 4-5, Controller Probes and Matched-Call Decision Visibility). Source-derived transfer is model-dependent, native-task evidence is almost entirely null or absent, open-language evidence is too small or unsuccessful, and human construct validation is inconsistent (pp. 4, 6-7). Thus the work currently supports TRI as a controlled unit test more strongly than it supports the broader practical value or validity of the tested intervention.

## Strongest strengths

1. **The evaluation unit directly tests the intended policy distinction.** Stable and one-sided sets can reward unconditional policies; matched changed-winner Preserve/Reevaluate pairs require both behaviors on the same transition (pp. 2-4, Table 1, Eq. 4, Fig. 2). Always-Lock and Always-Reevaluate are the right controls and both score 0/32 PairAcc despite acceptable aggregate/marginal scores.

2. **The paper separates initial grounding, referent replacement, and execution consequence.** Conditional substitution is restricted to correct initial bindings, completed refreshes, changed winners, and still-valid old targets (pp. 2-3). The SQLite test then shows refreshed-winner writes in 8/8 Qwen and 6/8 GLM strict opportunities versus 0/4 stable controls for each model (pp. 5-6, Fig. 4). This is much more diagnostic than reporting final task success alone.

3. **Limitations and evidence status are unusually explicit.** The paper states that the primary package contrast changes both structure and calls, the matched-call block is composite, Rule* is post-hoc, the public-suite retrieval has uncalibrated recall, and native prevalence/open-language generalization remain unresolved (pp. 4-7). These caveats materially improve interpretability.

4. **The baseline and boundary suite is broad for the center claim.** Deterministic extremes, Generic, CTA, Lifecycle, a history reminder, post-hoc Rule*, offline enforcement, model-facing execution, rewrites, source-derived schemas, unseen-schema grounding, two-refresh composition, and repeated passes probe distinct failure modes without wandering far from selective re-resolution (pp. 3-7).

## Main concerns

### 1. Positive evidence does not yet establish broad construct validity or practical prevalence

The strongest gains are on author-designed tasks and author-supplied timing contrasts. Cross-Schema Controlled Replication varies schemas and states but retains authored language templates; source-derived tasks retain author-supplied timing contrasts; volunteer rewrites yield only three complete actionable changed pairs; the model-authored audit yields no complete pair accepted by both judges; and a public-suite audit finds no strict native opportunities under an uncalibrated retrieval process (pp. 6-7, Transfer and Boundary Conditions; External Coverage and Composition; Limitations). The only observed repository substitution signal is 2/7 changed rows for one model/history cell on AgentDojo, with other repository-model cells at zero and no consistent execution improvement (p. 6).

Affected claim: TRI is a useful evaluation diagnostic for tool-using agents beyond the constructed benchmark. Current evidence strongly establishes internal discrimination on a controlled unit-test inventory, but external validity is poor. A publishable version would need either calibrated evidence that native workflows actually instantiate the construct or stronger, independently authored open-language evaluation. Clarification alone cannot repair this evidence gap, although narrowing the paper's practical claims would reduce its severity.

### 2. Human construct evidence is internally inconsistent

The actionable target labels are not uniformly validated. The earlier convenience sample reports 98.0% majority-gold agreement on 50 dynamic items but only 86.7% on 30 anchored actionable items and 55.0% on 20 invalid-target Reject items. More concerning, a separately frozen follow-up missed its eligibility gate and retained-label referent-gold agreement is only 38.6% (p. 4, Construct Scope). The manuscript reasonably separates fallback policy, but the low follow-up agreement raises questions about whether instruction timing reliably determines the prescribed referent for ordinary readers. The one-person rewrite protocol and three-person labeling protocol do not substitute for independent construction of the benchmark (p. 4, Construct and transfer protocols).

Affected claim: the gold distinction represents human-interpretable referential commitment rather than an author-defined formal convention. This is a major construct-validity concern. The current main text acknowledges but does not resolve it. Exact protocol/results may clarify which items failed, but stronger prospective validation would be needed if the disagreement reaches the actionable core.

### 3. The controller evidence does not isolate the claimed mechanism

The frozen primary estimand compares Generic with Lifecycle-Gated, but the latter changes controller structure and call count and skips actor calls on valid Preserve rows (pp. 3-5, Measurements and Denominators; Controller Probes; Primary Package Comparison). The later matched-call test is fairer, but its visible intervention jointly adds predicted mode, bound ID, and selector restatement; it begins after supplying the same initial ID to both actors (pp. 3, 5, Controller Probes; Matched-Call Decision Visibility; p. 7, Limitations). Therefore the reported gains identify the effect of a complete post-binding representation block, not resolution-mode visibility, a lifecycle field, compilation, or any specific controller architecture. Offline enforcement can also harm rows when the compiled decision is wrong (p. 5).

Affected claim: explicit timing representation causes better selective re-resolution. The narrow claim that this complete block improves authored PairAcc for Qwen and GLM is directly tested; stronger field- or architecture-specific interpretations are not. The paper mostly states the narrow version, but title/abstract/conclusion framing still risks readers attributing the effect to timing rather than the bundle. This is partly fixable by sharper wording, but component ablations would be needed to isolate a mechanism.

### 4. Confirmatory strength is weaker than the volume of reported analyses suggests

Only the Qwen all-row package difference is frozen/primary. GLM replication, cross-schema attribution, matched-call contrasts, construct studies, source-derived studies, and external audits are post-primary, and Rule* is post-hoc (p. 4, Evidence Status). The paper reports many bootstrap intervals and McNemar auxiliaries but defines no multiplicity-adjusted confirmatory family for later audits (p. 3, Measurements and Denominators). The central matched-call PairAcc results are encouraging (Qwen 5/32 to 13/32; GLM 8/32 to 25/32), but the numerous secondary slices, shared-eligibility conditioning, post-treatment audits, oracle replacements, and cross-dataset/model comparisons should remain descriptive.

Affected claim: robustness and generality of the intervention effect. The main text is commendably candid, so this is not hidden selective reporting; however, a reader can still mistake the dense collection of intervals for independent confirmatory support. This is substantially fixable by presentation: distinguish one confirmatory result from descriptive diagnostic evidence in the abstract, figures, and conclusion, and avoid significance-like emphasis on unadjusted secondary intervals.

### 5. The metric is useful but benchmark-specific and does not change selection in the studied candidate sets

PairAcc is sensitive to how rows are paired, as the paper notes (p. 3, Measurements and Denominators). It also discards partial success by requiring co-correctness, so its practical value depends on pairing legitimacy and changed-winner coverage. Most importantly, the zero-API selection audit finds that aggregate E2E already selects a PairAcc-optimal candidate in all five studied candidate sets; there is no observed model/controller ranking reversal (p. 4, Policy Discrimination). PairAcc therefore explains policy behavior but has not yet demonstrated that using it changes an actual evaluation decision.

Affected claim: TRI adds decision value beyond standard end-to-end evaluation. The paper supports explanatory and diagnostic value, but not incremental selection value in its candidate sets. The current text resolves this factually and states it in Discussion (p. 6); the issue is mainly one of importance, not correctness. A broader candidate pool or a naturally occurring ranking reversal would strengthen the contribution, but should not be demanded as proof of the formal identifiability point.

## Statistical, leakage, and reproducibility notes to verify in auxiliary materials

- Verify that cluster bootstrap resampling uses the independent state/workflow unit and preserves matched pairs, especially for the 240-row cross-schema data with only 40 state instances (pp. 3, 5).
- Verify exact denominators and exclusions for conditional substitution, shared-eligible analyses, PairAcc, and the SQLite strict opportunities; conditional denominators vary by model/controller and can invite selection effects if not frozen before outcomes (pp. 5-6, Figs. 3-4).
- Verify that task templates, post-hoc Rule* development, human rewrite sampling, source-derived construction, and the unseen-schema stress set are separated against leakage from error inspection (pp. 3-7).
- Verify model identifiers, prompts, parser/scoring rules, randomization, provider settings, raw outputs, hashes, repeat procedure, and all failure accounting. The main paper states these are in the anonymous artifact/supplement but also admits provider weights lack immutable revision identifiers (pp. 4, 7).
- Verify ethics details for consent, compensation, data release, and the absence of a formal review/exemption determination (p. 4).

## Submission-critical writing issues

The manuscript is visually clean and all figures/tables are legible. The writing problem is density, not polish. Pages 3-7 introduce many overlapping controller names, evidence phases, datasets, denominators, and conditioned subsets in rapid succession. A Phase 1 reader can easily lose which comparison is primary, which is fair but post-primary, and which supports only mechanism localization. Figure 2 explicitly mixes primary/frozen Qwen with post-primary GLM and post-hoc Rule* evidence (p. 4), which is transparent in the caption but rhetorically hazardous. The abstract also compresses conditional denominators and controller results before establishing that these are authored, shared-eligible rows. A compact evidence-status table mapping each claim to design, denominator, preregistration status, and scope would materially improve comprehensibility.

## Provisional ratings

- Importance: **Good** - selective re-resolution is a real agent-evaluation blind spot, but native prevalence and evaluation-decision impact are unestablished.
- Novelty: **Good** - the matched opposite-gold timing diagnostic and post-binding substitution endpoint are distinctive, even if built from familiar contrast-set principles.
- Technical Soundness: **Good** - formal definitions and restricted identifiability argument appear coherent, with appropriately limited claims.
- Experimental Rigor: **Fair** - strong controls and execution tracing are offset by a call-asymmetric primary contrast, composite matched-call intervention, small effective cluster counts, and mostly post-primary analyses.
- Construct Validity: **Fair** - the formal construct is crisp, but human validation is mixed and one frozen follow-up is strongly discordant.
- External Validity: **Poor** - positive evidence is mostly authored; native, open-language, and compositional evidence is limited or negative.
- Clarity: **Fair** - polished figures and explicit caveats, but high evidentiary and nomenclature density obscures the main inferential chain.
- Reproducibility: **Fair (pending supplement/checklist)** - the main text promises extensive artifacts, but model revision immutability is unavailable and procedures/denominators require verification.
- Ethics: **Fair** - consent/de-identification are stated, but there was no formal review or exemption determination.

Provisional overall: **5/10 (marginally below acceptance)**. Confidence: **4/5**. Expertise: **4/5**. Provisional recommendation: **Reject**. Deciding factor: the paper convincingly validates an authored diagnostic unit test, but current evidence does not yet validate its construct and intervention broadly enough for the practical tool-agent claims.
