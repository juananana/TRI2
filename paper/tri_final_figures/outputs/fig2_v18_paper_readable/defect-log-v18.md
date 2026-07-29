# Figure 2 v18 Defect Log

The first three cycles audit the editable draw.io source. The final red-team audit also checks the richer PPTX/PDF manuscript version. Earlier cycle findings are retained for provenance.

## Cycle 1

Screenshot: `drawio-cycle-1.png` (1920x800 canvas-only export).

| id | zone | finding | severity | fix and verification in cycle 2 |
|---|---|---|---|---|
| C1-01 | text/icons | fixed-contract icon renders as a broken-image placeholder | P1 | Removed unsupported image cell; placeholder absent: FIXED |
| C1-02 | text/icons | commitment-time icon renders as a broken-image placeholder | P1 | Removed unsupported image cell; placeholder absent: FIXED |
| C1-03 | text | `REFRESH` is crowded inside the amber lens and touches the rail | P1 | Moved label above the lens: FIXED |
| C1-04 | text | probe copy collapses into `opaque same inputs` inside one box | P1 | Split probe title/body/input into distinct lines and locations: FIXED |
| C1-05 | text | `GOLD WITHHELD` collides with the B target and dashed arrowhead | P1 | Replaced with `NO GOLD INPUT` beneath the boundary: FIXED |
| C1-06 | text | all bottom headings and formulas run together as long sentences | P1 | Split each readout into title and body rows: FIXED |
| C1-07 | text | `FIXED: states...` is less explicit than the manuscript contract | P1 | Carried forward; fixed in final sync as `S0, S1...`: FIXED |
| C1-08 | text | Reevaluate wording says `q post-refresh`, which is terse and awkward | P1 | Changed to `resolve q after refresh`: FIXED |
| C1-09 | arrows | Preserve label sits tightly on the upper route | P2 | Retained as a direct route label; screenshot remains readable: ACCEPTED |
| C1-10 | arrows | Reevaluate arrowhead competes with the withheld-gold note | P1 | Moved note and isolated the target: FIXED |
| C1-11 | arrows | probe input curves disappear behind merged probe text | P1 | Split text and reduced internal density: FIXED |
| C1-12 | arrows | output connectors compete with `T_P`/`T_R` chip borders | P2 | Direct endpoints remain traceable after probe cleanup: ACCEPTED |
| C1-13 | arrows | shared rail visually crosses the in-lens `REFRESH` word | P1 | External label removes the crossing: FIXED |
| C1-14 | arrows/boxes | information boundary appears as a stray mark instead of a screen | P1 | Rebuilt as a continuous vertical rule: FIXED |
| C1-15 | boxes | probe is a text container rather than a clear black-box object | P1 | Reflowed to `SAME / PROBE / black box`: FIXED |
| C1-16 | boxes | Reevaluate block's final line is denser than Preserve's | P1 | Reworded and balanced line breaks: FIXED |
| C1-17 | boxes | gold B is visually attached to the withheld note | P1 | Added separation and moved note right/down: FIXED |
| C1-18 | boxes | refresh lens behaves like a labeled box instead of an event marker | P1 | Made lens hollow with external label: FIXED |
| C1-19 | spacing | gold/probe boundary has no stable gap | P1 | Introduced a continuous screen and separated labels: FIXED |
| C1-20 | spacing | bottom readouts have no visible column separation | P1 | Added vertical separators; final geometry verified in cycle 3: FIXED |
| C1-21 | spacing | PairAcc formula is too close to its heading | P1 | Moved formula to a dedicated baseline: FIXED |
| C1-22 | spacing | conditional-substitution text wraps into an oversized two-line block | P1 | Split title/body with concise body text: FIXED |
| C1-23 | spacing | execution copy consumes the entire right readout width | P1 | Split title/body; later shortened to `ID -> write -> state diff`: FIXED |
| C1-24 | color | broken-image placeholders introduce unrelated blue/green pixels | P1 | Unsupported image cells removed: FIXED |
| C1-25 | color | gold-withheld gray overlaps the teal target, reducing contrast | P1 | Moved note into neutral boundary region: FIXED |
| C1-26 | typography | bottom title and formula hierarchy is nearly flat | P1 | Titles enlarged and formulas placed on separate baselines: FIXED |
| C1-27 | typography | probe title, body, and input share one crowded weight | P1 | Applied three-level hierarchy: FIXED |
| C1-28 | typography | `opaque same inputs` wraps as an unintended phrase | P1 | `black box` stays inside; `same inputs` moves below: FIXED |
| C1-29 | layout | central transition loses focus because `REFRESH` covers its center | P1 | External label restores the state-transition spine: FIXED |
| C1-30 | style coherence | broken icons and sentence-like readouts break the Figure 1 family | P1 | Removed broken icons and rebuilt the flat explanation band: FIXED |

