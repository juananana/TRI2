# Figure 2 v17 Diagram Brief

## User Goal

- Output: a more expressive, self-explanatory, editable TRI Figure 2 whose visual quality is comparable to the current Figure 1.
- Audience: AAAI reviewers reading the main paper at two-column width.
- Must communicate: one shared changed-winner transition, two opposite commitment times, the same probe/interface, and three distinct observable endpoints.
- Must not do: become a controller architecture, expose gold fields as probe input, look like equal template panels, or use decorative clouds/cartoon agents.

## Fit Decision

Adapt Figure 1's visual grammar, not its literal objects. Figure 1's useful pattern is a large illustrative scene followed by a structured explanatory band. Figure 2 will adopt that hierarchy, palette, and semantic icon language while retaining a neutral diagnostic lens instead of Figure 1's clouds, envelopes, and robot.

## Source Inventory

| id | source | role | priority | use |
|---|---|---|---|---|
| S1 | current Figure 1 PDF | style and hierarchy | must | title/subtitle treatment, large scene, bottom explanation band, teal/coral/gray palette |
| S2 | current Figure 2 v16 | scientific content | must | verified labels, routes, probe boundary, readout definitions |
| S3 | manuscript Methods/caption | terminology | must | exact states, targets, fixed variables, and denominator boundaries |
| S4 | TRI AGENTS.md | constraints | must | diagnostic not architecture; gold withheld; old A action-valid; grayscale redundancy |

## Requirement Traceability

| id | requirement | visual encoding |
|---|---|---|
| R1 | center must dominate | upper scene occupies full width and about two thirds of height |
| R2 | one shared transition | enlarged `S0 -> refresh -> S1` rail at the scene center |
| R3 | commitment timing differs | coral solid path binds before refresh; teal dashed path resolves on S1 |
| R4 | A remains valid | A persists in S1 with an explicit check mark and text label |
| R5 | same probe | one magnifying-lens-style probe receives P/R in two independent runs |
| R6 | gold withheld | visible information screen between gold paths and probe inputs |
| R7 | estimands readable | three unboxed readouts distributed across a bottom band |
| R8 | Figure 1 family resemblance | black title, italic teal subtitle, illustrative center, semantic outline icons, muted background wash |

## Semantic Model

| element | meaning | connector semantics |
|---|---|---|
| Preserve instruction | bind A before refresh | instruction commitment, solid coral |
| Reevaluate instruction | defer q until after refresh | delayed resolution, dashed teal |
| S0/refresh/S1 | one shared world-state transition | state update, dark gray rail |
| gold target A/B | expected referent under each instruction | gold annotation only; never crosses the information screen |
| probe | same controller and observable interface | two independent task runs |
| PairAcc | both pair members correct | all complete changed-winner pairs |
| conditional substitution | correct initial A becomes final B | eligible Preserve slice only |
| execution subset | selected target reaches a tool write | executed model-issued writes only |

## Style Contract Extracted From Figure 1

- Canvas aspect: target 1280 x 480 (2.67:1), closer to Figure 1's 2.14:1 than v16's 3.66:1.
- Background: white; main scene wash `#F1FAFA` / `#D6EEF0`.
- Preserve: `#B2242F` with solid 2.6-3 px curves.
- Reevaluate: `#318383` with dashed 2.6-3 px curves.
- Shared transition: `#3C535C`, 2.2-2.6 px.
- Main text: `#0D0D0E`; secondary text `#58585A`; muted `#7D8D91`.
- Title: Arial bold 25-27 px; subtitle Arial bold italic 14-16 px.
- Scene labels: 11-17 px; no scientifically necessary label below 9 px.
- Shapes: circular state snapshots, subtle-radius instruction sheets, no card grid and no shadow.
- Icons: coherent Lucide outline icons, 1.8-2 px stroke, semantic color.
- Bottom band: flat table-like explanation with rules and generous horizontal columns, echoing Figure 1's instruction table.

## Semantic Justification

| visual | represents | justified |
|---|---|---|
| instruction sheets | two matched task members | yes |
| state discs with entity nodes | candidate entities before/after refresh | yes |
| refresh database icon | controlled state update | yes |
| check on A in S1 | surviving action-valid old target | yes |
| crosshair targets | gold expected entity | yes |
| magnifying lens probe | diagnostic observation of one black-box interface | yes |
| bottom readout band | observable outputs and their denominator slices | yes |

## Open Assumptions

| assumption | risk | verification |
|---|---|---|
| A taller figure remains acceptable in the current page layout. | medium | compile the paper and inspect page count/reference start |
| Moving readouts below improves readability enough to justify extra height. | low | paper-scale render and side-by-side comparison with Figure 1 |
| A magnifying-lens probe does not imply internal mechanism access. | low | keep `black box` label and observable I/O text visible |
