# AAAI-27 Phase 1 Review - Reviewer B

## 1. Paper Overview

This paper introduces Temporal Referent Integrity (TRI), an evaluation diagnostic for a narrow but consequential ambiguity in tool-using agents: after an environment refresh, should the agent preserve an entity selected before the refresh, or reevaluate a selector whose resolution was deferred until afterward? The benchmark uses matched Preserve/Reevaluate pairs that hold the states, selector, transition, action, and schema fixed while changing the instruction's commitment timing. When the selector winner changes, the pair members have opposite correct targets. The proposed changed-winner PairAcc counts a pair only if both members are correct; conditional substitution further isolates replacement of a correct, still-valid pre-refresh binding by the refreshed winner (main pp. 2-3, Table 1, Eqs. 1-4).

The paper evaluates deterministic Always-Lock and Always-Reevaluate controls, Generic, Compile-then-act (CTA), Lifecycle variants, full-history/reminder baselines, and a post-hoc deterministic rule. It reports a frozen Qwen package comparison, extensive post-primary matched-call and cross-schema tests across Qwen, GLM, and DeepSeek, a 40-task model-facing SQLite test, human labels and rewrites, source-derived and source-anchored adaptations, public-suite opportunity audits, and compositional stress tests. The principal empirical pattern is that an author-designed Generic controller often substitutes the refreshed winner after a correct binding, while CTA-like explicit timing representations largely remove that conditional error on authored tasks. The strongest matched-call test improves changed-winner PairAcc from 5/32 to 13/32 for Qwen and 8/32 to 25/32 for GLM (main p. 5; supplement Sec. 4.2, Table 21). External and human evidence is explicitly mixed.

I recommend **Advance**, narrowly. The controlled diagnostic, policy controls, and execution tracing directly test the center claim, and the submission is unusually candid about evidence chronology and null results. The advance case is for TRI as a well-controlled unit-test diagnostic, not for native prevalence, a unique lifecycle architecture, or broad superiority of explicit records.

## 2. Strongest Strengths

1. **The matched unit directly identifies the claimed behavioral distinction.** Stable or one-sided accuracy cannot distinguish selective behavior from complementary unconditional policies; a changed-winner Preserve/Reevaluate pair can. Always-Lock and Always-Reevaluate both score 0/32 changed PairAcc while succeeding on opposite marginals (main pp. 2-4, Table 1, Fig. 2; supplement Sec. 1.3, Fig. 2). This is a clean control, not merely a relabeling of aggregate accuracy.

2. **The experiments separate grounding, post-binding substitution, and executed consequence.** Conditional substitution requires a correct observable initial ID, completed refresh, changed winner, and a surviving action-valid old target (main pp. 2-3). The model-facing SQLite test then records refreshed-winner writes in 8/8 Qwen and 6/8 GLM strict changed opportunities versus 0/4 stable controls for each model (main pp. 5-6, Fig. 4; supplement Sec. 5, Fig. 7). This directly connects the diagnostic error to state mutation without conflating it with initial selection or tool-order failures.

3. **The baseline and ablation suite is unusually responsive to alternative explanations.** The submission includes policy extremes, ordinary/full-history baselines, a timing reminder, mode-only and validity-only additions, an untyped plan, free versus gated lifecycle use, offline enforcement, a benchmark-aware deterministic rule, fixed-executor replay, and composition tests (supplement Secs. 3-5, Tables 8-26). The full-diagnostic matched-call comparison equalizes calls, base actor payloads, states, schemas, and prompts; only the parsed decision block differs (supplement Sec. 2.3 and Sec. 4.2). These controls show a representation/salience effect without pretending to identify one necessary architecture.

4. **Evidence status, denominators, and negative outcomes are disclosed with exceptional care.** The paper distinguishes primary, post-primary, frozen-before-own-calls, post-hoc, and repaired analyses (main p. 4; supplement Sec. 1.1, Table 1). ITT scoring retains API, parse, and missing-output failures; conditional denominators are shown; cluster units and crossed-dependence sensitivity are given; source-specific null/adverse transfers and failed human/model-language audits remain visible (supplement Secs. 4, 6, 10-12). This transparency substantially limits selective-reporting risk.

