# TRI-v7 Core Replication Decision Log

The 240-task dataset, 12-task smoke set, protocol, and hashes were frozen before any TRI-v7
model output was observed. All six full runs contain 240 unique rows and zero API, parse, or
internal failures. GLM CTA has one successful transport retry; the other five full runs have
none. No prompt or task was changed after the health outputs.

## Design

- 10 schemas disjoint from TRI-v3 primary and transfer;
- four independently parameterized state instances per schema (40 primary resampling clusters);
- anchored/dynamic, explicit/implicit, and flip/stable/name-collision are exactly balanced;
- all old targets remain present and action-valid, excluding fallback-policy ambiguity;
- deterministic gold generation and exact ID/final-state scoring, with no LLM judge.

## Frozen Results

| Model | Controller | Accuracy | Correct initial anchored | Core drift | Stable final errors | Mode accuracy |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | Generic Ledger | 47.5 | 107/120 | 43/72 | 4/40 | NA |
| Qwen3.5 | Exact CTA | 70.8 | 103/120 | 0/71 | 6/40 | 94.6 |
| Qwen3.5 | Lifecycle-Gated | 71.2 | 95/120 | 0/64 | 9/40 | 92.9 |
| GLM-5.1 | Generic Ledger | 70.0 | 120/120 | 38/80 | 2/40 | NA |
| GLM-5.1 | Exact CTA | 94.2 | 104/120 | 0/70 | 0/40 | 93.3 |
| GLM-5.1 | Lifecycle-Gated | 97.1 | 119/120 | 0/79 | 0/40 | 100.0 |

Generic conditional drift is 59.7% for Qwen with a state-cluster 95% interval of [46.5,72.4]
and 47.5% for GLM with [35.0,61.3]. The paired overall improvements are:

- Qwen CTA minus Generic: +23.3 points [16.2,30.4];
- Qwen Lifecycle minus Generic: +23.8 [16.2,31.2];
- GLM CTA minus Generic: +24.2 [19.6,28.7];
- GLM Lifecycle minus Generic: +27.1 [22.1,32.1].

## SQLite Consequences

All 1,440 predictions were replayed through the same action-precondition-enforcing SQLite
environment. Generic produces 43/72 Qwen and 38/80 GLM core TRI writes. Stable cases produce no
wrong write. The methods produce zero core TRI writes after a correct initial binding, but they
are not generally write-safe:

| Model | Controller | Core TRI writes | Total wrong writes | Dynamic-old writes | Invalid attempts | Unneeded rejects |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5 | Generic Ledger | 43 | 44 | 0 | 33 | 49 |
| Qwen3.5 | Exact CTA | 0 | 8 | 6 | 50 | 12 |
| Qwen3.5 | Lifecycle-Gated | 0 | 17 | 13 | 30 | 22 |
| GLM-5.1 | Generic Ledger | 38 | 38 | 0 | 0 | 34 |
| GLM-5.1 | Exact CTA | 0 | 14 | 4 | 0 | 0 |
| GLM-5.1 | Lifecycle-Gated | 0 | 7 | 6 | 0 | 0 |

Dynamic-old writes are the opposite authorization error: the controller preserves the old ID
when the instruction authorized reevaluation. Other wrong writes arise from mode or selector
errors outside the correctly compiled core denominator.

## Decisions

1. The pre-registered phenomenon criterion passes for both models. The existence claim no longer
   depends on eight SQLite opportunities: it has 72 and 80 conditional opportunities over 40 new
   state clusters, plus exact database consequences.
2. TRI-v7 does not estimate natural prevalence. It is a larger synthetic controlled replication.
3. Exact CTA remains the minimal leading mechanism. Typed Lifecycle state is useful for auditing
   and execution, but its Qwen point estimate is tied with CTA and the gate cannot repair compiler
   or selector errors.
4. Do not claim that gating eliminates wrong writes. It eliminates the narrowly conditioned core
   transition when compilation is correct, while opposite-mode and grounding errors remain.
5. Qwen's 4/40 Generic stable errors exceed the pre-specified 5% clean-control threshold, whereas
   GLM is exactly 2/40. Report this asymmetry and the difficult compound-selector errors rather
   than describing the entire replication as an isolated temporal-reference test.
