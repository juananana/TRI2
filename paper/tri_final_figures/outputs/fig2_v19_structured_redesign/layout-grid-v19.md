# Figure 2 v19 Layout Grid

Canvas: 1400x500 px. Grid: 5 px. Outer margin: 20 px. The 1400 px width is the generated v19
source size; the earlier 1200 px note described the initial plan and is superseded here.

## Global Regions

| region | x | y | width | height |
|---|---:|---:|---:|---:|
| title band | 20 | 12 | 1160 | 48 |
| panel A | 20 | 72 | 690 | 408 |
| divider A/B | 720 | 76 | 2 | 398 |
| panel B | 735 | 72 | 205 | 408 |
| divider B/C | 950 | 76 | 2 | 398 |
| panel C | 965 | 72 | 215 | 408 |

## Panel A

| element | x | y | width | height |
|---|---:|---:|---:|---:|
| header | 20 | 72 | 690 | 35 |
| fixed contract | 30 | 112 | 670 | 45 |
| Preserve band | 30 | 170 | 670 | 82 |
| shared state band | 30 | 260 | 670 | 105 |
| Reevaluate band | 30 | 373 | 670 | 82 |
| instruction column | 45 | band y+14 | 160 | 54 |
| S0 column center | 300 | - | 105 | 76 |
| refresh column center | 465 | - | 65 | 65 |
| S1 column center | 555 | - | 115 | 76 |
| target column center | 655 | - | 40 | 40 |

Panel A arrow-free zones: header y=72-107; contract text y=112-157; all instruction-card text; state labels inside state blocks.

## Panel B

| element | x | y | width | height |
|---|---:|---:|---:|---:|
| header | 735 | 72 | 205 | 35 |
| gold boundary label | 745 | 112 | 185 | 28 |
| input P | 748 | 192 | 40 | 40 |
| input R | 748 | 342 | 40 | 40 |
| probe | 800 | 162 | 78 | 250 |
| output TP | 888 | 195 | 45 | 34 |
| output TR | 888 | 345 | 45 | 34 |
| interface note | 742 | 430 | 192 | 32 |

### v19.1 Icon Anchors

| semantic anchor | x | y | width | height | source |
|---|---:|---:|---:|---:|---|
| pair/sync | 44 | 79 | 24 | 28 | Tabler rich export; `⇄` draw.io fallback |
| refresh | 446 | 223 | 32 | 32 | Tabler rich export; `↻` draw.io fallback |
| AI probe | 924 | 122 | 32 | 32 | Tabler `robot` rich export; `AI` draw.io fallback |
| execution DB | 1330 | 368 | 24 | 24 | Tabler `database-cog` rich export; `DB` cylinder fallback |

All P/R connectors are horizontal and terminate on fixed probe ports. No connector may enter probe text.

## Panel C

| element | x | y | width | height |
|---|---:|---:|---:|---:|
| header | 965 | 72 | 215 | 35 |
| PairAcc row | 970 | 115 | 205 | 95 |
| separator 1 | 975 | 214 | 195 | 1 |
| substitution row | 970 | 222 | 205 | 115 |
| separator 2 | 975 | 342 | 195 | 1 |
| execution row | 970 | 350 | 205 | 115 |

Readout titles share x=985. Mini-flow endpoints share y baselines within each row. Slice labels are one line, centered, 18 pt.
