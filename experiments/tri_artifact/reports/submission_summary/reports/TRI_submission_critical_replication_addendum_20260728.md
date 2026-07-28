# TRI Submission-Critical Replication Addendum

Status: **frozen before any addendum-specific model call**. Evidence produced under this addendum
is `post-primary replication/audit`. The addendum addresses fatal-review alternatives; it does not
replace the primary protocol or create independent-human, open-language, native-benchmark, or
prevalence evidence.

## Questions and alternatives

1. **Convention-told natural history.** Does stating the Preserve/Reevaluate convention in ordinary
   language improve matched PairAcc without a structured ID, reference-mode record, compiler
   decision, or extra call? This tests the alternative that the ordinary actor was simply not told
   the evaluation convention.
2. **Model coverage.** Do the equal-call History-only versus Decision-visible results extend from
   Qwen and GLM to DeepSeek and MiniMax on the unchanged 160-row full diagnostic?
3. **Negative-result stability.** Do the model-dependent source-derived result and the four-cell
   ToolSandbox-style null reproduce without changing their tasks, prompts, endpoints, or scoring?

## Frozen models and endpoint

- `Qwen/Qwen3.5-122B-A10B`
- `Pro/zai-org/GLM-5.1`
- `deepseek-ai/DeepSeek-V4-Pro`
- `Pro/MiniMaxAI/MiniMax-M2.5`
- endpoint: `https://api.siliconflow.cn/v1`
- temperature: 0; thinking disabled; exact JSON output; timeout 180 seconds; at most two retries
  with exponential backoff.

A model is never replaced after outcomes are observed. An unavailable model remains an incomplete
cell. Calls for one model are sequential; model processes may run concurrently.

## Matrix A: Convention-told control

The inventory and two prompts are those frozen in
`reports/TRI_convention_told_natural_history_protocol.md`. The inventory is
`data/call_matched_authorization_ablation_v1.jsonl`, SHA-256
`5862e0ae009e8fd87dff223a2d4e15d641e2bdb203e8bdf0c57eaa9fd12a826c`, with 80 rows and 40
complete changed-winner pairs. This addendum prospectively extends the unchanged two-condition
protocol from Qwen/GLM to DeepSeek/MiniMax.

- Smoke: the first eight pairs (16 rows), both conditions, separately for each model.
- Full: all 80 rows and both conditions; smoke calls are not reused as full calls.
- Primary: Convention-told minus Plain-history changed PairAcc, separately by model, using 10,000
  state-cluster bootstrap draws and seed 20260728.
- Secondary: Preserve/Reevaluate accuracy, E2E, refreshed-winner Preserve errors, old-target
  Reevaluate errors, API/parse failures, requests, retries, latency, and tokens.
- Complete main-text cell: both conditions have all 80 ITT rows for one model.

The user payload contains exactly `original_instruction`, `initial_state_before_refresh`,
`current_refreshed_state`, `action_schema`, and the frozen question. It must not contain initial or
gold IDs, selector metadata, reference mode, compiler output, pair labels, or design metadata.

## Matrix B: full-diagnostic model extension

- Unchanged inventory: `data/revision_full_diagnostic_v1.jsonl`, 160 rows, 80 pairs, including 32
  actionable changed-winner pairs.
- New models only: DeepSeek and MiniMax. Historical Qwen/GLM files are not rerun.
- Unchanged logical calls: compiler, History-only actor, Decision-visible actor. Decision-enforced
  remains a deterministic derivation from the same visible output.
- Primary: Decision-visible minus History-only changed PairAcc, separately by model.
- Complete main-text cell: all 160 ITT rows for one model.

## Matrix C: source-derived repeat

- Unchanged inventory: `data/revision_source_grounded_v1.jsonl`, 60 rows and 30 pairs balanced over
  STATE-Bench, AgentDojo, and ToolSandbox source substrates.
- Qwen, GLM, and DeepSeek receive one prospectively labeled repeat-2 pass. MiniMax receives a first
  pass and is not called a repeat.
- Report each pass separately: PairAcc, E2E, effect sign, exact-target agreement with the historical
  pass, requests, failures, and retries. Repetition does not increase the number of independent
  task pairs.

## Matrix D: ToolSandbox-style null repeat

- Unchanged 96-task inventory and prompts from
  `reports/TRI_single_user_turn_trajectory_protocol.md`.
- Four complete cells: Qwen/GLM by Full-history/Matched-generic.
- Primary: conditional substitution under the existing eligibility definition.
- Initial binding, tool order, parse failure, rejection, and wrong write remain separate outcomes.
- Complete cell: all 96 task trajectories for a model/interface condition.

## Failure, stopping, and reporting rules

- Every attempted request is retained. API, parse, and schema failures remain in ITT.
- Accuracy never gates continuation. Smoke gates only transport, schema, forbidden-field, and
  completeness checks.
- Prompts, parsers, denominators, and inventories are not changed after a smoke or full result.
- Only complete cells may enter the main paper. Partial cells remain archived with their failure
  reason and are not summarized by partial accuracy.
- Negative, null, mixed, and adverse results are reported without selection.
- Runs completed after the main-paper data lock may enter only the supplement/artifact.

## Prospective interpretation

- Convention-told null: a natural-language convention is insufficient on that model/inventory.
- Convention-told improvement below Decision-visible: both convention exposure and executable
  decision representation may contribute.
- Convention-told near Decision-visible: narrow the contribution to interface specification and
  the normative matched unit test; do not claim a model capability defect.
- Model-dependent results: report model-conditional effects without pooling.
- Reproduced external null: interface-specific stability, not absence or prevalence.
- Reversed or unstable negative result: retain it and narrow the corresponding boundary claim.

