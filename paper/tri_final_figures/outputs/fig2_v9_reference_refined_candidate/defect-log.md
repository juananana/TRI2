# Figure 2 v9 Defect Log

## Cycle 1

- Reference structure successfully restored: three outer panels, two complete state lanes, legend,
  fixed/changed checklist, two independent probe runs, and three readouts.
- P0/P1 findings: Preserve/Reevaluate band headings fragmented; probe input labels fragmented;
  probe connectors ran diagonally to the box center; C2/C3 connectors were hidden behind filled
  readout containers; legend timing tags wrapped; controller/black-box labels wrapped.
- Fixes: reduced only affected local fonts, widened input boxes, added four probe I/O anchors,
  made C2/C3 containers transparent, and tightened legend labels.

## Cycle 2

- Verification: probe paths became horizontal; C2 and C3 arrows became visible; input and legend
  labels fit.
- Remaining P1 findings: Preserve title still broke across lines; the reference's bound/deferred
  band icons were absent; band typography lacked the original hierarchy.
- Fixes: reduced Preserve title locally and restored editable lock and clock primitives.

## Cycle 3

- Verification: all band text is readable, lock/clock icons render correctly, Reevaluate terminates
  at B, and every arrow has the intended source, direction, and endpoint.
- PDF check: LibreOffice font substitution preserved all line breaks and geometry. Embedded fonts
  are TrueType; no Type 3 fonts are present. `slides_test.py` reports no overflow.

## Red-Team Residual Audit

1. The figure is intentionally tall and information-dense, matching the supplied reference.
2. Panel B retains whitespace around the probe to keep the black-box boundary explicit.
3. Formula notation uses `T_P/T_R` instead of native LaTeX subscripts in the editable PPT.
4. The amber validity strip has no shield icon, but its condition is explicit in text.
5. The action is labeled rather than represented by a decorative pencil.
6. The probe withholding block uses precise text instead of crossed decorative icons.
7. Conditional-substitution denominator text is smaller because all four eligibility conditions remain visible.
8. Solid/dashed path redundancy remains valid in grayscale.
9. The old A and refreshed B are both visible in each S1 snapshot.
10. No results, model names, percentages, or controller internals are shown.

## Self-Score

| Dimension | Score |
|---|---:|
| Text readability | 9/10 |
| Arrow accuracy | 10/10 |
| Color coherence | 9/10 |
| Layout consistency | 9/10 |
| Match to supplied reference | 9/10 |
| **Total** | **46/50** |
