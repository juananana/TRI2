# TRI-v2 Compiler Stage Report

| Model | Mode | Split | Style | Binding | n | Mode | ID | Policy | Compiler | Final | Actor-only | Compiler-induced | API |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GLM-5.1 | compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 97.5 | 1 | 0 | 0 |
| GLM-5.1 | compile_then_act | heldout | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| GLM-5.1 | compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 92.5 | 3 | 0 | 0 |
| GLM-5.1 | compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | heldout | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| GLM-5.1 | factorized_hybrid_compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 92.5 | 3 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | explicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | NA | 100.0 | 92.5 | 3 | 0 | 0 |
| Qwen3.5 | compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | explicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | explicit | dynamic | 40 | 75.0 | 75.0 | NA | 75.0 | 80.0 | 0 | 8 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | implicit | anchored | 40 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 0 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | heldout | implicit | dynamic | 40 | 100.0 | 100.0 | NA | 100.0 | 100.0 | 0 | 0 | 0 |

## Failure Details

- `v2h-mail-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=EM-104; compiler_correct=True actor_only=True
- `v2h-calendar-explicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2h-calendar-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=MTG-10; compiler_correct=True actor_only=True
- `v2h-repo-implicit_anchor-invalidate`: mode=pre_refresh expected=pre_refresh; gold=INVALID_BOUND_ENTITY prediction=BR-main; compiler_correct=True actor_only=True
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
