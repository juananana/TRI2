# Reviewer A - Main-Paper-Only Independent Assessment

Evidence boundary: this assessment was written after a complete read of the 8-page main paper, including references, and before opening either the supplementary material or the reproducibility checklist. Page numbers below refer to PDF pages.

## Bottom-line initial judgment

**Initial overall score: 4/10 (weak reject). Phase 1: Reject. Confidence: 4/5.**

The paper isolates a real semantic distinction in stateful tool use and turns it into a clean matched diagnostic. The opposite-gold Preserve/Reevaluate construction, conditional-substitution denominator, and target-to-write trace are technically coherent and unusually careful about what each endpoint does and does not establish. However, the main paper itself substantially undercuts the case for significance and novelty: the strongest results come from authored timing templates; open-language construct evidence is unresolved; native strict opportunities are almost absent in the examined benchmarks; source-derived transfer is model-dependent; and PairAcc never changes the candidate selected by aggregate E2E in the five studied candidate sets. The restricted identifiability claim is also elementary once the three-policy class is fixed, and the relation to the cited Entity Binding and Binding Drift work appears incremental rather than a clearly new technical principle. This is a useful diagnostic artifact, but the current evidence does not yet show that it identifies a practically consequential evaluation failure missed by existing end-to-end evaluation.

## Factual summary

- The paper defines temporal referent integrity (TRI) for a single-refresh workflow in which an action target is either committed before refresh (`bound(e0)`) or selected afterward (`deferred(qr)`) (p. 2, Eqs. 1-2; p. 3, Eq. 3).
- It constructs matched Preserve/Reevaluate tasks sharing states, selector, transition, action, and schema, but changing instruction timing so that changed-winner pairs require opposite targets (pp. 1-3, Fig. 1, Table 1).
- Changed-winner PairAcc scores a pair only when both members are correct; conditional substitution isolates Preserve rows where the initial binding is correct, refresh completes, the winner changes, and the old target remains present and valid (p. 3, Eq. 4 and Observable substitution).
- The core authored inventories are a 160-row Matched Timing Diagnostic (128 actionable plus 32 fallback-policy rows) and a 240-row, ten-schema Cross-Schema Controlled Replication (p. 3, Diagnostic Construction).
- The primary frozen comparison is a call-asymmetric package comparison: Qwen Generic 103/160 versus Lifecycle-Gated 157/160; the later GLM replication is 115/160 versus 160/160 (p. 5, Primary Package Comparison).
- On authored changed-winner pairs, Generic has low PairAcc and CTA has high PairAcc: Fig. 2 reports 3/32 to 7/32 for Generic and 30/32 to 31/32 for CTA; deterministic Always-Lock and Always-Reevaluate both score 0/32 (p. 4, Fig. 2).
- In the 240-task authored cross-schema replication, Generic substitutes the refreshed winner after correct initial binding on 41/66 Qwen, 30/70 GLM, and 50/69 DeepSeek shared-eligible rows; CTA records 0 substitutions (p. 5, Conditional Target Substitution; Fig. 3).
- A 40-task model-facing SQLite test shows the same substitution as a wrong-entity mutation in 8/8 Qwen and 6/8 GLM strict changed opportunities versus 0/4 stable controls for both models (pp. 5-6, Fig. 4).
- Under equal calls and matched base payloads, a composite Decision-visible block improves authored changed-pair PairAcc from 5/32 to 13/32 for Qwen and 8/32 to 25/32 for GLM; actionable E2E changes only modestly for Qwen (100/128 to 106/128) and more for GLM (102/128 to 120/128) (p. 5, Matched-Call Decision Visibility).
- Transfer is limited. On 30 source-derived pairs, only GLM has an actionable E2E interval excluding zero; Qwen is null and DeepSeek crosses zero (p. 6, Source-derived pairs; p. 7, Fig. 5). Rule*, though strong on authored inventories, falls to 2/30 PairAcc source-derived (p. 6).
- Native-opportunity evidence is mostly negative: a 96-task low-intervention extension finds zero substitutions, only one of the STATE-Bench/AgentDojo repository-model cells shows 2/7 substitutions, and an audit of six public suites finds no strict native opportunity, with retrieval recall uncalibrated (p. 6, External Coverage and Composition).
- Human construct evidence is mixed: an earlier convenience sample is strong for some actionable categories, a frozen follow-up has only 38.6% retained eligible agreement, rewrites contain only three complete actionable changed pairs, and a model-authored audit yields no complete pair accepted by both judges (pp. 4, 5, 7).

## Core claim-evidence-strength-gap matrix

