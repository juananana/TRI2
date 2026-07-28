# Frozen Rule* on Source-Grounded Contrasts

Rows correct: 15/60.
PairAcc: 2/30.

| Source | Row accuracy | PairAcc | Errors |
|---|---:|---:|---|
| AgentDojo | 0/20 | 0/10 | {'ambiguous_numeric_selector:': 20} |
| STATE-Bench | 9/20 | 0/10 | {'ambiguous_numeric_selector:price,quantity': 2, 'wrong_target': 9} |
| ToolSandbox | 6/20 | 2/10 | {'ambiguous_ranking_direction': 10, 'wrong_target': 4} |

The rule is post-hoc to authored TRI analyses but byte-frozen before this source-grounded application.