Cycle 1 audit: P0=0, P1=27, P2=3. Cycle 2 confirms every P1 except the explicit fixed-contract wording and final execution shortening, which remain tracked through the final sync.

## Cycle 2

Screenshot: `drawio-cycle-2.png` (1920x800 canvas-only export).

| id | zone | finding | severity | fix and verification |
|---|---|---|---|---|
| C2-01 | text | fixed contract still says generic `states` | P1 | Final sync names `S0, S1`: FIXED in `drawio-final.png` |
| C2-02 | typography | fixed-contract line is 14 pt while the final minimum is 15 pt | P1 | Raised to 15 pt: FIXED in `drawio-final.png` |
| C2-03 | text | execution body remains longer than necessary | P1 | Shortened to `ID -> write -> state diff`: FIXED in `drawio-final.png` |
| C2-04 | spacing/boxes | bottom separators appear as tiny specks rather than full rules | P1 | Rebuilt at stable 50 px height: FIXED in cycle 3 |
| C2-05 | arrows | Preserve route is visually dominant near the top band | P2 | Retained; it is the committed identity thread and remains below headings: ACCEPTED |
| C2-06 | arrows | Reevaluate label sits directly on the dashed route | P2 | Retained as direct labeling; no dash obscures the word: ACCEPTED |
| C2-07 | spacing | gold/probe boundary is the densest region | P2 | Retained; boundary, target, run token, probe, and output are distinct: ACCEPTED |
| C2-08 | spacing | P token is close to the probe input curve | P2 | Retained; solid coral encoding and label remain clear: ACCEPTED |
| C2-09 | spacing | R token is close to the probe input curve | P2 | Retained; dashed teal encoding and label remain clear: ACCEPTED |
| C2-10 | boxes | state discs are larger than instruction sheets' height | P2 | Retained to make the shared transition the visual center: ACCEPTED |
| C2-11 | icons | editable lens has no internal refresh icon | P2 | Retained as a simplified editable source; external `REFRESH` supplies meaning: ACCEPTED |
| C2-12 | color | pale amber lens has lower contrast than path colors | P2 | Retained so the update stays shared/neutral rather than competing: ACCEPTED |
| C2-13 | layout | fixed and timing headings do not form equal-width columns | P2 | Retained because they annotate different semantic spans: ACCEPTED |
| C2-14 | text | `NO GOLD INPUT` is not centered under the screen | P2 | Retained under the probe-side boundary where it reads most clearly: ACCEPTED |
| C2-15 | style coherence | editable source is less icon-rich than the PPTX/PDF | P2 | Intentional; draw.io prioritizes semantic editability, rich export carries Figure 1 detail: ACCEPTED |

Cycle 2 audit: P0=0, P1=4, P2=11. Cycle 3 verifies the separator repair; the three remaining text/source-sync P1 items are fixed after cycle 3 and verified in the final draw.io export.

## Cycle 3

Screenshot: `drawio-cycle-3.png` (1920x800 canvas-only export).

| id | zone | finding | severity | final verification |
|---|---|---|---|---|
| C3-01 | text | fixed contract still uses `states` | P1 | Now `S0, S1, q, action, schema, I/O`: FIXED |
| C3-02 | typography | fixed contract remains 14 pt | P1 | Now 15 pt: FIXED |
| C3-03 | text | execution body remains `target ID -> tool write -> state diff` | P1 | Now `ID -> write -> state diff`: FIXED |
| C3-04 | arrows | Preserve uses a long expressive upper route | P2 | Accepted; no text/box collision and direct label is visible |
| C3-05 | layout | gold/probe boundary remains locally dense | P2 | Accepted; information screen separates gold from inputs |
| C3-06 | icons | refresh lens relies on an external label | P2 | Accepted; label is directly above and shared rail passes through lens |
| C3-07 | spacing | P/R run tokens are compact relative to the probe | P2 | Accepted; labels and solid/dashed connectors remain legible |
| C3-08 | style coherence | draw.io omits some rich-version icons | P2 | Accepted; all required entities and relations remain editable |

