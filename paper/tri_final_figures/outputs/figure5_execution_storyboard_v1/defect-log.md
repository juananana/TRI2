# Figure 5 Defect Log

## Screenshot Review Cycle 1

### P0 Blockers
| id | zone | finding | status |
|---|---|---|---|
| C1-01 | layout | Strict evidence was detached from the SQLite branches, so the visual still read as two assembled panels. | fixed in cycle 2 |
| C1-02 | semantics | Stage 3 used coral globally, implying every model write was erroneous, including the Stable route. | fixed in cycle 2 |
| C1-03 | semantics | `row A expected` did not clearly state whether row A was actually modified. | queued for cycle 3 |

### P1 Visible Defects
| id | zone | finding | status |
|---|---|---|---|
| C1-04 | composition | Two full-width evidence boxes were visually dominant but encoded only four exact counts. | fixed in cycle 2 |
| C1-05 | composition | The method and evidence regions had no direct connector or shared alignment. | fixed in cycle 2 |
| C1-06 | data hierarchy | `0/4`, `8/8`, and `6/8` were not attached to the executed database rows that generated them. | fixed in cycle 2 |
| C1-07 | typography | Decisive strict counts were the same size as surrounding prose. | improved in cycle 2; queued for cycle 3 |
| C1-08 | layout | Large evidence boxes contained excessive unused horizontal space. | fixed in cycle 2 |
| C1-09 | data hierarchy | The compact 40-task totals looked like footnotes rather than a frozen outcome partition. | fixed in cycle 2 |
| C1-10 | color | Amber refresh introduced a yellow family the user had previously rejected. | fixed in cycle 2 with plum |
| C1-11 | visual grammar | The lower evidence boxes repeated a dashboard/card grammar instead of the execution path. | fixed in cycle 2 |
| C1-12 | semantics | `strict opportunities` appeared far from the counts it qualified. | improved in cycle 2; queued for cycle 3 |
| C1-13 | table | Qwen and GLM 40-task partitions were prose strings, slowing cross-model comparison. | fixed in cycle 2 |
| C1-14 | table | Correct, TRI, fallback, and reject categories had no shared columns. | fixed in cycle 2 |
| C1-15 | spacing | Bottom section had a large gap between the conclusion line and the ledger. | fixed in cycle 2 |
| C1-16 | style | Refresh and error branches did not clearly use the selected D palette roles. | fixed in cycle 2 |
| C1-17 | claim boundary | The 40-task context was visually subordinate enough to be missed. | fixed in cycle 2 |
| C1-18 | labels | Figure title emphasized the setup but not the executed consequence. | fixed in cycle 2 |

### P2 Polish
| id | zone | finding | status |
|---|---|---|---|
| C1-19 | text | Subtitle was slightly small at single-column preview size. | queued for cycle 3 |
| C1-20 | text | Stage labels were not equally prominent. | improved in cycle 2 |
| C1-21 | arrows | Tiny junction circle was visually stronger than necessary. | accepted; it denotes the shared branch point |
| C1-22 | arrows | Changed branch used a longer route than Stable and needed a clearer endpoint. | fixed by attaching evidence to row B |
| C1-23 | boxes | Database row miniatures lacked a strong grouping cue. | improved with aligned `SQLITE` labels |
| C1-24 | color | Neutral database rows were close to the page background. | accepted; strong outline preserves visibility |
| C1-25 | typography | Upper state and write labels could use slightly stronger weight consistency. | fixed in cycle 2 |
| C1-26 | spacing | Stable and Changed labels sat nearer to write blocks than to the full lane. | accepted; they label the action lane |
| C1-27 | layout | Canvas height was larger than needed for one-column placement. | fixed: 760 to 650 px |
| C1-28 | table | Reject zero for Qwen was implicit rather than explicit. | fixed in cycle 2 |
| C1-29 | table | Model identities and category identities competed for attention. | improved with row/column hierarchy |
| C1-30 | style coherence | The composition remained half flowchart and half two-box summary. | fixed in cycle 2 |
| C1-31 | caption boundary | Wilson uncertainty was not in the graphic. | accepted; exact counts are shown and CI stays in caption |
| C1-32 | accessibility | Color carried route meaning without enough direct textual redundancy. | fixed: Stable/Changed and row labels remain explicit |

