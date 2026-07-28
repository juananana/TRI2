# Figure 2 v16 Defect Log

## Screenshot Review Cycle 1

Screenshot: `outputs/fig2_v16_centered_final_candidate/fig2_tri_diagnostic_workflow_v16_centered.png`

### P0 - Blockers

| id | zone | defect | fix status after cycle 1 |
|---|---|---|---|
| C1-01 | arrows | shared `S0 -> refresh` edge is hidden behind the background ellipse | not fixed in cycle 2 |
| C1-02 | arrows | shared `refresh -> S1` edge is hidden | not fixed in cycle 2 |
| C1-03 | arrows | Preserve entry/binding edge is hidden | not fixed in cycle 2 |
| C1-04 | arrows | Preserve cross-refresh edge is hidden | not fixed in cycle 2 |
| C1-05 | arrows | Preserve target-A edge is hidden | not fixed in cycle 2 |
| C1-06 | arrows | Reevaluate defer-to-refresh edge is hidden | not fixed in cycle 2 |
| C1-07 | arrows | Reevaluate refresh-to-B edge is hidden | not fixed in cycle 2 |
| C1-08 | arrows | Reevaluate target-B edge is hidden | not fixed in cycle 2 |
| C1-09 | arrows | Preserve packet-to-probe edge is hidden | not fixed in cycle 2 |
| C1-10 | arrows | Reevaluate packet-to-probe edge is hidden | not fixed in cycle 2 |
| C1-11 | arrows | probe-to-`T_P` edge is hidden | not fixed in cycle 2 |
| C1-12 | arrows | probe-to-`T_R` edge is hidden | not fixed in cycle 2 |
| C1-13 | layout | ellipse outline crosses the fixed-variable contract row | fixed: border removed |
| C1-14 | text | action-valid note collides with the gold-target-B label | fixed: note moved to lower center |
| C1-15 | text | `T_P` wraps to two lines | fixed: output widened |
| C1-16 | text | `T_R` wraps to two lines | fixed: output widened |
| C1-17 | text | `WRITE` wraps to two lines | partial: changed to lowercase but still wraps in cycle 2 |

### P1 - Visible Defects

| id | zone | defect | fix status after cycle 1 |
|---|---|---|---|
| C1-18 | composition | central field reads as an empty container because its causal paths are absent | not fixed in cycle 2 |
| C1-19 | hierarchy | state snapshots appear as unrelated icons rather than one shared transition | not fixed in cycle 2 |
| C1-20 | hierarchy | target markers float without a visible relation to authorization timing | not fixed in cycle 2 |
| C1-21 | hierarchy | the probe appears as an isolated module rather than part of the matched diagnostic | not fixed in cycle 2 |
| C1-22 | color | heavy teal ellipse outline competes with coral/teal semantic routes | fixed: outline removed |
| C1-23 | spacing | ellipse top arc crowds the `same refresh` label | fixed: outline removed |
| C1-24 | text | action-valid qualifier is too close to the lower target crosshair | fixed: moved downward and left |
| C1-25 | icons | withholding icon lacks a clear boundary without the route context | pending route visibility |

### P2 - Polish

| id | zone | defect | disposition |
|---|---|---|---|
| C1-26 | typography | output labels are visually weaker than the probe ports | widened, retained compact size |
| C1-27 | spacing | S0 sits too close to the Preserve copy | fixed: state spine shifted right |
| C1-28 | spacing | refresh node is not centered between S0 and S1 | fixed: spine rebalanced |
| C1-29 | style | outline makes the scene look like another panel/card | fixed: fill-only scene |
| C1-30 | style | the readout strip feels detached because probe outputs lack connectors | pending route visibility |

## Fix Verification - Cycle 1

The background, state positions, target labels, and output widths visibly improved in cycle 2. The intended connector fix failed because the connector objects still rendered behind the background shape; C1-01 through C1-12 therefore remained blockers and were carried into cycle 2 rather than marked complete.

## Screenshot Review Cycle 2

Screenshot: `outputs/fig2_v16_centered_cycle2/fig2_tri_diagnostic_workflow_v16_centered.png`

### P0 - Blockers

| id | zone | defect | planned correction |
|---|---|---|---|
| C2-01 | arrows | `S0 -> refresh` still invisible | explicitly bring connector to front |
| C2-02 | arrows | `refresh -> S1` still invisible | explicitly bring connector to front |
| C2-03 | arrows | bound-A route into S0 invisible | explicitly bring connector to front |
| C2-04 | arrows | Preserve route across refresh invisible | explicitly bring connector to front |
| C2-05 | arrows | Preserve route to target A invisible | explicitly bring connector to front |
| C2-06 | arrows | defer-q route to refresh invisible | explicitly bring connector to front |
| C2-07 | arrows | Reevaluate route to B invisible | explicitly bring connector to front |
| C2-08 | arrows | Reevaluate route to target B invisible | explicitly bring connector to front |
| C2-09 | arrows | Preserve probe input invisible | explicitly bring connector to front |
| C2-10 | arrows | Reevaluate probe input invisible | explicitly bring connector to front |
| C2-11 | arrows | probe output to `T_P` invisible | explicitly bring connector to front |
| C2-12 | arrows | probe output to `T_R` invisible | explicitly bring connector to front |
| C2-13 | text | execution label `write` still wraps | shorten to `tool` |

