# Figure 2 v17 Defect Log

## Cycle 1

Screenshot: `outputs/fig2_v17_cycle1/fig2_tri_diagnostic_workflow_v17_expressive.png`

| id | zone | finding | severity | result |
|---|---|---|---|---|
| C1-01 | text | `MATCHED PAIR` breaks into unreadable fragments | P0 | fixed by moving it between instruction sheets |
| C1-02 | text | withheld note is a narrow six-line column | P1 | fixed by moving it to a horizontal boundary note |
| C1-03 | text | `one shared refresh` label is visually detached from refresh | P1 | fixed by moving it above the refresh node |
| C1-04 | text | bottom rule leaves a meaningless dash before its heading | P1 | fixed by starting the rule after the heading |
| C1-05 | text | execution heading drifts from manuscript term `Execution subset` | P1 | fixed |
| C1-06 | text | withheld wording omits `normalized` and `generator` qualifiers | P1 | fixed with exact field names |
| C1-07 | arrows | probe input arcs are visually heavier than necessary | P2 | reduced indirectly by shrinking probe area |
| C1-08 | arrows | probe output arcs dominate the output chips | P2 | reduced with smaller probe geometry |
| C1-09 | arrows | shared rail and Preserve arc are close near S0 | P2 | retained; both intentionally share A |
| C1-10 | arrows | paths are dense around S1 | P2 | retained with line-style and label redundancy |
| C1-11 | boxes | probe double ring is larger than state snapshots | P1 | fixed by reducing probe from 132 to 118 px |
| C1-12 | boxes | instruction sheets feel detached without a readable pair label | P1 | fixed by centered pair label |
| C1-13 | boxes | target A/B markers are smaller than their labels suggest | P2 | retained; crosshairs remain distinct |
| C1-14 | boxes | bottom metric columns have different internal density | P2 | retained because estimands differ |
| C1-15 | spacing | top shared-refresh label consumes unused right space | P1 | fixed by moving it to the state rail |
| C1-16 | spacing | bottom band begins too close to a short stray rule segment | P1 | fixed |
| C1-17 | spacing | pair label overlaps the left connector stem | P0 | fixed by horizontal relocation |
| C1-18 | spacing | withheld note approaches the probe R token | P1 | fixed by horizontal placement below the probe |
| C1-19 | spacing | two-independent-runs label competes with probe I/O line | P1 | fixed by moving it to the far right |
| C1-20 | spacing | target B label and action-valid note are close | P2 | retained; they remain non-overlapping |
| C1-21 | color | probe ring has too much dark visual weight | P1 | fixed by shrinking rings and icon |
| C1-22 | color | scene wash is much lighter than instruction fills | P2 | retained to keep grouping subordinate |
| C1-23 | color | bottom PairAcc uses blue while Preserve/Reevaluate use coral/teal | P2 | retained as readout-category encoding |
| C1-24 | typography | probe title rivals central state labels | P1 | fixed by reducing to 14 px |
| C1-25 | typography | `same controller + interface` is too close to the large probe | P2 | improved with probe shrink |
| C1-26 | layout | visual center drifts right toward probe | P1 | fixed by reducing and shifting probe |
| C1-27 | layout | main scene lacks a clear secondary-to-primary hierarchy | P1 | fixed by centralizing shared-refresh label |
| C1-28 | icons | probe icon is disproportionately large | P1 | fixed from 40 to 34 px |
| C1-29 | style | subtitle underline has no semantic function | P2 | removed in final pass |
| C1-30 | style | right readouts would have repeated v16's panel template | P2 | avoided by retaining the bottom explanatory band |

## Cycle 1 Verification

Cycle 2 resolves every P0/P1 except the probe's remaining dominance, which is carried forward explicitly.

## Cycle 2

Screenshot: `outputs/fig2_v17_cycle2/fig2_tri_diagnostic_workflow_v17_expressive.png`