| Core claim | Main-paper evidence and location | Evidence strength | Material gap |
|---|---|---|---|
| Stable-only or one-sided tests cannot distinguish selective timing from unconditional locking/reevaluation. | Formal state distinction and three-policy comparison (pp. 2-3, Eqs. 1-4, Table 1); deterministic baselines score 0/32 PairAcc despite strong marginals (p. 4, Fig. 2). | **Strong but narrow.** Correct within the explicitly restricted deterministic exact-target policy class. | The “identifiability” result is nearly definitional after fixing the three policies; stochastic/mixed policies, ambiguity, multi-refresh state, and partial observability are excluded. Matching is not necessary for the cardinality result, as the paper acknowledges (p. 3). |
| Generic controllers overwrite a correct committed referent after refresh. | Conditional substitution on authored cross-schema tasks for three backends (p. 5, Fig. 3), after conditioning on correct initial binding and validity. | **Strong internal diagnostic evidence.** Denominator is well chosen and cross-model pattern is large. | All three backends use the same author-designed controller and authored timing inventory. This establishes susceptibility of that interface, not prevalence in deployed/tool benchmarks. |
| The selection error causes wrong-world actions rather than only scoring disagreement. | Fixed executor maps all authored substitutions to wrong writes; separate 40-task SQLite tool loop shows 8/8 and 6/8 strict changed-opportunity writes (pp. 5-6, Fig. 4). | **Moderate.** The SQLite trace closes the causal chain for the studied interface. | The strict opportunity sample is tiny (8 per model, 4 stable controls) and still author-constructed; fixed replay is essentially deterministic consistency once the wrong target is selected. No demonstrated downstream harm on native tasks. |
| Explicit timing representation improves selective behavior. | Call-asymmetric package gains (p. 5); equal-call Decision-visible composite improves authored PairAcc and GLM E2E (p. 5); CTA yields zero substitutions on shared-eligible authored rows (Fig. 3). | **Moderate for the full composite on authored tasks.** Equal-call comparison addresses one confound. | The intervention bundles predicted mode, bound ID, and selector restatement and begins after an initial ID is supplied. It does not identify which representation component matters, and offline enforcement harms 8 Qwen rows (p. 5). |
| TRI reveals evaluation information missed by aggregate E2E. | PairAcc rejects complementary unconditional policies and shows co-correctness not determined by marginals (pp. 3-4, Eq. 4, Fig. 2). | **Strong as a conceptual possibility.** | In the actual five candidate sets, aggregate E2E always selects a PairAcc-optimal candidate; there is no observed ranking reversal (p. 4, Policy Discrimination). Thus practical added decision value is not demonstrated. |
| TRI transfers beyond authored templates and matters in existing benchmarks. | Source-derived pairs, rewrites, low-intervention extension, repository audit, and public-suite retrieval audit (pp. 5-7, Fig. 5). | **Weak/mixed.** Only source-derived GLM E2E is clearly positive. | Source-derived pairs retain author-written timing contrasts; rewrites have only three complete changed pairs; low-intervention tests are null; six public suites yield no strict native opportunity; retrieval recall is uncalibrated. Native prevalence and open-language generalization remain unresolved by the paper's own account. |
| TRI is a substantively new diagnostic relative to prior binding/state-tracking work. | Related Work distinguishes initial Entity Binding, committed-reference Binding Drift, and timing-variable TRI (p. 2). | **Fair conceptual distinction.** | The novelty appears to be a crossed contrast set plus joint scoring over two already familiar behaviors. The paper does not establish a deeper difference from contrast-set evaluation, binding persistence tests, or event-order-conditioned coreference beyond task construction. Two closest cited works are concurrent preprints, limiting the reader's ability to judge whether this is a significant advance rather than a narrow extension. |

## Decisive issues

### 1. Practical necessity is not demonstrated

**Location:** p. 4, final paragraph of Policy Discrimination; p. 6, External Coverage and Composition; p. 7, Limitations.

The paper motivates PairAcc as detecting failures that aggregate accuracy can miss, but its own zero-API selection audit reports that aggregate E2E selects a PairAcc-optimal candidate in all five candidate sets. The native audit then finds no strict opportunity in six suites, the low-intervention extension is entirely null, and repository evidence is 2/7 in only one cell. These are not merely limitations of breadth: they directly weaken the central claim that current evaluation is making a consequential selection error that TRI fixes. A diagnostic can be valid without high prevalence, but an AAAI main-track paper needs either a stronger theoretical contribution or convincing empirical evidence that the diagnostic changes conclusions. Here, neither is yet present.

### 2. Construct validity and language generalization are unresolved at the center of the task

**Location:** p. 4, Construct Scope; p. 5, Human rewrites; p. 7, first two Limitations paragraphs.

Gold mode is induced by authored instruction phrasing, so the entire task depends on humans agreeing that a phrase commits a referent before refresh or defers it. The frozen follow-up retained-label agreement is only 38.6%; volunteer rewrites contribute only three complete changed pairs; and model-authored language yields no complete pair accepted by both judges. The earlier convenience sample is stronger but protocol-dependent. Consequently, excellent authored-template performance may measure extraction of author-specific event-order cues rather than robust referential reasoning. Rule*'s collapse from more than 90% on authored inventories to 2/30 PairAcc source-derived reinforces this concern. The main paper is admirably candid, but candor does not repair the missing validation.

### 3. Claimed innovation is technically clean but limited and close to existing contrast-set methodology

**Location:** pp. 2-3, Related Work and Restricted identifiability observation; Table 1; Eq. 4.