## Fix Verification Cycle 1 → 2

All P0 and P1 items except C1-03 were visibly resolved in `figure5_execution_storyboard_cycle2_white.png`. C1-03 remained ambiguous and is promoted to the cycle-3 patch. No prior frozen count changed.

## Screenshot Review Cycle 2

### P0 Blockers
| id | zone | finding | status |
|---|---|---|---|
| C2-01 | semantics | `row A expected` is ambiguous about the observed database state. | queued for cycle 3 |

### P1 Visible Defects
| id | zone | finding | status |
|---|---|---|---|
| C2-02 | data hierarchy | Strict counts are readable but too small relative to their evidentiary importance. | queued for cycle 3 |
| C2-03 | grouping | Strict callouts use the same solid-box grammar as database rows and may be mistaken for DB records. | queued for cycle 3 |
| C2-04 | qualification | `STRICT OPPORTUNITIES` is detached beneath both callouts. | queued for cycle 3 |
| C2-05 | typography | Subtitle remains small at actual single-column scale. | queued for cycle 3 |
| C2-06 | color semantics | Stage 2 and Stage 3 are both plum, weakening stage differentiation. | queued for cycle 3 |
| C2-07 | table | Header, Qwen row, and GLM row need subtle rules to improve scanning. | queued for cycle 3 |
| C2-08 | table | Category values float in open space without a row baseline. | queued for cycle 3 |
| C2-09 | layout | Stable strict callout is slightly close to the neutral `row B unchanged` record. | queued for cycle 3 |
| C2-10 | layout | Changed strict callout needs a slightly stronger offset from `row B UPDATED`. | queued for cycle 3 |

### P2 Polish
| id | zone | finding | status |
|---|---|---|---|
| C2-11 | labels | `Qwen and GLM` should use `&` for compactness. | queued for cycle 3 |
| C2-12 | labels | Changed count line should visually emphasize the two fractions. | queued for cycle 3 |
| C2-13 | typography | `n = 40 per model` can move closer to the table title. | queued for cycle 3 |
| C2-14 | style | Bottom table could use the same restrained line grammar as the top separator. | queued for cycle 3 |
| C2-15 | color | Reject values need neutral, not high-emphasis, treatment. | already satisfied; verify after cycle 3 |
| C2-16 | accessibility | Callouts require dashed borders so color is not the only distinction from DB rows. | queued for cycle 3 |
| C2-17 | composition | The route is now integrated; remaining polish should not add a new panel or legend. | constraint for cycle 3 |

## Fix Verification Cycle 2 → 3

Cycle 3 resolves C2-01 through C2-14 and C2-16 in `figure5_execution_storyboard_cycle3_white.png`: row A is explicitly unchanged; strict counts use dashed evidence callouts and larger fractions; the qualifier is inside each callout; Stage 3 uses neutral ink; and the outcome table has aligned rules. C2-15 remains correctly neutral. No regression was observed in route direction or frozen counts.

## Screenshot Review Cycle 3

### P0 Blockers

None. All arrows terminate at the intended state, write, or database-row object; no text or object is clipped.

### P1 Visible Defects
| id | zone | finding | status |
|---|---|---|---|
| C3-01 | layout | Changed strict callout is wider than its text and reads as a detached empty container. | queued for final polish |
| C3-02 | data hierarchy | Changed fractions need one additional size step to match their claim importance. | queued for final polish |
| C3-03 | spacing | Changed callout should align more tightly under the changed SQLite miniature. | queued for final polish |

