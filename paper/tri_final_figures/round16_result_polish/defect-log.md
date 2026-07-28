# Result-Figure Defect Log

## Screenshot Review Cycle 1

Evidence: `cycle1/fig3_substitution_flow.png` and `cycle1/fig4_sqlite_outcome_tree.png`.
The audit treats both figures as one coordinated result-figure system.

### P0 - Blockers

No data, interval, clipping, or semantic-direction blocker was found.

### P1 - Visible defects

| id | zone | element | defect | planned fix |
|---|---|---|---|---|
| C1-01 | text | Fig. 2 panel-B `100` tick | Tick sits too close to the right canvas edge. | Extend x-limit/right breathing room. |
| C1-02 | text | Fig. 2 panel-B model/count labels | Labels dominate numeric ticks more than needed. | Reduce direct-label size slightly. |
| C1-03 | text | Fig. 2 panel-A DeepSeek/Qwen labels | Two two-line labels form a tight vertical block. | Add small label-only vertical offsets. |
| C1-04 | line | Fig. 2 panel-A CTA endpoints | Three interval stems and markers form a dense knot near zero. | Increase x offsets and lighten interval strokes. |
| C1-05 | line | Fig. 2 panel-B grid | Vertical grid lines visually compete with horizontal intervals. | Reduce grid linewidth/opacity. |
| C1-06 | texture | Fig. 3 fallback dots | Dots resemble isolated data points rather than a category texture. | Replace with sparse vertical hatch. |
| C1-07 | texture | Fig. 3 fallback segment | Dot texture crowds the value `5`. | Use line texture that avoids glyph-like dots. |
| C1-08 | texture | Fig. 3 reject segment | A single long slash looks accidental instead of categorical. | Use a sparse repeated backslash hatch. |
| C1-09 | color | Cross-figure teal | DeepSeek and Correct use the same exact teal family for different semantics. | Move Correct to a neutral cool blue-gray. |
| C1-10 | typography | Fig. 3 model labels | Qwen/GLM are regular ticks while model identities in Fig. 2 are bold direct labels. | Treat model names consistently as bold identity labels. |
| C1-11 | spacing | Fig. 2 panel-B title/legend row | Legend and title occupy the same narrow row with little separation. | Tighten legend and move it slightly right/up. |
| C1-12 | hierarchy | Fig. 3 panel-A legend | Swatch outlines are stronger than the bar segment outlines. | Reduce legend patch linewidth. |

### P2 - Polish findings

| id | zone | element | defect | planned fix |
|---|---|---|---|---|
| C1-13 | text | Fig. 3 `both 0/4` | Annotation is close to the overlapping Stable intervals. | Nudge left/up without detaching it from Stable. |
| C1-14 | text | Fig. 3 right direct labels | Labels use more right margin than necessary. | Move slightly toward endpoints. |
| C1-15 | text | Fig. 2 panel-A labels | Counts and model names have identical emphasis. | Keep name bold; reduce line spacing/count prominence. |
| C1-16 | line | Fig. 2 panel-A grid | Top 100% grid line reads like a top frame. | Lighten all grids consistently. |
| C1-17 | line | Fig. 3 Stable intervals | Two stems overlap nearly exactly. | Increase condition offsets slightly. |
| C1-18 | box | Fig. 3 legend swatches | Swatches are slightly tall relative to text. | Reduce handle height. |
| C1-19 | box | Fig. 3 bars | Segment borders are visible but slightly darker than plot lines. | Lighten outline and retain 0.38 pt width. |
| C1-20 | spacing | Fig. 2 panel-A left labels | Left padding is uneven across the three labels. | Use one x anchor and explicit y offsets. |
| C1-21 | spacing | Fig. 2 panel-B y labels | Two-line labels create a ragged left block. | Retain two lines but reduce size/line spacing uniformly. |
| C1-22 | spacing | Fig. 3 panel-A legend | Gap between title and legend is slightly tight. | Lower legend a small amount. |
| C1-23 | spacing | Fig. 3 panel-A bars | Large white gap between Qwen and GLM is a little loose. | Reduce y separation/ylim slightly if paper preview supports it. |
| C1-24 | color | Fig. 2 model fills | Filled markers are a little pale at full-size preview. | Keep pale fill but strengthen edges. |
| C1-25 | color | Fig. 3 Stable band | Band is barely distinguishable from white. | Increase alpha modestly. |
| C1-26 | color | Fig. 3 reject | Reject fill and grid share a close value. | Preserve hatch and slightly darker outline. |
| C1-27 | typography | Cross-figure titles | Fig. 2 and Fig. 3 use the same point size but different visual width/weight. | Keep size; shorten only if paper-scale audit requires it. |
| C1-28 | typography | Fig. 2 controller labels | Generic/CTA and numeric ticks have matching size but different roles. | Retain regular weight; add no extra emphasis. |
| C1-29 | layout | Fig. 2 panels | Panel A is visually denser than panel B. | Slightly reduce A label density and keep B compact. |
| C1-30 | layout | Fig. 3 panels | Panel B visually starts close to the y-axis label. | Check after paper insertion and adjust left margin only if needed. |
| C1-31 | style | Fig. 2 controller legend | Neutral CTA fill does not exactly match model-specific fills. | Keep neutral controller grammar but clarify through open/filled state. |
| C1-32 | icons | Both figures | No icons appear, unlike the method figure. | Accepted: icons have no quantitative semantic role here. |