| id | zone | finding | severity | result |
|---|---|---|---|---|
| C2-01 | layout | probe remains larger than each state snapshot | P1 | fixed in cycle 3 |
| C2-02 | layout | double probe ring remains the strongest dark shape | P1 | fixed in cycle 3 |
| C2-03 | text | withheld note lacks exact normalized/generator qualifiers | P1 | fixed in cycle 3 |
| C2-04 | text | probe I/O line is slightly low relative to ring | P1 | raised in cycle 3 |
| C2-05 | text | two-independent-runs label can use far-right whitespace better | P2 | retained after relocation |
| C2-06 | arrows | probe P input curve has a long sweep | P2 | shortened by probe/input shift |
| C2-07 | arrows | probe R input curve has a long sweep | P2 | shortened by probe/input shift |
| C2-08 | arrows | probe output curves appear symmetric but not identical | P2 | retained because P/R rows differ vertically |
| C2-09 | boxes | TP/TR chips sit far from the probe center | P2 | reduced by probe shift |
| C2-10 | spacing | probe heading has too much space above the ring | P1 | fixed |
| C2-11 | spacing | main scene right half remains slightly heavy | P1 | fixed by smaller probe |
| C2-12 | typography | probe title size competes with bottom headings | P1 | fixed |
| C2-13 | typography | exact withheld fields need one stable line | P1 | fixed |
| C2-14 | icons | scan icon dominates the probe's black-box label | P1 | fixed |
| C2-15 | style | subtitle underline remains decorative | P2 | removed after cycle 3 paper-scale check |

## Cycle 2 Verification

Cycle 3 confirms the probe no longer competes with the shared transition and all scientific wording is restored.

## Cycle 3

Screenshot: `outputs/fig2_v17_cycle3/fig2_tri_diagnostic_workflow_v17_expressive.png`

| id | zone | finding | severity | result |
|---|---|---|---|---|
| C3-01 | style | subtitle underline is decorative and absent from Figure 1 | P1 | removed in final candidate |
| C3-02 | text | withheld exact-field line remains compact | P2 | accepted; caption repeats the boundary |
| C3-03 | arrows | Preserve and shared rail meet at A | P2 | accepted; semantically required |
| C3-04 | arrows | dense fan-out at S1 requires careful tracing | P2 | accepted; solid/dashed and labels disambiguate |
| C3-05 | spacing | two-independent-runs label is far from P/R tokens | P2 | accepted; far-right whitespace keeps probe uncluttered |
| C3-06 | typography | bottom conditional denominator is the smallest readout text | P2 | accepted; it retains the complete eligibility slice |
| C3-07 | layout | instruction sheets are visually larger than target markers | P2 | accepted; they define the matched pair |
| C3-08 | color | pale wash nearly disappears in grayscale | P2 | accepted; grouping survives through layout and rules |

## Cycle 3 Verification

The final candidate removes C3-01 without changing scientific content. PPTX rendering confirms no overlap, clipping, or unwanted wrapping.

## Red-Team Audit

| id | residual observation | disposition |
|---|---|---|
| RT-01 | fixed-variable contract is smaller than route labels | accepted as secondary contract text |
| RT-02 | main title occupies substantial vertical space | accepted; mirrors Figure 1 and states the visual thesis |
| RT-03 | subtitle is italic and colored | accepted; matches Figure 1 hierarchy |
| RT-04 | state candidates are intentionally schematic | accepted; no empirical entity count is implied |
| RT-05 | Preserve sheet uses more saturated text than Reevaluate | accepted; palette follows Figure 1 |
| RT-06 | shared rail is partially adjacent to Preserve path | accepted; source/target semantics remain clear |
| RT-07 | S1 is the densest local region | accepted; it must show B wins while A survives |
| RT-08 | information screen has a very small EyeOff icon | accepted; label and caption carry the boundary |
| RT-09 | probe ring has two outlines | accepted; outer probe and inner diagnostic lens have distinct roles |
| RT-10 | TP/TR outputs do not directly arrow into all bottom readouts | accepted; the three readouts use different slices and should not be merged |
| RT-11 | bottom band uses vertical separators | accepted; they form one table-like explanatory band, not cards |
| RT-12 | PairAcc formula uses `AND` rather than a glyph | accepted for font robustness and plain-language readability |
| RT-13 | conditional denominator is long | accepted; shortening would remove eligibility conditions |
| RT-14 | execution boxes are the most UI-like shapes | accepted; they depict a real tool-write sequence |
| RT-15 | main scene wash extends farther right than the output chips | accepted; it unifies the full diagnostic scene |

## Self-Score

| dimension | score | evidence |
|---|---:|---|
| Text readability | 9/10 | all headline and route text is clear at paper scale; denominator notes remain compact |
| Arrow accuracy | 9/10 | shared update, solid Preserve, dashed Reevaluate, and probe I/O are directionally correct |
| Color coherence | 10/10 | palette and semantic mapping directly match Figure 1 |
| Layout consistency | 10/10 | one dominant scene plus one flat explanation band |
| Style match | 9/10 | strong Figure 1 family resemblance without copying clouds or cartoon agents |
| **Total** | **47/50** | allowed for handoff |

No P0/P1 defect remains.
