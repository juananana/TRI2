# Current Paper-Facing Experiment Registry

This registry separates experimental design from result interpretation. It complements
`current_claim_provenance.md`, which maps each claim to exact frozen data, raw outputs, reports,
and code. Evidence labels use the manuscript's four statuses: `primary/frozen`, `post-primary
replication/audit`, `post-hoc`, and `planned/unverified`.

## Registry

| Experiment | Research question and contrast | Inventory and estimand | Inclusion / failure rule | Evidence status | Supported claim and boundary |
|---|---|---|---|---|---|
| v3 package comparison | Does the complete Lifecycle-Gated controller outperform Generic Structured Ledger? | 160 tasks, 20 pre-specified language-template analysis clusters; Qwen primary and GLM replication; E2E and cluster-bootstrap difference | Complete inventory; final API/parse failures are incorrect; no task deletion | `primary/frozen` | Estimates the complete controller-package effect. It does not isolate mode, typing, pre-refresh timing, or gating. |
| v3 component addenda | Which package components explain the contrast? | Same v3 inventory; validity-only gate, Lifecycle-free, mode-only, untyped plan, and exact historical CTA | Each addendum uses its frozen protocol; zero-API derived cells and new-call cells remain distinct | `post-primary replication/audit`; frozen before each addendum's own calls | Associates the gain with an executable discourse-sensitive transition decision; cannot be relabeled as primary causal decomposition. |
| v7 core replication | Does conditional refreshed-winner substitution recur on new states and schemas? | 240 tasks, 10 new schemas, 40 state clusters; Qwen, GLM, DeepSeek; E2E, changed PairAcc, and conditional substitution | Conditional denominator requires correct observable initial ID, completed refresh, surviving action-valid old target, and a distinct refreshed winner; ITT for E2E | `post-primary replication/audit`; frozen before calls | Supports model- and controller-conditional substitution in the controlled interface, not natural prevalence. |
| PairAcc / identifiability / shared eligibility | Do aggregate, Stable, or one-sided scores identify selective authorization? | Frozen v3/v7 outputs; changed PairAcc, marginal scores, and same-task Generic/CTA eligibility | Missing/API/parse/protocol rows are incorrect; shared denominator requires both controllers to bind correctly | `post-primary replication/audit`; zero API | Matched changed-winner PairAcc rejects both policy extremes. Shared eligibility removes controller-specific denominator selection only. |
| Evaluation-selection regret | Can a proxy evaluation license a worse tested policy? | Five frozen dataset/model candidate sets; all exact maximizers under four proxy regimes | Candidate set is limited to tested controllers plus two deterministic extremes; all ties retained | `post-primary replication/audit`; zero API | A proxy can license a zero-PairAcc maximizer. Worst-case tie regret is not a prediction of actual developer choice. |
| 40-task model-facing SQLite | Do model target decisions reach an actual mutation boundary? | 40 frozen tasks; Qwen and later GLM; final state, wrong write, invalid attempt, rejection, collateral change | Every query, refresh, proposal, mutation, and final diff is retained | Secondary frozen execution test; GLM is a later replication | Stronger execution evidence: models issue tool mutations. It remains controller-orchestrated, not an autonomous external benchmark. |
| v7 deterministic SQLite replay | What database consequence follows from each frozen v7 target output? | Frozen Generic/CTA outputs; deterministic in-memory mutation | No new model calls; every source row is replayed and non-core writes remain visible | `post-primary replication/audit`; zero API | Verifies that observed core substitutions map to wrong-entity writes; not a new behavioral or external replication. |
| Matched full-history baselines | Is the finding confined to Generic ledger serialization? | 240 v7 tasks; ordinary and final-step-aware history for three model families; CTA as matched comparison | Full-history methods have no separately scorable pre-refresh ID, so their replacements are unconditional rather than conditional TRI | `post-primary replication/audit`; protocol frozen before its own calls | Shows the result is not confined to one ledger, while Qwen aware history nearly ties CTA and causal mechanism remains unresolved. |
| Blind human construct validation | Do people recover the scalar Preserve/Reevaluate targets? | Three labels per 100 randomized original/rewrite items | All responses retained; determinate, unanimous, Clarify, and Reject slices reported separately | `post-primary replication/audit` | Supports the scalar core. Weak Reject agreement prevents treating fallback policy as equally validated semantics. |
| Human-rewrite model replication | Does the controller pattern survive volunteer rewriting? | 50 volunteer rewrites; unchanged four controllers and two models | Dataset and prompts frozen before the first rewrite-model response; complete ITT inventory | `post-primary replication/audit`; frozen before own calls | Supports transfer to adaptations of authored tasks, not independent natural-request elicitation or open-language generalization. |
| Deterministic Rule v2 | Can a simple event-order rule solve much of the controlled task? | v3, 50 rewrites, and v7; E2E and PairAcc | Built after inspecting Rule v1 failures; benchmark event vocabulary is disclosed | `post-hoc` | Limits algorithmic novelty and supports the separation principle; cannot establish unrestricted discourse generalization. |
| 24-task ToolSandbox-compatible pilot | Can the diagnosis appear on a stateful external-style tool substrate? | Custom 24-task intervention; post-hoc strict Preserve/Flip opportunity audit | Correct compiled ID, present old target, changed winner, and no protocol error required | Strict audit is `post-hoc` | Small positive bridge evidence only; not an official ToolSandbox score, confirmatory effect, or prevalence estimate. |
| 96-task ToolSandbox-style extension | Does lower-intervention behavior reproduce the controlled mechanism? | Four paper-facing conditions: Qwen/GLM full history and matched Generic; opportunities 70/73/64/87 | Correct, timely, observable binding and completed refresh; upstream wrong writes remain separate | `post-primary replication/audit` | All four have zero conditional substitutions; argues against universality, not against the controlled diagnosis. |
| Qwen state-observed sensitivity | What happens under an additional unmatched Qwen interface? | 96 rows; 73 opportunities; 6 wrong writes; 13 prohibited-schema/process errors | Retained as run, not pooled with the four matched conditions | `post-primary replication/audit`, exploratory/secondary | Transparency-only sensitivity evidence. It is not paper-facing evidence and does not strengthen the four-condition zero result. |
| Pinned public-suite coverage audits | Do the audited released tasks expose strict native opportunities? | ToolSandbox 129 families, AppWorld 244 families, tau3 2,449 tasks and released traces | Checklist applied to pinned versions; near-matches and exclusions retained | `post-primary replication/audit`; descriptive, zero API | Zero strict opportunities under the checklist in these versions. No independent recall estimate, other-benchmark claim, or prevalence inference. |
| Multi-refresh / role composition | Does scalar lifecycle state compose across epochs and referential roles? | v5 Qwen stress and v6 scalar-vs-role addendum | ITT retains transport failures; recovered GLM is sensitivity only | `post-primary replication/audit`; role repairs follow observed scalar failure | Scalar lifecycle does not compose automatically. Role indexing is promising but lacks stable cross-model superiority. |

## Active Alternative Explanations

- The controlled tasks may substantially measure temporal-order parsing followed by reliable
  execution. Perfect v3 mode prediction and strong post-hoc Rule v2 performance keep this
  explanation active.
- Public-suite zero opportunities may reflect benchmark undercoverage, missed opportunities in the
  author checklist, or a controlled-interface amplification effect. Current evidence cannot choose
  among them.
- Conditional substitution isolates one specific refreshed-winner error. PairAcc, E2E, initial
  binding, Stable errors, all wrong writes, and rejection must remain visible because zero
  conditional substitution is not general task success.

## Planned but Unverified

- Independent public-suite opportunity-recall audit;
- independently authored natural-request, ordinary-agent, real-tool holdout;
- larger frozen role-indexed multi-refresh evaluation.

These are not current-submission evidence. The external-confirmation gate remains No-Go because
the required independent writers and annotators are unavailable.
