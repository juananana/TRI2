# TRI-v7 Matched Full-History Baseline Protocol

Frozen: 2026-07-21, before inspecting any new baseline output.

## Question

Does the controlled TRI result persist against agents that receive the same original instruction,
initial state, and refreshed state without a Generic ledger or compiled commitment?

## Conditions

1. `interactive`: two-call ordinary full-history trajectory. The first call is required only to
   request refresh; the second retains the full conversation and receives the refreshed state.
   The prompt does not mention TRI, Preserve/Reevaluate, commitment, binding time, or locking.
2. `full_history_once`: one-call discourse-aware upper baseline. It receives both states and is
   explicitly asked to decide whether to preserve, reevaluate, or reject. It has no structured
   ledger or deterministic gate.
3. Exact CTA: existing unchanged v7 runs, used only for matched accuracy comparisons.

Models: Qwen3.5-122B-A10B, GLM-5.1, DeepSeek-V4-Pro. Temperature 0, thinking disabled,
1,200 output-token cap, same SiliconFlow-compatible endpoint.

## Stages

- Health/smoke: frozen first 16 v7 scalar rows in
  `data/temporal_referent_method_upgrade_smoke_v1.jsonl`.
- Full: unchanged `data/temporal_referent_v7_core_replication.jsonl`, SHA-256
  `2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891`.

Proceed to full only when each model/controller smoke has 16 rows, at most one API/parse error,
and no systematic response-format failure. Do not require a favorable accuracy direction.

## Metrics

- authorized-target accuracy and state-cluster bootstrap interval;
- anchored/dynamic accuracy;
- unconditional refreshed-winner substitution on anchored flip/name-collision rows;
- old-target retention on dynamic changed-winner rows;
- stable anchored errors, API/parse errors, requests, retries, latency, and usage.

Full-history methods do not expose a separately scored pre-refresh binding. Their substitution
rate is therefore unconditional and must not be reported as conditional TRI. API/parse failures
count as incorrect under intention-to-treat.
