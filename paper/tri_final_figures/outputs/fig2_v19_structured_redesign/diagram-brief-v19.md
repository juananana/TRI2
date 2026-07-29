# Figure 2 v19 Diagram Brief

## User Goal

- Output: a major structural redraw of TRI Figure 2 that is orderly, large, and paper-readable.
- Audience: AAAI reviewers reading the figure at 0.95 text width.
- Must communicate: one matched pair, one shared world transition, two commitment rules, one opaque probe, withheld gold information, and three observable slices.
- Must not do: cross identity paths through labels, duplicate the shared transition, fragment the figure into decorative cards, or expose gold fields to the probe.

## Corrected Interpretation

The previous v17-v18 composition over-prioritized an expressive central scene. It forced the Preserve and Reevaluate paths, gold targets, information boundary, probe, and readouts into one crowded field. The redraw adopts the alignment discipline of the supplied `draw_learning` method figures and the larger A/B/C structure of v12-v15, while removing their repeated state rows and small explanatory text.

## Source Inventory And Fit

| id | source | role | fit decision | use |
|---|---|---|---|---|
| S1 | `paper/Figures/fig1_shared_transition.pdf` | palette and family style | adopt | black heading, teal accent, coral/teal semantics, pale fills |
| S2 | `draw_learning/01407-AAAI24.ZhaoA.pdf` (ExpeL) | layout reference | adapt | large aligned regions, clear panel hierarchy, restrained connectors |
| S3 | `draw_learning/accept_ACL_4820_Revealing_Procedural_Reas.pdf` (GSD) | layout reference | adopt | one horizontal baseline, short direct labels, strong region alignment |
| S4 | `draw_learning/26253-AAAI26.GuoZ-NLP.pdf` (MCP-AgentBench) | band reference | adapt | top/bottom process bands; reject hand-drawn decoration and density |
| S5 | `draw_learning/16627-AAAI26.WangZ-NLP.pdf` (MetaEval) | compact-flow reference | adopt | small number of direct arrows and short outcome labels |
| S6 | `draw_learning/accept_ICML_9079_The_Geometry_of_Narrow_Fi.pdf` | plot reference | reject | plot geometry does not match a diagnostic workflow |
| S7 | `draw_learning/KDD_3421_Mining_Point_of_No_Return.pdf` | plot reference | reject | phase-space plots do not match Figure 2 semantics |
| S8 | `draw_learning/accept_SymPareto_...pdf` | mechanism reference | reject | visually dense and topic-specific; would reintroduce clutter |
| S9 | v12-v15 TRI Figure 2 candidates | layout baseline | adapt | restore large A/B/C organization, remove repeated transitions and microtext |
| S10 | manuscript Figure 2 caption and project `AGENTS.md` | scientific content | adopt exactly | terminology, claim boundary, and denominator scope |

## Requirement Traceability

| id | requirement | planned encoding |
|---|---|---|
| R1 | Figure must be orderly | three fixed columns with vertical dividers and aligned panel headers |
| R2 | one shared transition | one central `S0 -> refresh -> S1` rail in panel A |
| R3 | two commitment rules | two parallel commitment bands above and below the shared rail; no crossings |
| R4 | fixed pair contract | one compact top band in panel A |
| R5 | A survives in S1 | explicit `A valid` badge inside the S1 state block |
| R6 | one probe, two runs | one rectangular probe with aligned P/R ports in panel B |
| R7 | gold withheld | a gray information boundary before the probe and direct label |
| R8 | three readouts | three equal-height rows in panel C with one formula/mini-flow each |
| R9 | paper readability | 1200x500 source; required source text 18 pt or larger |
| R10 | grayscale decoding | coral solid Preserve, teal dashed Reevaluate, direct P/R labels, fixed vertical lanes |

## Semantic Model

| relationship | source -> target | meaning | visual grammar |
|---|---|---|---|
| shared update | S0 -> refresh -> S1 | same world transition in both pair members | charcoal straight rail |
| Preserve commitment | P instruction -> bind A at S0 -> gold A | referent committed before refresh | coral solid upper band |
| Reevaluate commitment | R instruction -> resolve q at S1 -> gold B | referent selected after refresh | teal dashed lower band |
| surviving target | S1 contains B winner and A valid | old target remains action-valid | B teal badge + A coral outline badge |
| information boundary | gold side -> screen | gold mode/target not probe input | vertical gray rule + `GOLD WITHHELD` |
| probe run P | P -> same probe -> T_P | first independent matched run | coral solid horizontal row |
| probe run R | R -> same probe -> T_R | second independent matched run | teal dashed horizontal row |
| PairAcc | T_P=A and T_R=B | both pair members correct | formula row |
| substitution | A -> refresh -> B | eligible Preserve target replacement | three-node mini-flow |
| execution | ID -> tool write -> state diff | executed model-issued write | three-box mini-flow |

## Style Extraction

### Figure 1 Palette Contract

