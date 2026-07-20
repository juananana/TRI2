# Binding Drift Reproducibility and Comparability Audit

Audit date: 2026-07-20

## Source

- Repository: `https://github.com/shashank-indukuri/binding-drift`
- Audited commit: `0e040e0954b18d4621a6f9b16f6e6e9591c822e1`
- Commit subject: `v2: 200-workflow benchmark, LLM re-verifier, 8-model full sweep`
- Code license: MIT. Data/results license stated in README: CC BY 4.0.

## Offline reproduction

The repository README asks users to run `code/test_offline.py` and expects 25/25 assertions.
At the audited commit, the script looks for `data/workflows_hard.jsonl` and then
`data/workflows_multistep.jsonl`, but both files were deleted in the same commit. The current
dataset is `data/workflows_200.jsonl`; therefore the documented command fails with
`FileNotFoundError` on a clean checkout.

We copied the unmodified `environment.py` and `test_offline.py` to a temporary directory and
made the current `workflows_200.jsonl` available under the legacy filename expected by the test.
Result: **25/25 assertions passed**. This validates the deterministic metric and defense logic,
but the path adaptation must be reported and must not be described as an unmodified clean-checkout
reproduction.

## Method semantics

- `lock` pins the first concrete entity ID. On TRI tasks this is equivalent in spirit to the
  existing Always-Lock baseline and cannot represent user-authorized post-refresh reevaluation.
- `reverify` in `environment.py` reads `state.gold_target` and is explicitly documented by the
  authors as an oracle upper bound. It is not a learned baseline and cannot appear in the TRI main
  table as ordinary model performance.
- `llm_self_reverify` and `llm_cross_reverify` independently resolve the original step-1 referent.
  They target initial misbinding and propagation, whereas TRI distinguishes Preserve from
  Reevaluate after a state transition.
- The Binding Drift workflow benchmark and TRI therefore overlap on entity persistence but have
  different authorization semantics. Directly pooling their scores or significance tests would
  be invalid.

## Submission decision

1. Cite and reproduce the official offline harness separately.
2. Use existing Always-Lock as the matched entity-lock comparison on TRI.
3. If time permits, implement an `author adaptation` of LLM re-verification that receives the full
   temporal instruction and both state epochs; label it as an adaptation, not the official method.
4. Keep official oracle `reverify` out of the learned-method main table.
5. Report the current clean-checkout path defect and exact adaptation.
