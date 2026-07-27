# Source-Anchored External Transfer Model Addendum

**Frozen:** 2026-07-24, after the zero-API Go decision and before the first model request.

**Evidence status:** planned/unverified until the frozen smoke and any full run complete.

**Parent protocol:** `reports/TRI_source_anchored_external_transfer_protocol.md`

## Frozen Claim and Boundary

The run tests whether the timing-dependent target contrast transfers to author-adapted matched
tasks built from independently released STATE-Bench and AgentDojo states and source tools. It tests
the alternative explanation that the controlled result depends only on the TRI generator's own
schemas or entity inventory.

Any result is `source-anchored external transfer`. It is not a native benchmark result, natural
traffic prevalence, official benchmark score, or independent human evidence. A positive result in
only one repository is limited bridge evidence. A null in both repositories retains the current
controlled-interface limitation and stops expansion.

## Frozen Inventory

- Inventory: `data/source_anchored_external_transfer_tasks_v1.jsonl`
- Rows: 80 from 20 workflow clusters, with Preserve/Reevaluate x Stable/Changed per cluster
- Repositories: 10 STATE-Bench clusters and 10 AgentDojo clusters
- Inventory SHA-256: `73e30875928b60c49fad286d667795643c6a2369bdbdac6dfa2062de862b7907`
- Zero-API gate: 20/20 eligible clusters and 80/80 source-tool final-state checks passed
- Zero-API report: `reports/source_anchored_external_transfer_zero_api_v1.json`
- Source manifest: `reports/source_anchored_external_transfer_source_manifest_v1.json`

The source refresh changes one ranking field on an existing source entity. The old selected entity
remains present and action-valid. No source schema field or gold target is supplied to the model.

## Frozen Model Interfaces and Prompts

Both conditions make the same first request: after a source read result, the model returns one
observable selected ID and waits. Both receive the complete interaction and the same refreshed
source result for the final source write call.

The ordinary condition receives only that complete history. The execution-record condition also
receives a deterministic record derived from the user timing language: select before the update
and retain the observed ID, or select after the update and reapply the source selector. The model
prompts do not use the paper's terminology or condition names.

- First-selection prompt SHA-256:
  `6c4dca6915d7f90d7836695e2893b2c399149294b9e6d4eb4ebc63e53e70ef1d`
- Ordinary full-history prompt SHA-256:
  `69198c44451a15bf7c4c18ba3e155e0f84e51a2580fdc44287d0d96c9c17706e`
- Execution-record prompt SHA-256:
  `47ca76de23590d21c9366bd84309e96197e50325566f69d6d2fe0e18468b71d2`
- Runner: `scripts/run_source_anchored_external_transfer.py`
- Runner SHA-256: `26adf50395a38b9e273076ca812266e0823ccf3e69a7af1cf6fb634c06492a6e`
- Report script SHA-256:
  `f74eb5a439a1abb2970a855930495d03ddf4056692d13329e641b565e4e1c180`
- Smoke-gated execution wrapper SHA-256:
  `65891e3b6b4a7bccaf3b565cd45301ef64c380a6007abf56e72d5f96ccbc0fdd`

Model-selected targets are executed against a fresh isolated source environment. The report keeps
correct writes, wrong-entity writes, rejected/missing writes, invalid tool calls, source execution
failures, parse failures, and transport/API failures separate.

## Endpoint and Decoding

- Endpoint: `https://api.siliconflow.cn/v1/chat/completions`
- Models: `Qwen/Qwen3.5-122B-A10B` and `Pro/zai-org/GLM-5.1`
- Temperature: 0
- Thinking: disabled
- Output cap: 500 tokens per request
- Timeout: 180 seconds
- Workers: 4
- Credentials: environment only (`SILICONFLOW_API_KEY` or `LLM_API_KEY`), never serialized

Each model-condition-task row has at most two content requests: the observable initial selection
and the final source write. An explicit transport, HTTP 429, or HTTP 5xx failure is retried once.
Content, parse, schema, missing-call, wrong-tool, and source execution failures are not retried.
All attempted rows and raw model content are append-only and count under intention-to-treat.

