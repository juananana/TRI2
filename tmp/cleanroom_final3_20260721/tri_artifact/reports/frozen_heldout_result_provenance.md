# Frozen Held-out Result Provenance

## Protocol

- Dataset: `data/temporal_referent_v2_heldout.jsonl`
- Dataset SHA-256: `9a63be2a2f25685db33e9a0c0048fcd2e86fe5f3bdc813dc592d01f8eda18d89`
- Tasks per run: 160
- Temperature: 0
- Thinking: disabled
- Maximum output tokens: 1200
- Exact target-ID scoring; no LLM judge
- API failures are audited separately and are not interpreted as model failures

All ten final runs contain 160 unique expected task IDs, no missing or extra IDs, no
duplicates, no API errors, and no retry events.

## Qwen3.5-122B-A10B

| Controller | Correct | Requests | Total latency (s) | SHA-256 |
|---|---:|---:|---:|---|
| state overwrite | 97 | 160 | 73.3 | `30074c6e6f3a7cb9c3ea4c7fadd8bd5fa992c514a94e65f136f938b5b00584f9` |
| full history | 97 | 160 | 71.1 | `3ebf0b2d327fc22d239db41d4b9677a6bba330d1edaf69aba0020767636e2d1a` |
| generic plan | 125 | 320 | 349.1 | `d33018422982bf40ce1f011fd54e9c8659d43b7ed62462a77f3a744aae67530b` |
| compile then act | 154 | 320 | 296.8 | `5541f803e1da13d4d7cf4f81bfbd8eb942e34188292c3c894ad4d35657fee241` |
| factorized hybrid | 152 | 230 | 312.7 | `937d1f87a7fea50cd1605bf5f2ac604335bc4c1a2fcaefb43a18741f6a9f6bc6` |

Source files:

- `runs/20260716T165006Z_Qwen_Qwen3.5-122B-A10B_state_overwrite_once_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T165119Z_Qwen_Qwen3.5-122B-A10B_full_history_once_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T165230Z_Qwen_Qwen3.5-122B-A10B_generic_plan_then_act_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T165820Z_Qwen_Qwen3.5-122B-A10B_compile_then_act_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T164359Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v2_heldout_frozen_nothinking.jsonl`

## GLM-5.1

| Controller | Correct | Requests | Total latency (s) | SHA-256 |
|---|---:|---:|---:|---|
| state overwrite | 96 | 160 | 203.4 | `f5a6c4cdaa9ff26abd8cf1ede8b396214def0a3974ff41691358caa36d7d75ab` |
| full history | 113 | 160 | 199.0 | `820639096f9d918f35264ed6fc6b8a4e2470e38dfd9fbf8861af3546886f20c3` |
| generic plan | 129 | 320 | 738.9 | `fcbb4daaebf0c6a40d2d01123be1a1ee96693097a091a2ee3f8bbdc782465bba` |
| compile then act | 156 | 320 | 611.7 | `5f81024acb1d1e9cfeb27b7cd90d7cb5804ac2ff0bf564141c2d8a64d25caeff` |
| factorized hybrid | 160 | 240 | 605.5 | `b876ef609f3916709a8c5a55e7f7b10c2bdcb437c30592a15306fb4a8e34fbbc` |

Source files:

- `runs/20260716T171359Z_Pro_zai-org_GLM-5.1_state_overwrite_once_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T171722Z_Pro_zai-org_GLM-5.1_full_history_once_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T172041Z_Pro_zai-org_GLM-5.1_generic_plan_then_act_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T173301Z_Pro_zai-org_GLM-5.1_compile_then_act_v2_heldout_frozen_nothinking.jsonl`
- `runs/20260716T174313Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v2_heldout_frozen_nothinking.jsonl`

## Derived Artifacts

- `reports/frozen_heldout_cross_model_audit.json`
- `reports/frozen_heldout_cross_model_report.json`
- `reports/frozen_heldout_cross_model_factor.json`
- `reports/frozen_heldout_cross_model_pairwise.json`
- `reports/frozen_heldout_cross_model_stage.json`
- `reports/figures/frozen_heldout_binding_profiles.pdf`

The failed Qwen3.5-397B and MiniMax endpoint runs are excluded from all final tables.
