# Figure 5 Handoff Lens Brief

## User Goal

- Output: one compact result figure, not stacked subfigures.
- Audience: reviewers who must understand the experiment without reconstructing it from prose.
- Must communicate: bind A, refresh, Stable versus Changed ranking, the ID-to-action handoff, model call, SQLite row diff, and strict counts.
- Must not do: repeat dumbbells, forests, heatmaps, ordinary grouped bars, or a detached lower result panel.

## Source Inventory

| id | source | role |
|---|---|---|
| S1 | `AnonymousSubmission2027.tex`, Executed target consequences | claim and experiment semantics |
| S2 | `data/summary_csv/sqlite_model_facing_outcomes.csv` | frozen counts |
| S3 | `forest_ember_palette.py` | shared paper palette and model identities |
| S4 | user feedback on prior Figure 5 candidates | composition constraints |

## Requirement Traceability

| requirement | visual encoding |
|---|---|
| Show the full experiment | numbered left-to-right route from bound target to row diff |
| Make the connection explicit | narrow Gate column between ranking and model call |
| Show where the mechanism fails | plum bound-ID path terminates at an ember X while the B route crosses the gate |
| Keep Stable and Changed comparable | two aligned lanes sharing the same bind and refresh |
| Attach evidence to mechanism | exact-count dot rows beside the corresponding SQLite diff |
| Avoid another conventional result chart | ranking cards, execution calls, row diffs, and exact-count dots instead of axes or bars |

## Style Contract

- Forest Ember palette: ink `#264A56`, Qwen plum `#8B6F8E`, GLM coral `#E56D4E`, stable leaf `#60AA84`.
- White background, thin neutral structure, no shadows or decorative gradients.
- Direct labels and redundant text/shape encoding; no legend except the dot meaning.
- Physical size: approximately `3.35 x 2.55 in`; vector PDF/SVG plus 400-dpi PNG.

## Claim Boundary

- The strict paths show Stable `0/4` for both models and Changed `8/8` Qwen, `6/8` GLM.
- The full experiment is 40 tasks per model; aggregate partitions remain in the paragraph/caption.
- Model-issued SQLite writes are controlled consequences, not prevalence estimates.

