# Visual Spec

## Source
- Reference image: `<local-reference-image>`
- Target: `fig2_tri_diagnostic_workflow_v8_candidate.drawio`
- Canvas: 1800 x 720, landscape, no embedded caption.
- Font policy: Arial throughout; body >= 20 px.

## Global Style
- White background; three pale panels separated by white gutters.
- TRI palette from `style-extraction.md`.
- Rounded 2 px borders and 4 px semantic arrows.
- Solid coral Preserve; dashed teal Reevaluate.

## Regions
| id | bbox x,y,w,h | role | notes |
|---|---|---|---|
| panel_a | 20,16,860,688 | construct pair | summary, shared transition, two lanes |
| panel_b | 896,16,384,688 | run pair | identical probe under two independent runs |
| panel_c | 1296,16,484,688 | readouts | three numbered endpoint blocks |

## Text Blocks
| id | bbox | text | font | alignment | priority |
|---|---|---|---|---|---|
| a_title | 40,28,500,42 | A. Construct the matched pair | 34 bold | left | high |
| b_title | 916,28,330,42 | B. Run the pair | 34 bold | left | high |
| c_title | 1316,28,420,42 | C. Observable readouts | 34 bold | left | high |
| shared_strip | 44,78,808,56 | Shared across pair / only commitment timing changes | 24-26 | center | high |

## Shapes
| id | bbox | type | fill | stroke | notes |
|---|---|---|---|---|---|
| state_s0 | 212,160,214,104 | rounded rect | coral pale | coral | q(S0)=A |
| state_s1 | 556,160,270,104 | rounded rect | teal pale | teal | q(S1)=B; A remains valid |
| preserve_lane | 44,304,808,136 | rounded group | coral pale | coral | solid |
| reevaluate_lane | 44,456,808,136 | rounded group | teal pale | teal dashed | dashed |
| controller | 1002,226,166,260 | rounded rect | white | ink | black box, no internals |

## Connectors
| id | from | to | route | arrowheads | label | meaning |
|---|---|---|---|---|---|---|
| refresh_edge | state_s0 | state_s1 | straight | end | refresh | shared state change |
| preserve_path | bound_a | target_a | straight | end | bound before refresh | committed identity |
| reevaluate_path | deferred_q | target_b | straight dashed | end | resolve q on S1 | deferred selection |
| probe_p_in/out | P | controller / TP | orthogonal | end | none | Preserve run |
| probe_r_in/out | R | controller / TR | orthogonal dashed | end | none | Reevaluate run |

## Semantic Relations And Flow
| id | source | target | meaning | direction | evidence |
|---|---|---|---|---|---|
| SR1 | S0 | S1 | same transition used by both tasks | left-to-right | manuscript Methods |
| SR2 | A at S0 | A target | authorized persistence | left-to-right | Preserve definition |
| SR3 | q deferred | B target | authorized post-refresh resolution | left-to-right | Reevaluate definition |
| SR4 | outputs | readouts | observations, not controller internals | left-to-right conceptually | Measurements |

## Icons And Images
| id | bbox | meaning | status | plan |
|---|---|---|---|---|
| refresh_clock | 472,184,54,54 | refresh boundary | exact primitive | ellipse plus two hands |
| valid_marker | 736,218,26,26 | A action-valid | exact primitive | green check circle |
| write_db | 1372,572,58,56 | tool write | exact primitive | cylinder |
| state_diff | 1632,574,102,52 | state diff | exact primitive | rounded document box |

