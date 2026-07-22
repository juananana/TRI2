# TRI-v2 Compiler Stage Report

| Model | Mode | Split | Style | Binding | n | Mode | ID | Policy | Compiler | Final | Actor-only | Compiler-induced | API |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | test | explicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 97.5 | 1 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | implicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 95.0 | 2 | 0 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | test | explicit | anchored | 40 | 0.0 | 0.0 | NA | 0.0 | 45.0 | 0 | 22 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | test | explicit | dynamic | 40 | 0.0 | 100.0 | NA | 0.0 | 97.5 | 0 | 1 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | test | implicit | anchored | 40 | 0.0 | 0.0 | NA | 0.0 | 22.5 | 0 | 31 | 0 |
| Qwen3.5 | generic_structured_ledger_then_act | test | implicit | dynamic | 40 | 0.0 | 100.0 | NA | 0.0 | 92.5 | 0 | 3 | 0 |

## Failure Details

- `tri-v3-language-mail-explicit_anchor-t1-flip`: mode=None expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-support-explicit_anchor-t1-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-docs-explicit_anchor-t1-name_collision`: mode=None expected=pre_refresh; gold=DOC-7 prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-crm-explicit_anchor-t1-flip`: mode=None expected=pre_refresh; gold=LEAD-17 prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-explicit_anchor-t1-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-explicit_anchor-t2-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-explicit_anchor-t3-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-support-explicit_anchor-t3-flip`: mode=None expected=pre_refresh; gold=TCK-41 prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-crm-explicit_anchor-t3-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-17; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-explicit_anchor-t3-name_collision`: mode=None expected=pre_refresh; gold=SHP-88 prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-mail-explicit_anchor-t4-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-explicit_anchor-t4-name_collision`: mode=None expected=pre_refresh; gold=MTG-10 prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-commerce-explicit_anchor-t4-flip`: mode=None expected=pre_refresh; gold=SKU-11 prediction=SKU-29; compiler_correct=False actor_only=False
- `tri-v3-language-crm-explicit_anchor-t4-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-repo-explicit_anchor-t4-name_collision`: mode=None expected=pre_refresh; gold=BR-main prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-explicit_anchor-t4-flip`: mode=None expected=pre_refresh; gold=SHP-88 prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-mail-explicit_anchor-t5-name_collision`: mode=None expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-explicit_anchor-t5-flip`: mode=None expected=pre_refresh; gold=MTG-10 prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-support-explicit_anchor-t5-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-docs-explicit_anchor-t5-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-crm-explicit_anchor-t5-name_collision`: mode=None expected=pre_refresh; gold=LEAD-17 prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-repo-explicit_anchor-t5-flip`: mode=None expected=pre_refresh; gold=BR-main prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-mail-implicit_anchor-t1-flip`: mode=None expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-commerce-implicit_anchor-t1-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SKU-29; compiler_correct=False actor_only=False
- `tri-v3-language-support-implicit_anchor-t1-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-docs-implicit_anchor-t1-name_collision`: mode=None expected=pre_refresh; gold=DOC-7 prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-crm-implicit_anchor-t1-flip`: mode=None expected=pre_refresh; gold=LEAD-17 prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-implicit_anchor-t1-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-implicit_anchor-t2-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-commerce-implicit_anchor-t2-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SKU-29; compiler_correct=False actor_only=False
- `tri-v3-language-support-implicit_anchor-t2-name_collision`: mode=None expected=pre_refresh; gold=TCK-41 prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-docs-implicit_anchor-t2-flip`: mode=None expected=pre_refresh; gold=DOC-7 prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-repo-implicit_anchor-t2-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-implicit_anchor-t2-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-implicit_anchor-t3-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-commerce-implicit_anchor-t3-name_collision`: mode=None expected=pre_refresh; gold=SKU-11 prediction=SKU-29; compiler_correct=False actor_only=False
- `tri-v3-language-support-implicit_anchor-t3-flip`: mode=None expected=pre_refresh; gold=TCK-41 prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-crm-implicit_anchor-t3-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-repo-implicit_anchor-t3-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-implicit_anchor-t3-name_collision`: mode=None expected=pre_refresh; gold=SHP-88 prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-mail-implicit_anchor-t4-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-implicit_anchor-t4-name_collision`: mode=None expected=pre_refresh; gold=MTG-10 prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-commerce-implicit_anchor-t4-flip`: mode=None expected=pre_refresh; gold=SKU-11 prediction=SKU-29; compiler_correct=False actor_only=False
- `tri-v3-language-docs-implicit_anchor-t4-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-crm-implicit_anchor-t4-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-repo-implicit_anchor-t4-name_collision`: mode=None expected=pre_refresh; gold=BR-main prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-shipping-implicit_anchor-t4-flip`: mode=None expected=pre_refresh; gold=SHP-88 prediction=SHP-91; compiler_correct=False actor_only=False
- `tri-v3-language-mail-implicit_anchor-t5-name_collision`: mode=None expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `tri-v3-language-calendar-implicit_anchor-t5-flip`: mode=None expected=pre_refresh; gold=MTG-10 prediction=MTG-22; compiler_correct=False actor_only=False
- `tri-v3-language-support-implicit_anchor-t5-remove`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-52; compiler_correct=False actor_only=False
- `tri-v3-language-docs-implicit_anchor-t5-invalidate`: mode=None expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=DOC-8; compiler_correct=False actor_only=False
- `tri-v3-language-crm-implicit_anchor-t5-name_collision`: mode=None expected=pre_refresh; gold=LEAD-17 prediction=LEAD-22; compiler_correct=False actor_only=False
- `tri-v3-language-repo-implicit_anchor-t5-flip`: mode=None expected=pre_refresh; gold=BR-main prediction=BR-rel; compiler_correct=False actor_only=False
- `tri-v3-language-mail-explicit_dynamic-t3-remove`: mode=None expected=post_refresh; gold=EM-205 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-language-repo-implicit_dynamic-t2-remove`: mode=None expected=post_refresh; gold=BR-rel prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-language-mail-implicit_dynamic-t3-remove`: mode=None expected=post_refresh; gold=EM-205 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-language-docs-implicit_dynamic-t4-remove`: mode=None expected=post_refresh; gold=DOC-8 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-language-crm-explicit_dynamic-t3-remove`: mode=reevaluate expected=reevaluate; gold=LEAD-22 prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
- `tri-v3-language-crm-implicit_dynamic-t3-remove`: mode=reevaluate expected=reevaluate; gold=LEAD-22 prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
- `tri-v3-language-repo-implicit_dynamic-t3-invalidate`: mode=reevaluate expected=reevaluate; gold=BR-rel prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
