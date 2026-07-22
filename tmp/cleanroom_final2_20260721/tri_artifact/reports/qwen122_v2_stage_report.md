# TRI-v2 Compiler Stage Report

| Model | Mode | Split | Style | Binding | n | Mode | ID | Policy | Compiler | Final | Actor-only | Compiler-induced | API |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | dev | explicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 90.0 | 4 | 0 | 0 |
| Qwen3.5 | compile_then_act | dev | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | compile_then_act | dev | implicit | anchored | 40 | 87.5 | 87.5 | NA | 87.5 | 85.0 | 2 | 4 | 0 |
| Qwen3.5 | compile_then_act | dev | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 92.5 | 3 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 92.5 | 3 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dev | explicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dev | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dev | implicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | dev | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 97.5 | 1 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | explicit | dynamic | 40 | 75.0 | 75.0 | NA | 75.0 | 80.0 | 0 | 8 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |

## Failure Details

- `v2-mail-implicit_anchor-flip`: mode=post_refresh expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `v2-mail-implicit_anchor-remove`: mode=post_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=EM-205; compiler_correct=False actor_only=False
- `v2-mail-implicit_anchor-invalidate`: mode=post_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=EM-205; compiler_correct=False actor_only=False
- `v2-mail-implicit_anchor-name_collision`: mode=post_refresh expected=pre_refresh; gold=EM-104 prediction=EM-205; compiler_correct=False actor_only=False
- `v2-calendar-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2-calendar-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2-support-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-41; compiler_correct=True actor_only=True
- `v2-support-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=TCK-41; compiler_correct=True actor_only=True
- `v2-crm-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-17; compiler_correct=True actor_only=True
- `v2-repo-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-main; compiler_correct=True actor_only=True
- `v2-crm-implicit_dynamic-remove`: mode=reevaluate expected=reevaluate; gold=LEAD-22 prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
- `v2h-calendar-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2h-calendar-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2h-crm-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=LEAD-17; compiler_correct=True actor_only=True
- `v2h-repo-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-main; compiler_correct=True actor_only=True
- `v2h-repo-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-main; compiler_correct=True actor_only=True
- `v2h-shipping-implicit_anchor-flip`: mode=pre_refresh expected=pre_refresh; gold=SHP-88 prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
- `v2h-calendar-explicit_dynamic-flip`: mode=preserve expected=reevaluate; gold=MTG-22 prediction=MTG-10; compiler_correct=False actor_only=False
- `v2h-calendar-explicit_dynamic-remove`: mode=preserve expected=reevaluate; gold=MTG-22 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `v2h-calendar-explicit_dynamic-invalidate`: mode=preserve expected=reevaluate; gold=MTG-22 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `v2h-calendar-explicit_dynamic-name_collision`: mode=preserve expected=reevaluate; gold=MTG-22 prediction=MTG-10; compiler_correct=False actor_only=False
- `v2h-shipping-explicit_dynamic-flip`: mode=preserve expected=reevaluate; gold=SHP-91 prediction=SHP-88; compiler_correct=False actor_only=False
- `v2h-shipping-explicit_dynamic-remove`: mode=preserve expected=reevaluate; gold=SHP-91 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `v2h-shipping-explicit_dynamic-invalidate`: mode=preserve expected=reevaluate; gold=SHP-91 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `v2h-shipping-explicit_dynamic-name_collision`: mode=preserve expected=reevaluate; gold=SHP-91 prediction=SHP-88; compiler_correct=False actor_only=False
