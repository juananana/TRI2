# LLM-Assisted Public-Benchmark Coverage Reproducibility Protocol

**Status:** planned/unverified, zero-API framework. This protocol does not create an
independent external confirmation, an independent human review, or a new empirical result.
It must not be described in the paper as such.

## Purpose and Boundary

The released public-coverage audit currently reports a narrow, source-bound conclusion: the
audited versions of ToolSandbox, AppWorld, and tau3-bench contain zero strict native TRI
opportunities under the frozen definition. This framework permits a language model to locate
candidate passages in already frozen source audits. It does not permit a model to establish
facts about a benchmark, to replace an independent reviewer, or to revise that conclusion.

An LLM may be used only as a retrieval and structured-extraction aid. The LLM output must be
retained verbatim with provider, model identifier, prompt SHA-256, output SHA-256, date, and
the exact frozen source file hash. It must be labeled `candidate_labels`, never `review` or
`adjudication`.

## Frozen Inputs

The template binds one closest-case record per benchmark to the following reports and hashes:

- ToolSandbox: `reports/official_toolsandbox_tri_prevalence_audit.json`
- AppWorld: `reports/appworld_public_trace_tri_audit.json`
- tau3-bench: `reports/official_tau3_native_tri_audit.json`

Before any assisted extraction, run
`scripts/validate_llm_assisted_coverage_audit.py` on the blank template. A hash mismatch
invalidates the template until its source change is documented and independently re-reviewed.

## Rubric

For each closest case, assess only these frozen feature labels: stable entity ID, observable
pre-refresh binding, independent post-binding transition, competing same-role entity, changed
selector winner, old target remains actionable, later target mutation, and evaluable authorized
target. Each suggested label must be `yes`, `no`, or `partial`, with a source locator and a
quoted passage. `Partial` is not a strict opportunity.

The strict label requires all features, plus a correct observable initial binding, a completed
refresh, a surviving/action-valid old target, and a distinct refreshed winner where applicable.
The LLM must not infer an omitted fact from a benchmark description or from another benchmark.

## Human Review and Reporting

Two qualified human reviewers who were not the LLM system must independently inspect the
frozen source and the upstream released material. They record their own labels and rationale
without seeing each other's labels; an adjudicator resolves disagreements. Reviewers must state
whether they contributed to TRI task/rule construction. A reviewer who did cannot be represented
as independent for the external-confirmation claim.

The blank template supplied with this artifact is intentionally incomplete: it has no LLM output,
human review, or adjudication. It is therefore `non_evidence`. Do not list LLM agents as authors,
independent annotators, or independent reviewers, and do not conceal material LLM assistance if
the framework is ever used in a submitted artifact or report. Existing public-coverage results
remain unchanged unless a separately documented human-led audit changes them.