Final verification screenshot: `drawio-final.png`. P0=0 and P1=0. The three source-sync fixes are visible; no regression appears in routes, targets, probe, or readout separators.

## Final Red-Team Audit

Evidence: `fig2_tri_diagnostic_workflow_v18_paper_readable.png`, grayscale export, `drawio-final.png`, `fig1-v18-side-by-side.png`, and final manuscript page 5.

| id | zone | hostile-review finding | severity | disposition |
|---|---|---|---|---|
| RT-01 | text | 15 pt source labels are close to the project's minimum after paper scaling | P2 | Verified at about 7.2 pt and readable on page 5 |
| RT-02 | text | `NO GOLD INPUT` uses two lines in the rich figure | P2 | Accepted; it avoids shrinking below the minimum and remains clear |
| RT-03 | text | `A still valid` is small relative to A/B node labels | P2 | Accepted; check icon and coral direct label provide redundancy |
| RT-04 | arrows | Preserve's angular path is more expressive than the shared rail | P2 | Accepted; it makes the commitment thread traceable without crossings |
| RT-05 | arrows | Reevaluate bends near the S1 candidate nodes | P2 | Accepted; dashed route does not cover labels or nodes |
| RT-06 | arrows | four short connectors converge around the same probe | P2 | Accepted; P/R spatial lanes and solid/dashed styles prevent ambiguity |
| RT-07 | boxes | the probe double ring carries more outline weight than the gold targets | P2 | Accepted; the probe is the shared measurement object |
| RT-08 | spacing | gold targets, screen, run tokens, and probe form the tightest local cluster | P2 | Accepted after page-scale inspection; no overlap or clipped label |
| RT-09 | spacing | bottom right formula has less left padding than PairAcc | P2 | Accepted; centered alignment balances the column visually |
| RT-10 | color | pale scene wash nearly disappears in grayscale | P2 | Accepted; grouping also follows spatial enclosure and bottom rule |
| RT-11 | color | coral and teal converge in luminance in grayscale | P2 | Solid/dashed routes, P/R labels, and upper/lower lanes preserve meaning |
| RT-12 | typography | title consumes more height than a caption-only figure would | P2 | Accepted to match Figure 1's in-figure hierarchy and state the visual thesis |
| RT-13 | layout | the left instruction blocks are denser than the central lens | P2 | Accepted; instructions require two-line semantics while lens is one event |
| RT-14 | icons | draw.io source omits rich-version Lucide detail | P2 | Accepted and documented; semantic labels and geometry are preserved |
| RT-15 | style coherence | Figure 2 is more diagrammatic than Figure 1's illustrative scenario | P2 | Accepted; side-by-side shows shared family without copying topic-specific art |

Final red-team result: 15 residual P2 observations, 0 P0, 0 P1. No blocker remains.

## Self-Score

| dimension | score | evidence / deduction |
|---|---:|---|
| Text readability | 9/10 | All necessary text is >=15 pt at source and readable on page 5; one point deducted because `NO GOLD INPUT` wraps to two lines. |
| Arrow accuracy | 9/10 | Every connector has a defined source/target and no collision; one point deducted for the expressive Preserve bend near S1. |
| Color coherence | 9/10 | Figure 1 palette is used consistently with grayscale redundancy; one point deducted because the pale scene wash largely vanishes in grayscale. |
| Layout consistency | 9/10 | One dominant transition and one flat readout band; one point deducted for unavoidable density at the gold/probe boundary. |
| Style match to reference | 9/10 | Title, subtitle, palette, refresh lens, scene, and bottom band match Figure 1; one point deducted because the editable draw.io source is intentionally less icon-rich. |
| **Total** | **45/50** | ALLOWED: every dimension >=6 and total >=40. |

## Remaining Gaps

| gap | severity | reason | next action |
|---|---|---|---|
| Preserve path remains visually expressive. | P2 | Straightening it would reduce identity-thread separation around S1. | Revisit only if a reviewer finds the bend confusing. |
| Gold/probe boundary remains the densest region. | P2 | It must show gold targets, withholding, matched runs, one probe, and two outputs. | Keep direct labels; do not add more detail. |
| Rich PDF and draw.io source differ in icon detail. | P2 | PPTX is the rich editable production source; draw.io is the simplified semantic edit source. | Preserve both sources in the handoff directory. |