### Five-dimension cross-check

- Requirement: data and endpoints are present; cross-figure identity needs the fixes above.
- Semantic: all lines connect within-model contrasts; no direction is reversed.
- Visual hygiene: no clipping, but texture and endpoint-density defects remain.
- Style: palette is coordinated; category/model color reuse and hatch grammar need refinement.
- Regression: source counts match the accepted figures; no numerical regression detected.

## Fix Verification - Cycle 1 to Cycle 2

| cycle-1 ids | status | screenshot evidence |
|---|---|---|
| C1-01, C1-02, C1-21 | fixed | Panel-B right tick has breathing room and direct labels are smaller. |
| C1-03, C1-04, C1-15, C1-20 | fixed | Panel-A label offsets and wider endpoint offsets separate the three models. |
| C1-05, C1-16 | fixed | Grid strokes are lighter and no longer read as a frame. |
| C1-06, C1-07, C1-08 | fixed | Dots are gone; fallback/reject use non-glyph line textures. |
| C1-09 | fixed | Correct now uses cool blue-gray rather than DeepSeek teal. |
| C1-10 | fixed | Model identity labels use coordinated bold/color treatment. |
| C1-11, C1-12, C1-18, C1-22 | fixed | Legend geometry and title-row spacing are lighter and more compact. |
| C1-13, C1-14, C1-17, C1-25 | fixed | Stable annotation/endpoints and right labels have more separation; band is visible. |
| C1-19, C1-23, C1-24, C1-26-C1-32 | fixed or accepted | Paper-scale review shows no clipping, numerical regression, or unjustified decoration. |

## Screenshot Review Cycle 2

Evidence: standalone cycle-2 PNGs plus compiled paper pages 5 and 6 in color and grayscale.

### P0 - Blockers

None. All values, denominators, intervals, and panel references match the source and caption.

### P1 - Visible defects

| id | zone | element | defect | planned fix |
|---|---|---|---|---|
| C2-01 | text | Fig. 2 panel-A direct labels | The 75% and 50% grid lines remain visible through the label block at paper scale. | Add a white label knockout with no visible border. |
| C2-02 | line | Fig. 2 grids | Grid remains slightly prominent in grayscale relative to data strokes. | Reduce grid alpha again. |
| C2-03 | texture | Fig. 3 fallback | Vertical hatch can be read as internal bar subdivision on the narrow `2` segment. | Replace with sparse horizontal hatch. |
| C2-04 | typography | Fig. 3 model y labels | 7.2 pt bold labels are slightly more dominant than the 7.0 pt model labels in Fig. 2. | Set both to 7.0 pt. |
| C2-05 | spacing | Fig. 3 right endpoint labels | Labels retain more right-side whitespace than necessary. | Move them 0.02 x-units toward the estimates. |

