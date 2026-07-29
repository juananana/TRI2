# Decision Decomposition v2

Evidence status: `planned post-primary; frozen before calls`.

## Pro/zai-org/GLM-5.1

Calls: 720/720 logical, 720 HTTP attempts, 0 retries; observed request time 954.82s.

| Cell | PairAcc | E2E | Substitution | E2E repairs/harms vs H | Failures | HTTP/retries | Prompt tokens | Completion tokens |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| history_only | 12/40 | 52/80 | 12/24 | 0/0 | {'none': 80} | 80/0 | 45214 | 1968 |
| placebo | 7/40 | 47/80 | 17/24 | 0/5 | {'none': 80} | 80/0 | 49326 | 1968 |
| selector_only | 7/40 | 47/80 | 16/24 | 0/5 | {'none': 80} | 80/0 | 46342 | 1968 |
| id_control | 13/40 | 52/80 | 12/24 | 3/3 | {'none': 80} | 80/0 | 46510 | 1968 |
| mode_only | 11/40 | 50/80 | 13/24 | 1/3 | {'none': 80} | 80/0 | 46150 | 1968 |
| mode_plus_id | 16/40 | 56/80 | 8/24 | 5/1 | {'none': 80} | 80/0 | 46813 | 1968 |
| mode_plus_id_selector | 18/40 | 58/80 | 6/24 | 8/2 | {'none': 80} | 80/0 | 47621 | 1968 |
| full_follow | 19/40 | 59/80 | 4/24 | 8/1 | {'none': 80} | 80/0 | 49541 | 1968 |

| Contrast | Metric | Difference | 95% CI | Repairs | Harms | Holm p | dHTTP | dRetry | dPrompt tok. | dWall s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| placebo - history_only | changed_pairacc | -12.5 pp | [-22.5, -2.5] | 0 | 5 | 1 | 0 | 0 | 4112 | 9.153 |
| placebo - history_only | e2e | -6.2 pp | [-11.3, -1.3] | 0 | 5 | 1 | 0 | 0 | 4112 | 9.153 |
| placebo - history_only | preserve_conditional_substitution | 20.8 pp | [4.8, 38.5] | 0 | 5 | 1 | 0 | 0 | 4112 | 9.153 |
| selector_only - history_only | changed_pairacc | -12.5 pp | [-22.5, -2.5] | 0 | 5 | 1 | 0 | 0 | 1128 | 3.079 |
| selector_only - history_only | e2e | -6.2 pp | [-11.3, -1.3] | 0 | 5 | 1 | 0 | 0 | 1128 | 3.079 |
| selector_only - history_only | preserve_conditional_substitution | 16.7 pp | [3.8, 33.3] | 0 | 4 | 1 | 0 | 0 | 1128 | 3.079 |
| id_control - history_only | changed_pairacc | 2.5 pp | [-7.5, 12.5] | 3 | 2 | 1 | 0 | 0 | 1296 | 0.341 |
| id_control - history_only | e2e | 0.0 pp | [-6.2, 6.2] | 3 | 3 | 1 | 0 | 0 | 1296 | 0.341 |
| id_control - history_only | preserve_conditional_substitution | 0.0 pp | [-16.7, 16.7] | 2 | 2 | 1 | 0 | 0 | 1296 | 0.341 |
| mode_only - history_only | changed_pairacc | -2.5 pp | [-12.5, 5.0] | 1 | 2 | 1 | 0 | 0 | 936 | -1.821 |
| mode_only - history_only | e2e | -2.5 pp | [-7.5, 2.5] | 1 | 3 | 1 | 0 | 0 | 936 | -1.821 |
| mode_only - history_only | preserve_conditional_substitution | 4.2 pp | [-9.5, 19.0] | 1 | 2 | 1 | 0 | 0 | 936 | -1.821 |
| mode_plus_id - mode_only | changed_pairacc | 12.5 pp | [2.5, 22.5] | 5 | 0 | 1 | 0 | 0 | 663 | 0.167 |
| mode_plus_id - mode_only | e2e | 7.5 pp | [2.5, 13.7] | 6 | 0 | 0.6562 | 0 | 0 | 663 | 0.167 |
| mode_plus_id - mode_only | preserve_conditional_substitution | -20.8 pp | [-38.1, -5.0] | 5 | 0 | 1 | 0 | 0 | 663 | 0.167 |
| mode_plus_id_selector - mode_plus_id | changed_pairacc | 5.0 pp | [-5.0, 15.0] | 3 | 1 | 1 | 0 | 0 | 808 | 2.917 |
| mode_plus_id_selector - mode_plus_id | e2e | 2.5 pp | [-2.5, 7.5] | 3 | 1 | 1 | 0 | 0 | 808 | 2.917 |
| mode_plus_id_selector - mode_plus_id | preserve_conditional_substitution | -8.3 pp | [-25.0, 7.7] | 3 | 1 | 1 | 0 | 0 | 808 | 2.917 |
| full_follow - mode_plus_id_selector | changed_pairacc | 2.5 pp | [-7.5, 12.5] | 3 | 2 | 1 | 0 | 0 | 1920 | 2.071 |
| full_follow - mode_plus_id_selector | e2e | 1.3 pp | [-3.8, 6.2] | 3 | 2 | 1 | 0 | 0 | 1920 | 2.071 |
| full_follow - mode_plus_id_selector | preserve_conditional_substitution | -8.3 pp | [-25.0, 7.7] | 3 | 1 | 1 | 0 | 0 | 1920 | 2.071 |
| full_follow - placebo | changed_pairacc | 30.0 pp | [15.0, 45.0] | 13 | 1 | 0.04211 | 0 | 0 | 215 | -5.818 |
| full_follow - placebo | e2e | 15.0 pp | [7.5, 22.5] | 13 | 1 | 0.04211 | 0 | 0 | 215 | -5.818 |
| full_follow - placebo | preserve_conditional_substitution | -54.2 pp | [-74.1, -33.3] | 13 | 0 | 0.005859 | 0 | 0 | 215 | -5.818 |

