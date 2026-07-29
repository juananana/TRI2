# TRI Figure Working Agreement

These instructions apply to figure scripts, source data, previews, and exported assets in this
directory. They supplement the repository-level `AGENTS.md`. The current official AAAI author kit
and submission instructions always take precedence over local conventions or community advice.

## Design Priority

1. Preserve numerical accuracy, denominators, uncertainty intervals, and evidence scope.
2. Prevent overlap, clipping, ambiguous grouping, misleading axes, and mixed-denominator visuals.
3. Make the figure self-explanatory at its final inserted size.
4. Use space efficiently with compact, orderly structure and deliberate visual hierarchy.
5. Improve visual richness only when the chosen form matches the data-generating structure.

Do not use radar, flow, stacked, or decorative chart forms merely for variety. A more complex form
must communicate a real comparison, hierarchy, pairing, attribution, or trajectory more clearly
than a simpler alternative.

For result figures, prefer geometric evidence over prose: phase maps, uncertainty-aware slopes,
small multiples, distributions, heatmaps, or proportional flows. Boxes and arrows are appropriate
for a mechanism or system overview, but a result figure must not become a flowchart or a graphical
table. If exact values require many sentences inside the graphic, move them to the caption or a
table and let the figure show the pattern.

## Typography

- Use one consistent, commonly available font family across all paper figures. Prefer Helvetica,
  Arial, Times New Roman, or a compatible embedded Type 1/OpenType font.
- Export PDFs with all fonts embedded. Type 3 fonts are prohibited.
- Design toward 9--10 pt text at final publication size. Ten point is the preferred target when
  space permits.
- During exploratory submission-stage drawing, font size alone is not a blocking condition. A
  temporary minimum of 7 pt is allowed while layout and visual structure are being developed, but
  the figure must remain comfortably readable at its actual LaTeX insertion size.
- Before camera-ready delivery, recheck the then-current official AAAI requirements and raise text
  toward 9--10 pt wherever possible. Never retain text below 7 pt.
- Use larger type for the figure's conclusion or panel heading only when it does not consume space
  needed by data. Avoid oversized titles inside the graphic when the caption already supplies one.

## Color And Redundancy

- Figures must remain interpretable in grayscale and under common color-vision deficiencies.
- Never encode a comparison by color alone. Also use marker shape, fill state, line style, direct
  labels, or spatial grouping.
- Maintain strong foreground/background contrast. Treat a 4.5:1 contrast ratio as the project
  target for ordinary text and important labels.
- Avoid light green, yellow, or orange text on white. Use the established teal, coral, amber,
  charcoal, and neutral-gray palette consistently.
- For filled bars, areas, and color blocks, avoid a universal black or charcoal border. Use an
  outline from the same hue family that is slightly darker than the fill. Error bars or intervals
  drawn inside a colored mark should also use a darker tone from that mark's hue family. Reserve
  dark neutral ink for axes, reference lines, and structural marks that need neutral emphasis.

## Size, Export, And Lines

- Design at the intended publication width: approximately 8 cm for one column and 17 cm for two
  columns, subject to the current AAAI template.
- Prefer vector PDF for plots and diagrams. Raster assets must be at least 300 dpi at final size.
- Crop and size the asset in the figure-generation workflow. Do not rely on LaTeX `trim` or `clip`
  to repair the composition.
- Use visible strokes of at least 0.5 pt at final size. Avoid hairlines and very pale grid lines.
- Keep legends compact or replace them with direct labels when that reduces eye movement.

## Layout Requirements

- No text, marker, interval, connector, legend, or panel may overlap another element.
- No label may be clipped by the canvas or become unreadable after single-column reduction.
- Use line breaks, aligned columns, and concise labels to reduce unused whitespace.
- Keep related values adjacent and visibly separate different endpoints or denominators.
- State shared row definitions and denominators once in a compact header or key instead of
  repeating them at every y-axis tick. Keep repeated tick labels to the shortest unambiguous form.
- Do not connect independent metrics, datasets, or denominators in a way that implies a trajectory
  or common scale.
- Every figure must communicate one review-critical question. Its title, labels, and caption must
  identify the endpoint, denominator, comparison, and evidence status where relevant.
- Keep the in-figure text budget low. Use axis titles, short direct labels, and at most one compact
  legend. Do not repeat the caption as an internal title or subtitle.

## Required QA Before Paper Inclusion

1. Render the standalone PDF and inspect it at 100% and at its actual paper insertion width.
2. Render the complete manuscript page and check neighboring text, caption, float placement, and
   cross-column reading order.
3. Check all labels, markers, intervals, and canvas boundaries for overlap or clipping.
4. Inspect a grayscale rendering and a common color-vision simulation.
5. Run `pdffonts` and require every font to be embedded and no font to be Type 3.
6. Confirm vector output or at least 300 dpi for every raster component.
7. Verify every plotted number and denominator against the source report or generated data table.
8. Preserve the previous accepted version under a versioned filename; do not overwrite it until
   the replacement passes all checks.

Font-size refinement may follow structural refinement during drafting. All other accuracy,
embedding, non-overlap, grayscale, export, and verification requirements apply from the first
candidate figure onward.

## Method-Figure Representation Lessons

- First decide whether the paper needs a problem figure, a method figure, or both. A problem figure
  motivates the failure with a concrete case; a method figure must add the construction, execution,
  or scoring logic that the problem figure does not already show.
- Match the representation to the contribution type. For TRI, a generic component pipeline or
  controller architecture overstates the contribution and fragments the core idea. The more faithful
  representation is one controlled world-state transition with two referent threads layered over it.
- Prefer one integrated visual grammar over a row of interchangeable boxes. Use trajectories for
  world-state change, solid and dashed identity threads for binding state, a lens for the shared
  controller, a branch for the observable substitution error, and a database glyph for executed
  consequence.
- Make the scientific object, not the section list, the visual center. The shared refresh and crossed
  Preserve/Reevaluate threads should dominate; task specification and metric explanations should act
  as compact annotations around that center.
- Give every visual form a semantic job. Icons should identify object types (lock, deferred clock,
  controller, database), not decorate empty space. A new panel, border, or arrow is justified only
  when it encodes a distinct state, relation, or denominator.
- Use direct labels on trajectories and endpoints. Put evidence status, denominators, and detailed
  qualifications in the caption unless they are required to interpret the geometry.
- For the user-approved tropical-forest palette, use `#264a56` for primary ink, `#407a7f` for shared
  interfaces, `#248d82` for deferred/reevaluate paths, `#60aa84` for valid execution consequences,
  `#b4b87f` for neutral shared structure, `#eabc6b` for the refresh lens, `#f1a464` for warnings,
  and `#e56d4e` for Preserve and substitution errors. Preserve/Reevaluate must also differ by solid
  versus dashed line style.
- Inspect the final figure at its actual two-column width. Long technical labels should be shortened
  before reducing font size, and connectors must remain visible after Office/PDF z-order conversion.
