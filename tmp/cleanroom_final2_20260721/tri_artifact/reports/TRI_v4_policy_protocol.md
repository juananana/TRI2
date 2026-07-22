# TRI-v4 Guarded Policy Evaluation Protocol

Frozen before any model call on TRI-v4.

## Motivation and status

TRI-v3 distinguishes preserved from dynamically reevaluated references, but all invalid
preserved targets use the same reject policy. It therefore does not establish that a lifecycle
record needs a conditional guard or multiple fallback policies. TRI-v4 is a separately frozen,
exploratory extension designed to test that missing semantic distinction. It is not part of the
TRI-v3 pre-specified primary comparison.

## Minimal policy pair

Each task binds an entity before refresh and authorizes reevaluating the selector under one of
two guards:

1. `action_validity`: preserve the bound identity while it satisfies action preconditions;
   otherwise reevaluate the selector.
2. `selector_match`: preserve the bound identity only while the selector still chooses it;
   otherwise reevaluate the selector.

On flip and name-collision updates, the old entity remains action-valid but is no longer the
selector result. The two policies therefore require opposite targets under the same state
transition. On remove and invalidate updates both policies reevaluate; on stable updates both
preserve. This prevents a controller from solving the set with a single unconditional rule.

## Frozen data and code

- Full data: `data/temporal_referent_v4_policy.jsonl`
- Full-data SHA-256: `7440812377718fe5b691523eee977842b571e42cc2644a2bcf05ba1035f51c9c`
- 40 tasks, 10 template clusters, four unseen-domain schemas.
- Every guard x update x domain combination occurs once.
- Smoke data: `data/temporal_referent_v4_policy_smoke.jsonl`
- Smoke SHA-256: `7ca5b082245c0531bdcd4e8f4d613f69e242aa28a7099ba15aac1ed248f95bab`
- Data generator SHA-256: `f6875b62dd9f17210e7948752a043939efbff7611f9ae141264df28685eb307c`
- Runner: `tri/run_v4_policy_models.py`
- Runner SHA-256: `7d5eb6440259e72fd6bae56c176ff680f4bf40a072a16bbec14fa026c46a2f90`

The hashes above replace earlier pre-call drafts after grammar validation found duplicated
articles and awkward phrasal-verb constructions, including one residual duplicated article in
the final template. No TRI-v4 model call had been made. The corrected files were regenerated,
scanned for the known patterns, tested, and frozen before execution.

## Controllers

- Generic Structured Ledger, using the same implementation as TRI-v3. It receives the original
  instruction at the actor stage and is not deprived of policy language.
- Guarded Lifecycle Controller, which compiles `guard_type`, bound identity, selector, and
  fallback policy. It uses a deterministic gate when an `action_validity` guard is satisfied;
  otherwise the actor evaluates the guarded policy on refreshed state.

Both are two-stage controllers except when the lifecycle gate resolves a target after one model
call. Temperature is zero, thinking is disabled, and maximum output length is 1200 tokens.

## Run gate

Run Qwen3.5-122B-A10B on the 10-task smoke set first. Proceed to all 40 tasks only if each
controller has at most one API/parse failure and the output is scientifically interpretable.
Run GLM only if Qwen reveals an informative policy distinction or a useful negative result.

## Metrics and analysis

- exact target accuracy;
- accuracy by guard type and update;
- compiler guard classification and bound-ID accuracy;
- actor-only versus compiler-induced failures;
- template-level macro accuracy;
- 10,000-sample template-cluster bootstrap confidence intervals;
- paired discordance and exact McNemar test;
- API errors, retries, request count, and latency.

The result may support a broader guarded-lifecycle representation. It must not be used to claim
that TRI-v3 already varied fallback policy, and a negative result must be retained and reported
in the decision log.
