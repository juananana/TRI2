# Figure 2 v16 Diagram Brief

## User Goal

- Output: a compact editable vector Figure 2 for the TRI AAAI paper.
- Audience: skeptical AAAI reviewers reading at two-column paper scale.
- Must communicate: one shared state transition, a matched Preserve/Reevaluate pair that differs only in commitment timing, the same controller probe/interface, and three observables with distinct denominator boundaries.
- Must not do: look like three assembled template panels, imply a controller architecture or internal mechanism, expose gold-only fields to the probe, or display empirical results.

## Source Inventory

| id | source | type | role | priority | notes |
|---|---|---|---|---|---|
| S1 | `paper/Figures/fig1_shared_transition.pdf` | current paper figure | style + composition | must | one dominant asymmetric scene; teal/red/gray palette; semantic icons |
| S2 | TRI `AGENTS.md` | project contract | content + boundaries | must | fixes Figure 2's scientific role and forbidden implications |
| S3 | v15 Figure 2 source/render | prior candidate | content inventory | must | retain verified labels and readout definitions; reject its three-panel composition |
| S4 | manuscript Diagnostic Construction section | paper text | terminology | must | exact state, target, probe, and denominator language |

## Requirement Traceability

| id | requirement | source evidence | priority | visual encoding |
|---|---|---|---|---|
| R1 | A single visual center | user feedback + Figure 1 | must | one large matched-diagnostic field occupying about 75% width |
| R2 | Same transition | TRI Figure 2 role | must | one shared `S0 -> refresh -> S1` spine, not duplicated lanes |
| R3 | Only commitment timing varies | diagnostic definition | must | one central split label with coral solid and teal dashed arcs |
| R4 | A remains valid in S1 | denominator boundary | must | A and B co-exist in S1; explicit action-valid note attached to A |
| R5 | Same probe/interface | matched comparison | must | paired P/R task tokens converge on one black-box probe |
| R6 | Gold is not probe input | evaluation validity | must | target cues remain on the gold-path side; EyeOff note below probe |
| R7 | Three estimands differ | metric definitions | must | narrow right-side evidence spine with formulas and denominator captions |
| R8 | Grayscale redundancy | accessibility | must | Preserve is coral + solid + lock; Reevaluate is teal + dashed + clock/refresh label |

## Semantic Model

| id | entity or relationship | direction / hierarchy | visual encoding | uncertainty |
|---|---|---|---|---|
| E1 | shared transition | `S0 -> refresh -> S1` | dark-blue horizontal spine | none |
| E2 | Preserve commitment | bind A before refresh | upper coral solid arc with lock | none |
| E3 | Reevaluate commitment | defer q, resolve on S1 | lower teal dashed arc with refresh marker | none |
| E4 | expected targets | Preserve=A, Reevaluate=B | small target endpoints separated from probe outputs | none |
| E5 | repeated matched runs | P and R independently use same interface | two input tokens feeding one probe | none |
| E6 | observed outputs | controller emits target IDs | `T_P` / `T_R` output chips | none |
| E7 | PairAcc | both outputs correct | first readout on evidence spine | none |
| E8 | conditional substitution | correct initial A becomes final B on eligible Preserve rows | second readout with compact A-to-B path and explicit slice | none |
| E9 | execution subset | selected ID becomes tool write and state diff | third readout on evidence spine | none |

## Style Extraction: Current Figure 1

### Palette

| role | hex | used on |
|---|---|---|
| background | `#FDFDFD` | full canvas |
| primary fill | `#D6EEF0` | shared diagnostic field |
| secondary fill | `#F7E8E8` | Preserve emphasis |
| accent / highlight | `#318383` | Reevaluate path and headings |
| contrast accent | `#B2242F` | Preserve path and A |
| border stroke | `#7FADB4` | central scene boundary and muted rules |
| arrow stroke | `#3C535C` | shared state transition |
| heading text | `#0D0D0E` | primary labels |
| body text | `#58585A` | explanatory labels |
| muted gray | `#95A3A6` | denominator notes and secondary rules |

Total distinct colors: 8.

### Typography

- Heading font: Arial, 20-22 px, bold.
- Subheading font: Arial, 14-16 px, bold.
- Body font: Arial, 10-12 px.
- Small label: Arial, 8-10 px.
- Mathematical symbols: Times New Roman, 11-14 px, italic where appropriate.

### Shape Language

- Corner radius: subtle, 8-12 px; no repeated card grid.
- Box stroke: 1.2-1.8 px.
- Main arrows: 2.4-3.0 px.
- Reevaluate dash pattern: visually long dashes, not dots.
- Shadow: none.
- Background-region fill opacity: visually about 55-70%.

### Layout Rhythm

- Outer margin: 18-24 px.
- Major-region gap: 20-28 px.
- Same-row gaps: 14-22 px.
- Internal padding: 8-12 px vertical and 10-16 px horizontal.
- Grid: approximately 4 px.

### Arrow Grammar

- Shared state update: straight dark-gray arrow.
- Preserve authorization: solid coral curved route.
- Reevaluate authorization: dashed teal curved route.
- Arrowheads: medium stealth.
- Labels sit adjacent to routes, never on top of arrowheads.

### Icon Language

- Minimal outline icons, 18-24 px, 1.8-2 px stroke.
- Icons inherit the semantic path color.
- Icons used only for commitment, refresh, probe/withheld information, and execution.

### Density and Composition

- Diagram type: asymmetric evaluation workflow centered on one state-transition scene.
- Major regions: one dominant scene plus one narrow evidence strip.
- Density: medium-dense.
- Whitespace: moderate and purposeful.
- Panel labels: none.
- Caption remains in LaTeX, not inside the figure.

## Semantic Justification

| element | visual form | represents | each unit corresponds to | justified? |
|---|---|---|---|---|
| central pale field | single bounded scene | the matched TRI diagnostic | one field = one fixed comparison contract | yes |
| S0/S1 circles | state snapshots | pre/post refresh candidate sets | one labeled node = one action-valid entity | yes |
| coral solid route | authorization path | binding A before refresh | one path = Preserve gold commitment | yes |
| teal dashed route | authorization path | deferring q to S1 | one path = Reevaluate gold commitment | yes |
| one probe ellipse | black-box measurement interface | same controller and observable interface | one ellipse = repeated use of one probe configuration | yes |
| three evidence nodes | ordered readout spine | three distinct measured slices | one node = one estimand | yes |
| icons | semantic anchors | lock, refresh, probe, withholding, write | one icon = one named operation | yes |

## Open Assumptions

| assumption | risk | verification |
|---|---|---|
| The Figure 1 palette is sampled from its rendered PDF and may differ slightly from source values. | low | compare final render side-by-side with Figure 1 |
| A 1280x350 source remains readable at 0.95 text width. | medium | inspect the actual compiled paper page |
| The narrow readout strip can retain denominator boundaries without becoming a card dashboard. | medium | three visual review cycles and paper-scale render |