## 3. Major Issues

### 3.1 Construct validation is inconsistent across the two human protocols

**Exact problem and location.** The first blind convenience sample supports the dynamic core strongly (98.0% majority-gold on 50 items) but is weaker for anchored actionable items (86.7% on 30; only 63.3% unanimous) and poor for the Reject slice (55.0% on 20) (main p. 4, Construct Scope; supplement Sec. 10, Table 34). More seriously, the separately frozen six-form follow-up fails its eligibility gate: only 11/31 submissions are eligible, no item obtains the planned five labels, eligible referent-gold agreement is 51/132 (38.6%), execution agreement is 34/132 (25.8%), and the all-response sensitivity gives changed-pair accuracy of 3/18 (supplement Sec. 10, Table 35). Median completion is only 330 seconds for 42 response questions, and prohibited assistance/technical issues are common.

**Affected claim.** The formal Preserve/Reevaluate gold corresponds to a stable human interpretation of temporal commitment rather than an author-defined convention.

**Severity category.** Major construct-validity limitation, but not a demonstrated technical error. The earlier blind labels do support the dynamic/actionable core, and re-scoring model outputs against determinate human majorities preserves a Generic-to-compiled gap (supplement Sec. 10, Table 36).

**Fixability by clarification.** Partly. The current paper appropriately excludes fallback policy from the referential core and calls the follow-up a failed-gate audit. Sharper wording can prevent the failed follow-up from being read as validation, but only a prospectively repaired, monitored study could resolve the disagreement.

**Do current materials resolve it?** No. They diagnose and bound it honestly; they do not establish robust human construct validity across protocols.

### 3.2 External validity and incremental evaluation value remain limited

**Exact problem and location.** Positive controller effects are concentrated in authored timing contrasts. Cross-Schema Controlled Replication changes schemas and states but retains authored language/templates (main pp. 5-7; supplement Sec. 4.4). The 30-pair source-derived study still uses author-supplied opposite-gold instructions and yields a clear E2E gain only for GLM; Qwen is null and DeepSeek's interval crosses zero (main p. 6, Fig. 5; supplement Sec. 6.1, Tables 28-29). A 96-task lower-intervention ToolSandbox extension and custom AppWorld study record zero conditional substitutions despite other errors (supplement Secs. 6.2 and 6.5, Table 32). The public-suite audit finds zero strict native opportunities in six suites under an author retrieval procedure with uncalibrated natural recall (main p. 6; supplement Secs. 6.2-6.3, Fig. 9, Table 30). Source-anchored occurrence is limited to 2/7 Qwen ordinary-history AgentDojo rows, with other repository-model cells at zero and no stable record advantage (supplement Sec. 6.4, Table 31). Separately, aggregate E2E already selects a PairAcc-optimal candidate in all five candidate sets, so TRI produces no observed ranking reversal (main p. 4; supplement Sec. 3.4, Table 17).

**Affected claim.** TRI has broad practical value for evaluating tool agents, beyond explaining policy behavior on a constructed unit test.

**Severity category.** Major importance/external-validity limitation. It does not invalidate the controlled diagnostic, but it weakens the case that current public evaluations systematically miss a consequential behavior or that PairAcc changes model/controller selection.

**Fixability by clarification.** Largely for claim scope, not for evidence. The abstract, Discussion, Limitations, and supplement already say native prevalence, recall, and open-language generalization are unresolved. More evidence would be needed to support a stronger practical claim; I do not require an unrelated deployment study for the narrower diagnostic contribution.

**Do current materials resolve it?** No, but they resolve the risk of overclaiming better than most submissions. My advance recommendation depends on reading the contribution as a controlled diagnostic construction.

### 3.3 The intervention evidence identifies a composite representation effect, not a timing field or unique controller mechanism

