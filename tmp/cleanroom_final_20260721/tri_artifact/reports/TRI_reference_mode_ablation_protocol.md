# P0 Generic + reference_mode ablation

## Question

Does the main benefit of pre-refresh compilation come from explicitly classifying the reference
as `preserve` or `reevaluate`, or does the larger lifecycle/provenance record contribute beyond
that mode decision?

## Frozen protocol

- Dataset: `data/temporal_referent_v3_language_clusters.jsonl`.
- Inventory: 160 scalar tasks, all five update types, both anchored and dynamic language, all
  frozen language clusters.
- Models: Qwen3.5-122B-A10B and GLM-5.1, matching the primary paper runs.
- Temperature: 0.0; thinking disabled; timeout and retry settings are recorded by the runner.
- Baseline: the existing Generic Structured Ledger and free actor.
- Treatment: the same Generic ledger plus only `reference_mode`.
- Excluded from the treatment: `binding_time`, `invalidity_policy`, `guard`, `fallback`, and
  deterministic execution gating.
- Primary statistic: paired task accuracy difference with 10,000 cluster bootstrap resamples,
  seed 20260719.
- API failures and incomplete rows count as failures; the analyzer rejects missing or duplicate
  task IDs.

## Commands

```bash
cd experiments/tri_artifact
export LLM_API_KEY='set-in-your-shell-only'
scripts/run_reference_mode_ablation.sh
```

Then analyze each model against its already frozen Generic run:

```bash
python3 -m tri.analyze_reference_mode_ablation \
  --generic runs/20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl \
  --reference-mode runs/NEW_QWEN_REFERENCE_MODE_RUN.jsonl \
  --output reports/reference_mode_ablation_qwen.json

python3 -m tri.analyze_reference_mode_ablation \
  --generic runs/20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl \
  --reference-mode runs/NEW_GLM_REFERENCE_MODE_RUN.jsonl \
  --output reports/reference_mode_ablation_glm.json
```

The results must be interpreted as mechanism evidence. A high treatment score supports explicit
mode classification as the main causal factor; a lower score supports additional value from the
pre-refresh identity/provenance representation. Neither result licenses a claim that the typed
Lifecycle-Gated controller is universally superior.