### P2 - Polish findings

| id | zone | element | finding | disposition |
|---|---|---|---|---|
| C2-06 | text | Fig. 2 panel-B controller legend | Legend is small but readable at 200 dpi paper scale. | Retain 7 pt minimum. |
| C2-07 | text | Fig. 3 legend | Legend is compact and remains readable at paper scale. | Retain. |
| C2-08 | line | Fig. 2 CTA zero intervals | Three estimates remain close by construction. | Marker shape and x offset adequately separate them. |
| C2-09 | line | Fig. 3 Stable intervals | Stems overlap in y but have separate x offsets and marker shapes. | Retain truthful geometry. |
| C2-10 | box | Fig. 3 reject texture | Backslashes are visible without looking like a heavy border. | Retain. |
| C2-11 | spacing | Fig. 2 two-panel gap | Gap is larger standalone but balanced after caption insertion. | Retain. |
| C2-12 | spacing | Fig. 3 bar rows | White space is generous but not wasteful at the current float height. | Retain. |
| C2-13 | color | Fig. 2 grayscale | Lines have similar luminance. | Marker shape and fill state provide redundant decoding. |
| C2-14 | color | Fig. 3 grayscale | Correct/fallback/reject fills are close in value. | Position, labels, and three distinct hatch grammars preserve decoding. |
| C2-15 | typography | Cross-figure panel titles | Same point size and weight survive insertion. | Retain. |
| C2-16 | layout | Manuscript page count | Figure replacements preserve the eight-page PDF. | Retain. |
| C2-17 | icons | Result figures | No icons used. | Correct: icons would be decoration, unlike Figure 1. |

### Five-dimension cross-check

- Requirement: model colors, fonts, units, and scope are now consistent.
- Semantic: all connectors are within-model condition/controller contrasts.
- Visual hygiene: no clip or overlap; five local refinements remain.
- Style: palette and typography match the extracted contract in color and grayscale.
- Regression: the compiled PDF remains eight pages and figure placement is unchanged.

## Screenshot Review Cycle 3

Evidence: `cycle3/fig3_substitution_flow.png`, `cycle3/fig4_sqlite_outcome_tree.png`, and the
cycle-3 compiled manuscript pages.

### Inventory

| id | zone | finding | severity | disposition |
|---|---|---|---|---|
| C3-01 | text | Figure 2A still labels both model and exact count although the count is duplicated in body text. | P1 | Remove exact counts from panel A. |
| C3-02 | typography | Figure 2A model/count blocks are all bold and compete with the panel title. | P1 | Keep model names only and use regular weight. |
| C3-03 | typography | Figure 2B model/count row labels are all bold. | P1 | Use regular weight; retain color and marker redundancy. |
| C3-04 | typography | Figure 3 model y labels are bold despite being ordinary category labels. | P1 | Use regular weight. |
| C3-05 | typography | Figure 3 `both 0/4` is a contextual annotation, not a headline. | P1 | Use regular weight. |
| C3-06 | hierarchy | Figure 3 segment counts remain sufficiently salient without full bold. | P2 | Use semibold only for count values. |
| C3-07 | hierarchy | Figure 3 changed-condition labels are the key quantitative conclusion. | P2 | Keep semibold; avoid bold. |
| C3-08 | color | Figure 2 remains distinguishable in grayscale by marker shape and fill. | P2 | Retain. |
| C3-09 | texture | Horizontal fallback and diagonal reject textures remain readable at paper scale. | P2 | Retain. |
| C3-10 | layout | No float shift or page-count regression occurred. | P2 | Retain. |

### User-found correction

The user explicitly identified that excessive exact labels and widespread bold weight were harming
the figure. This was missed by self-supervision cycle 3. The corrected interpretation is: exact
values should appear only where they are necessary to decode the estimand or denominator; bold
weight should identify panel hierarchy and focal outcomes, not every label.

