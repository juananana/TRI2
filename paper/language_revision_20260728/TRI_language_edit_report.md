# TRI English Language Proofreading Report

## Scope and result

The review covered the title, abstract, all main-paper sections, captions, tables, mathematical
prose, footnotes, the full supplementary material, the included external-transfer table, the
reproducibility checklist, and bibliography formatting. The checklist questions and verbatim prompt
blocks were left unchanged.

- 60 source-level edit groups: 58 language/consistency edits and 2 ethics-status updates.
- Language categories: grammar 13; naturalness 12; long-sentence/readability 13; terminology 7;
  abbreviations 7; reference clarity 2; AI-like or inflated phrasing 4.
- Most edits occurred in the supplementary protocol/results sections, the human-agreement audit,
  and the external-boundary sections. In the main paper, Related Work, the formal definition,
  RQ4, and Limitations changed most.
- No technical definition, mathematical symbol, algorithm, experiment, evidence status, result,
  denominator, citation key, label, or cross-reference was changed.
- No experimental numeric value was changed. One written number, “one candidate,” was standardized
  to “1 candidate” without changing its value.
- The two obsolete ethics disclosures were replaced with the confirmed anonymous statement:
  “The study was reviewed by the authors' institution and determined to be exempt.”

## Recorded substantive edits

Pure source reflow and minor punctuation changes are omitted from this table.

