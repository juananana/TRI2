# Source-Anchored External Transfer Protocol

**Frozen:** 2026-07-24, after public documentation/source inspection and before cloning,
task materialization, scoring, or any model/API call for this study.

**Evidence status:** planned/unverified until the zero-API gate and any authorized model run
complete. Any completed result is post-primary.

## Claim and Alternative Explanation

This study tests whether the controlled TRI timing contrast and any resulting target substitution
transfer to independently released stateful task/tool substrates. It specifically addresses the
alternative explanation that the current behavioral result is created by the TRI generator,
its schemas, or its controller interface.

The study cannot establish native benchmark prevalence or natural-request prevalence because the
matched instructions and refresh interventions are author adaptations. STATE-Bench also discloses
that its benchmark tasks were generated with language models. Results must be called
`source-anchored external transfer`, not official benchmark scores or native positives.

## Frozen Sources

1. Microsoft STATE-Bench, commit
   `0962c71af0e52fcf7c7de1f33e5095165d23183e`, MIT license.
2. ETH Zurich AgentDojo, commit
   `089ed468cf3ed0322acc66b0211f26d9d90dbf60`, MIT license.

The source repositories are downloaded outside the submission artifact. A manifest records remote,
commit, file hashes, and the exact source files used. WorkArena is excluded from this study because
its current setup requires access to gated ServiceNow instances.

## Zero-API Eligibility Gate

A workflow cluster is eligible only when the pinned source provides:

1. a query or read operation over multiple same-role entities;
2. a stable entity identifier consumed by a later inspect, preview, or write operation;
3. a deterministic selector with a unique winner in both states;
4. an independently applied refresh between observable binding and final action;
5. a distinct refreshed winner in the Changed condition;
6. continued presence and action validity of the old target after refresh;
7. a target-specific write or externally visible action;
8. an automatic target-level final-state check.

The model-facing prompt may not use `TRI`, `commitment`, `authorization`, `binding mode`, or
controller names. The adapter may add a deterministic refresh hook but may not replace the source
tool schema, invent unavailable entity fields, or supply gold winner IDs to the model.

Proceed beyond zero API only if there are at least eight eligible clusters from both repositories,
with at least three clusters per repository, and every materialized task passes automatic checks.
The target full inventory is 20 clusters and 80 tasks:

- Preserve/Reevaluate x Stable/Changed for each cluster;
- no language paraphrase expansion in the primary transfer inventory;
- balanced repository, domain, timing, and transition reporting.

If fewer than eight clusters pass, the study is `NO-GO`. Missing clusters may not be replaced with
LLM-generated schemas, entities, or tools.

## Model Conditions

If the zero-API gate passes, freeze the exact inventory hash and prompt bytes in an addendum before
the first request. The intended provider is SiliconFlow with:

- `Qwen/Qwen3.5-122B-A10B`;
- `Pro/zai-org/GLM-5.1`;
- temperature 0, thinking disabled, and an output cap recorded in the addendum.

The primary interface is an ordinary full-history tool controller using the external tool names and
schemas. Historical CTA is a matched controller probe. Always-Lock and Always-Reevaluate are
zero-API policy controls. No prompt or task change is allowed after smoke outcomes are visible.

## Execution and Failure Policy

The smoke contains at least one cluster from each repository and all four timing/transition cells
for both model families and both model-facing controllers. Full execution starts only if:

- every smoke task completes its deterministic refresh and final-state check;
- both repositories have valid model outputs;
- at least 90% of smoke rows parse and execute without transport/API failure.

All attempted rows are append-only. API, timeout, parse, missing-call, and invalid-tool failures are
incorrect under intention-to-treat. At most one retry is allowed for explicit transport, HTTP 429,
or 5xx failure; content and parse failures are not retried. Interrupted runs resume only missing
pairs under unchanged hashes.

## Metrics

Report separately:

- exact target and final-state success over all rows;
- observable initial binding/preview success;
- changed-winner matched-pair accuracy;
- conditional substitution after correct binding and completed refresh;
- wrong-entity writes;
- rejection, invalid attempt, tool-order error, and collateral modification;
- API/parse failures and request attempts;
- per-repository, per-domain, per-model, and per-controller results.

Cluster bootstrap resamples workflow clusters. Shared-eligible comparisons require both controllers
to have the correct observable initial binding. Zero observed substitutions never establishes zero
population risk.

## Interpretation and Stopping Rule

- Results in both repositories with consistent model direction strengthen transfer to external
  task/tool substrates.
- A result in only one repository is limited bridge evidence and narrows the conclusion.
- Null ordinary-interface results in both repositories stop further expansion and retain the
  current controlled-interface limitation.
- A CTA reduction counts only when exact final-state utility is not replaced by rejection or
  invalid attempts.
- Regardless of outcome, do not claim native benchmark failure, natural prevalence, or universal
  model behavior.

## Required Artifacts

- source manifest and zero-API eligibility report;
- executable adapter, task builder, scorer, and tests;
- frozen task JSONL and prompt/config hashes;
- append-only raw model JSONL;
- machine-readable and Markdown reports;
- updates to current claim provenance and experiment registry;
- paper changes only after the final report is reproducibly generated.