### P2 Polish
| id | zone | finding | status |
|---|---|---|---|
| C3-04 | typography | Subtitle is now readable but intentionally remains subordinate to the route. | accepted |
| C3-05 | arrows | Small branch hub remains visible; it is semantically necessary to show a shared refresh. | accepted |
| C3-06 | table | Table rules are intentionally neutral and do not compete with route arrows. | accepted |
| C3-07 | color | Plum appears only on refresh/fallback roles; this preserves the D palette and Figure 4 reference. | accepted |
| C3-08 | accessibility | Dashed callouts distinguish evidence from database-row objects without relying on color alone. | accepted |
| C3-09 | composition | Internal title consumes one line but helps the standalone preview; caption can be shortened later. | accepted for candidate |
| C3-10 | claim boundary | Wilson intervals are absent from marks but remain required in the manuscript caption. | accepted |

## Fix Verification Cycle 3 → Final Candidate

C3-01 through C3-03 are visibly resolved in `figure5_execution_storyboard_preview.png`: the Changed callout is reduced to 200 px, aligned directly beneath the changed SQLite miniature, and the 8/8 and 6/8 fractions are enlarged. The semantic route and table alignment did not regress.

## Red-Team Audit

The final canvas was rescanned as a hostile reviewer across all nine zones.

| id | zone | residual finding | severity | disposition |
|---|---|---|---|---|
| RT-01 | text | Subtitle is intentionally smaller than route labels. | P2 | accepted; readable in preview |
| RT-02 | text | Bottom boundary note is the smallest full sentence. | P2 | accepted; caption-level qualification |
| RT-03 | text | `SQLITE` repeats for the two branch-specific miniatures. | P2 | accepted; prevents branch ambiguity |
| RT-04 | arrows | Shared junction hub is small. | P2 | accepted; visible and semantically exact |
| RT-05 | arrows | Changed route is longer than Stable. | P2 | accepted; it encodes the actual branch geometry |
| RT-06 | boxes | Stable strict callout spans both state and write columns. | P2 | accepted; it summarizes the full strict branch |
| RT-07 | boxes | Database rows are not enclosed by a larger DB container. | P2 | accepted; direct row labels reduce decorative framing |
| RT-08 | spacing | Stage gaps are not mathematically equal. | P2 | accepted; stage widths differ semantically |
| RT-09 | spacing | Changed callout sits closer to the table separator than the Stable callout. | P2 | accepted; branch heights differ |
| RT-10 | color | Plum is reserved for refresh and fallback, not model identity. | P2 | accepted; role mapping is consistent |
| RT-11 | typography | Internal title could be moved to the caption in final integration. | P2 | defer until user selects structure |
| RT-12 | layout | Top route is denser than the exact-count table. | P2 | accepted; mechanism is the visual focus |
| RT-13 | layout | Table has no vertical grid lines. | P2 | accepted; aligned columns and two horizontal rules suffice |
| RT-14 | icons | No decorative database icon is used. | P2 | accepted; row-level records are more informative |
| RT-15 | style | Figure is a hybrid execution storyboard plus exact-count table. | P2 | accepted; this is deliberate and distinct from other figures |
| RT-16 | accessibility | Route meaning remains readable without color through Stable/Changed, A/B, and updated/unchanged labels. | P2 | verified |
| RT-17 | evidence | CIs are not visual marks. | P2 | accepted only if final caption retains Wilson 95% intervals |

No P0 or P1 findings remain.

## Self-Score

| dimension | score | evidence |
|---|---:|---|
| Text readability | 8/10 | All route, callout, and table labels are readable; subtitle and boundary note remain intentionally subordinate. |
| Arrow accuracy | 9/10 | Eight connectors have correct sources, targets, and heads; the branch hub is compact but visible. |
| Color coherence | 9/10 | Forest Ember roles are stable; every route also has direct textual redundancy. |
| Layout consistency | 9/10 | One continuous execution route feeds a compact aligned table; no overlap or clipping remains. |
| Style match | 9/10 | Muted Figure-4-like teal/coral/plum balance, direct labels, thin rules, no repeated result-chart grammar. |
| **Total** | **44/50** | Allowed for structural review. |

## Remaining Gaps

- This is a structural candidate and has not replaced the manuscript's formal Figure 5.
- Final integration must retain Wilson 95% intervals in the caption and verify the smallest text at actual LaTeX insertion width.
