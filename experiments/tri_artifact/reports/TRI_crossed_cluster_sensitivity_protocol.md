# TRI Primary Crossed-Dependence Sensitivity Protocol

Date fixed: 2026-07-25 (Asia/Shanghai)

## Status and purpose

This is a `post-primary replication/audit` designed after the TRI-v3 primary result was
observed. It is a zero-API sensitivity analysis of existing frozen outputs. It does not replace
the primary language-template cluster confidence interval, and it is not a new confirmatory
analysis or a multiplicity-adjusted test.

The audit asks whether the paired end-to-end accuracy contrast remains directionally stable when
dependence is attributed to domains, language-template clusters, or both crossed generator axes.
The estimand is Lifecycle-Gated minus Generic exact-target accuracy on the complete 160-task
inventory. Qwen is the primary/frozen run; GLM is reported as a post-primary package replication.

## Frozen inputs

The analysis reads the following completed run files without model calls or row filtering:

- Qwen Generic: `runs/20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl`
- Qwen Lifecycle-Gated: `runs/20260717T030034Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl`
- GLM Generic: `runs/20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl`
- GLM Lifecycle-Gated: `runs/20260717T034201Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl`

Every input must contain exactly 160 unique `task.id` values. Paired files must have identical ID
sets and identical complete `task` metadata for each ID. Each task must have nonempty `domain`
and `template_id` fields. The inventory must form a complete 8-domain by 20-template cross with
exactly one task in every cell. Any failed check aborts the analysis.

API, parse, and protocol failures retain the existing end-to-end scoring rule and count as
incorrect through the repository's shared `success` function. No task is excluded.

## Frozen analysis

All intervals use 10,000 bootstrap draws, seed `20260725`, and the 2.5th and 97.5th linearly
interpolated percentiles. Each draw computes the paired mean of
`success(Lifecycle-Gated) - success(Generic)`.

1. **Language-template cluster bootstrap.** Sample 20 template clusters with replacement and
   retain all eight domain rows in every sampled cluster. This reproduces the dependence axis
   used by the primary analysis.
2. **Domain cluster bootstrap.** Sample eight domains with replacement and retain all 20 template
   rows in every sampled domain.
3. **Two-way pigeonhole bootstrap.** Independently sample eight domains and 20 template clusters
   with replacement. For task `(d, t)`, assign weight `N_d(d) * N_t(t)`, where `N_d` and `N_t`
   are the sampled multiplicities. Compute the weighted paired mean over the complete crossed
   inventory. This preserves the crossed design while allowing dependence along both generator
   axes.

For each model, report the common full-sample point estimate, all three percentile intervals,
their widths, and the method producing the widest interval. Also report the widest interval over
both model analyses. No p-values or multiplicity-adjusted confirmatory claims are produced.

## Interpretation fixed before execution

- If every interval remains above zero, the result strengthens the limited claim that the paired
  package contrast is not explained solely by choosing the original template clustering axis.
- If a domain or two-way interval includes zero, the primary estimate remains unchanged, but its
  uncertainty is sensitive to crossed generator dependence and this must be reported.
- Wider intervals narrow precision claims. They do not establish natural-world prevalence,
  controller-component causality, or independence of authored templates.
