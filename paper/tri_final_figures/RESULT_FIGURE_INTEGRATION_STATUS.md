# TRI Result Figure Integration Status

This file records the selected result-figure assets currently integrated into the paper.

| paper figure | selected candidate | formal target | current formal state | caption action |
|---|---|---|---|---|
| Figure 3: policy discrimination | `outputs/figure3_palette_final_v3/figure3_palette_d_forest_ember.pdf` | `paper/Figures/result_policy_discrimination.pdf` | integrated composition chart | Complete; category names, Rule* boundary, and shared Forest Ember neutrals retained. |
| Figure 4: conditional substitution | `outputs/result_closure_v6/result_conditional_pairing_ab.pdf` | `paper/Figures/fig3_substitution_flow.pdf` | integrated direct endpoints plus PairAcc bars | Complete; no ellipse or decorative enclosure remains. |
| Figure 5: executed consequence | `outputs/figure5_integrated_profile_v1/figure5_integrated_profile.pdf` | `paper/Figures/fig4_sqlite_outcome_tree.pdf` | provisional integrated outcome/strict profile | Integrated for manuscript review; 3.35 x 2.16 in, minimum 7 pt; complete 40-task outcomes and Stable/Changed strict B-write rates share one percentage profile. Further visual optimization remains planned. |
| Figure 6: equal-call effects | `outputs/fig_submission_critical_pairacc_effects_v1.pdf` | `paper/Figures/fig_submission_critical_pairacc_effects.pdf` | integrated two-color grouped effect bars | Complete; 2.80 x 2.48 in source scaled to 0.97 column width; lavender/teal follow the paper palette, and the caption defines both baselines and separate denominators. |

## Proposed Caption Revisions

### Figure 4

Ten-schema outcomes after correct initial binding. A: Generic versus CTA substitution on rows eligible under both controllers (Wilson 95% CIs); open Generic and filled CTA endpoints are linked within model, and zero CTA estimates lie at the lower bound. B: changed-winner PairAcc over 80 pairs (cluster-bootstrap 95% CIs); labels are rounded percentages. Counts (Qwen/GLM/DeepSeek) are Generic 7/15/17 of 80 and CTA 31/66/64 of 80. CTA makes no common-eligible substitutions; neither endpoint is a safety rate.

### Figure 5

Complete 40-task SQLite outcomes and strict refreshed-winner writes for Generic. Outcome strips partition each model's trajectories into correct final states, strict B writes, fallback B writes, and unneeded rejections (left to right). Stable keeps A ranked first; Changed makes B first while A remains valid. Strict B-write rates use Wilson 95% CIs; exact fractions are 0/4 Stable for both models and 8/8 Qwen, 6/8 GLM in Changed. This controlled test is not a prevalence estimate.

### Figure 6

Post-primary equal-call changed-winner PairAcc effects. Left lavender bars: Convention told versus Plain history (40 changed pairs); right teal bars: Decision visible versus History only (32 actionable changed pairs). Whiskers are cluster-bootstrap 95% CIs. Inventories are separate and unpooled; side-by-side placement is descriptive.

## Integration Gates

- Keep versioned backups for every formal asset replacement.
- Keep each caption synchronized with the plotted geometry and denominator.
- Compile the main paper and verify float order, single-column readability, page count, embedded fonts, and no clipping.
- Re-run grayscale/CVD inspection and `git diff --check` after manuscript integration.

## Live Integration Validation

- The main paper and supplement compile successfully with TeX Live 2026 and the AAAI style.
- The formal main PDF is 8 pages; Figure 2 and Figure 3 appear on page 5, Figure 4 and Figure 5 appear on page 6, Figure 6 appears on page 7, and References start on page 8.
- The formal supplement is 34 pages; the reused Figure 5 strict-opportunity chart appears on page 23.
- Full-page renders show no clipped labels, figure overlap, float inversion, table overflow, or column overflow.
- Formal Figure 5 and Figure 6 sources now declare a 7 pt minimum text size; all labels remain readable at single-column insertion.
- All fonts in the integrated PDFs and the four result-figure PDFs are embedded; no Type 3 fonts remain.
- Formal Figure 3--6 hashes match their selected versioned candidates, and `git diff --check` passes.
- The current non-figure manuscript body ends on page 7 and References start on page 8; the final figure heights preserve this page boundary.
