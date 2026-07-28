# Layout Grid

## Canvas
- width: 1800
- height: 720
- scale assumption: final two-column width about 17 cm
- margin: 20

## Grid Lines
| name | x | y | purpose |
|---|---:|---:|---|
| left_panel | 20 | 16 | panel A origin |
| mid_panel | 896 | 16 | panel B origin |
| right_panel | 1296 | 16 | panel C origin |
| heading_baseline | 40 | 28 | all panel titles |
| summary_band | 44 | 78 | fixed/varied strip |
| shared_transition | 44 | 150 | shared world-state band |
| preserve_lane | 44 | 304 | Preserve trajectory |
| reevaluate_lane | 44 | 456 | Reevaluate trajectory |

## Region Boxes
| id | x | y | w | h |
|---|---:|---:|---:|---:|
| panel_a | 20 | 16 | 860 | 688 |
| panel_b | 896 | 16 | 384 | 688 |
| panel_c | 1296 | 16 | 484 | 688 |

## Repeated Components
| family | count | cell size | spacing | start |
|---|---:|---|---:|---|
| trajectory endpoints | 4 | 62 x 62 | 500 horizontal | 224,342 |
| probe I/O cards | 4 | 70 x 62 | 170 vertical | 918,204 |
| readout blocks | 3 | 436 x 180 | 14 vertical | 1320,82 |

## Drawing Order
1. page and panels
2. summary/trajectory/readout containers
3. connectors
4. entity and icon primitives
5. text labels
6. small validity and slice annotations