## Qwen/Qwen3.5-122B-A10B

Calls: 708/720 logical, 794 HTTP attempts, 86 retries; observed request time 465.43s.

| Cell | PairAcc | E2E | Substitution | E2E repairs/harms vs H | Failures | HTTP/retries | Prompt tokens | Completion tokens |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| history_only | 11/40 | 51/80 | 14/32 | 0/0 | {'none': 80} | 89/9 | 47514 | 1408 |
| placebo | 11/40 | 48/80 | 13/32 | 7/10 | {'none': 80} | 94/14 | 51626 | 1408 |
| selector_only | 12/40 | 51/80 | 13/32 | 5/5 | {'none': 78, 'upstream': 2} | 90/12 | 47474 | 1372 |
| id_control | 12/40 | 49/80 | 11/32 | 3/5 | {'none': 78, 'upstream': 2} | 83/5 | 47646 | 1372 |
| mode_only | 14/40 | 52/80 | 11/32 | 4/3 | {'none': 78, 'upstream': 2} | 87/9 | 47259 | 1372 |
| mode_plus_id | 15/40 | 53/80 | 12/32 | 7/5 | {'none': 78, 'upstream': 2} | 90/12 | 48053 | 1372 |
| mode_plus_id_selector | 12/40 | 51/80 | 12/32 | 7/7 | {'none': 78, 'upstream': 2} | 86/8 | 48833 | 1372 |
| full_follow | 11/40 | 47/80 | 15/32 | 4/8 | {'none': 78, 'upstream': 2} | 83/5 | 50705 | 1372 |

