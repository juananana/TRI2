# TRI 2025--2026 Related-Work Primary-Source Audit

Audit date: 2026-07-21 (Asia/Shanghai)

Scope: every 2025--2026 entry currently cited by the main paper. Metadata was checked against
the linked primary paper page or official repository, not against a search snippet or secondary
bibliography. Publication status is reported conservatively.

| Key | Verified metadata and status | Primary source | Material overlap with TRI | Material difference / permitted wording |
|---|---|---|---|---|
| `lu2025toolsandbox` | Jiarui Lu et al.; *ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities*; Findings of NAACL 2025, pp. 1160--1183; DOI matches BibTeX. | [ACL Anthology](https://aclanthology.org/2025.findings-naacl.65/) | Stateful, conversational tool execution and state dependencies. | Its official gold does not annotate the post-binding Preserve/Reevaluate contrast. TRI's audit can support only a benchmark-coverage claim, not real-world absence. |
| `barres2025tau2` | Victor Barres, Honghua Dong, Soham Ray, Xujie Si, Karthik Narasimhan; *tau2-Bench: Evaluating Conversational Agents in a Dual-Control Environment*; arXiv:2506.07982, submitted 2025-06-09. | [arXiv](https://arxiv.org/abs/2506.07982) | Dynamic shared world and tool-mediated user/agent coordination. | Primary problem is dual control and communication, not authorization to revise a previously resolved referent. |
| `sierra2026tau3` | Official `tau2-bench` repository release `v1.0.0`, titled *tau3-bench 1.0.0: Voice, Knowledge, Task Quality*, released 2026-03-18. It is a software release, not a single paper with the former synthetic title. | [GitHub release](https://github.com/sierra-research/tau2-bench/releases/tag/v1.0.0) | Expanded dynamic agent benchmark distribution audited by TRI. | Cite as software. Component papers cover voice, knowledge, and task fixes; none is an omnibus tau3 paper establishing TRI labels. BibTeX corrected accordingly. |
| `babu2026entitybinding` | Rahul Suresh Babu, Shashank Indukuri; *Entity Binding Failures in Tool-Augmented Agents*; arXiv:2606.30531, submitted 2026-06-29. | [arXiv](https://arxiv.org/abs/2606.30531) | Wrong-entity actions, confidence-gated binding, clarification, provenance, and completion/safety trade-offs. | Focuses on resolving an entity before action, especially ambiguity and incorrect initial binding. TRI conditions on correct initial binding to isolate later transition authorization. Do not call the problems disjoint. |
| `indukuri2026bindingdrift` | Rahul Suresh Babu, Shashank Indukuri; *Binding Drift in Multi-Step Tool-Augmented Agents*; official companion repository; arXiv link still marked forthcoming on 2026-07-21. | [Official repository](https://github.com/shashank-indukuri/binding-drift) | Direct overlap: silent replacement after a correct step-1 binding, Entity Lock, LLM self/cross re-verification, and propagation analysis. | This is the closest work and substantially covers TRI's Preserve branch. TRI's defensible addition is the matched, symmetric Reevaluate branch and the separation of persistence from user-authorized deferred resolution. Repository re-verifiers are LLM-based, not trained/"learned"; wording corrected. TRI's adapted interface is not information-matched and remains an interface audit only. |
| `uddin2026ledgeragent` | Md Nayem Uddin, Amir Saeidi, Eduardo Blanco, Chitta Baral; *LedgerAgent: Structured State for Policy-Adherent Tool-Calling Agents*; arXiv:2606.20529, submitted 2026-06-18. | [arXiv](https://arxiv.org/abs/2606.20529) | Explicit task-state ledger and policy checks before environment-changing calls. | LedgerAgent targets stale/missing facts and state-dependent policy compliance. A validity/policy contract does not by itself decide whether discourse authorized an old or refreshed entity, but it is a strong structured-state baseline family. |
| `tang2026entitytracking` | Zilu Tang et al.; *Do Language Models Track Entities Across State Changes?*; arXiv:2605.30233; arXiv comments state "ICML main conference 2026, 9 pages." | [arXiv](https://arxiv.org/abs/2605.30233) | Entity state changes and behavioral/mechanistic failure analysis. | Studies how LMs compute evolving entity states in text; TRI assumes both states are available and studies which state is authorized to determine an action referent. ICML status is verified from author-supplied arXiv metadata, not independently from proceedings. |
| `cheng2026temporalblindness` | Yize Cheng et al.; *Your LLM Agents are Temporally Blind: The Misalignment Between Tool Use Decisions and Human Time Perception*; arXiv:2510.23853, v3 dated 2026-04-15. | [arXiv](https://arxiv.org/abs/2510.23853) | Dynamic environments, stale context, and deciding whether to invoke a tool as time passes. | It asks whether/when to refresh or call a tool; TRI asks what a completed refresh is authorized to revise. This is a clean but adjacent distinction. |
| `ji2026clawarena` | Haonian Ji et al.; *ClawArena: Benchmarking AI Agents in Evolving Information Environments*; arXiv:2604.04202, v2 dated 2026-05-16. | [arXiv](https://arxiv.org/abs/2604.04202) | Dynamic belief revision across contradictory, staged, multi-source updates. | Evaluates belief revision and personalization. It does not isolate post-binding referent-transition authority under matched world states. |
| `xu2026evoarena` | Jundong Xu et al.; *EvoArena: Tracking Memory Evolution for Robust LLM Agents in Dynamic Environments*; arXiv:2606.13681, v2 dated 2026-06-17. | [arXiv](https://arxiv.org/abs/2606.13681) | Progressive environment changes and patch-based memory histories. | Targets memory evolution and evidence capture. TRI's narrower question is whether updated evidence may alter a previously resolved target. EvoMem remains a plausible alternative memory architecture, not an implementation-equivalent TRI baseline. |
| `sohail2026bounded` | Sarmad Sohail, Ghufran Haider; *Bounded Autonomy for Enterprise AI: Typed Action Contracts and Consumer-Side Execution*; arXiv:2604.14723, submitted 2026-04-16. | [arXiv](https://arxiv.org/abs/2604.14723) | Typed action contracts, validation, consumer-side enforcement, and wrong-entity mutations. | Its own abstract reports two wrong-entity mutations escaping consumer-contributed layers and requiring disambiguation/confirmation. This supports the distinction between action validity and entity authorization, but TRI must not claim typed contracts generally lack entity controls. |

## Novelty conclusion after primary-source checking

- **New problem:** only partially. Binding Drift already directly identifies post-binding entity
  replacement. TRI's narrower novelty is a symmetric authorization formulation in which Preserve
  and authorized Reevaluate share the same state transition but require opposite targets.
- **New formalization:** modest but defensible if presented as transition authorization plus the
  mode-blind impossibility proposition, not as discovery of entity persistence itself.
- **New method:** weak. CTA, typed lifecycle state, and the post-hoc rule are simple realizations of
  an executable control decision; the rule result explicitly prevents a method-complexity claim.
- **New benchmark/evidence:** controlled diagnostic evidence is the strongest novelty. Its value
  depends on transparent synthetic construction, matched pairs, human semantic validation, strong
  history/state baselines, and explicit external-validity limits.
- **Safe paper wording:** "substantially overlaps Binding Drift's Preserve branch and adds matched
  authorized Reevaluate contrasts". Unsafe wording: "first study of binding drift," "disjoint from
  Binding Drift," or "existing structured-state/runtime methods cannot solve TRI."

## Remaining verification boundary

All titles, author lists, years, identifiers, and repository/release statuses above were checked.
The ICML 2026 status of Tang et al. is supported by its arXiv comments; a proceedings record was not
independently located in this audit. Binding Drift had no live arXiv paper link in its official
repository on the audit date, so claims about its paper beyond the repository artifacts remain
limited to that primary repository.