**Exact problem and location.** The frozen primary estimand compares Generic with Lifecycle-Gated, but the latter changes the record, deterministic gate, and call count, skipping the actor on valid Preserve rows (main pp. 3-5, Measurements and Denominators, Controller Probes, Primary Package Comparison; supplement Secs. 2.1-2.2, Tables 4-5). The better matched-call experiment adds a composite compiler decision containing predicted mode, bound ID, and selector restatement after both actors have already received the same observable initial ID; the supplement confirms that the selector and ID restatements duplicate existing values in 760/760 records (main p. 5; supplement Secs. 2.3 and 4.2, Tables 21-22). The mode-only ablation improves Generic by +10.6 points for Qwen but only +3.1 for GLM with an interval crossing zero; the full typed/free variants do much better (supplement Sec. 3.2). Enforcement repairs and harms Qwen rows and does not consistently improve source transfer (supplement Secs. 4.2-4.3 and 6.1, Fig. 4).

**Affected claim.** Explicit resolution timing itself causes the gain, or Lifecycle/CTA is the uniquely appropriate implementation.

**Severity category.** Major causal-attribution limitation, minor for the paper's narrowest behavioral conclusion. The full block's authored matched-call effect is directly tested; field-specific mediation and architectural necessity are not.

**Fixability by clarification.** Yes for the current claims. The paper should consistently say "complete decision block/representation" rather than using "timing visibility" as shorthand where it invites field-specific interpretation. Component-randomized ablations would be required for causal attribution to individual fields.

**Do current materials resolve it?** Mostly. Main p. 5 and supplement Secs. 3-4 explicitly state observational non-uniqueness and show that Rule* can match the authored inventory. The residual concern is rhetorical framing, not missing awareness.

### 3.4 Confirmatory support is much narrower than the volume of analyses and intervals

**Exact problem and location.** Only the Qwen Generic versus Lifecycle-Gated package comparison is primary/frozen. The GLM replication, matched-call confirmation, cross-schema analyses, human studies, external audits, and most sensitivities are post-primary; Rule* is post-hoc (main p. 4, Evidence Status; supplement Sec. 1.1, Table 1). Secondary intervals are not globally multiplicity-adjusted (main p. 3; supplement Sec. 4). There are also transparently retained analysis/protocol repairs: a selection-regret implementation initially omitted Lifecycle-Gated rows (supplement Sec. 3.4), an early matched-call Qwen smoke exhausted a token cap before thinking was disabled (Sec. 4.3), and the model-authored audit required a frozen exact-ID parser repair after an all-zero normalization result (Sec. 12). The primary interval's original resampling axis is one of two crossed factors; a later two-way pigeonhole sensitivity remains positive but was designed after the primary result (supplement Secs. 4-4.1, Table 20).

**Affected claim.** The many reported effects constitute convergent confirmatory evidence for a general intervention benefit.

**Severity category.** Moderate-to-major statistical interpretation risk, not evidence of concealed selective reporting. The frozen primary package effect is large, ITT-complete, and robust to the disclosed crossed sensitivity; the post-primary matched-call effects should remain descriptive/replicative.

**Fixability by clarification.** Yes. A single claim-evidence table in the main paper should distinguish the one confirmatory package claim, frozen-before-own-calls replications, exploratory intervals, post-hoc baselines, and repaired audits. Avoid significance-like prose for unadjusted secondary families.

**Do current materials resolve it?** Substantially. Supplement Table 1 and the checklist's item 4.12 are explicit, but the eight-page main presentation still makes the evidence volume easy to overread.

## 4. Minor Issues

- PairAcc depends on frozen pairing and is not determined by marginals; the paper notes that re-pairing can change it (main p. 3, Eq. 4). The supplement should state whether every reported bootstrap draw preserves complete pairs before resampling clusters; the described state/template clustering strongly suggests yes but does not always say so adjacent to each table.
- The primary inventory's effective repeated construction units are 20 language-template clusters, not 160 independent tasks (supplement Sec. 4). Main-text result prose should foreground cluster counts when quoting tight-looking row denominators.
- Figure 2 in the main paper combines Qwen primary/frozen, GLM post-primary, and post-hoc Rule* results. The caption discloses this, but a Phase 1 reader may still read the rows as one contemporaneous comparison (main p. 4, Fig. 2).
- "Initial binding" sometimes means a compiler output and elsewhere an observable selector/tool event. The distinction matters because ordinary full-history baselines cannot support the same conditional substitution estimand (supplement Sec. 4.5, Table 26).
- Exact provider weight revisions, inference seeds, and serving hardware are unavailable, so raw-output analysis is reproducible more strongly than live API inference (main p. 7; supplement Sec. 13; checklist 4.7-4.8).
- The human study had informed consent and de-identified release, but recruitment channel, prior relationship, exact honoraria, completion times for the first study, and language background were not recorded; no formal review/exemption determination was obtained (main p. 4; supplement Sec. 10).

