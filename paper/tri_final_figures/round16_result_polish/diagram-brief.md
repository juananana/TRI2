# Result-Figure Polish Brief

## User Goal

- Output: coordinated, publication-ready replacements for the two main-text result figures.
- Audience: AAAI reviewers reading a single-column figure at actual paper scale.
- Must communicate: the controller-conditioned substitution contrast, joint success, complete
  SQLite outcome accounting, and Stable-versus-Changed strict-opportunity rates.
- Must not do: change data or denominators, turn result charts into flowcharts, add decorative
  icons, imply prevalence, or overwrite the current accepted assets before QA.

## Source Inventory

| id | source | type | role | priority | notes |
|---|---|---|---|---|---|
| S1 | `AnonymousSubmission2027.tex` and compiled PDF | paper | content + insertion layout | must | Captions define scope and estimands. |
| S2 | summary CSV files | data | content | must | Sole source of plotted numbers. |
| S3 | current Figure 2 and Figure 3 PDFs | figure | baseline + regression | must | Preserve accepted comparison grammar. |
| S4 | three user-provided SCI-chart posters | raster references | style + advice | should | Learn hierarchy, restraint, units, and consistency; do not copy poster decoration. |
| S5 | user-selected pastel palette | explicit preference | style | must | Defines cross-figure model identity and outcome fills. |
| S6 | Draw.io Diagram Builder skill | workflow | audit process | must | Use source-role separation and screenshot defect cycles. |

## Requirement Traceability

| id | requirement | source evidence | level | planned encoding |
|---|---|---|---|---|
| R1 | Same model uses the same color and marker in every result panel. | user feedback | must | Qwen lavender circle; GLM coral square; DeepSeek teal diamond. |
| R2 | Same-level axis text uses one font size and regular weight. | user feedback + posters | must | 7.2 pt ticks; 7.6 pt axis labels; bold only for panel titles and direct result labels. |
| R3 | Every quantitative axis includes a unit. | posters | must | Percent sign retained in all quantitative axis labels. |
| R4 | Reduce visual interference. | posters | must | Soft grid, thin neutral strokes, no heavy black outlines, restrained hatch density. |
| R5 | Preserve grayscale decoding. | project instructions | must | Marker shape, fill state, hatch, and position supplement color. |
| R6 | Keep exact values and uncertainty intervals. | paper + project instructions | must | Regenerate directly from CSV; Wilson/bootstrap intervals unchanged. |
| R7 | One review-critical question per figure. | project instructions | must | Figure 2: substitution/joint success. Figure 3: executed outcome accounting. |
| R8 | Remain legible in the compiled single-column paper. | project instructions | must | Render standalone and manuscript pages at publication scale. |

## Semantic Model

| id | entity or relation | direction / hierarchy | visual encoding | uncertainty |
|---|---|---|---|---|
| E1 | model backend | repeated category | fixed color + marker across figures | none |
| E2 | Generic-to-CTA substitution contrast | within-model controller contrast | slope line and open-to-filled markers | none |
| E3 | Generic-to-CTA PairAcc contrast | within-model controller contrast | horizontal interval/dumbbell | none |
| E4 | complete final-state partition | mutually exclusive parts summing to 40 | proportional stacked bar | none |
| E5 | Stable-versus-Changed write rates | same endpoint under two opportunity types | point intervals with a light connector | connector is comparison, not time |
| E6 | outcome category | mutually exclusive semantic class | fill + sparse texture | none |

## Semantic Justification

| element | visual form | represents | each unit corresponds to | justified? |
|---|---|---|---|---|
| Figure 2 slope | line between controller points | change from Generic to CTA for one model | one endpoint = one controller estimate | yes |
| Figure 2 intervals | capped interval | 95% uncertainty interval | one interval = one model-controller estimate | yes |
| Figure 3 stacked segment | proportional rectangle | mutually exclusive final outcome count | one width unit = one task | yes |
| Figure 3 texture | hatch/dot pattern | redundant outcome-category code | one pattern = one outcome category | yes |
| Figure 3 connector | light line between Stable/Changed | contrast in the same strict-write endpoint | one endpoint = one opportunity type | yes, caption prevents temporal reading |
| Decorative icons | none | no quantitative meaning in result figures | n/a | no - excluded |

## Style Contract

| id | font | palette | stroke | marker/texture | layout density | source |
|---|---|---|---|---|---|---|
| C1 | DejaVu Sans | ink `#393642`, grid `#D5D3DF` | axes 0.65 pt | clean, no shadow | compact | current figures + references |
| C2 | 8.2 pt panel title | Qwen `#9995BE`/`#B6B3D6` | data 1.1 pt | circle | medium | user palette |
| C3 | 7.6 pt axis label | GLM `#DF706B`/`#F1837B` | interval 0.8 pt | square | medium | user palette |
| C4 | 7.2 pt ticks | DeepSeek `#519D9E`/`#9DC8C8` | segment 0.38 pt | diamond | medium | user palette |
| C5 | 7.2 pt legend/direct labels | category fills lavender/rose/peach/gray | hatch 0.26 pt | sparse hatch | compact | user palette + grayscale need |

## Open Assumptions

| assumption | risk | verification |
|---|---|---|
| The user wants result figures optimized, not the separately assigned first/problem figure. | scope drift | Leave Figure 1 untouched and state this in the audit. |
| Poster references specify principles more than an exact paper palette. | style mismatch | Use their restraint/hierarchy while honoring the user's explicit palette. |
| Light connectors will not be read as temporal trajectories. | semantic ambiguity | Caption remains explicit; direct condition labels and marker offsets are retained. |

