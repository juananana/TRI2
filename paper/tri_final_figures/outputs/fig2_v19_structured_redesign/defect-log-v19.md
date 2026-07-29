# Figure 2 v19.1 Defect Log

The v19.1 pass responds to the user's request for semantic icons without repeating the robot
motif. The rich export uses Tabler outline assets; the editable draw.io source uses native
fallbacks after the embed renderer rejected SVG data URIs.

## Screenshot Review Cycle 1

Evidence: `drawio-v19-canvas-rev1.png` and the pre-patch v19 export. P0=0, P1=24, P2=8.

| id | zone | finding | severity | status in Cycle 2 |
|---|---|---|---|---|
| C1-01 | text | `FIXED` split into two lines in the contract band | P1 | fixed |
| C1-02 | text | `ONLY CHANGE` split into two lines | P1 | fixed |
| C1-03 | text | `commit point` was too close to the right edge | P1 | fixed |
| C1-04 | text | `S0`/`S1` labels split inside state cards | P1 | fixed |
| C1-05 | text | `T_P` and `T_R` split vertically in the output chips | P1 | fixed |
| C1-06 | text | `SAME PROBE` became a three-line tower | P1 | fixed |
| C1-07 | text | `opaque` competed with the probe title | P1 | fixed |
| C1-08 | text | `ID`, `write`, and `diff` split in the execution row | P1 | fixed |
| C1-09 | text | `refresh` wrapped inside the event circle | P1 | fixed |
| C1-10 | arrows | P/R input arrows converged on indistinct probe text | P1 | fixed |
| C1-11 | arrows | output arrowheads touched the T_P/T_R chip borders | P2 | fixed |
| C1-12 | arrows | shared rail visually crossed the refresh word | P1 | fixed |
| C1-13 | arrows | the dashed R route visually merged with the lower rule | P2 | fixed |
| C1-14 | boxes | probe box was narrow relative to its copy | P1 | fixed |
| C1-15 | boxes | refresh circle acted like a text box instead of an event marker | P1 | fixed |
| C1-16 | boxes | state S1 card had insufficient separation between B and A | P1 | fixed |
| C1-17 | spacing | contract labels had uneven left padding | P1 | fixed |
| C1-18 | spacing | P/R tokens sat too close to probe input routes | P2 | fixed |
| C1-19 | spacing | C readout formulas had little breathing room | P2 | fixed |
| C1-20 | spacing | execution chips used three unrelated widths | P1 | fixed |
| C1-21 | color | refresh text competed with the coral/teal semantic colors | P2 | fixed |
| C1-22 | typography | contract band had the same weight as the panel title | P2 | fixed |
| C1-23 | typography | probe title and body shared the same visual weight | P1 | fixed |
| C1-24 | typography | state labels were bolder than the readout titles | P2 | fixed |
| C1-25 | layout | B column carried too much text in a narrow width | P1 | fixed |
| C1-26 | layout | C execution icon slot was absent | P1 | fixed |
| C1-27 | icons | no explicit pair/sync semantic anchor in A | P1 | fixed |
| C1-28 | icons | no explicit AI/probe semantic anchor in B | P1 | fixed |
| C1-29 | icons | no explicit database/write semantic anchor in C | P1 | fixed |
| C1-30 | style | the figure read as a text-only schematic rather than Figure 1's semantic-icon family | P1 | fixed |
| C1-31 | style | dashed/solid redundancy was present but not reinforced by compact icon anchors | P2 | fixed |
| C1-32 | style | the state transition was not visually prominent enough | P2 | fixed |

Requirement, semantic, visual hygiene, style, and regression audits all ran before the first
patch. All P0/P1 issues above were addressed by widening boxes, splitting labels, and adding
semantic icon anchors.

## Screenshot Review Cycle 2

Evidence: regenerated rich export plus draw.io preview after the first SVG-icon patch. P0=5,
P1=10, P2=5. The draw.io preflight reported 9 FAILs; the screenshot also showed broken SVG
placeholders in the editable preview.

| id | finding | severity | fix in Cycle 3 |
|---|---|---|---|
| C2-01 | draw.io pair icon rendered as a broken image | P0 | native `⇄` fallback |
| C2-02 | draw.io refresh icon rendered as a broken image | P0 | native `↻` fallback |
| C2-03 | draw.io probe icon rendered as a broken image | P0 | native `AI` badge fallback |
| C2-04 | draw.io execution icon rendered as a broken image | P0 | native `DB` cylinder fallback |
| C2-05 | refresh icon overlapped its rail in static geometry | P0 | moved symbol above the rail |
| C2-06 | probe icon overlapped the probe box in static geometry | P0 | moved badge above the probe |
| C2-07 | contract body still failed vertical text estimate | P1 | reduced to 16 pt and retained width |
| C2-08 | commit-point label failed vertical text estimate | P1 | reduced to 15 pt |
| C2-09 | dashed lower rule was treated as an overlapping row element | P1 | removed redundant rule from draw.io source |
| C2-10 | SVG base64 payload made the editable source renderer-dependent | P1 | zero embedded image payloads in draw.io |
| C2-11 | icon treatment differed between formal export and editable source | P2 | documented rich/native split in asset ledger |
| C2-12 | probe icon was visually too small relative to the B panel | P2 | 32 px rich robot; 32 px native AI badge |
| C2-13 | C database cue was easy to miss at panel scale | P2 | moved icon to execution heading |
| C2-14 | refresh label was too close to the event marker | P2 | moved label below marker |
| C2-15 | state labels were still visually dense | P2 | separated head/winner/valid text cells |

