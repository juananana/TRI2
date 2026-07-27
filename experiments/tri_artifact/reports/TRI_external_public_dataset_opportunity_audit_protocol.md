# External Public-Dataset TRI Opportunity Audit Protocol

**Frozen:** 2026-07-24, before downloading or inspecting the three new source inventories.
**Evidence status:** planned/unverified until the zero-API reports are generated.
**API status:** no model/API call is authorized by this protocol before the Go/No-Go gate below.

## Claim and Alternative Explanation

The audit tests whether independently released multi-turn tool datasets contain structurally
eligible native TRI opportunities or enough executable workflow clusters for a source-anchored
matched contrast. It excludes the alternative explanation that all apparent external support is
created by the TRI generator or by selecting examples after model outcomes are known.

This audit does **not** estimate natural prevalence unless retrieval recall is separately
calibrated. A source-anchored contrast does not become a native benchmark result.

## Frozen Source Inventory

The inventory is exhaustive over the following pinned repository subsets; commit hashes and
file hashes will be recorded immediately after download and before content classification.

1. BFCL, commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`: all official multi-turn test cases, function documents, executable app state/config,
   and possible-answer files in a shallow checkout of
   `https://github.com/ShishirPatil/gorilla.git`.
2. ToolTalk, commit `e05f4ce6132c80ed33392b81535b077d56ab28fd`: all released easy/hard dialogue/task files, tool/plugin definitions, databases,
   and reference answers in a shallow checkout of
   `https://github.com/microsoft/ToolTalk.git`.
3. API-Bank author Hugging Face release, commit `12e8158b7628c168f07e8f31fbbe3445e99f44cf`: all files under the released dataset's `test-data`
   inventory from `https://huggingface.co/datasets/liminghao1630/API-Bank`.

Training data are excluded from the paper-facing native-opportunity count because API-Bank's
training set is LLM-generated. If retained for parser testing, it must be reported separately.

No source unit may be removed after inspection except duplicate bytes, non-data build artifacts,
or files that cannot contain tasks/trajectories by schema; all exclusions are counted by path and
reason.

## Frozen Structural Rubric

For each task/dialogue/trajectory unit, record:

1. prior selector query or entity-selection operation;
2. an observable stable target ID before the update;
3. binding before the update;
4. an independent, synchronization, user, or environment update after binding;
5. a competing entity in the same referential role;
6. a distinct post-update selector winner;
7. continued presence and action-validity of the old target;
8. a later entity-directed mutation;
9. instruction evidence for Preserve, Reevaluate, ambiguous, or absent timing;
10. a target-level observable outcome.

A **strict native opportunity** requires all necessary features, a completed update, a correct
observable initial binding, a surviving/action-valid old target, and a distinct refreshed winner.
`Partial` or `unclear` never enters the strict count.

A **source-anchored eligible cluster** may lack a native transition or timing contrast, but must
provide a stable ID, executable/queryable state, a same-role selector, a reproducible target-level
mutation, and enough environment control to add a deterministic Stable/Changed transition without
rewriting the tool schema.

## Zero-API Procedure

1. Download each pinned source under ignored `external_sources/`.
2. Record repository commit, remote URL, source file list, byte sizes, and SHA-256 hashes.
3. Parse every frozen unit and produce a schema/field-availability inventory.
4. Apply deterministic high-recall retrieval using event/tool names, mutation schemas, state
   configs, stable-ID fields, and temporal/update vocabulary.
5. Retain all candidates and exclusion reasons. Deterministic retrieval cannot declare a strict
   positive when a semantic or state-transition fact is absent.
6. Run unit tests and emit JSON plus Markdown reports.

## Go/No-Go Gate for SiliconFlow Annotation

Proceed to model-assisted annotation only if the zero-API audit finds:

- at least eight distinct source-anchored eligible workflow clusters;
- clusters from at least two of the three external datasets;
- source text/trajectory and state/tool fields that fit the frozen rubric without invented facts;
- no need to generate new tasks to satisfy the gate.

Otherwise the decision is **NO-GO**. The structural null is retained and no model-generated
replacement inventory is allowed.

## SiliconFlow Annotation Protocol if Go

Before the first request, freeze the exact candidate JSONL, its SHA-256, the system/user prompt,
endpoint, models, temperature, output cap, parser, retry policy, and stopping rule in an addendum.
The intended endpoint is `https://api.siliconflow.cn/v1`; credentials are read only from
`SILICONFLOW_API_KEY` or `LLM_API_KEY` and never written to artifacts.

Two different model families independently label every frozen candidate. The intended models are
`Qwen/Qwen3.5-122B-A10B` and `Pro/zai-org/GLM-5.1`, temperature 0, thinking disabled, with at most
one transport retry and no content retry. Candidate labels are `yes/no/unclear` with exact source
locators and quoted evidence. The candidate union is retained; model agreement cannot establish
benchmark facts without deterministic or author verification.

All API/parse failures remain in the attempted inventory. No prompt change, candidate deletion,
or stopping-rule change is allowed after seeing model labels.

## Outcomes and Interpretation

- Strict native positives strengthen external opportunity coverage, not behavioral prevalence.
- Source-anchored eligible clusters support a later matched transfer study, not a native score.
- Zero strict positives with adequate field coverage narrow the paper and are not a failed run.
- Missing state/ID fields mean the dataset cannot identify TRI; they are a coverage result, not
  evidence that TRI is absent.
- Any future behavior run is post-primary and cannot replace or relabel the frozen v3 primary.

## Required Artifacts

- raw source manifest with commits and hashes;
- executable parser/audit script and tests;
- all attempted/candidate JSONL;
- machine-readable and Markdown reports;
- if Go, frozen annotation addendum, raw API JSONL, parser report, and failure accounting;
- update to `reports/current_claim_provenance.md` and `reports/current_experiment_registry.md`.
