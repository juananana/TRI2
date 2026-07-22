# TRI-v2 Compiler Stage Report

| Model | Mode | Split | Style | Binding | n | Mode | ID | Policy | Compiler | Final | Actor-only | Compiler-induced | API |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | factorized_hybrid_compile_then_act | test | explicit | anchored | 20 | 100.0 | 55.0 | 100.0 | 55.0 | 70.0 | 0 | 6 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | explicit | dynamic | 20 | 100.0 | 100.0 | NA | 100.0 | 95.0 | 1 | 0 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | implicit | anchored | 20 | 100.0 | 50.0 | 100.0 | 50.0 | 70.0 | 0 | 6 | 0 |
| Qwen3.5 | factorized_hybrid_compile_then_act | test | implicit | dynamic | 20 | 100.0 | 100.0 | NA | 100.0 | 95.0 | 1 | 0 | 0 |

## Failure Details

- `tri-v3-unseen-inventory-explicit_anchor-t1-flip`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-explicit_anchor-t1-flip`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-explicit_anchor-t2-stable`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-explicit_anchor-t2-stable`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-explicit_anchor-t5-name_collision`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-explicit_anchor-t5-name_collision`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-implicit_anchor-t1-flip`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-implicit_anchor-t1-flip`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-implicit_anchor-t2-stable`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-implicit_anchor-t2-stable`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-implicit_anchor-t5-name_collision`: mode=preserve expected=preserve; gold=ITM-K4 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-deployments-implicit_anchor-t5-name_collision`: mode=preserve expected=preserve; gold=DEP-X12 prediction=INVALID_BOUND_ENTITY; compiler_correct=False actor_only=False
- `tri-v3-unseen-inventory-explicit_dynamic-t3-remove`: mode=reevaluate expected=reevaluate; gold=ITM-P8 prediction=INVALID_BOUND_ENTITY; compiler_correct=True actor_only=True
- `tri-v3-unseen-deployments-implicit_dynamic-t2-stable`: mode=reevaluate expected=reevaluate; gold=DEP-X12 prediction=DEP-Q44; compiler_correct=True actor_only=True