The formal contribution says that, within `{Always-Lock, Always-Reevaluate, Selective}`, one needs one changed Preserve and one changed Reevaluate case; scoring both jointly rejects the two extremes. This is correct but elementary and follows immediately from the policy definitions. PairAcc is the conjunction of two correctness indicators and is bounded by the marginals in a standard way. Matching controls nuisance content, which is useful experimental design, but the paper explicitly concedes that matching is unnecessary for the cardinality claim. The manuscript does not yet show that “temporal referent integrity” is more than a well-packaged special case of contrast sets/behavioral tests applied to binding timing. The distinction from the paper's cited Binding Drift work is described, but not enough evidence is given in the main text to establish a substantial methodological leap.

### 4. The intervention evidence cannot support a field- or architecture-level conclusion

**Location:** pp. 4-5, Controller Probes and Matched-Call Decision Visibility; p. 6, Discussion; p. 7, Limitations.

The strongest matched-call intervention exposes a composite of predicted mode, bound ID, and selector restatement. This is a legitimate package test, but it cannot identify whether improvement comes from making timing explicit, duplicating the selector, anchoring an ID, or adding another model pass. Further, Decision-enforced repairs some rows but harms eight Qwen rows, and no representation dominates across models/datasets. The paper mostly phrases this carefully, yet its controller framing risks suggesting a representation prescription that the evidence does not isolate.

## Preliminary scoring rationale

- **Technical correctness: 7/10.** Definitions, denominators, matched construction, and endpoint interpretations are mostly careful. The restricted result is correct but weak.
- **Novelty: 4/10.** New name and systematic construction for a narrow timing contrast; limited conceptual distance from binding persistence plus contrast-set evaluation.
- **Significance: 3/10.** No observed selection reversal under aggregate E2E and almost no native opportunity in audited suites.
- **Empirical support: 5/10.** Strong internal authored evidence and a useful executable trace, but weak external/native and human-language support.
- **Clarity: 6/10.** Dense but generally precise; evidence chronology and many controller variants are hard to reconstruct from eight pages.
- **Reproducibility from main paper: 5/10 pending supplement.** The main paper states frozen inventories, interfaces, hashes, and raw outputs exist, but most operational details are deferred.

## Writing and presentation risks

1. **Terminology density may overstate conceptual novelty.** “TRI,” “Lifecycle-Gated,” “Decision-visible,” “Decision-enforced,” “conditional substitution,” “strict opportunity,” and multiple inventories appear quickly. The underlying distinction is simple, but the layered vocabulary makes the work feel more architecturally novel than the formal result supports (pp. 1-5).
2. **Evidence chronology is difficult to audit.** Primary/frozen, later replication, post-primary, post-hoc, secondary/frozen, source-derived, and low-intervention results are interleaved (pp. 4-6). The labels are responsible, but the main narrative does not provide a single table separating confirmatory from exploratory evidence.
3. **Figure 2 mixes evidence statuses.** The caption says package runs mix Qwen primary/frozen and GLM post-primary evidence and Rule* is post-hoc (p. 4). A visually unified ranking invites comparison across results with different status.
4. **Denominators change frequently.** 160 all-row, 128 actionable, 32 changed pairs, 240 cross-schema rows, shared-eligible counts, 40 SQLite tasks, and 30 source pairs are all relevant. Captions usually disclose them, but readers can easily compare conditional and unconditional rates incorrectly (pp. 3-6).
5. **The title and abstract can be read as broader than the evidence.** The demonstrated scope is single-refresh scalar, mostly author-constructed workflows; native prevalence and open-language generalization are unresolved (pp. 1, 7).
6. **Related-work differentiation is asserted more than demonstrated.** The main text gives one paragraph distinguishing initial binding and Binding Drift from timing, but does not provide a concrete side-by-side comparison of inputs, gold labels, intervention, and endpoint (p. 2).

## Main-paper-only questions that could change the judgment

1. Can the authors show at least one realistic benchmark or deployed-style workflow where TRI changes the controller/model selected relative to aggregate E2E, rather than only explaining an already aligned selection?
2. What independent annotation protocol establishes the Preserve/Reevaluate gold mode for naturally occurring instructions, and what agreement is obtained on a sufficiently large set of complete changed-winner pairs?
3. Relative to Binding Drift and general contrast-set evaluation, what theorem, failure class, or empirical conclusion is uniquely enabled by matching and PairAcc beyond simply evaluating both timing orders?
4. In the equal-call study, can predicted mode, bound ID, and selector restatement be ablated factorially so that the timing-specific causal component is identified?
5. How sensitive are PairAcc conclusions to pair construction/re-pairing, given the manuscript's explicit note that marginals do not determine joint correctness and re-pairing changes PairAcc (p. 3)?

## Initial decision

**Reject at Phase 1.** The paper is technically competent and unusually transparent, so this is not a correctness-based rejection. The decisive factor is that the paper has not yet established the necessity or general impact of the proposed diagnostic: aggregate E2E already makes the same selections in the studied candidate sets, native strict opportunities are essentially absent in the audited suites, and construct validity in natural language remains mixed. The supplement could improve confidence in reproducibility and fill operational details, but it would need materially stronger pre-existing evidence on these central points to change the decision.
