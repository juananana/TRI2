# TRI-v2 Baseline Integrity Update

Generated after auditing the user-run SiliconFlow matrix on 2026-07-16.

## Usable results

- GLM-5.1 state_overwrite_once: 160/160 complete, 0 API/internal errors, 61.3% accuracy.
- GLM-5.1 compile_then_act: 160/160 complete, 0 API/internal errors, 89.4% accuracy.
- The paired GLM comparison is strong: +28.1 points for compile_then_act, 45 tasks fixed, 0 tasks regressed, exact McNemar p = 5.684e-14.

## Mechanistic pattern

- GLM state_overwrite_once solves dynamic references perfectly (80/80) but fails most anchored cases (18/80).
- GLM compile_then_act preserves anchored identities much better (63/80) and keeps dynamic performance perfect (80/80).
- The remaining GLM compile_then_act failures are concentrated in validity/action-precondition cases: anchored invalidate is 0/16, while anchored remove is 16/16. This supports the upgraded paper claim that identity/time binding is insufficient without lifecycle validity.

## Contaminated runs

- Qwen3.5 state_overwrite_once is clean: 160/160 complete, 0 API/internal errors, 60.0% accuracy.
- Qwen3.5 compile_then_act has 52/160 internal API errors: 46 HTTP 403 failures and 6 timeouts. Overall accuracy counting API failures is 53.8%; completed-call accuracy is 79.6%. This run should be retried before being used as a model-comparison result.
- MiniMax-M2.5 state_overwrite_once and compile_then_act both have 160/160 internal HTTP 403 failures. These runs are not interpretable as model performance.

## New reproducibility support

- `tri/v2_retry_subset.py` extracts failed API samples from a run into a JSONL retry dataset.
- `tri/v2_merge_retry.py` merges successful retry rows back into the original run while preserving retry provenance.
- `scripts/retry_v2_api_failures.sh` runs the extract/retry/merge sequence for a specified run, model, and mode.
- `tri/v2_pairwise_report.py` produces paired McNemar-style comparisons on identical task ids.

## Next experiment priority

1. Rerun only the 52 Qwen3.5 compile_then_act API failures and merge them.
2. Run GLM-5.1 schema_compile_then_act on the full 160-task scalar subset. This directly tests whether lifecycle/action-schema prompting fixes the anchored-invalidate gap.
3. If API access permits, rerun MiniMax with a model id that SiliconFlow accepts for chat completions; do not use the current 403-only logs as model results.
