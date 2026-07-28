# Decision-Block Stratification Audit

Evidence status: `post-primary zero-API descriptive audit`. No model calls were made.

The compiler strata below are post-treatment. They are descriptive associations, not
mediation estimates or causal effects of mode, bound-ID, selector restatement, or enforcement.

## Authored matched-call stratification

### Qwen

| Stratum | Rows | History exact | Visible exact | History E2E | Visible E2E | Repairs | Harms |
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 160 | 121/160 (75.6%) | 131/160 (81.9%) | 121/160 (75.6%) | 131/160 (81.9%) | 16 | 6 |
| Compiler mode correct | 137 | 105/137 (76.6%) | 119/137 (86.9%) | 105/137 (76.6%) | 119/137 (86.9%) | 16 | 2 |
| Compiler mode wrong | 23 | 16/23 (69.6%) | 12/23 (52.2%) | 16/23 (69.6%) | 12/23 (52.2%) | 0 | 4 |
| Preserve bound ID correct | 70 | 39/70 (55.7%) | 52/70 (74.3%) | 39/70 (55.7%) | 52/70 (74.3%) | 15 | 2 |
| Preserve bound ID wrong | 10 | 4/10 (40.0%) | 2/10 (20.0%) | 4/10 (40.0%) | 2/10 (20.0%) | 0 | 2 |

### GLM

| Stratum | Rows | History exact | Visible exact | History E2E | Visible E2E | Repairs | Harms |
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 160 | 113/160 (70.6%) | 141/160 (88.1%) | 113/160 (70.6%) | 141/160 (88.1%) | 29 | 1 |
| Compiler mode correct | 141 | 110/141 (78.0%) | 136/141 (96.5%) | 110/141 (78.0%) | 136/141 (96.5%) | 27 | 1 |
| Compiler mode wrong | 19 | 3/19 (15.8%) | 5/19 (26.3%) | 3/19 (15.8%) | 5/19 (26.3%) | 2 | 0 |
| Preserve bound ID correct | 61 | 32/61 (52.5%) | 57/61 (93.4%) | 32/61 (52.5%) | 57/61 (93.4%) | 25 | 0 |
| Preserve bound ID wrong | 19 | 3/19 (15.8%) | 5/19 (26.3%) | 3/19 (15.8%) | 5/19 (26.3%) | 2 | 0 |

## Interface redundancy

| Dataset/model | Rows | Selector exact | Task initial ID = pre-refresh | Compiler copy | History copy | Visible copy | Actor copies equal |
|---|---:|---:|---:|---:|---:|---:|---:|
| Authored / Qwen | 160 | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) |
| Authored / GLM | 160 | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) | 160/160 (100.0%) |
| Rewrite / Qwen | 50 | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) |
| Rewrite / GLM | 50 | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) | 50/50 (100.0%) |
| Source-derived / Qwen | 60 | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) |
| Source-derived / GLM | 60 | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) |
| Source-derived / DeepSeek | 60 | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) | 60/60 (100.0%) |
| Cross-schema matched / Qwen | 80 | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) |
| Cross-schema matched / GLM | 80 | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) | 80/80 (100.0%) |
| **Pooled** | **760** | **760/760 (100.0%)** | **760/760 (100.0%)** | **760/760 (100.0%)** | **760/760 (100.0%)** | **760/760 (100.0%)** | **760/760 (100.0%)** |

Exact equality shows value redundancy in the recorded interface. It does not rule out a salience effect from restatement.

## Existing v7 end-to-end boundary

