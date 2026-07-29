# Figure 2 v19.1 Asset Ledger

| id | source | path | usage | editability |
|---|---|---|---|---|
| pair_icon | Tabler Icons, MIT | `assets/icons/tabler/outline/arrows-right-left.svg` | matched-pair contract in rich PPTX/PNG | embedded SVG |
| refresh_icon | Tabler Icons, MIT | `assets/icons/tabler/outline/refresh.svg` | shared refresh event in rich PPTX/PNG | embedded SVG |
| probe_icon | Tabler Icons, MIT | `assets/icons/tabler/outline/robot.svg` | one AI probe marker in B | embedded SVG |
| execution_icon | Tabler Icons, MIT | `assets/icons/tabler/outline/database-cog.svg` | executed state-diff/write subset in C | embedded SVG |

## Editable Draw.io Fallbacks

| id | primitive | reason |
|---|---|---|
| pair_icon | text symbol `⇄` | avoids broken SVG data URI in embed.diagrams.net |
| refresh_icon | text symbol `↻` | keeps the event editable and small |
| probe_icon | native ellipse labeled `AI` | preserves the measurement-interface meaning without a broken image |
| execution_icon | native `shape=cylinder3` labeled `DB` | editable storage/write cue |

The browser preview path currently rejects the embedded SVG data-URI cells used by the rich
source, so the draw.io file intentionally uses these native fallbacks. The formal PPTX/PNG
uses the licensed Tabler SVGs above. No iconfont.cn asset was downloaded because the service
returned HTTP 429 during the previous attempt.
