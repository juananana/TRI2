# TRI-v3 Exact Historical Compile-Then-Act Audit

All accuracy metrics are intention-to-treat: API and parse failures count as incorrect.
Template-cluster bootstrap: 10000 resamples; seed 20260717.

## Overall

| Model | Controller | n | ITT Acc. | Cluster 95% CI | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Final failures | Actor failures | Compiler-induced failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | compile_then_act | 160 | 95.0 | [91.2, 98.1] | 0 | 0 | 99.4 | 100.0 | 8 | 7 | 1 |
| GLM-5.1 | compile_then_act | 160 | 96.2 | [91.9, 99.4] | 0 | 0 | 97.5 | 95.0 | 6 | 2 | 4 |

## Binding Slices

| Model | Binding | n | ITT Acc. | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Actor failures | Final failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | anchored | 80 | 91.2 | 0 | 0 | 100.0 | 100.0 | 7 | 7 |
| Qwen3.5 | dynamic | 80 | 98.8 | 0 | 0 | 98.8 | NA | 0 | 1 |
| GLM-5.1 | anchored | 80 | 92.5 | 0 | 0 | 95.0 | 95.0 | 2 | 6 |
| GLM-5.1 | dynamic | 80 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |

## Explicitness Slices

| Model | Explicitness | n | ITT Acc. | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Actor failures | Final failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | explicit | 80 | 96.2 | 0 | 0 | 100.0 | 100.0 | 3 | 3 |
| Qwen3.5 | implicit | 80 | 93.8 | 0 | 0 | 98.8 | 100.0 | 4 | 5 |
| GLM-5.1 | explicit | 80 | 97.5 | 0 | 0 | 98.8 | 97.5 | 1 | 2 |
| GLM-5.1 | implicit | 80 | 95.0 | 0 | 0 | 96.2 | 92.5 | 1 | 4 |

## Update Slices

| Model | Update | n | ITT Acc. | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Actor failures | Final failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | flip | 32 | 93.8 | 0 | 0 | 96.9 | 100.0 | 1 | 2 |
| Qwen3.5 | invalidate | 32 | 81.2 | 0 | 0 | 100.0 | 100.0 | 6 | 6 |
| Qwen3.5 | name_collision | 32 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | remove | 32 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | stable | 32 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | flip | 32 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | invalidate | 32 | 93.8 | 0 | 0 | 96.9 | 93.8 | 1 | 2 |
| GLM-5.1 | name_collision | 32 | 96.9 | 0 | 0 | 100.0 | 100.0 | 1 | 1 |
| GLM-5.1 | remove | 32 | 90.6 | 0 | 0 | 90.6 | 81.2 | 0 | 3 |
| GLM-5.1 | stable | 32 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |

## Template-Cluster Slices

| Model | Template | n | ITT Acc. | API | Parse | Binding-time Acc. | Anchored bound-ID Acc. | Actor failures | Final failures |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 | explicit_anchor-t1 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | explicit_anchor-t2 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | explicit_anchor-t3 | 8 | 75.0 | 0 | 0 | 100.0 | 100.0 | 2 | 2 |
| Qwen3.5 | explicit_anchor-t4 | 8 | 87.5 | 0 | 0 | 100.0 | 100.0 | 1 | 1 |
| Qwen3.5 | explicit_anchor-t5 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | explicit_dynamic-t1 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | explicit_dynamic-t2 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | explicit_dynamic-t3 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | explicit_dynamic-t4 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | explicit_dynamic-t5 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | implicit_anchor-t1 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | implicit_anchor-t2 | 8 | 87.5 | 0 | 0 | 100.0 | 100.0 | 1 | 1 |
| Qwen3.5 | implicit_anchor-t3 | 8 | 75.0 | 0 | 0 | 100.0 | 100.0 | 2 | 2 |
| Qwen3.5 | implicit_anchor-t4 | 8 | 87.5 | 0 | 0 | 100.0 | 100.0 | 1 | 1 |
| Qwen3.5 | implicit_anchor-t5 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| Qwen3.5 | implicit_dynamic-t1 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | implicit_dynamic-t2 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | implicit_dynamic-t3 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | implicit_dynamic-t4 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| Qwen3.5 | implicit_dynamic-t5 | 8 | 87.5 | 0 | 0 | 87.5 | NA | 0 | 1 |
| GLM-5.1 | explicit_anchor-t1 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | explicit_anchor-t2 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | explicit_anchor-t3 | 8 | 87.5 | 0 | 0 | 100.0 | 100.0 | 1 | 1 |
| GLM-5.1 | explicit_anchor-t4 | 8 | 87.5 | 0 | 0 | 87.5 | 87.5 | 0 | 1 |
| GLM-5.1 | explicit_anchor-t5 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | explicit_dynamic-t1 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | explicit_dynamic-t2 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | explicit_dynamic-t3 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | explicit_dynamic-t4 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | explicit_dynamic-t5 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | implicit_anchor-t1 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | implicit_anchor-t2 | 8 | 87.5 | 0 | 0 | 87.5 | 87.5 | 0 | 1 |
| GLM-5.1 | implicit_anchor-t3 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | implicit_anchor-t4 | 8 | 62.5 | 0 | 0 | 75.0 | 75.0 | 1 | 3 |
| GLM-5.1 | implicit_anchor-t5 | 8 | 100.0 | 0 | 0 | 100.0 | 100.0 | 0 | 0 |
| GLM-5.1 | implicit_dynamic-t1 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | implicit_dynamic-t2 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | implicit_dynamic-t3 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | implicit_dynamic-t4 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |
| GLM-5.1 | implicit_dynamic-t5 | 8 | 100.0 | 0 | 0 | 100.0 | NA | 0 | 0 |

## Protocol-Frozen Audit Comparisons

Delta is exact historical compile-then-act minus the named comparator.

| Comparison | Exact controller | Comparator | Paired n | Templates | Exact Acc. | Comparator Acc. | Delta | Cluster 95% CI | Unpaired exact/comparator |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| untyped_pre_refresh | compile_then_act | pre_refresh_untyped_compile_then_act | 160 | 20 | 95.0 | 81.2 | 13.8 | [6.2, 22.5] | 0/0 |
| lifecycle_free | compile_then_act | factorized_schema_compile_then_act | 160 | 20 | 95.0 | 96.9 | -1.9 | [-6.9, 2.5] | 0/0 |
| untyped_pre_refresh | compile_then_act | pre_refresh_untyped_compile_then_act | 160 | 20 | 96.2 | 70.6 | 25.6 | [13.8, 38.1] | 0/0 |
| lifecycle_free | compile_then_act | factorized_schema_compile_then_act | 160 | 20 | 96.2 | 98.1 | -1.9 | [-5.0, 1.2] | 0/0 |
