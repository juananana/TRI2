# TRI AAAI-27 Post-Restructure Skeptical Pass

Status: internal review and freeze recommendation; not empirical evidence.

## Judgment

The revised manuscript now has a coherent evaluation-paper identity and a complete main-text
argument chain. It is plausibly competitive for a score of 6 from reviewers who accept
policy-identifying diagnostics as a substantive AAAI contribution. A score of 7 remains possible
but cannot be made reliable through further wording or opportunistic experiments: it depends on a
reviewer's valuation of the problem relative to Binding Drift and tolerance for controlled rather
than naturalistic evidence.

No remaining existing-evidence P0 scientific defect was found in this pass. The residual risks are
structural and are disclosed rather than rhetorically hidden.

## Closed argument

1. At the refresh boundary, discourse leaves the action target as either a bound commitment
   `B(e0)` or a pending query `U(q)`.
2. Stable and one-sided evaluation regimes cannot identify selective target updating; matched
   changed-winner Preserve/Reevaluate PairAcc rejects both unconditional extremes.
3. Frozen controlled runs isolate refreshed-winner substitution after correct observable binding.
4. Deterministic target-level replay connects the identified substitution to wrong-entity writes
   while keeping non-core errors visible.
5. CTA, Lifecycle, and the post-hoc rule show that the executable decision has non-unique
   realizations; they do not establish a unique architecture.
6. Human validation supports the scalar semantic contrast more strongly than fallback rejection.
7. Public-suite coverage audits and lower-intervention nulls bound opportunity and external
   validity; they do not estimate prevalence.

## Resolved reviewer attacks

| Attack | Resolution in the revised main text |
|---|---|
| "This is just Binding Drift with another lock." | Refresh-boundary `B(e0)` versus `U(q)`, the matched opposite-gold contrast, and the closest-neighbor table state the incremental variable. |
| "The formalism calls deferred resolution a rebind." | Reevaluate is now explicitly the first resolution of a pending query; `Gamma` is reserved for a genuine transition out of an existing binding. |
| "Aggregate improvement is the only result." | Policy-identifiability table, PairAcc, conditional substitution, initial binding, and wrong writes form separate estimands. |
| "Generic's serialization creates the result." | The information-matched full-history and final-step reminder baselines now appear beside the main v7 evidence, including the Qwen tie. |
| "CTA is a simple prompt trick or claimed unique method." | CTA, Lifecycle, and Rule v2 are presented as non-unique probes; Rule v2 is explicitly post-hoc and limits method novelty. |
| "The paper hides adverse evidence in the supplement." | Rule v2, external nulls, composition failure, reject disagreement, non-core writes, and temporal parsing remain in the main text. |
| "The consequence is only a label." | Target-level SQLite replay and the source-validated REM-1A/REM-1B trace close the controlled consequence chain. |

## Residual structural risks

1. Binding Drift already covers correct-binding-then-replacement on the Preserve side; TRI's
   novelty is the symmetric timing variable and evaluation identifiability, not the phenomenon.
2. Lower-intervention external agents are null, so natural incidence and practical prevalence
   remain unknown.
3. The strongest replications are synthetic and post-primary; their status is disclosed.
4. Rule v2 and mode-only gains leave temporal instruction parsing as a live alternative account.
5. Scalar authorization does not compose automatically across referential roles or refresh epochs.

These risks cap confidence but do not expose an internal contradiction. New model families,
template volume, rule tuning, LLM-only paraphrases, or another custom external pilot would not
repair them under the current submission gate.

## Validation observed in this pass

- Main paper compiles to 9 US-Letter pages: 7 content pages and 2 reference-only pages.
- Supplement compiles to 17 pages; standalone reproducibility checklist compiles to 2 pages.
- Main-paper evidence audit passes 10/10 checks.
- Development artifact tests pass 191/191; clean-room archived tests pass 190/190, with the
  packaging-only test intentionally absent from the archive.
- ZIP integrity, source manifest, author-name, secret-pattern, and local-path scans pass.
- `git diff --check` passes.

## Freeze recommendation

Freeze the scientific story after coauthor review. Permit only corrections to facts, evidence
provenance, anonymity, reproducibility, page compliance, and presentation. Do not reopen method
search or model experiments without a verified fatal review concern and the existing experiment
gate.
