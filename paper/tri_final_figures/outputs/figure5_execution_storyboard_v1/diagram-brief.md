# Figure 5 Execution Storyboard Brief

## User Goal
- Output: one editable, single-column scientific figure plus PNG preview.
- Audience: reviewers who need to understand the controlled SQLite experiment without reconstructing it from prose.
- Must communicate: correct initial bind A; refresh; Stable versus Changed winner; model-issued write; executed SQLite row; strict-case counts; 40-task context.
- Must not do: reuse dumbbells, forests, ordinary grouped bars, stacked panels, or decorative shapes without data meaning.

## Source Inventory
| id | source | type | role | priority | notes |
|---|---|---|---|---|---|
| S1 | `AnonymousSubmission2027.tex`, Executed target consequences | paper text | content and claim boundary | must | Frozen 40-task Generic-controller experiment. |
| S2 | `sqlite_model_facing_outcomes.csv` | frozen data | counts | must | Qwen 27 correct, 8 TRI, 5 fallback; GLM 26 correct, 6 TRI, 2 fallback, 6 reject. |
| S3 | current formal Figure 4 | paper figure | style reference | should | Muted purple/coral/teal balance and direct labeling. |
| S4 | Forest Ember palette | design decision | style contract | must | Stable model identity and semantic colors across figures. |

## Requirement Traceability
| id | requirement | source evidence | priority | visual encoding |
|---|---|---|---|---|
| R1 | show what experiment was run | user request | must | one left-to-right execution path with a refresh branch |
| R2 | show the connection from representation to execution | user request and S1 | must | explicit model-issued `write(id=...)` followed by SQLite row diff |
| R3 | show Stable control and Changed winner | S1 | must | two aligned lanes sharing the same initial bind and refresh |
| R4 | show decisive counts | S1/S2 | must | counts placed at the corresponding executed branch |
| R5 | preserve 40-task outcome context | S2 | should | compact footer ledger, not a second chart |
| R6 | remain distinct from Figures 3, 4, and 6 | user request | must | execution storyboard, no statistical endpoint plot |

## Semantic Model
| id | entity or relationship | direction | visual encoding | uncertainty |
|---|---|---|---|---|
| E1 | initial correct bind A | entry | filled A target node | none |
| E2 | refresh | E1 to branch | amber refresh lens | none |
| E3 | Stable winner A | refresh to safe write | upper teal lane | none |
| E4 | Changed winner B | refresh to wrong write | lower coral lane | none |
| E5 | model-issued write | lane state to DB mutation | code-like action block | none |
| E6 | SQLite row changed | write to final state | two-row DB miniature with highlighted row | none |
| E7 | strict evidence | branch outcome | direct exact counts | Wilson intervals remain in caption/table |

## Style Contract
| item | value |
|---|---|
| font | Arial; 18 px heading, 14 px stage, 12 px body, 10 px annotation |
| palette | ink `#264A56`; teal `#407A7F`; leaf `#60AA84`; coral `#E56D4E`; amber `#EABC6B`; gray `#D8D4CF` |
| fills | pale teal `#EAF2F0`; pale coral `#FBE6DF`; pale amber `#FFF5DE`; white background |
| strokes | 1.5 px normal, 2.5 px semantic routes; no shadows |
| shapes | subtle 8 px corners; target circles; one cylinder/table DB miniature |
| layout | 820 x 760 px; 30 px margin; medium density; generous lane separation |
| arrows | classic heads; solid teal for safe execution; solid coral for unauthorized route; gray for shared setup |

## Style Extraction: Current Figure 4 + Forest Ember

### Palette
| role | hex | use |
|---|---|---|
| background | `#FFFFFF` | canvas |
| primary | `#407A7F` | shared setup and model identity |
| valid result | `#60AA84` | Stable safe execution |
| error result | `#E56D4E` | Changed unauthorized write |
| refresh accent | `#EABC6B` | refresh operation |
| border / heading | `#264A56` | text and structure |
| neutral | `#D8D4CF` | secondary structure |

### Typography And Shape Language
- Arial/Helvetica-like sans serif; bold hierarchy only for headings and decisive counts.
- Subtle corners, 1.5 px box strokes, 2.5 px semantic paths, no shadow.
- Direct labels replace legends wherever possible.
- 30 px outer margin, 20--28 px region gaps, 12--16 px internal padding.

### Arrow Grammar
- Gray: shared experimental setup.
- Teal/green: authorized Stable execution.
- Coral: changed-winner substitution and wrong-row mutation.
- Every arrow has a concrete source, target, and execution meaning.

## Semantic Justification
| element | visual form | represents | each unit corresponds to | justified |
|---|---|---|---|---|
| A/B circles | target nodes | concrete entity identity | one selected database entity | yes |
| refresh lens | amber operation node | actual refresh between binding and action | one tool-loop refresh | yes |
| two lanes | aligned execution paths | Stable control and Changed winner | one frozen condition family | yes |
| DB rows | two-row table | executed mutation target | one entity row | yes |
| footer ledger | compact text/count strip | all 40 frozen outcomes | one model's aggregate run | yes |

## Open Assumptions
| assumption | risk | verification |
|---|---|---|
| strict path illustrates Preserve-like retained target A | could be read as all 40 tasks | label strict subset and keep 40-task totals separate |
| no CI drawn in the storyboard | uncertainty not visible in marks | retain Wilson-CI statement in manuscript caption |

