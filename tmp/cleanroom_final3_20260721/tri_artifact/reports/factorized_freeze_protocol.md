# Factorized TRI Freeze Protocol

Freeze time: `2026-07-16T16:36:46Z`

This protocol separates prompt development from the held-out paraphrase evaluation.
The factorized lifecycle prompt and hybrid action gate were developed using only the
original 160-task TRI-v2 scalar development set. The final development-set changes
separate reference mode from invalidity policy, make discourse order explicit, and
prevent a preserved target's selector from being reused as an action precondition.

The held-out set changes only instruction wording. Initial states, refreshed states,
action schemas, and gold targets are copied from the development tasks and checked by
unit tests. It therefore measures paraphrase transfer, not unseen-domain transfer.

Frozen SHA-256 values:

- `tri/run_models.py`: `ed46b4d06dddfc1a4cd321de126a4ce4351e56a6c9b244aa086129c0c108caeb`
- `tri/v2_heldout.py`: `57a376d555a75fb171a5a3a8acd71c063ec7edcee332ad79ad43da7542d93bd6`
- `data/temporal_referent_v2_heldout.jsonl`: `9a63be2a2f25685db33e9a0c0048fcd2e86fe5f3bdc813dc592d01f8eda18d89`

After this freeze, held-out results may be analyzed but must not be used to revise the
factorized compiler prompt or hybrid gate. Any later method revision requires a new
test set and a separately recorded protocol.

Planned frozen evaluations:

1. Qwen3.5-122B-A10B factorized hybrid on development and held-out paraphrases.
2. GLM-5.1 factorized hybrid on development and held-out paraphrases.
3. Strong held-out baselines sufficient to test whether full history or generic
   planning closes the gap.

All model calls use temperature 0. API/transport failures are audited separately and
are never interpreted as model errors.
