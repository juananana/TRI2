# Figure code snapshot

This directory keeps the plotting source beside the experiment-result snapshot used for figure
redesign. `plot_result_closure_v2.py` generates the two compact main-paper result figures from
`../data/figure_ready/` and writes PDF, SVG, 400-dpi PNG, grayscale, deuteranopia, and manifest
outputs to `../figure_outputs/result_closure_v2/`.

Run from the repository root:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/tri-mpl-result-v2 \
  python3 planning/TRI_experiment_summary_for_figure_redesign_20260728/figure_code/plot_result_closure_v2.py
```

The script validates all displayed counts, denominators, effects, and confidence intervals before
drawing. The manifest records SHA-256 hashes of the two source CSV files. The paper-facing source
copy is `paper/tri_final_figures/plot_result_closure_v2.py`; update both copies together when the
figure logic changes.

`plot_result_conditional_ab.py` generates the refined left/right Figure 4 from
`v7_shared_eligible_pairacc_and_substitution.csv` and writes its synchronized outputs to
`../figure_outputs/result_closure_v4/`. Its paper-facing source copy is
`paper/tri_final_figures/plot_result_conditional_ab.py`.

## Compact single-column result-figure lessons

Figure 4's refinement establishes the default review checklist for the remaining TRI result
figures:

- Start from the comparison the claim needs, then choose the smallest suitable mark set. Figure 4
  uses linked endpoints for within-model change and grouped bars for the resulting paired score.
- Keep paired panels visually balanced: equal panel widths, aligned baselines, one shared model
  encoding, and no duplicate legends.
- Let adjacent panels divide the work. Because Figure 4A already shows within-model controller
  changes, Figure 4B groups bars by controller to expose cross-model consistency; regrouping B by
  model would duplicate A and require another controller legend.
- When several series share an endpoint, use a small, consistent positional dodge so shapes and
  confidence intervals remain individually visible, then reduce the marker before enlarging the
  enclosing region. The ellipse denotes the condition, not an additional statistic.
- Use direct values only when they remain sparse and legible. Figure 4B places rounded percentages
  above the intervals and keeps exact counts in the caption and frozen result table.
- Remove encoding instructions such as `open`/`filled` from category labels when condition names
  and redundant shape/fill encoding are already clear.
- Remove arrows unless their direction has a defined analytic meaning. Axis order and linked marks
  already express the Generic-to-CTA comparison in Figure 4.
- Preserve a minimum 7 pt final-paper font, vector PDF output, embedded non-Type-3 fonts, and
  grayscale/color-vision-deficiency checks. Never solve crowding by shrinking essential text.
- Regenerate from frozen CSV/JSON inputs, assert every plotted value, and synchronize the paper
  source, experiment snapshot, PDF/SVG/PNG outputs, and manifest together.

The unified result pass adds `plot_result_closure_v5.py` for policy discrimination,
`plot_result_conditional_ab.py` for the boundary-aware conditional result, and
`plot_result_transfer_matrix_v6.py` for the selected non-forest transfer matrix. The round-17
SQLite matrix remains an unselected candidate under `figure_outputs/round17/`; the paper restores
the prior SQLite slope version. Selected outputs live under `figure_outputs/result_closure_v5/`
and `figure_outputs/result_closure_v6/`, and prior accepted PDFs remain versioned in
`paper/figure-backup/`.
