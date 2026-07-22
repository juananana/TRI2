# TRI-v7 Repeat Stability Execution Log

Execution date: 2026-07-21 (Asia/Shanghai)

## Frozen input

- `data/temporal_referent_v7_repeat_stability_v1.jsonl`
- SHA-256: `06afa1a2a40f78eaa817a5f98f107e4972f7ea4c2b099535c7023498cd174446`
- Protocol: `reports/TRI_v7_repeat_stability_protocol.md`

The user explicitly authorized sending this 40-task frozen synthetic file to SiliconFlow for
Qwen/GLM Generic and CTA repeat-2/3 runs. The API key was entered with terminal echo disabled and
was not written to the workspace.

## Completed outputs

| File | SHA-256 |
|---|---|
| `runs/v7_repeat_qwen_generic_r2_v1.jsonl` | `3dfc13ad9929872351515110346e497d39190081750081a7539d65b5c3f41dc1` |
| `runs/v7_repeat_qwen_generic_r3_v1.jsonl` | `05b1492033de3a767bca026479d2e5b91249438cd9e9876288fcf3ea0b287ba8` |
| `runs/v7_repeat_qwen_cta_r2_v1.jsonl` | `a3e6d8e8ed6ca690fae7cac4ef7d454a7d802ca8395b48b22b744462e93a273f` |
| `runs/v7_repeat_qwen_cta_r3_v1.jsonl` | `9107ff971e593f738f81732facce9e1465b9923c4c9364ab526664148775e3ca` |
| `runs/v7_repeat_glm_generic_r2_v1.jsonl` | `2fa7e5b583d96f6682ea12cb88da547c40c6b4258cb3eb2d614742232e11d85c` |
| `runs/v7_repeat_glm_generic_r3_v1.jsonl` | `9d2ea92bf54fbf29883d549d71c90d60c012558c16a3d61d3a0d1478bdb342c2` |
| `runs/v7_repeat_glm_cta_r2_v1.jsonl` | `76978c385776e3dc11e3d107f59728a8244a1aa627e4ce58acc5399fea783d69` |
| `runs/v7_repeat_glm_cta_r3_v1.jsonl` | `374b7e9ce52d33ebebed9464995e396f04d8af172122d00fc562971e39163c95` |

All eight files contain exactly 40 expected task IDs. The new runs total 320 task-controller
executions, 640 request attempts, zero retries, 313,692 provider-reported tokens, zero API errors,
and zero parse/internal errors. The frozen analysis result is `MIXED`; see
`reports/v7_repeat_stability_v1.md` for the complete denominators and decision flags.