## Frozen Smoke and Stopping Rule

The smoke contains all four timing/transition cells from exactly these two clusters:

- `state-shopping-add-01`
- `agentdojo-calendar-meeting-earliest-reschedule`

Across two models and two model-facing conditions this is 32 rows. The smoke passes only if all 32
unique rows are present, at least 90% parse and execute without transport/API/infrastructure
failure, and every model-condition pair has at least one valid row from each repository. A smoke
failure stops the full run. Only transport repair under identical hashes is allowed.

The execution wrapper stops after a passing smoke by default. The full run requires the explicit
`--full-after-smoke` flag so that its additional request cost is separately authorized.

If the smoke passes, the full stopping rule is 320 unique model-condition-task rows. Interrupted
runs request only missing rows under the same inventory, prompt, model, endpoint, parser, and retry
hashes. No task, prompt, parser, or reporting-rule changes are allowed after smoke outcomes become
visible.

## Frozen Metrics and Interpretation

The report separates exact target/final-state success, observable initial selection, changed-cell
matched accuracy, conditional substitution after a correct initial selection, wrong-entity writes,
rejection or missing action, invalid tool or target, collateral modification, source execution
failure, parse failure, and transport/API failure. Results are split by repository, domain, model,
and condition. Cluster bootstrap resamples the 20 workflow clusters in the full report.

Consistent direction in both repositories strengthens transfer to these two external source
substrates. A benefit from the execution record counts only if exact final-state success improves
without replacement by rejection or invalid calls. Zero observed substitutions does not establish
zero population risk.

## Smoke Infrastructure Repair and Result

**Added:** 2026-07-24, after the first smoke returned and before any full-run request.

The original 32 model-condition-task rows completed with no transport failure. The source
checkouts and AgentDojo temporary dependencies had disappeared from `/tmp` before final source
execution, causing 31 infrastructure failures (`ModuleNotFoundError` for STATE-Bench and
`FileNotFoundError` for AgentDojo); the remaining row had a model JSON parse failure. The original
append-only run and NO-GO report are retained and must not be interpreted as behavioral results:

- Original raw SHA-256:
  `521da38095556ed3825b848ff1197a93d6fd21b1ba4e75e19eb20d65615abb56`
- Original report: `reports/source_anchored_external_transfer_smoke_v1.{json,md}`

The pinned repositories were restored under the gitignored persistent `external_sources/`
directory. Their commits and manifest file hashes matched exactly. A repair script then replayed
only the source writes from the already serialized model-selected targets. It made zero model or
network requests and preserved all prompts, raw model text, response IDs, usage, selections,
targets, parse failures, and request counts. It changed only source-execution and derived scoring
fields. The original rows remain separate.

- Repaired smoke seed SHA-256:
  `4804bce16d005fda44229b3108e4d777b0dec288a4340607607354e9bcbc07be`
- Repair script SHA-256:
  `5ee4cd036398d1375fc4c7e53086cfdc3b13dc0e40b90da14da5f2eab4307580`
- Repaired report SHA-256:
  `3085392e407f9c94dbbbe1cca07a528e2e301f4a4a9725168c36bc85897513af`
- Repaired report: `reports/source_anchored_external_transfer_smoke_repaired_v1.{json,md}`

The repaired smoke has 31/32 valid rows (96.9%), no transport or source-execution failure, and one
retained GLM JSON parse failure, so it passes the frozen smoke gate. Exact-target success is 26/32.
Among 12 Changed rows with correct observable initial selection, exact-target success is 11/12.
There are zero Preserve/Changed substitutions to the refreshed winner and one Reevaluate/Changed
failure to substitute. Ordinary full history scores 14/16 exact versus 12/16 for the execution
record in this two-cluster smoke. This adverse direction is retained; the smoke is an execution
gate, not evidence for selecting a preferred condition.

