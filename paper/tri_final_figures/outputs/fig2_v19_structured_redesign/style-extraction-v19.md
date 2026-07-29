# Figure 2 v19.1 Style Extraction

## Figure 1 Family Contract

| role | value | evidence / use |
|---|---|---|
| background | `#FFFFFF` | Figure 1 canvas |
| ink | `#264A56` | rails, outlines, shared labels |
| heading | `#0D0D0E` | panel titles and readout names |
| shared accent | `#407A7F` | fixed/shared labels and neutral readouts |
| Preserve | `#C12A36` | solid P lane, A target, P output |
| Reevaluate | `#248D82` | dashed R lane, B target, R output |
| refresh | `#EABC6B` / `#FFF5DE` | shared refresh event |
| neutral rule | `#A9B6B8` | dividers and withheld boundary |
| pale fills | `#F7FAFA`, `#F8E8E9`, `#DCEFF0` | neutral, Preserve, Reevaluate chips |

## Typography

- Panel title: Arial bold, 28 pt source.
- Panel/readout heading: Arial bold, 21-24 pt source.
- Workflow labels: Arial bold, 15-22 pt source depending on semantic weight.
- Notes: Arial italic, 11-20 pt source; all required manuscript labels remain readable in the rich export.

## Shape And Arrow Grammar

- Rounded boxes use a subtle 8 px arc and 1.5-1.8 px stroke.
- Shared rails are charcoal straight arrows; Preserve is coral solid; Reevaluate is teal dashed.
- No shadows, gradients, clouds, envelopes, or unlabeled color blocks.
- Panel dividers are neutral vertical rules; the gold boundary is a short neutral horizontal screen.

## Icon Language

- Rich export: Tabler outline SVGs, 24-32 px, recolored to the Figure 1 palette.
- Editable draw.io fallback: native symbols and shapes only, because the embed renderer showed broken `data:image/svg+xml` cells.
- Icon semantics are deliberately non-repetitive: pair/sync in A, one AI probe badge in B, database write in C.

## Semantic Justification

| element | meaning | encoding |
|---|---|---|
| pair/sync mark | matched pair contract | `arrows-right-left.svg` in rich export; editable `⇄` fallback |
| refresh mark | one shared state transition | `refresh.svg` in rich export; editable `↻` fallback |
| AI probe mark | same opaque measurement interface | `robot.svg` in rich export; editable `AI` badge fallback |
| database mark | executed state-diff/write subset | `database-cog.svg` in rich export; editable cylinder `DB` fallback |

The icons are semantic anchors, not decoration. No icon is repeated across every row.