| Contrast | Metric | Difference | 95% CI | Repairs | Harms | Holm p | dHTTP | dRetry | dPrompt tok. | dWall s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| placebo - history_only | changed_pairacc | 0.0 pp | [-17.5, 17.5] | 6 | 6 | 1 | 5 | 5 | 4112 | 3.395 |
| placebo - history_only | e2e | -3.7 pp | [-13.7, 6.2] | 7 | 10 | 1 | 5 | 5 | 4112 | 3.395 |
| placebo - history_only | preserve_conditional_substitution | -3.1 pp | [-21.9, 15.2] | 5 | 4 | 1 | 5 | 5 | 4112 | 3.395 |
| selector_only - history_only | changed_pairacc | 2.5 pp | [-10.0, 15.0] | 4 | 3 | 1 | 1 | 3 | -40 | 1.148 |
| selector_only - history_only | e2e | 0.0 pp | [-7.5, 6.2] | 5 | 5 | 1 | 1 | 3 | -40 | 1.148 |
| selector_only - history_only | preserve_conditional_substitution | -3.1 pp | [-14.3, 6.7] | 2 | 1 | 1 | 1 | 3 | -40 | 1.148 |
| id_control - history_only | changed_pairacc | 2.5 pp | [-7.5, 12.5] | 3 | 2 | 1 | -6 | -4 | 132 | -0.682 |
| id_control - history_only | e2e | -2.5 pp | [-10.0, 5.0] | 3 | 5 | 1 | -6 | -4 | 132 | -0.682 |
| id_control - history_only | preserve_conditional_substitution | -9.4 pp | [-20.6, 0.0] | 3 | 0 | 1 | -6 | -4 | 132 | -0.682 |
| mode_only - history_only | changed_pairacc | 7.5 pp | [-2.5, 20.0] | 4 | 1 | 1 | -2 | 0 | -255 | 0.913 |
| mode_only - history_only | e2e | 1.3 pp | [-5.0, 7.5] | 4 | 3 | 1 | -2 | 0 | -255 | 0.913 |
| mode_only - history_only | preserve_conditional_substitution | -9.4 pp | [-23.3, 3.2] | 4 | 1 | 1 | -2 | 0 | -255 | 0.913 |
| mode_plus_id - mode_only | changed_pairacc | 2.5 pp | [-12.5, 17.5] | 5 | 4 | 1 | 3 | 3 | 794 | -0.867 |
| mode_plus_id - mode_only | e2e | 1.2 pp | [-6.2, 8.8] | 6 | 5 | 1 | 3 | 3 | 794 | -0.867 |
| mode_plus_id - mode_only | preserve_conditional_substitution | 3.1 pp | [-13.3, 19.4] | 3 | 4 | 1 | 3 | 3 | 794 | -0.867 |
| mode_plus_id_selector - mode_plus_id | changed_pairacc | -7.5 pp | [-20.0, 5.0] | 2 | 5 | 1 | -4 | -4 | 780 | 1.030 |
| mode_plus_id_selector - mode_plus_id | e2e | -2.5 pp | [-10.0, 3.8] | 3 | 5 | 1 | -4 | -4 | 780 | 1.030 |
| mode_plus_id_selector - mode_plus_id | preserve_conditional_substitution | 0.0 pp | [0.0, 0.0] | 0 | 0 | 1 | -4 | -4 | 780 | 1.030 |
| full_follow - mode_plus_id_selector | changed_pairacc | -2.5 pp | [-12.5, 7.5] | 2 | 3 | 1 | -3 | -3 | 1872 | 0.341 |
| full_follow - mode_plus_id_selector | e2e | -5.0 pp | [-12.5, 1.3] | 3 | 7 | 1 | -3 | -3 | 1872 | 0.341 |
| full_follow - mode_plus_id_selector | preserve_conditional_substitution | 9.4 pp | [0.0, 20.7] | 0 | 3 | 1 | -3 | -3 | 1872 | 0.341 |
| full_follow - placebo | changed_pairacc | 0.0 pp | [-15.0, 15.0] | 5 | 5 | 1 | -11 | -9 | -921 | -1.979 |
| full_follow - placebo | e2e | -1.2 pp | [-11.3, 8.8] | 7 | 8 | 1 | -11 | -9 | -921 | -1.979 |
| full_follow - placebo | preserve_conditional_substitution | 6.2 pp | [-9.1, 21.2] | 2 | 4 | 1 | -11 | -9 | -921 | -1.979 |

## deepseek-ai/DeepSeek-V4-Pro

Calls: 714/720 logical, 714 HTTP attempts, 0 retries; observed request time 1387.12s.

| Cell | PairAcc | E2E | Substitution | E2E repairs/harms vs H | Failures | HTTP/retries | Prompt tokens | Completion tokens |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| history_only | 7/40 | 47/80 | 32/40 | 0/0 | {'none': 80} | 80/0 | 47486 | 1608 |
| placebo | 11/40 | 51/80 | 29/40 | 4/0 | {'none': 80} | 80/0 | 51934 | 1524 |
| selector_only | 8/40 | 46/80 | 32/40 | 1/2 | {'none': 79, 'upstream': 1} | 79/0 | 48201 | 1570 |
| id_control | 10/40 | 48/80 | 29/40 | 3/2 | {'none': 79, 'upstream': 1} | 79/0 | 48505 | 1554 |
| mode_only | 11/40 | 50/80 | 28/40 | 4/1 | {'none': 79, 'upstream': 1} | 79/0 | 47984 | 1558 |
| mode_plus_id | 15/40 | 53/80 | 21/40 | 11/5 | {'none': 79, 'upstream': 1} | 79/0 | 48793 | 1526 |
| mode_plus_id_selector | 16/40 | 55/80 | 21/40 | 11/3 | {'none': 79, 'upstream': 1} | 79/0 | 49642 | 1542 |
| full_follow | 12/40 | 51/80 | 25/40 | 7/3 | {'none': 79, 'upstream': 1} | 79/0 | 51696 | 1586 |

