# Figure 2 v18 Diagram Brief

## User Goal

- Output: a paper-readable, editable TRI Figure 2 that matches Figure 1's visual family.
- Audience: AAAI reviewers reading a 0.95-text-width figure in a two-column paper.
- Must communicate: one fixed changed-winner transition, two valid commitment times, one opaque probe, withheld gold information, and three observable slices.
- Must not do: imply an internal model mechanism, expose gold targets to the probe, duplicate the transition into unrelated panels, or display empirical results.

## Fit Decision

Adapt Figure 1's hierarchy and palette, not its literal envelopes, clouds, or character art. Figure 2 uses the same black-title/teal-subtitle treatment, a central illustrated scene, and a flat bottom explanation band. Its scientific center is `S0 -> refresh -> S1`, crossed by the solid Preserve and dashed Reevaluate identity threads.

## Source Inventory

| id | source | type | role | priority | use |
|---|---|---|---|---|---|
| S1 | `paper/Figures/fig1_shared_transition.pdf` | reference figure | style and hierarchy | must | title/subtitle, forest palette, central scene, bottom band |
| S2 | `paper/AnonymousSubmission2027.tex` Figure 2 section/caption | manuscript | content and terminology | must | fixed variables, valid-old-target condition, readout meanings |
| S3 | repository `AGENTS.md` | project contract | claim boundary | must | diagnostic rather than architecture; no internal-mechanism claim |
| S4 | `paper/tri_final_figures/AGENTS.md` | figure contract | publication QA | must | >=7 pt, vector PDF, embedded fonts, grayscale redundancy |
| S5 | v17 accepted candidate | prior figure | regression baseline | should | preserve verified semantics while increasing paper-scale readability |

## Requirement Traceability

| id | requirement | source evidence | level | visual encoding |
|---|---|---|---|---|
| R1 | central transition dominates | user goal + Figure 1 | must | enlarged state discs and amber refresh lens in the middle 40% |
| R2 | fixed within-pair contract is explicit | caption | must | top-left `FIXED: S0, S1, q, action, schema, I/O` |
| R3 | only commitment time changes | diagnostic definition | must | top-center direct statement plus two differently styled paths |
| R4 | Preserve commits to A before refresh | method | must | coral solid path, lock icon, `BIND A` label |
| R5 | Reevaluate resolves q after refresh | method | must | teal dashed path, hourglass icon, `DEFER q` label |
| R6 | A remains action-valid in S1 | denominator boundary | must | A remains in S1 with check icon and `A still valid` |
| R7 | same opaque probe/interface | matched design | must | one double-ring probe with P/R run markers and `same inputs` |
| R8 | gold is withheld | evaluation validity | must | vertical information screen, EyeOff icon, `NO GOLD INPUT` |
| R9 | three observables stay distinct | caption | must | separate PairAcc, conditional substitution, and execution columns |
| R10 | readable at final paper width | figure agreement | must | 960x400 design, required text >=15 pt before export |
| R11 | grayscale redundancy | figure agreement | must | solid/dashed routes, P/R labels, direct target labels, spatial lanes |

## Semantic Model

| id | entity or relationship | direction / cardinality | visual encoding | uncertainty |
|---|---|---|---|---|
| E1 | shared state update | `S0 -> refresh -> S1`, one-to-one | charcoal horizontal rail | none |
| E2 | Preserve commitment | instruction -> A at S0 -> A at S1 -> gold A | coral solid route | none |
| E3 | Reevaluate commitment | instruction -> refresh/S1 -> B -> gold B | teal dashed route | none |
| E4 | surviving old target | A persists in S1 and remains action-valid | coral A node plus green check | none |
| E5 | gold boundary | gold targets stop before probe | vertical gray screen + EyeOff | none |
| E6 | matched probe runs | P and R independently use the same probe | two labeled run tokens into one probe | none |
| E7 | probe outputs | probe -> `T_P` and `T_R` | solid/dashed output connectors | none |
| E8 | PairAcc | both pair members correct | `P -> A AND R -> B` | none |
| E9 | conditional substitution | correct initial A becomes final B | `A bound -> refresh -> B final` | none |
| E10 | execution subset | selected ID reaches write/state diff | `ID -> write -> state diff` | none |

## Style Extraction: Figure 1 Reference

### 1. Palette

