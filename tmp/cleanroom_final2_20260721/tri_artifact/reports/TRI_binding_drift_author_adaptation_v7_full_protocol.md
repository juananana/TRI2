# Binding Drift Author-Adaptation Full v7 Protocol

Frozen: 2026-07-21, before any full-v7 adapted re-verifier output.

## Question

Can a practical Binding Drift-style re-verifier replace TRI's discourse-conditioned transition
decision when evaluated on a complete, matched Preserve/Reevaluate inventory?

This is an author adaptation on TRI tasks. It is not an official Binding Drift result and does not
test repair of an initially incorrect binding.

## Frozen inventory

- Source: `data/temporal_referent_v7_core_replication.jsonl`.
- Source SHA-256: `2504f4979f1b4bfad5357e0cf734cbe4881adcadbe4e3cb1ca4fca0620657891`.
- 240 unique tasks in 40 state clusters, six tasks per cluster.
- 120 Preserve and 120 Reevaluate tasks.
- 80 Flip, 80 Stable, and 80 name-collision tasks.
- Every task has an actionable authorized target; no Reject-policy case is included.

The complete existing v7 inventory is used without selection or task modification. The Stable
slice is a negative control, Flip requires different old/new targets, and name-collision tests
whether identity survives a distractor with overlapping surface attributes.

## Methods

1. `Entity Lock analogue`: deterministically retain the pre-refresh ID.
2. `GLM self-reverify author adaptation`: apply the already frozen official re-verification prompt
   frame to the complete TRI instruction and refreshed candidates.
3. `Exact CTA`: reuse the existing frozen GLM v7 output without rerunning or changing its prompt.
4. `Handcrafted rule v2`: reuse the already completed post-hoc benchmark-aware output and retain
   its post-hoc label. It is contextual, not confirmatory evidence.

The GLM endpoint is `Pro/zai-org/GLM-5.1`, temperature 0, thinking disabled, 300 output tokens,
180-second timeout, and at most three transport retries. API and parse failures remain in the ITT
denominator. The API key is passed only through `LLM_API_KEY`.

The original Binding Drift interface normally receives a short referent. TRI supplies the complete
temporal instruction because deleting its event order would delete the variable under test. This
interface difference is disclosed in every report and prevents labeling the result an official
reproduction.

## Frozen metrics

Primary descriptive metrics:

- exact authorized-target accuracy over all 240 tasks;
- Preserve and Reevaluate accuracy separately;
- paired authorization success: both members of each matched `(state_cluster_id, update)` pair
  must be correct;
- Flip, Stable, and name-collision accuracy;
- Preserve substitution to the refreshed winner;
- Reevaluate premature retention of the old target;
- other-visible-target, clarify, API/parse error, retry, token, and latency counts.

For the paired GLM CTA-minus-reverify accuracy difference, report a 10,000-draw paired bootstrap
over the 40 complete state clusters with seed 20260721. This interval is descriptive and does not
turn the post-primary adaptation into a preregistered primary experiment.

## Interpretation gates

- **Substitution supported:** reverify is within 5 percentage points of CTA overall, is nonzero and
  within 10 points of CTA in both modes, and its paired authorization success is within 10 points.
  This would substantially weaken any claim that TRI adds an empirically distinct authorization
  capability beyond practical re-verification.
- **Complementary-policy result:** reverify differs by at least 40 points between modes and paired
  authorization success is at most 50%. This supports the narrower claim that unconditional
  re-resolution and identity locking solve opposite sides of the task.
- **Grounding-limited result:** at least 20% of outputs select other visible targets or fail to
  parse. The adaptation is then not a clean temporal-policy comparison and must be interpreted as
  an interface/grounding boundary.
- **Mixed result:** any other outcome. Report all slices without claiming dominance.

No result establishes open-language generalization, prevalence, or superiority on Binding Drift's
original initial-misbinding benchmark.

