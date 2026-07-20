# Lossy Summary Controller Case Study

The bounded memory module was instructed to summarize the controller transcript in at most 18 words without entity IDs, exact names, or exact numeric values. These summaries are model-generated controller state, not hand-edited benchmark inputs.

## Aggregate

| Binding | Update | n | Accuracy | Drift | Temporal Anchor in Summary | Entity ID in Summary |
|---|---|---:|---:|---:|---:|---:|
| anchored | flip | 15 | 26.7 | 53.3 | 100.0 | 0.0 |
| dynamic | flip | 15 | 93.3 | 0.0 | 0.0 | 0.0 |

## Representative Anchored-Flip Summaries

| Task | Summary | Predicted | Correct | Outcome |
|---|---|---|---|---|
| incident-p0-anchored-flip | Escalate the incident identified as highest severity in the initial state. | INC-205 | INC-104 | drift |
| incident-p1-anchored-flip | Escalate the originally chosen highest-severity incident, ignoring updated severities from the refresh. | INC-104 | INC-104 | correct |
| incident-p2-anchored-flip | Escalate originally bound highest-severity incident, disregarding refreshed state showing a new highest severity. | INC-104 | INC-104 | correct |
| incident-p3-anchored-flip | Escalate the incident that was highest severity before the refresh. | INC-205 | INC-104 | drift |
| incident-p4-anchored-flip | Apply later actions to pre-refresh highest-severity incident, not post-refresh highest. | INVALID_BOUND_ENTITY | INC-104 | invalid/other |