| Contrast | Metric | Difference | 95% CI | Repairs | Harms | Holm p | dHTTP | dRetry | dPrompt tok. | dWall s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| placebo - history_only | changed_pairacc | 10.0 pp | [2.5, 20.0] | 4 | 0 | 1 | 0 | 0 | 4448 | 2.892 |
| placebo - history_only | e2e | 5.0 pp | [1.2, 10.0] | 4 | 0 | 1 | 0 | 0 | 4448 | 2.892 |
| placebo - history_only | preserve_conditional_substitution | -7.5 pp | [-17.5, 0.0] | 3 | 0 | 1 | 0 | 0 | 4448 | 2.892 |
| selector_only - history_only | changed_pairacc | 2.5 pp | [0.0, 7.5] | 1 | 0 | 1 | -1 | 0 | 715 | 4.606 |
| selector_only - history_only | e2e | -1.3 pp | [-5.0, 2.5] | 1 | 2 | 1 | -1 | 0 | 715 | 4.606 |
| selector_only - history_only | preserve_conditional_substitution | 0.0 pp | [0.0, 0.0] | 0 | 0 | 1 | -1 | 0 | 715 | 4.606 |
| id_control - history_only | changed_pairacc | 7.5 pp | [0.0, 15.0] | 3 | 0 | 1 | -1 | 0 | 1019 | 67.455 |
| id_control - history_only | e2e | 1.2 pp | [-3.8, 6.2] | 3 | 2 | 1 | -1 | 0 | 1019 | 67.455 |
| id_control - history_only | preserve_conditional_substitution | -7.5 pp | [-17.5, 0.0] | 3 | 0 | 1 | -1 | 0 | 1019 | 67.455 |
| mode_only - history_only | changed_pairacc | 10.0 pp | [2.5, 20.0] | 4 | 0 | 1 | -1 | 0 | 498 | -9.388 |
| mode_only - history_only | e2e | 3.7 pp | [-1.3, 8.8] | 4 | 1 | 1 | -1 | 0 | 498 | -9.388 |
| mode_only - history_only | preserve_conditional_substitution | -10.0 pp | [-20.0, -2.5] | 4 | 0 | 1 | -1 | 0 | 498 | -9.388 |
| mode_plus_id - mode_only | changed_pairacc | 10.0 pp | [-7.5, 27.5] | 8 | 4 | 1 | 0 | 0 | 809 | 4.062 |
| mode_plus_id - mode_only | e2e | 3.7 pp | [-5.0, 12.5] | 8 | 5 | 1 | 0 | 0 | 809 | 4.062 |
| mode_plus_id - mode_only | preserve_conditional_substitution | -17.5 pp | [-32.5, -5.0] | 8 | 1 | 0.9375 | 0 | 0 | 809 | 4.062 |
| mode_plus_id_selector - mode_plus_id | changed_pairacc | 2.5 pp | [-7.5, 12.5] | 3 | 2 | 1 | 0 | 0 | 849 | 8.725 |
| mode_plus_id_selector - mode_plus_id | e2e | 2.5 pp | [-3.7, 10.0] | 4 | 2 | 1 | 0 | 0 | 849 | 8.725 |
| mode_plus_id_selector - mode_plus_id | preserve_conditional_substitution | 0.0 pp | [-7.5, 7.5] | 1 | 1 | 1 | 0 | 0 | 849 | 8.725 |
| full_follow - mode_plus_id_selector | changed_pairacc | -10.0 pp | [-20.0, -2.5] | 0 | 4 | 1 | 0 | 0 | 2054 | -8.730 |
| full_follow - mode_plus_id_selector | e2e | -5.0 pp | [-10.0, -1.2] | 0 | 4 | 1 | 0 | 0 | 2054 | -8.730 |
| full_follow - mode_plus_id_selector | preserve_conditional_substitution | 10.0 pp | [2.5, 20.0] | 0 | 4 | 1 | 0 | 0 | 2054 | -8.730 |
| full_follow - placebo | changed_pairacc | 2.5 pp | [-10.0, 15.0] | 4 | 3 | 1 | -1 | 0 | -238 | -8.224 |
| full_follow - placebo | e2e | 0.0 pp | [-7.5, 6.2] | 5 | 5 | 1 | -1 | 0 | -238 | -8.224 |
| full_follow - placebo | preserve_conditional_substitution | -10.0 pp | [-22.5, 0.0] | 5 | 1 | 1 | -1 | 0 | -238 | -8.224 |

## Claim gate

Report eligible for promotion: `True`.
Field and composite claims require a validated full three-model matrix, positive PairAcc intervals in at least two models, and no significant reverse-model interval. The gate cannot promote architecture, mechanism, transfer, or prevalence claims.