### P1 - Visible Defects

| id | zone | defect | planned correction |
|---|---|---|---|
| C2-14 | composition | without routes, the middle remains a set of disconnected symbols | restore all semantic paths |
| C2-15 | style coherence | the figure does not yet reproduce Figure 1's single visual story | restore colored solid/dashed arcs as the dominant read |

## Fix Verification - Cycle 2

Cycle 3 changes the connector z-order explicitly rather than relying on insertion order. It also replaces the execution mini-label with `tool`, which is short enough to stay on one line at paper scale.

## Screenshot Review Cycle 3

Screenshot: `outputs/fig2_v16_centered_cycle3/fig2_tri_diagnostic_workflow_v16_centered.png`

### P1 - Visible Defects

| id | zone | defect | final status |
|---|---|---|---|
| C3-01 | text | withheld-information note is too small at paper scale | fixed: concise four-line wording and bounded placement |
| C3-02 | text | action-valid condition is undersized relative to its scientific importance | fixed: enlarged and widened to remain one line |
| C3-03 | text | conditional-substitution denominator is difficult to read | fixed: shortened while retaining every eligibility condition |
| C3-04 | text | execution denominator is difficult to read | fixed: increased font size |
| C3-05 | text | gold-target labels are weaker than the target markers | fixed: increased font size |
| C3-06 | text | solid/dashed legend is too faint | fixed: increased font size |

### P2 - Polish

| id | zone | defect | disposition |
|---|---|---|---|
| C3-07 | arrows | Preserve arc is visually dominant near S1 | retained: this is the primary authorization contrast and remains clear in grayscale |
| C3-08 | spacing | readout 2 is denser than readouts 1 and 3 | retained: its denominator is intrinsically longer and cannot be removed without changing the estimand |

## Fix Verification - Cycle 3

The final-candidate screenshot confirms that C3-01 through C3-06 are readable without introducing clipping. The first enlargement of the withholding note wrapped too close to the probe's `R` token; the final pass shortened its lines and constrained the text box above that token. No P0 or P1 issue remains unresolved.

## Red-Team Audit - Final Candidate

Screenshot: `outputs/fig2_v16_centered_final_candidate/fig2_tri_diagnostic_workflow_v16_centered.png`

All findings below are residual P2 tradeoffs, not hidden blockers.

| id | zone | finding | decision |
|---|---|---|---|
| RT-01 | text | the fixed-variable row is smaller than the main path labels | accept: it is a contract annotation, not the primary read |
| RT-02 | text | `same refresh, replayed twice` is intentionally muted | accept: the shared spine and caption repeat the fact |
| RT-03 | text | withholding details remain the smallest scientific annotation | accept: wording is complete and the caption repeats the gold boundary |
| RT-04 | arrows | coral and gray paths meet at the S0 A node | accept: both relations intentionally share the same resolved entity |
| RT-05 | arrows | coral and teal paths are dense around S1 | accept: this is the central changed-winner contrast; arrowheads remain traceable |
| RT-06 | arrows | probe input curves are close to the ellipse boundary | accept: they terminate cleanly and do not cross text |
| RT-07 | boxes | the probe ellipse is taller than neighboring state nodes | accept: it contains the observable input/output contract |
| RT-08 | spacing | the left matched-pair bracket has more whitespace than the probe region | accept: asymmetry prevents a return to equal template panels |
| RT-09 | spacing | target A/B markers are vertically farther apart than S0/S1 labels | accept: separation keeps the two gold outcomes unmistakable |
| RT-10 | color | the pale diagnostic wash has low contrast | accept: it groups the scene without competing with semantic paths |
| RT-11 | typography | the italic kicker is secondary to the main title | accept: hierarchy matches Figure 1's title/subtitle treatment |
| RT-12 | typography | readout 2 uses more lines than other readouts | accept: exact denominator boundaries are required |
| RT-13 | layout | the right evidence spine is visually narrow | accept: readouts must remain subordinate to the central diagnostic scene |
| RT-14 | icons | the execution `tool` label is shorter than the caption's `tool write` | accept: pen icon and execution heading supply the missing verb |
| RT-15 | style | the bottom solid/dashed legend is spatially distant from the upper Preserve path | accept: proximity to the lower route avoids crossing the main scene |

## Self-Score - Final Candidate

| dimension | score | evidence / deduction |
|---|---:|---|
| Text readability | 9/10 | all labels fit; the withholding and denominator annotations remain necessarily compact at paper scale |
| Arrow accuracy | 9/10 | every route has the correct source, target, direction, arrowhead, and solid/dashed semantics; S1 is intentionally dense |
| Color coherence | 9/10 | palette is directly adapted from Figure 1 and remains legible in grayscale; the grouping wash is deliberately faint |
| Layout consistency | 9/10 | one dominant scene and one evidence trail; residual asymmetry is intentional |
| Style match | 9/10 | matches Figure 1's hierarchy, palette, icon language, and central-story composition without copying its cloud/cartoon elements |
| **Total** | **45/50** | allowed for handoff |

## Remaining Gaps

No P0/P1 visual blocker remains. The readout-strip denominator text is compact because the figure must remain a single wide diagnostic overview; the LaTeX caption provides the full prose interpretation.
