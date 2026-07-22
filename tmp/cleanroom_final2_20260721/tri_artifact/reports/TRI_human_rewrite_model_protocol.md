# TRI Independent Human-Rewrite Model Evaluation Protocol

Frozen after completion of the human construct study and before any model call on this dataset.
This is a post-human exploratory OOD evaluation, not part of the pre-specified TRI-v3 primary
comparison.

## Question

Do the Generic, Historical Compile-then-act, Lifecycle-free, and Lifecycle-Gated patterns persist
when the instruction is independently rewritten by a volunteer rather than selected from the
author templates?

## Frozen data

- Source tasks: `human_validation/selected_sources.jsonl` (50 sampled TRI-v3 scalar tasks).
- Rewrites: `human_validation/paraphrase_authoring.csv` (one independent rewrite per source).
- Evaluation data: `data/temporal_referent_human_rewrites_v1.jsonl`.
- SHA-256: `9cd91c908fb9e76938277459a5ec8a78e7c406d91c77034e203084d719697e39`.
- The data builder changes only `instruction`, retains the source instruction for audit, and adds
  `text_variant=independent_human_rewrite`.
- No task, rewrite, gold label, prompt, parser, or interpretation rule may change after the first
  model response.

## Controllers and models

Run unchanged TRI-v3 implementations for:

1. Generic Structured Ledger;
2. exact historical Compile-then-act;
3. Lifecycle-free actor;
4. Lifecycle-Gated.

Use Qwen3.5-122B-A10B and GLM-5.1 with the frozen TRI-v3 inference settings: temperature zero,
thinking disabled, 1,200 output tokens, existing timeout/retry policy. A four-item balanced smoke
checks endpoint and parser health only; smoke responses cannot trigger prompt edits.

## Estimands

- exact benchmark-gold accuracy on all 50 rewrites;
- accuracy against the determinate human majority for rewrite items;
- benchmark-gold sensitivity on human-majority and unanimous-gold subsets;
- anchored/dynamic, explicit/implicit, update, and template slices;
- wrong-target, invalid-target, and unnecessary-rejection counts;
- paired discordances and exact McNemar tests;
- request counts, retries, and API errors.

The all-50 result is primary for this exploratory addendum. Human-supported subset results are
sensitivity analyses and may not replace unfavorable all-item outcomes.

## Interpretation

- If pre-refresh compiled methods retain a clear advantage over Generic, the mechanism is not
  limited to the original author templates.
- If Historical CTA and Lifecycle remain tied, retain pre-refresh compilation as the main
  accuracy mechanism.
- If Lifecycle loses its advantage or human-majority alignment, narrow language-generalization
  claims and report the failure.
- Invalid-target rejection remains a normative policy outcome because the human study found low
  agreement on that slice.
