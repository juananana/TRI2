# Figure 5 Handoff Lens Defect Log

## Cycle 1

The first handoff layout was rejected after full-size inspection. P0/P1 findings included: stage labels colliding with the title; Stable and Changed descriptors overlapping headings; ranking headers overflowing; model-call labels escaping their boxes; SQLite row labels colliding; result dots touching fractions; a detached footer; and an oversized title relative to the single-column canvas. The content was correct, but the rendered hierarchy was not usable.

Fixes: shortened text, separated title and stage rows, simplified ranking and row-diff labels, reduced type, removed duplicate lane prose, and collapsed the footer to two centered scope lines.

## Cycle 2

The second render made the execution route readable. Remaining P1 findings were: `HANDOFF` and `CALL` stage labels too close; the Changed heading touched the gate; model names, dots, and fractions were crowded; `compiled ID = A` overflowed its chip; and the full-count footer still competed with the route.

Fixes: renamed the stage to `GATE`, reduced the Changed heading, assigned fixed right-aligned fraction positions, shortened the chip to `bound ID = A`, widened that chip, and simplified footer wording.

## Cycle 3

The third render had no clipped text or box overlap. The remaining visible issue was semantic route hygiene: the plum bound-ID line crossed the Changed ranking card, making it look like ranking consumed the compiled ID.

Fix: rerouted the bound-ID path below the Changed card and into the gate chip. The line now bypasses ranking and terminates at the gate X, while the refreshed-winner path continues to `write(B)`.

## Final Red-Team Audit

| id | zone | finding | severity | disposition |
|---|---|---|---|---|
| RT-01 | text | Footer text is the smallest text in the figure. | P2 | accepted as scope annotation |
| RT-02 | text | Dot rows are compact at single-column scale. | P2 | exact fractions remain directly readable |
| RT-03 | arrows | The bound-ID path has no arrowhead. | P2 | intentional carried-state thread, not action flow |
| RT-04 | arrows | Stable and Changed fan-out paths have different curvature. | P2 | required by lane geometry |
| RT-05 | boxes | Ranking cards use three nested rectangles. | P2 | each rectangle encodes a real rank/validity state |
| RT-06 | boxes | SQLite is represented as row diffs rather than a database icon. | P2 | row-level consequence is more informative |
| RT-07 | spacing | The top stage row has more whitespace than the footer. | P2 | preserves title/stage hierarchy |
| RT-08 | spacing | Right result labels sit close to the page edge. | P2 | no clipping in PDF or PNG |
| RT-09 | color | Qwen and compiled-ID thread share plum. | P2 | model label and semantic thread are directly labeled |
| RT-10 | color | Deuteranopia simulation shifts coral toward yellow-green. | P2 | labels, routes, A/B identities, and fill state are redundant |
| RT-11 | typography | Title duplicates information expected in the caption. | P2 | retained for candidate review; removable on integration |
| RT-12 | layout | Stage 6 combines diff and result. | P2 | keeps the execution consequence in one terminal region |
| RT-13 | evidence | Wilson intervals are not shown. | P2 | exact small-sample counts are shown; CI remains caption text |
| RT-14 | evidence | Full 40-task outcome partitions are not marks. | P2 | paragraph/caption retain 27/8/5 and 26/6/2/6 |
| RT-15 | accessibility | Open-dot meaning is inferred from the filled-dot note. | P2 | `0/4` and `6/8` fractions remove ambiguity |

No P0 or P1 findings remain after the final route repair.

## Self-Score

| dimension | score | evidence |
|---|---:|---|
| Text readability | 9/10 | All essential labels and exact counts are readable; footer is intentionally smaller. |
| Arrow accuracy | 9/10 | Every action route has a clear source/target; bound ID now bypasses ranking and stops at the gate. |
| Color coherence | 9/10 | Forest Ember roles match the shared palette and survive grayscale through labels/fills. |
| Layout consistency | 9/10 | One shared setup, two aligned lanes, one gate, and attached terminal evidence. |
| Style match | 8/10 | Compact and paper-like; internal title may be removed during manuscript integration. |
| **Total** | **44/50** | Allowed for user selection. |

## Remaining Integration Work

- Do not replace `paper/Figures/fig4_sqlite_outcome_tree.pdf` until the user selects this structure.
- On selection, revise the caption from Panel A/Panel B language to the handoff-lens semantics and compile at actual column width.