| Model | Controller | Preserve initial binding | Preserve E2E | Reevaluate E2E | PairAcc |
|---|---|---:|---:|---:|---:|
| Qwen | Generic | 34/40 (85.0%) | 4/40 (10.0%) | 22/40 (55.0%) | 3/40 (7.5%) |
| Qwen | Historical CTA | 35/40 (87.5%) | 35/40 (87.5%) | 16/40 (40.0%) | 14/40 (35.0%) |
| Qwen | Lifecycle-Gated | 30/40 (75.0%) | 30/40 (75.0%) | 22/40 (55.0%) | 17/40 (42.5%) |
| GLM | Generic | 40/40 (100.0%) | 8/40 (20.0%) | 39/40 (97.5%) | 7/40 (17.5%) |
| GLM | Historical CTA | 34/40 (85.0%) | 34/40 (85.0%) | 36/40 (90.0%) | 30/40 (75.0%) |
| GLM | Lifecycle-Gated | 40/40 (100.0%) | 40/40 (100.0%) | 36/40 (90.0%) | 36/40 (90.0%) |

The v7 controller table is not call- or information-matched. It bounds end-to-end grounding and execution behavior but does not decompose the matched decision block.

## Input provenance

| Input | Rows | SHA-256 |
|---|---:|---|
| `runs/revision_full_diagnostic_qwen_full_v1.jsonl` | 160 | `b672d74de3e31ee323acbf36e61f3c3d223cf9a9ca40ca148aa9677c55b6bda2` |
| `runs/revision_full_diagnostic_glm_full_v1.jsonl` | 160 | `fd8911ed7c2cfbbfb1bf8efca243f3b6931be9e881e6ade89d4c6e96741efc0b` |
| `runs/revision_human_rewrite_qwen_full_v1.jsonl` | 50 | `eea8e29531c133fc22b0cb48e81c56c0b0c09e9af20e887442676de342b8fbdc` |
| `runs/revision_human_rewrite_glm_full_v1.jsonl` | 50 | `05bd78fd4dd95c29bd23474b2b3a388cfead9d6794da0a22301d129acdd2b850` |
| `runs/revision_source_grounded_qwen_full_v1.jsonl` | 60 | `0bc4e782abd425605baec59669dc7eb60676b8c7cf4a85bf094401e5b26ebb34` |
| `runs/revision_source_grounded_glm_full_v1.jsonl` | 60 | `abf87c52db74d7688ff6c1fcf796c2f22824e3a6b75ecb2c011af221d8658d19` |
| `runs/revision_source_grounded_deepseek_full_v1.jsonl` | 60 | `0d52868491a41f747f6db82d38f26e9886b9045942766fc9ec9079d54fc423f6` |
| `runs/call_matched_authorization_qwen_full_v2.jsonl` | 80 | `19177befd807b7f3fac8692b8a42b7fc112569f810c219e161ffb46fee0c063f` |
| `runs/call_matched_authorization_glm_full_v2.jsonl` | 80 | `f996d8267d69f7efde3441df806aa6985fbfe4a8ede87e425441736eec47e9f5` |
| `runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl` | 240 | `91d7d042e4539d7e748fd213ce096ffb7018ac9f1efa14e9bca4c1b4de8d2a4b` |
| `runs/v7_qwen_compile_then_act_full.jsonl` | 240 | `8975072588396f30f74b1a46b19238f053d680212cce5fc7692f5621fdb6adcf` |
| `runs/v7_qwen_factorized_hybrid_compile_then_act_full.jsonl` | 240 | `7f13cee82f434a66a0a58993463337f7552526859c4c37d851422af4e898d6f5` |
| `runs/v7_glm_generic_structured_ledger_then_act_full.jsonl` | 240 | `773c8bbe3ab65f4e5899568c6440bbd303a840521975f4504d1bcd33c4ee0f0e` |
| `runs/v7_glm_compile_then_act_full.jsonl` | 240 | `87eb48ddf9f71e18862a2e51006b436127b72f291a72b473bfbdb61d25d6ec75` |
| `runs/v7_glm_factorized_hybrid_compile_then_act_full.jsonl` | 240 | `5f5906905269a25dabdfffad35168e19e01f4688fd1388acd8f6918faa8ef53b` |
