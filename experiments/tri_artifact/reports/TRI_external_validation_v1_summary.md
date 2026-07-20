# TRI External Validation Summary

## Scope

The frozen ToolSandbox-based 96-task inventory was evaluated with one-user-turn, multi-tool
trajectories. The primary mechanism estimand is conditional on a correct, auditable initial
binding and a completed refresh. It excludes initial selector/grounding errors.

## Results

| Model/controller | Rows | Opportunities | TRI mechanism errors | Wrong writes | Interpretation |
|---|---:|---:|---:|---:|---|
| Qwen full-history | 96 | 70 | 0 | 6 | All wrong writes were initial Reevaluate/selector errors |
| GLM full-history | 96 | 73 | 0 | 13 | Initial grounding plus four tool-name errors |
| Qwen generic state observed | 96 | 73 | 0 | 6 | 13 prohibited-schema/process errors; exploratory only |
| Qwen matched Generic Ledger | 96 | 64 | 0 | 5 | All wrong writes had incorrect compiler binding |
| GLM matched Generic Ledger | 96 | 87 | 0 | 4 | Wrong writes were initial Reevaluate selector errors |

The five external conditions therefore produce `0` post-binding TRI mechanism errors in their
auditable denominators. This is negative evidence against a universal-LLM or universal-tool-loop
claim. It does not invalidate the controlled TRI-v3 result, because the external full-history
agent and matched controller often fail before the post-binding opportunity.

## Corrected Controlled-Benchmark Audit

The original v3 Generic Ledger stage report read the lifecycle-only field `bound_target_id`.
Generic Ledger actually stores the initial target as `selected_entity_id`. The corrected audit
conditions on that field:

| Model | Update | Correct initial binding | Core opportunities | Drift to refreshed leader | Drift rate |
|---|---|---:|---:|---:|---:|
| Qwen3.5 | flip | 16/16 | 16 | 15 | 93.8% |
| Qwen3.5 | name collision | 16/16 | 16 | 14 | 87.5% |
| GLM-5.1 | flip | 16/16 | 16 | 3 | 18.8% |
| GLM-5.1 | name collision | 16/16 | 16 | 7 | 43.8% |
| Both models | stable | 32/32 | 0 core drift opportunities | 0 | 0% |

The controlled Generic results thus do contain the target phenomenon. The effect is strongly
model-dependent and is concentrated in updates where the old entity remains present/actionable
but loses the selector ranking. Remove/invalidate cases are excluded from this referential-core
table because they test invalid-target policy.

The separate model-facing SQLite audit applies the same conditioning to actual database writes.
Both Generic runs compile the correct initial ID on all 20 anchored tasks. Qwen writes the
refreshed winner on 8/8 core opportunities and GLM on 6/8, while each model has 0/4 wrong writes
on stable controls. Of the 13 and 8 total wrong writes, the remaining 5 and 2 follow removal or
invalidation and are classified as reject-policy errors, not referential-core TRI.

## Claim Boundary

The defensible claim is:

> A correctly bound entity can be replaced by a refreshed selector winner in a generic, model-
> mediated Agent state workflow; a lifecycle-aware pre-refresh commitment prevents this failure
> in the controlled benchmark. The failure is not universal across models or environments, and
> initial binding/selector errors are a separate class.

Do not claim that every LLM exhibits TRI, that the ToolSandbox extension establishes prevalence,
or that every wrong-entity write is a TRI failure.

## Official Opportunity and AppWorld Trace Audit

The unmodified ToolSandbox inventory has 129 semantic scenario families (1,032 tool-presentation
instances), zero strict native TRI opportunities, and one natural TRI-like post-binding trace.
The downloaded AppWorld release has 732 task instances from 244 generator families, zero strict
exogenous-transition opportunities, and one stronger TRI-like Todoist family (`8ce6779`). In that
family, reassignment makes tasks fail the original assigned-to-me selector, but `leave a comment
there` preserves their discourse identity.

Across 42 released AppWorld Agent trajectories from 14 experiment configurations, 16 correct
target-binding operations are followed by 16 comments on the same task IDs and zero post-binding
substitutions. Most failures omit a target before any correct binding; unconditioned non-gold
assignments/comments are reported separately. This supports natural problem structure, not a
positive TRI failure rate.

The official current tau3-bench repository was audited at commit `cf71a807`. Across 2,449
airline/retail/telecom tasks, strict native TRI opportunities are zero. Eight telecom task
definitions naturally bind an overdue bill, let the user pay, and continue by resuming an
associated line, but bill and line are different roles and there is no competing same-role target.
The repository's 26 released files contain 10,832 GPT-4.1, GPT-4.1-mini, Claude 3.7, and o4-mini
trajectories. They broaden ordinary-Agent and provider coverage but cannot estimate TRI because
the task inventory contains no strict opportunity.

## Custom AppWorld Case Study

The Todoist adaptation was frozen first; a post-primary Simple Note extension adds a different
application, alphabetical selector, and content-append write. Both use native AppWorld APIs and
stable database IDs. Across 32 two-model trajectories, 31/32 write the authorized target and 24/32
form a correct, correctly timed observable binding opportunity. Conditional TRI is 0/24, including
0/4 Preserve/Flip opportunities. The sole wrong write occurs when Qwen searches A, synchronizes
without recording a commitment, searches again, binds B, and writes B. It is a delayed-binding/
tool-order error outside the conditional TRI denominator. The two-cluster custom study is not an
AppWorld leaderboard score or a prevalence estimate.

## Lower-Intervention Ordinary-Agent Addendum

The addendum removes the explicit binding sidecar and all prompt language about TRI, commitment,
temporal authorization, Preserve, or Reevaluate. Ordinary selector APIs return one stable ID and
the runner records that normal result as binding. Across 32 two-app, two-model trajectories,
28 form a correct, correctly timed binding and conditional TRI is 0/28, including 0/6
Preserve/Flip opportunities. Qwen makes two real wrong writes, one per app, because it synchronizes
before its first selector call on one Preserve template. Matched Stable rows have the same order
defect but the unchanged winner masks the consequence. These are pre-binding temporal-order
errors, not post-binding drift.
