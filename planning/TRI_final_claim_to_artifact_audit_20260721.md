# TRI Final Claim-to-Artifact Audit

Audit date: 2026-07-21 (Asia/Shanghai)

Scope: every empirical number or numeric inventory in the main manuscript, grouped by the claim
that gives the number meaning. A `PASS` means the manuscript value agrees with the cited derived
report and that the report is linked to raw rows and executable analysis in
`reports/current_claim_provenance.md`. Formal symbols such as $S_0/S_1$ and equation indices are
not empirical claims.

| Main-text location / claim | Manuscript numbers | Authoritative artifacts | Status |
|---|---|---|---|
| Abstract; symmetric calibration figure; historical CTA | Generic 64.4/71.9; CTA 95.0/96.2; extremes 60.0; post-hoc rule 92.5 | `reports/v3_qwen_language_cluster.json`; `reports/v3_glm_language_cluster.json`; `reports/v3_exact_predecessor_two_model.json`; `reports/policy_extreme_controls.json`; `reports/deterministic_discourse_rule_v2.json` | PASS |
| Supplementary component audit, all eight rows | 64.4/71.9; 75.0/75.0; 65.0/73.1; 81.2/70.6; 92.5/92.5; 95.0/96.2; 96.9/98.1; 98.1/100.0 | `reports/reference_mode_ablation_{qwen,glm}.json`; `reports/v3_primary_free_actor_representation_contrasts.json`; `reports/v3_prefrefresh_untyped_primary_report.json`; files above | PASS |
| v3 inventory/statistics | 160 tasks; 20 clusters; four styles; eight domains; five update types; 10,000 bootstrap draws | `data/temporal_referent_v3_language_clusters.jsonl`; `reports/TRI_v3_preregistered_protocol.md`; `tri/v3_cluster_report.py` | PASS |
| Transfer, SQLite, and guarded-policy main-table rows | 80 transfer tasks; 46.2/82.5; SQLite 67.5/100 and 65/100; guarded policy 52.5/85; displayed cluster intervals | `reports/v3_qwen_unseen_cluster.json`; `reports/v3_qwen_sqlite_trajectory_report.json`; `reports/v3_two_model_sqlite_trajectory_report.json`; `reports/v4_qwen_policy_model.json` | PASS |
| Primary paired analysis and mode slices | Lifecycle 98.1/100; discordance 3/57 and 0/45; exact McNemar p-values; anchored/dynamic slices 33.8/100, 95/96.2, 56.2/100, 87.5/100 | `reports/v3_qwen_language_pairwise.json`; `reports/v3_glm_language_pairwise.json`; `reports/v3_qwen_language_factor.json`; `reports/v3_glm_language_factor.json` | PASS |
| Component attribution prose | validity gate +0.6/+1.2; free 96.9/98.1; gate +1.2/+1.9; reference mode and untyped-plan differences/intervals | `reports/v3_primary_free_actor_representation_contrasts.json`; `reports/reference_mode_ablation_{qwen,glm}.json`; `reports/v3_prefrefresh_untyped_primary_report.json` | PASS |
| Rule disclosure | v1 60.6 on v3 and 74.0 on rewrites; v2 92.5/96.0/91.7; CTA deltas and intervals | `reports/deterministic_discourse_rule_v1.json`; `reports/deterministic_discourse_rule_v2.json`; corresponding deterministic run JSONL | PASS; v2 remains explicitly post-hoc |
| Extreme controls and policy sensitivity | 96/160 each; 80/80 and 16/80 complementary slices; actionable 128, reject 32; actionable method accuracies | `reports/policy_extreme_controls.json`; `reports/v3_referential_policy_slices.json` | PASS |
| Matched-pair consistency | v3 changed-winner Generic 3/32 and 7/32; CTA 30/32 and 31/32; Gated 32/32; post-hoc rule 28/32; extreme controls 0/32; complete v3/v7 tables | `reports/matched_pair_consistency.json`; `tri/matched_pair_consistency.py`; source runs enumerated in provenance | PASS; Stable and invalidity-policy slices remain separate; missing/errors are ITT failures |
| v3 conditional drift | Qwen 15/16 flip and 14/16 collision; GLM 3/16 and 7/16; no Stable drift | `reports/v3_sqlite_conditional_tri_audit.json`; v3 stage/audit reports listed in provenance map | PASS |
| v7 Qwen/GLM replication | 240 tasks, ten schemas, 40 state clusters; initial binding 107/120 and 120/120; drift 43/72 and 38/80 with intervals; stable errors 4/40 and 2/40; CTA deltas/intervals | `reports/v7_core_replication.json`; `reports/v7_core_replication.md`; raw matched v7 Generic/CTA files | PASS |
| DeepSeek v7 and write consequences | Generic/CTA 73.8/91.2; drift 59/79 vs 0/70; +17.5 [10.8,23.3]; 59 drift writes; CTA 17 non-core wrong writes | `reports/v7_deepseek_full_v1.json`; `reports/v7_deepseek_write_audit_v1.json`; `reports/v7_deepseek_sqlite_replay_v1.json` | PASS |
| Leave-group-out and repeat stability | all domain/template exclusion ranges; 40-cluster repeat set; six positive cells; range and unanimity values | `reports/v7_leave_group_out_sensitivity_v1.json`; `reports/v7_repeat_stability_v1.json` | PASS |
| Full-history baselines | ordinary 63.3/67.1/68.8; aware 69.6/80.8/75.8; substitutions 56/38/42 of 80; CTA 70.8/94.2/91.2; paired differences/intervals | `reports/v7_matched_full_history_three_model_final_v1.json`; six complete matched raw files | PASS |
| Blind human validation | 100 items; kappa .708; alpha .709; 86%, 91.5% of 94; 84/88; 46 determinate originals; 35 unanimous; all model subset accuracies; Reject 55/25 | `human_validation/analysis.json`; `human_validation/model_human_subset.json`; de-identified normalized returns and `scripts/analyze_human_validation.py` | PASS; private answer key excluded intentionally |
| Independent human rewrites | 50 rewrites; Qwen 60/90/88/90; GLM 74/98/92/94; 48 majorities; CTA 89.6/93.8 | `reports/human_rewrite_model_results.json`; eight complete raw run files; rewrite protocol and execution log | PASS |
| Custom/external boundary | custom pilot 24; strict slices 3/6, 0/2, 0/6; frozen extension 96 and eligible range 64--87 | `reports/toolsandbox_tri_matched_two_model_v1.json`; `reports/toolsandbox_tri_pilot_conditional_audit_v1.json`; related custom reports | PASS; labeled custom/post-hoc where applicable |
| Main and supplementary qualitative cases | v7 task ID and REM-1A/REM-1B ledger, target, write, and CTA contrast; ToolSandbox-compatible positive; AppWorld correct opportunity and pre-binding error | `reports/qualitative_trace_cases.json`; five raw run/replay files recorded there; executable extractor and test | PASS; custom external cases are not official scores |
| Public benchmark opportunity audit | ToolSandbox 129 families; AppWorld 244 families; tau3 2,449 tasks and 10,832 trajectories; zero strict native opportunities | `reports/official_toolsandbox_tri_prevalence_audit.json`; `reports/appworld_public_trace_tri_audit.json`; `reports/official_tau3_native_tri_audit.json` | PASS; supports coverage only |
| Public benchmark feature checklist | eight strict-opportunity features for each closest natural near-match | `reports/benchmark_coverage_checklist.json`; three source audit JSON files and their audit scripts | PASS; partial/no cells prevent strict denominator and do not imply prevalence |
| Compositional boundary | Qwen 32/40 Generic vs 28/40 scalar, 39/40 role-indexed; GLM 40/40 tie | `reports/v5_qwen_multirefresh_report.json`; `reports/v6_matched_scalar_role_report.json` | PASS; negative result retained |
| Schema/write error analysis | mode 100; bound-ID 55/50; transfer 46.2/82.5; SQLite final 27/40 and 26/40; wrong writes 13/8; conditional writes 8/8, 6/8, stable 0/4; gated 40/40 | `reports/v3_qwen_unseen_factor.json`; two-model SQLite report; `reports/v3_sqlite_conditional_tri_audit.json` | PASS |
| Model/API description | two primary model IDs, DeepSeek post-primary, temperature 0, 1,200-token cap, zero final v3/v4 API errors/retries | run metadata, cost/audit JSON reports, and protocols enumerated in `reports/current_claim_provenance.md` | PASS |

## Audit findings and repairs

1. No empirical-number discrepancy was found between the current main TeX and the authoritative
   derived reports.
2. The Binding Drift full-v7 author adaptation is correctly excluded from the main performance
   results because it lacks $S_0$ and the resolved old ID. Its 39/120 versus 116/120 asymmetry is
   not used as a CTA superiority claim.
3. Deterministic-rule report paths were absolute in source JSON. The report generator now emits
   artifact-relative `data/...` and `runs/...` paths; v1 and v2 reports were regenerated without
   changing predictions or scores.
4. The manuscript distinguishes E2E accuracy, initial binding, conditional TRI, wrong writes,
   invalid attempts, and rejection. No conditional denominator was silently promoted to E2E.

## Final gate

This audit must be rerun conceptually after any numerical TeX edit. The final build is acceptable
only if all scientific tests pass, the anonymous archive contains the exact TeX/report revisions,
the archive manifest verifies, and the PDF remains within seven content pages plus references.