| role | hex | use |
|---|---|---|
| background | `#FFFFFF` | full canvas |
| ink | `#264A56` | outlines, shared rail, body labels |
| heading | `#0D0D0E` | panel titles and key readout names |
| shared accent | `#407A7F` | subtitle and fixed/shared labels |
| Reevaluate | `#248D82` | R band, B, dashed path |
| Preserve | `#C12A36` | P band, A, solid path |
| refresh | `#EABC6B` | shared refresh node |
| neutral rule | `#A9B6B8` | dividers and gold screen |
| shared wash | `#F1FAFA` | panel-A state field |

### ExpeL Layout Extraction

| parameter | extracted value | v19 decision |
|---|---|---|
| composition | one large left region plus two stacked right subfigures | use one large A region plus narrower B/C regions |
| density | medium, with large objects and short labels | match |
| corner radius | subtle 6-10 px | 6 px |
| box stroke | about 1.5-2 px | 1.5-2 px |
| arrow routing | mostly straight or short curved routes | straight/orthogonal only |
| whitespace | 18-28 px between functional regions | 20 px major gaps |
| typography | bold panel labels, compact body copy | 24 pt panel titles, 18-20 pt body |
| sampled fills | gray `#A2A3A2`, lavender-gray `#AFA7B6`, warm white `#FBF8F1` | do not adopt; Figure 1 palette has priority |

### GSD Layout Extraction

| parameter | extracted value | v19 decision |
|---|---|---|
| composition | one left-to-right problem/method pipeline | shared state rail uses one baseline |
| density | sparse-to-medium | match |
| boxes | sharp or very subtle corners | use 6 px radius |
| arrows | straight, medium heads, direct labels | match |
| region gap | about one object width | 18-24 px |
| typography | one bold method header and short italic annotations | short direct annotations only |
| sampled colors | blue-gray `#737D81`, pale amber `#F5ECD8` | map to project ink and refresh amber |

### MCP-AgentBench Layout Extraction

| parameter | extracted value | v19 decision |
|---|---|---|
| composition | two full-width horizontal bands | use three horizontal semantic bands inside panel A |
| container | dashed outer group with flat internal rows | no outer dashed group; use flat bands |
| arrow grammar | left/right flow with few vertical transitions | horizontal flow only |
| icon density | high, hand-drawn | reject; use direct labels and simple native shapes |
| sampled fills | warm gray `#DFDAD7`, pale rose `#FCF1ED`, muted teal `#ABBBB8` | map to project tints |

### MetaEval Layout Extraction

| parameter | extracted value | v19 decision |
|---|---|---|
| composition | compact stacked process and outcome rows | panel C uses three stacked equal-height rows |
| arrow grammar | short straight arrows | match |
| labels | brief nouns near endpoints | match |
| palette | mostly neutral with blue/green/red outcomes | preserve project coral/teal/gray instead |

## Synthesized Style Contract

| parameter | chosen value | evidence |
|---|---|---|
| canvas | 1200x500 | v12-v15 large structure with paper-safe height |
| columns | 700 / 210 / 230 px | ExpeL hierarchy + v15 A/B/C workflow |
| major gaps | 16-22 px | ExpeL/GSD whitespace rhythm |
| panel header | Arial 24 pt bold | reference hierarchy, paper scale |
| body | Arial 18-20 pt | maps to about 7-8 pt in manuscript |
| stroke | 1.5 px boxes, 2.4-2.8 px arrows | GSD/ExpeL line grammar |
| routes | straight/orthogonal; no long arcs | explicit user request for orderliness |
| palette | Figure 1 tropical-forest contract | project consistency |
| shadows | none | paper figure clarity |
| icons | native circles/labels only | avoid MCP-style visual noise |

## Semantic Justification

| element | visual form | represents | justified? |
|---|---|---|---|
| three columns | aligned workflow stages | construct, run, read evidence | yes |
| three panel-A bands | parallel horizontal lanes | Preserve, shared state update, Reevaluate | yes |
| state blocks | labeled state snapshots | S0 and S1 candidate/winner state | yes |
| refresh circle | shared update event | one refresh in both tasks | yes |
| one probe block | repeated measurement interface | same opaque probe in both runs | yes |
| three panel-C rows | aligned readout slices | three distinct observables | yes |

No decorative token bars, matrix grids, clouds, cartoons, or unlabeled colored blocks are permitted.

## Open Assumptions

| assumption | risk | verification |
|---|---|---|
| Parallel commitment bands communicate timing without identity arcs. | medium | three screenshot cycles and manuscript caption cross-check |
| A taller source will remain within the current page layout. | medium | compile and inspect final manuscript page/page count |
| Short denominator labels are sufficient inside the figure. | low | exact denominator remains in caption/body |

## v19.1 Icon Pass

The user requested semantic icons without repeating the robot motif everywhere. The rich
export therefore uses four different Tabler outline assets: pair/sync in A, one robot probe in
B, refresh at the shared transition, and database-cog only in the execution readout. The
editable draw.io source uses native fallbacks (`⇄`, `↻`, `AI`, and a `DB` cylinder) because the
embed renderer displayed the SVG data-URI cells as broken images. See `asset-ledger-v19.md` and
`style-extraction-v19.md` for provenance and the exact style contract.