| 位置 | 原文 | 修改后 | 问题类型 | 修改原因 |
| -- | -- | -- | -- | -- |
| Main, Abstract | `We / introduce temporal referent integrity` | `We introduce temporal referent integrity` | Naturalness | Removed an unnatural sentence break. |
| Main, Introduction | One line carried substitution, replication, and SQLite evidence | Split into three sentences | Long sentence | Separated the diagnostic, replication, and execution evidence without changing their relation. |
| Main, Related Work | `Coreference and entity-tracking work studies` | `Research on coreference and entity tracking studies` | Grammar | Corrected the malformed subject phrase. |
| Main, Related Work | `which representation is the action allowed to resolve` | `which representation may be used to resolve the action reference` | Naturalness | Made the grammatical object and permission relation explicit. |
| Main, Definition | Repeated `fallback-policy slice` in adjacent sentences | One definition covering non-actionable rows | Clarity | Removed duplicate wording while preserving the fallback boundary. |
| Main, PairAcc prose | `$A_P$ and $A_R$ ... use the same ... pairs` | `the quantities ... are computed over the same ... pairs` | Grammar | The quantities do not themselves “use” pairs. |
| Main, risk reporting | `unnecessary rejection` | `unnecessary rejections` | Grammar | Restored plural parallelism in the list. |
| Main, Figure 2 caption | `A changed-winner pair fixes ...` | `holds ... fixed` | Naturalness | Used the standard experimental-control collocation. |
| Main, human protocol | `No formal institutional review ... was obtained` | Institution reviewed the study and determined it exempt | Ethics status | Synchronized the manuscript with the newly confirmed exemption. |
| Main, human rewrites | Three results and a scope limit in one sentence chain | Split the scope limit into its own sentence | Long sentence | Kept the negative transfer boundary visible. |
| Main, public adaptations | `Qwen is null` | `the Qwen estimate is null` | Grammar | A model is not itself a statistical estimate. |
| Main, Discussion | `it need not reverse every ranking` | `the diagnostic need not reverse every ranking` | Reference clarity | Removed an ambiguous pronoun. |
| Main, Limitations | Two independent limitations joined in one sentence | Split into two sentences | Long sentence | Separated richer-state needs from scalar non-composition. |
| Main, RQ2 | First `CI` used without expansion | `confidence interval (CI)` | Abbreviation | Defined the abbreviation at first use. |
| Supplement, protocol | `pre-/post-refresh` | `pre- and post-refresh` | Naturalness | Used standard coordinated-modifier form. |
| Supplement, chronology | First `CTA` used without expansion | `Compile-then-act (CTA)` | Abbreviation | Made the supplement independently readable. |
| Supplement, chronology | `two model judges jointly validate no complete pair` | `no complete pair is accepted by both model judges` | Grammar/clarity | Removed an ungrammatical negative construction. |
| Supplement, evidence table | `Blind labels and independent rewrites` | `Blinded labels and volunteer rewrites` | Terminology | Used the correct adjective and avoided implying independent open-language evidence. |
| Supplement, controller table | `Lifecycle free` | `Lifecycle-free` | Terminology | Unified the condition name. |
| Supplement, interface | `byte-canonical History-only payload` | `byte-identical History-only payload` | Terminology | Matched the actual equality claim and main-paper wording. |
| Supplement, pair caption | `opposite gold target` | `opposite gold targets` | Grammar | Two pair members have two targets. |
| Supplement, Binding Drift | First `LLM` used without expansion | `large language model (LLM)` | Abbreviation | Defined the abbreviation in the standalone supplement. |
| Supplement, policy caption | `re-evaluation` | `reevaluation` | Terminology | Unified spelling with the paper while retaining `Reevaluate` as the condition name. |
| Supplement, identifiability | Markdown-style single backticks | Standard LaTeX quotation marks | Typesetting | Corrected quotation syntax. |
| Supplement, matched-call protocol | `identical ... state, tool schema` | `identical ... states, tool schemas` | Grammar | Matched the plural payload objects. |
| Supplement, replication setup | One overloaded 240-task inventory sentence | Three shorter clauses/sentences | Long sentence | Clarified schema, instance, and balancing information. |
| Supplement, baseline protocol | Protocol timing and baseline definition on one long line | Split after the protocol sentence | Long sentence | Improved reading rhythm without changing chronology. |
| Supplement, qualitative cases | `They demonstrate` | `They show` | AI-like/strength | Removed an unnecessary strong reporting verb. |
| Supplement, recall triage | First `BFCL` used without expansion | `Berkeley Function Calling Leaderboard (BFCL)` | Abbreviation | Defined the dataset/software name at first use. |
| Supplement, recall triage | Completed audit used `labels` | `labeled` | Tense | Matched the completed evidence status. |
| Supplement, AppWorld audit | `The Agent selects` | `The agent selects` | Capitalization | Treated “agent” as a common noun. |
| Supplement, tau3 audit | `At current ... commit` | `At the current ... commit` | Article | Added the required article. |
| Supplement, coverage | `can make these benchmarks unable` | `means that these benchmarks may be unable` | Naturalness | Removed an unnatural causative construction while retaining uncertainty. |
| Supplement, candidate labels | `contain 25 and one candidates` | `contain 25 and 1 candidate, respectively` | Grammar | Corrected number agreement and mapping. |
| Supplement, source transfer | Source sentence broken after the repository name | Joined and reflowed | Readability | Kept the compound source name together. |
| Supplement, AppWorld setup | Omitted repeated verb in the Stable/Flip parallelism | Added `adds` and parallel commas | Parallelism | Made the two branches grammatically parallel. |
| Supplement, composition | First sentence carried inventory size and four components | Split into two sentences | Long sentence | Reduced clause load. |
| Supplement, method-upgrade result | Multiple method-status and oracle claims in one sentence chain | Split into four sentences | Long sentence | Separated method selection from executor evidence. |
| Supplement, subsampling | `We additionally subsample` | `We subsample` | AI-like/filler | Removed an unnecessary transition adverb. |
| Supplement, repeat audit | `Before repeat calls` | `Before the repeat calls` | Article | Added the required determiner. |
| Supplement, human audit | Obsolete no-review statement | Institution reviewed the study and determined it exempt | Ethics status | Synchronized the supplement with the confirmed exemption. |
| Supplement, agreement audit | Analysis-script sentence attached to the interpretation | Split into a new sentence/line | Long sentence | Separated interpretation from artifact availability. |
| Supplement, follow-up | `required no ... and no technical issue` | `required respondents to report no ... and no ... issue` | Grammar | Made the reporting requirement explicit. |
| Supplement, follow-up | `Completion time has median` | `The median completion time is` | Grammar | Corrected the statistical collocation. |
| Supplement, follow-up | `needed, / distributed ...` | One continuous sentence | Readability | Removed an awkward sentence break. |
| Supplement, rewrite results | Error-count and error-type clauses on one line | Split and reflowed | Long sentence | Kept the negative errors easy to parse. |
| Supplement, matched-call transfer | Completed calls described in present tense | `completed` | Tense | Matched the completed run. |
| Supplement, model-authored audit | `Before calls` | `Before the calls` | Article | Added the required article. |
| Supplement, model judges | `prevents a jointly validated PairAcc sensitivity` | Explicitly states that no complete pair was accepted by both judges | Clarity | Grounded the limitation in the reported acceptance condition. |
| Supplement, transport repair | `is labeled post-primary transport-repaired` | `with a post-primary, transport-repaired evidence status` | Naturalness | Corrected an awkward evidence-status construction. |
| Supplement, transport repair | `intended open-language objection` | `open-language concern` | AI-like/naturalness | Removed argumentative wording. |
| Supplement, artifact map | Long inventory sentence | Split and reflowed | Long sentence | Improved scanability without changing listed files. |
| Supplement, AI disclosure | Pronoun stranded on a new line | Joined with its predicate | Reference clarity | Kept the antecedent and pronoun together. |
| Supplement, provenance | Settings and per-row metadata joined by a semicolon | Split into two sentences | Long sentence | Separated inference settings from stored provenance. |
| Supplement, chronology | First `PairAcc` used without expansion | `Pair accuracy (PairAcc)` | Abbreviation | Defined the metric before later uses. |
| Supplement, metric definition | `intention to treat` not tied to later `ITT` | `intention-to-treat (ITT) scoring` | Abbreviation/terminology | Defined and standardized the term. |
| Supplement, selection audit | First `E2E` used without expansion | `end-to-end (E2E) accuracy` | Abbreviation | Defined the metric in the standalone supplement. |
| Supplement, replication result | First `CI` used without expansion | `confidence interval (CI)` | Abbreviation | Defined the statistical abbreviation. |

## Validation

- Main paper compiled successfully: 8 pages; pages 1--7 contain the paper body and page 8 contains references only.
- Supplement compiled successfully: 33 pages.
- Reproducibility checklist compiled successfully: 2 pages.
- All PDFs are US Letter. All fonts are embedded; no Type 3 fonts are present.
- No fatal LaTeX errors, undefined citations/references, or overfull boxes were reported.
- Existing underfull warnings occur in narrow table cells and long monospaced paths; visual review found no clipping or overlap.
- Every page of all three PDFs was rendered and visually reviewed.
- Four focused audit files passed: 14 tests passed.
- `git diff --check` passed for the edited manuscript and audit files.

