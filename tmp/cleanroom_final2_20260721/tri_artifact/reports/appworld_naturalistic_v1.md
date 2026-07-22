# AppWorld Ordinary Full-History Selector-API Results

## Scope

This post-primary addendum removes the explicit binding sidecar and all prompt language
about TRI, commitment, temporal authorization, Preserve, or Reevaluate. The ordinary
selector API returns one stable ID; the runner observes that normal tool result as binding.
Todoist and Simple Note each contribute eight custom AppWorld-backed tasks.

## Results

| App | Model | Rows | Strict | Correct write | Bind opp. | Conditional TRI | Wrong write |
|---|---|---:|---:|---:|---:|---:|---:|
| simple_note | Pro/zai-org/GLM-5.1 | 8 | 8/8 | 8/8 | 8/8 | 0/8 | 0 |
| simple_note | Qwen/Qwen3.5-122B-A10B | 8 | 6/8 | 7/8 | 6/8 | 0/6 | 1 |
| todoist | Pro/zai-org/GLM-5.1 | 8 | 8/8 | 8/8 | 8/8 | 0/8 | 0 |
| todoist | Qwen/Qwen3.5-122B-A10B | 8 | 6/8 | 7/8 | 6/8 | 0/6 | 1 |

## Combined Attribution

Across 32 trajectories, strict success is 28/32 and authorized writes are 30/32. There are 28 correct, correctly timed selector bindings and 0 conditional TRI errors. Preserve/Flip is 0/6.

Qwen makes two wrong writes, one in each application, on the same Preserve template.
It calls sync before the first selector API, then selects and writes the refreshed
winner. The matched Stable rows use the same incorrect order but still write A because
the winner is unchanged. The Stable/Flip pair therefore identifies a real masked
pre-binding temporal-order error rather than post-binding referent drift.

## Interpretation

No conditional post-binding TRI occurs in the 28 auditable opportunities. Qwen makes two real Preserve/Flip wrong writes because it synchronizes before the first selector call on one instruction template; matched Stable rows have the same ordering error but the unchanged winner masks the target consequence. These are pre-binding temporal-order errors, not referent drift after a correct binding.
This experiment is less measurement-intrusive and closer to ordinary function calling,
but it remains a custom opportunity-conditioned benchmark and does not estimate
uncontrolled deployment prevalence.