### Submission-Critical Writing Failures

The paper is visually clean and figures are legible, but the evidence architecture is too dense for an eight-page Phase 1 read. Pages 3-7 rapidly introduce Generic, CTA, Lifecycle-free/Gated, History-only, Decision-visible/enforced, Timing-reminder, Rule*, fixed replay, SQLite, authored, rewrite, source-derived, source-anchored, native, and compositional results with different denominators and evidence statuses. This is not cosmetic: it obscures which result tests discrimination, which localizes mechanism, which measures execution, and which supports transfer. Figure 2's mixed chronology and Figure 5's two endpoints intensify the problem (main pp. 4 and 7). The paper needs one compact claim-to-evidence table in the main text and more literal labels such as "authored composite-block effect". Without that restructuring, careful caveats are present but too easy to miss.

## 5. Questions

1. Would the authors explicitly define their acceptance-level claim as "TRI is a controlled diagnostic that identifies selective re-resolution on constructed matched pairs," rather than a claim about native opportunity prevalence or controller superiority? This scope determines whether I remain at Advance.
2. What prospective human-validation result would the authors regard as falsifying the actionable Preserve/Reevaluate gold, and will the failed six-form follow-up be repaired with monitored recruitment before using human validity as a headline claim (supplement Sec. 10, Table 35)?
3. Can the authors provide, in the main paper, the matched-call effect of the mode field alone versus the full decision block for both models and state unambiguously that the latter does not isolate a field-specific mechanism (supplement Secs. 3.2 and 4.2)?
4. For every PairAcc interval, does cluster resampling preserve complete pair membership and all crossed rows within the sampled construction unit? A concise algorithmic statement would remove the remaining uncertainty about dependence handling (supplement Secs. 4-4.4).

## 6. Ratings

- **Importance: Good.** Selective re-resolution is a meaningful evaluation blind spot, though native frequency and model-selection impact are not established.
- **Novelty: Good.** The matched opposite-gold timing unit, changed-winner PairAcc, and conditional post-binding substitution endpoint form a distinctive diagnostic contribution built on contrast-set principles.
- **Technical Soundness: Good.** The restricted identifiability statement is correct for its stated deterministic exact-target policy class, and the empirical endpoints align with the formal distinction.
- **Experimental Rigor: Good.** Strong controls, ITT accounting, matched-call studies, execution traces, cluster-aware intervals, and negative results outweigh the narrow primary estimand and extensive post-primary family.
- **Construct Validity: Fair.** The first blind study supports the actionable core, but the failed follow-up and model-authored judge disagreement leave substantial uncertainty.
- **External Validity: Poor.** Positive evidence is mainly authored; native, open-language, and low-intervention occurrence is limited, null, or unresolved.
- **Clarity: Fair.** Local explanations and graphics are polished, but controller/evidence/denominator density makes the global inferential chain difficult to recover.
- **Reproducibility: Good.** The supplement specifies prompts, parsers, seeds, ITT rules, cluster units, hashes, model IDs, settings, and artifact structure; exact live API replay is limited by immutable provider revision and seed availability.
- **Ethics: Fair.** The study is low-risk and reports consent/de-identification, but lacks formal review/exemption and complete recruitment/compensation metadata, and the follow-up has serious eligibility/comprehension problems.

## 7. Overall Recommendation

- **Overall score: 6/10**
- **Confidence: 4/5**
- **Expertise: 4/5**
- **Recommendation: Advance**
- **Deciding factor:** The matched diagnostic, deterministic policy controls, matched-call actor comparison, and model-facing write traces directly establish the narrow center claim under controlled conditions. The recommendation would change to Reject if the work were framed as evidence of native prevalence, broad open-language validity, or a uniquely effective lifecycle controller; the current manuscript mostly avoids those claims and exposes its negative boundaries.
