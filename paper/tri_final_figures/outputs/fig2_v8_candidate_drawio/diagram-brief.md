# Diagram Brief

## User Goal
- Output: an editable vector Figure 2 candidate plus a high-resolution preview.
- Audience: skeptical AAAI reviewers reading at two-column paper width.
- Must communicate: shared changed-winner transition; the sole Preserve/Reevaluate contrast;
  identical controller/interface across independent runs; PairAcc, conditional substitution, and
  execution-state-diff readouts with distinct slices.
- Must not do: depict TRI as a new controller architecture; imply hidden internal mechanisms;
  expose gold information as controller input; repeat result numbers; claim every winner ID is hidden.

## Source Inventory
| id | source | type | role | priority | notes |
|---|---|---|---|---|---|
| S1 | user reference PNG | screenshot | layout and density reference | high | Retain three-panel composition, not its scientific errors. |
| S2 | current manuscript | paper text | content and terminology | highest | Diagnostic Construction and Measurements define semantics. |
| S3 | project AGENTS.md | constraints | style and claim boundaries | highest | Figure 2 is workflow, not architecture; must remain legible. |
| S4 | current Figure 1 palette | project asset | style coordination | high | Coral Preserve, teal Reevaluate, amber refresh, green execution. |

## Requirement Traceability
| id | requirement | source evidence | level | planned visual encoding |
|---|---|---|---|---|
| R1 | show what is shared | user + manuscript | must | top strip: states, selector, action, schema, interface |
| R2 | show unique change | user + manuscript | must | coral label: commitment timing only |
| R3 | old target remains valid | manuscript | must | explicit S1 note beside A |
| R4 | same controller/interface | manuscript | must | two colored inputs enter one neutral probe |
| R5 | distinguish endpoints | manuscript | must | three numbered readout blocks with slice labels |
| R6 | do not imply architecture | AGENTS.md | must | black-box probe without internal modules/gears |
| R7 | redundant color encoding | AGENTS.md | must | coral solid vs teal dashed plus direct labels |

## Semantic Model
| id | entity or relationship | direction / cardinality | visual encoding | uncertainty |
|---|---|---|---|---|
| M1 | shared transition | S0 to S1, one-to-one | amber arrow with refresh label | none |
| M2 | Preserve | bound A at S0 to target A | solid coral trajectory | none |
| M3 | Reevaluate | deferred q to resolve at S1 to target B | dashed teal trajectory | none |
| M4 | controller comparison | two independent runs, same probe | parallel inputs and outputs | none |
| M5 | PairAcc | conjunction over complete pair | formula block | none |
| M6 | conditional substitution | A to refreshed winner B after correct bind | compact temporal trace | none |
| M7 | execution subset | selected ID to write to state diff | database/document primitives | none |

## Style Contract
| id | font | palette | stroke | icon style | density | source |
|---|---|---|---|---|---|---|
| ST1 | Arial/Helvetica | ink, coral, teal, amber, green, neutral gray | 2-3 px | editable outline primitives | medium-dense | reference adapted to TRI palette |

## Open Assumptions
| assumption | risk | verification |
|---|---|---|
| A wide 1800 x 720 canvas is readable at 17 cm. | body labels could shrink below 7 pt | inspect actual-width export before paper replacement |
| A single shared state transition is clearer than duplicated state snapshots. | may feel less literal than reference | 10-second blind-read check |