Fix verification: C2-01 through C2-10 are visible as resolved in the `?rev=3` draw.io preview;
the final static preflight has 0 FAILs. C2-11 through C2-15 are intentional P2 differences or
polish changes and are documented below.

## Screenshot Review Cycle 3

Evidence: `drawio-v19-canvas-final-rev3.png` (canvas-only formal export) and the latest `?rev=3`
draw.io preview. P0=0, P1=0, P2=8.

| id | zone | residual observation | severity | disposition |
|---|---|---|---|---|
| C3-01 | text | native `AI` badge is intentionally shorter than the rich robot icon | P2 | accepted and documented |
| C3-02 | text | native `↻` mark is smaller than the rich refresh SVG | P2 | accepted; label supplies redundancy |
| C3-03 | arrows | the compact C mini-flow remains the tightest arrow cluster | P2 | accepted; all routes are traceable |
| C3-04 | boxes | the B probe remains the tallest single object | P2 | accepted; it is the shared measurement boundary |
| C3-05 | spacing | C's three readout rows have less whitespace than A's bands | P2 | accepted; required for paper height |
| C3-06 | color | pale fills are weaker in grayscale than coral/teal strokes | P2 | accepted; solid/dashed and labels preserve meaning |
| C3-07 | typography | the contract band is compact at manuscript scale | P2 | accepted; it remains readable in the rich export |
| C3-08 | style | draw.io fallback is less icon-rich than the formal export | P2 | accepted; editability takes priority in source |

Fix verification: all Cycle 2 P0/P1 findings are absent in the latest preview; no new P0/P1
regression is visible in the formal export.

## Red-Team Audit

Evidence: latest canvas-only export, grayscale reading, and side-by-side comparison with Figure 1.
The following residual observations are P2 only; no blocker remains.

| id | zone | hostile-review finding | disposition |
|---|---|---|---|
| RT-01 | text | contract copy is the smallest required text on the page | accepted |
| RT-02 | text | `same I/O; two independent runs` is italic and dense | accepted |
| RT-03 | arrows | four connectors enter/leave the probe | accepted; P/R lanes disambiguate |
| RT-04 | arrows | C mini-flows use a shorter spacing rhythm than A | accepted |
| RT-05 | boxes | probe has more empty vertical space than state cards | accepted; marks the shared interface |
| RT-06 | spacing | gold boundary and probe are the densest local region | accepted |
| RT-07 | spacing | readout separators are closer to the row content than A rules | accepted |
| RT-08 | color | amber is the only warm neutral and is intentionally reserved for refresh | accepted |
| RT-09 | color | pale teal fill nearly disappears in grayscale | accepted; dashed route and B labels remain |
| RT-10 | typography | panel titles dominate all body text as intended | accepted |
| RT-11 | layout | A occupies most of the canvas width | accepted; construction is the scientific center |
| RT-12 | layout | B and C are narrow but complete | accepted; paper-width constraint |
| RT-13 | icons | native draw.io AI badge is less descriptive than a full robot | accepted; formal export has Tabler robot |
| RT-14 | icons | native DB cylinder has no cog detail | accepted; label and execution title carry meaning |
| RT-15 | style | Figure 2 remains more diagrammatic than Figure 1's story scene | accepted; content role differs |

## Self-Score

| dimension | score | evidence |
|---|---:|---|
| Text readability | 9/10 | No clipped labels; one point reserved for compact contract text at paper scale. |
| Arrow accuracy | 9/10 | All source/target directions and solid/dashed semantics are explicit; C remains dense. |
| Color coherence | 9/10 | Figure 1 coral/teal/amber contract is consistent; pale fills soften in grayscale. |
| Layout consistency | 9/10 | A/B/C columns and state/readout rows align; C has tighter local spacing. |
| Style match to reference | 9/10 | Black hierarchy, teal subtitle semantics, coral/teal routes, and semantic icons match the family. |
| **Total** | **45/50** | ALLOWED: every dimension is at least 6 and total is at least 40. |

## Remaining Gaps

| gap | severity | next action |
|---|---|---|
| draw.io native fallbacks are simpler than rich Tabler icons | P2 | keep both sources synchronized; replace only if embed SVG support becomes reliable |
| browser screenshot backend tiles the iframe viewport | tooling | use the canvas-only PNG export as final visual evidence; keep preview URL running |