Before the full run, the runner was changed only to use persistent ignored source paths and to fail
before an API request if a required source runtime is absent. The wrapper now reruns the 80/80
zero-API gate before any model request and uses the repaired 32-row seed, so the full runner requests
only the 288 missing rows. The reporting module was expanded to emit the metrics already frozen in
this addendum (ITT, conditional Changed, changed pairs, shared-initial-selection comparisons, and
cluster bootstrap); no estimand or outcome rule changed after viewing the smoke.

- Repaired runner SHA-256:
  `e897fed584ba024b2885eaa45a8d8132555de086068c105ab4c32f8d5053ca3c`
- Repaired execution-wrapper SHA-256:
  `cea03059ee7d494c83f4ae20da25ed4ce6de0f51da791cecd4fbc8cf3104c1fd`
- Expanded reporting-module SHA-256:
  `402812967db47fb6cfc33e6f82f2343068a0290d5be7a942faa18a5f80ecb188`

Inventory and all three model-facing prompt hashes remain exactly as frozen above. No task,
selection, model, endpoint, temperature, output cap, parser rule, retry rule, or model-facing byte
changed.

## Full-Run Completion

**Completed:** 2026-07-24 under the repaired infrastructure path and unchanged model-facing
inventory, prompts, models, endpoint, decoding, parser, and retry rules.

The full stopping rule was reached: 320/320 unique model--condition--task rows. The repaired seed
contributes the original 32 smoke model responses and the runner adds only the 288 missing rows.
There are 306 valid rows, 14 retained GLM parse/schema failures, zero transport failures, and zero
source-execution failures. All 306 parsed writes execute in fresh source environments; 50 target a
non-gold entity, but most follow initial selection or non-TRI errors and are not pooled into the
conditional numerator.

Among 126 Changed rows with a correct observable initial selection and a surviving action-valid old
target, 118 choose the exact target. Preserve/Changed has 2/64 substitutions to the refreshed
winner; Reevaluate/Changed has 3/62 failures that retain the initial winner. Both Preserve
substitutions are Qwen ordinary-history file actions in AgentDojo (2/7 versus 0/7 matched Stable).
STATE-Bench has 0/34 Preserve substitutions, and GLM AgentDojo has zero. Per the frozen
interpretation rule, this is limited single-repository bridge evidence rather than consistent
two-repository transfer.

The execution record is not a stable improvement. On shared correct-initial-selection rows,
ordinary history versus execution record is 57/59 versus 52/59 for GLM and 62/65 versus 63/65 for
Qwen. Cluster bootstrap estimates execution-record minus ordinary exact-target accuracy at
$-8.75$ percentage points (95% CI $[-16.25,-2.5]$) for GLM and $-1.25$ points
($[-6.25,3.75]$) for Qwen. This adverse evidence narrows the implementation claim.

- Final raw JSONL SHA-256:
  `fc904a0e64cd6b3205b8d78daf6d918bc2443c0be5805d39f1bfbb09ad5d5d36`
- Final JSON report SHA-256:
  `309feed986d1006ce63e34960ad563fba94252fce0a7f40d9c02baed434cfc77`
- Final Markdown report SHA-256:
  `5b9db8adb36ddae530cfa6288e90a03a0c8414d58ec8106d7aee0295fafb13db`
- Final reporting module SHA-256:
  `bbdfaac5aea4388812d52e97f94b2e12b92c92d2a3bb46352d2c086705ba1ef5`
- Final report CLI SHA-256:
  `2b106f63cdfcbe7a77229d0fd988f22fbbc13fc9f3c8a6c0d578e90dc324580d`
- Generated supplement table SHA-256:
  `3487c237a09edd5fc06c031619b0b904fab7ff07d494109ec38f4af4ba4a912f`

The result is source-anchored external transfer on author-adapted matched tasks. It is not native
benchmark prevalence, natural traffic, an official STATE-Bench or AgentDojo score, independent
human evidence, or support for a universal execution-record advantage.
