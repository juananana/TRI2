# Official tau3-bench Native TRI Opportunity Audit

## Frozen Scope

- Upstream: `https://github.com/sierra-research/tau2-bench.git`
- Commit: `cf71a8070269883e38a365ffa85f78f46844c1f4`
- Core tasks audited: **2449**
- Domains: airline, retail, telecom

A strict opportunity requires a correct same-role entity binding, an independent later
user/environment mutation, a subsequent action that may preserve or reevaluate that
referent, stable IDs, a competing selector candidate, and a scoreable wrong-target outcome.
Statefulness, multiple tools, or initial entity lookup alone do not qualify.

## Inventory Screen

| Domain | Tasks | User-mutation tasks | User mutation with stable ID | Metadata candidates |
|---|---:|---:|---:|---:|
| airline | 50 | 0 | 0 | 0 |
| retail | 114 | 0 | 0 | 0 |
| telecom | 2285 | 2250 | 0 | 0 |

## Result

- Strict native TRI opportunities after semantic audit: **0**
- Natural dual-control near-match: **8** telecom overdue-payment task definitions

In the near-match, the Agent identifies an overdue bill, the user pays it through a
user tool, and the Agent resumes an associated line. This independently demonstrates
a natural bind--user-transition--continue workflow, but it is not TRI: the bill and line
are different roles and there is no competing same-role target or selector flip.

## Released-Trajectory Coverage

The repository includes 26 released result files and
10832 trajectories. Domain counts are airline: 800, retail: 1824, telecom: 4560, telecom-workflow: 3648.
Agent-model counts are claude-3-7-sonnet-20250219: 1112, gpt-4.1-2025-04-14: 4304, gpt-4.1-mini-2025-04-14: 1112, o4-mini-2025-04-16: 4304.
The payment near-match appears in 936
released trajectories. Because the task inventory has no strict opportunity,
these trajectories cannot estimate a conditional TRI failure rate.

## Interpretation

The official inventory adds natural language, dual control, and ordinary published Agents, but it has zero strict TRI opportunities under the frozen definition. It therefore measures benchmark coverage, not TRI prevalence or absence.
This is stronger evidence about external benchmark coverage and ordinary Agent
families, but it is not positive evidence that TRI occurs in uncontrolled traffic.