| role | hex | used on |
|---|---|---|
| background | `#FFFFFF` | canvas and bottom band |
| primary wash | `#F1FAFA` | central shared scene |
| shared interface | `#407A7F` | subtitle and secondary headings |
| reevaluate | `#248D82` | deferred path, B, R run |
| preserve | `#C12A36` | committed path, A, P run |
| refresh accent | `#EABC6B` | refresh lens stroke |
| valid consequence | `#60AA84` | action-valid check |
| main stroke | `#264A56` | state/probe outlines and shared rail |
| muted rule | `#A9B6B8` | screen, separators, secondary nodes |
| heading text | `#0D0D0E` | title and readout headings |

Total distinct semantic colors: 8, plus white background and pale tints derived from them.

### 2. Typography

- Heading font: Arial, 27 pt, bold.
- Subheading font: Arial, 16 pt, bold italic.
- Section/direct-label font: Arial, 15-19 pt, bold.
- Small label/caption font: Arial or Times New Roman, 15 pt at source.
- Mathematical labels: Times New Roman, 15-16 pt, italic.
- Final insertion estimate: the 15 pt source minimum maps to about 7.2 pt at `0.95\textwidth`.

### 3. Shape Language

- Corner radius: subtle, about 6-8 px; no nested card system.
- Box stroke: 1.2-2.2 px; state outlines 2 px.
- Arrow stroke: 2.5-3 px; shared rail 2.6 px.
- Dash pattern: long dashes, approximately 8 px on / 6 px off.
- Shadow: none.
- Scene fill: very pale teal, visually below 15% saturation.

### 4. Layout Rhythm

- Canvas: 960x400, 2.4:1.
- Outer margin: 22-27 px.
- Gap between major regions: 18-30 px.
- Same-row gaps: 14-24 px when elements share a function.
- Internal padding: 8-12 px vertical, 10-16 px horizontal.
- Typical instruction block: about 202x61 px; state disc: 108x108 px.
- Grid alignment: 4 px.

### 5. Arrow Grammar

- Shared world update: straight charcoal arrow.
- Preserve: solid coral route with medium stealth head.
- Reevaluate: dashed teal route with medium stealth head.
- Probe I/O repeats the same solid/dashed grammar.
- Labels are direct and sit beside routes; no separate legend is required.

### 6. Icon Language

- Minimal Lucide outline icons, typically 18-34 px.
- Stroke width: 1.8-2 px.
- Icons inherit their semantic category color.
- Source: locally bundled `lucide`; no external network assets.

### 7. Density And Composition

- Diagram type: one integrated diagnostic scene plus a bottom readout band.
- Major regions: transition scene, gold/probe boundary, three-column readout band.
- Content density: medium-dense.
- Whitespace: moderate around the central transition, tighter at the gold/probe boundary.
- Panel labels: none.
- Legend: none; direct labels and line styles carry semantics.
- Caption: LaTeX only, not embedded in the graphic.

## Semantic Justification

| element | visual form | method meaning | each unit corresponds to | justified? |
|---|---|---|---|---|
| state discs | circles with candidate nodes | pre/post-refresh candidate states | one node = one available entity | yes |
| amber lens | circular refresh control | the one shared world-state update | one lens = one refresh event | yes |
| coral solid thread | continuous route | Preserve's pre-refresh binding to A | one route = one pair member | yes |
| teal dashed thread | discontinuous route | Reevaluate's post-refresh resolution to B | one route = one pair member | yes |
| target crosshairs | labeled gold markers | expected referent for each pair member | one target = one gold outcome | yes |
| information screen | vertical rule + EyeOff | gold targets are unavailable to the probe | one screen = one input boundary | yes |
| P/R tokens | two labeled circles | independent matched probe invocations | one token = one task run | yes |
| readout band | three unframed columns | three different observable slices | one column = one estimand | yes |

No token bars, matrices, decorative color blocks, or icons without a named semantic role are used.

## Open Assumptions

| assumption | risk | verification |
|---|---|---|
| A 960x400 source remains readable across 0.95 text width. | medium | compile paper and inspect page 5 in color/grayscale |
| The expressive Preserve bend does not imply an extra state. | low | direct `BIND A`, A nodes, and gold A target labels |
| The gold/probe boundary can be dense without ambiguity. | medium | standalone, draw.io, and paper-page screenshots |
| A simplified draw.io edit source may omit decorative icons while retaining semantics. | low | compare `drawio-final.png` with the rich PDF and audit all entities/arrows |
