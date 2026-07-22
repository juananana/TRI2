# TRI-v7 Temperature-Zero Repeat Stability Protocol

Status: frozen before any repeat-2 or repeat-3 model call.

## Question

Do temperature-zero SiliconFlow calls reproduce the direction and approximate magnitude of the
matched Generic-versus-CTA result, or does provider-side nondeterminism materially change the
conclusion?

## Frozen subset

- File: `data/temporal_referent_v7_repeat_stability_v1.jsonl`
- SHA-256: `06afa1a2a40f78eaa817a5f98f107e4972f7ea4c2b099535c7023498cd174446`
- 40 tasks from 40 distinct state clusters and all 10 v7 domains.
- Binding: 20 anchored, 20 dynamic.
- Language: 20 explicit, 20 implicit.
- Update: 14 stable, 13 flip, 13 name-collision.
- Selection was deterministic and used no model outputs or correctness labels.

## Conditions

- Models: `Qwen/Qwen3.5-122B-A10B`, `Pro/zai-org/GLM-5.1`.
- Controllers: Generic Structured Ledger and Exact CTA (`compile_then_act`).
- Temperature 0, thinking disabled, maximum 1,200 output tokens.
- Same SiliconFlow endpoint, timeout, retry policy, prompts, parser, and scorer as the frozen v7
  replication.

The matching rows from the already completed 240-task run form repeat 1. Two new complete passes
form repeats 2 and 3. Therefore the experiment needs 320 new task-controller executions rather
than rerunning the first pass. Each execution normally uses two model requests, for approximately
640 requests before transport retries.

## Outcomes

Report, without selecting a favorable repeat:

1. Exact authorized-target accuracy for each model, controller, and repeat.
2. CTA-minus-Generic paired difference for each repeat.
3. Conditional TRI and stable-control errors with their explicit denominators.
4. Per-task target unanimity across the three repeats and pairwise target agreement.
5. API errors, parse errors, retries, tokens, and latency under intention-to-treat.

With only three repeats, report ranges and raw counts rather than a variance significance test.
The result measures endpoint repeatability on the frozen controlled inventory; it is not evidence
about natural-world prevalence.

## Decision rule

- Stable: the CTA-minus-Generic direction is positive in all model-repeat cells, and no repeat
  introduces a conditional CTA drift after correct initial binding.
- Mixed: direction remains positive but accuracy varies by more than 10 points or target unanimity
  is below 90% for either controller.
- Unstable: any model repeat reverses the paired direction, or CTA exhibits conditional drift.

All complete outputs are retained regardless of the decision.
