# TRI-v3 2x2 Factorial Addendum Protocol

Frozen on 2026-07-17 before any new model call for this addendum. This is a disclosed
post-primary-analysis experiment prompted by a strong-baseline concern. It does not replace the
pre-registered Generic Structured Ledger versus Lifecycle-Gated primary comparison.

## Question

Separate the contribution of post-binding temporal-authorization state from controller-level
enforcement:

| Representation | Execution | Experimental cell |
|---|---|---|
| Generic task state | Free actor | Generic Structured Ledger (existing run) |
| Generic task state | Action-validity gate | Generic Validity-Gated Ledger (derived) |
| Lifecycle state | Free actor | Lifecycle Free Actor (new actor completions) |
| Lifecycle state | Lifecycle gate | Lifecycle-Gated Controller (existing run) |

The representation factor changes whether the compiled record explicitly contains
`reference_mode`, `bound_target_id`, selector provenance, and invalidity policy. The enforcement
factor applies the executable constraints available in that representation. The generic gate can
reject a missing or action-invalid actor target but cannot infer whether a valid old or new target
is authorized. The lifecycle gate can additionally enforce a correctly compiled preserve
commitment.

## Paired Construction

- Generic Validity-Gated rows reuse the exact Generic Structured Ledger and actor outputs. A
  deterministic post-actor check changes a missing or action-invalid target to
  `INVALID_BOUND_ENTITY`; valid targets are unchanged. No model call is added.
- Lifecycle Free Actor rows reuse the exact compiler output from the Lifecycle-Gated run.
  Dynamic rows already invoked the actor and are copied unchanged. Preserve rows receive exactly
  one new actor call using the frozen lifecycle record and the same actor prompt used by the
  original runner.
- This construction fixes compiler output within each representation and therefore isolates the
  execution decision more tightly than independent full reruns.
- API failures remain failures and are reported separately. No prompt will change after smoke
  output is inspected.

## Frozen Inputs

- Primary language clusters: `bea0b48c5092e64fd3860069a5a81f09982940ca0b964b297d2e8a8f7f5970d6`
- Unseen schemas: `6a42f556d6cb176575070475855549b85c08b063c8b0b75b0ee40663770aca61`
- SQLite trajectories: `43b5613ef64fe2a3fc578e9d07686d044fb6efa7fd7bf07f609967da920f47e8`
- Main runner: `a71a68dc2f07579485833a2a361c50071430fa209f5654a9687402bfb2284afb`
- SQLite runner: `7d247f84016e767f2f5f7631e999787ce840fb191f6b7c24a921e6d7f1b882c7`
- Generic derivation: `98e069b49b24a3b59fb2985d3375cc735e569b9541571d016b4d6c1d0b22fe53`
- Lifecycle actor completion: `4a4274b3394f5bb86484c457412e615a88d22dab6c320bf1b461a71b5f113d26`

## Run Gate and Inference

Qwen3.5-122B-A10B, temperature zero, thinking disabled, 1,200 output-token cap. First complete
the existing 20-task balanced primary smoke and eight-task SQLite smoke. Proceed only when each
has at most one API or parse failure. Then complete the 160-task primary, 80-task transfer, and
40-task SQLite sources. Because only preserve rows need new calls, the expected maximum is 80,
40, and 20 calls respectively, excluding logged retries.

GLM replication is run only after the Qwen factorial identifies a scientifically relevant
representation or enforcement effect. It is not used to select the Qwen interpretation.

## Outcomes

- Exact target or final-state accuracy.
- Wrong-entity writes, invalid attempts, and unnecessary rejection.
- Anchored and dynamic accuracy separately.
- Compiler-correct conditional actor violation rate.
- Cluster-bootstrap intervals and paired McNemar tests.
- Main effects are descriptive because enforcement consumes different representational fields;
  the four cells are not treated as a linear ANOVA with exchangeable trials.

## Interpretation Commitments

- If Lifecycle Free Actor matches Lifecycle-Gated, the paper will treat the gate as a deployment
  mechanism rather than the main contribution.
- If Lifecycle Free Actor matches on target accuracy but causes SQLite wrong writes, the gate
  claim will be limited to mutation-boundary enforcement.
- If Generic Validity-Gated matches lifecycle cells, the lifecycle-representation necessity
  claim will be withdrawn.
- If dynamic accuracy falls under lifecycle gating, the method will not be described as selective
  invariance without reporting that cost.
- The paper's primary novelty claim is post-binding temporal authorization, not structured state
  or deterministic gating in general.
