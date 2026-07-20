# Temporal Referent Integrity

This artifact studies temporal referent integrity (TRI): after an entity has been
correctly selected, an environment refresh updates world knowledge but does not
automatically authorize the agent to substitute another entity. Some instructions
commit to a pre-refresh identity, while others intentionally defer selection until
after refresh. The paper diagnoses this distinction, evaluates pre-refresh commitment
compilation, and reports both real SQLite consequences and external-validity boundaries.

The benchmark has four matched conditions:

- anchored + flip: bind before refresh; refreshed state changes the selector.
- anchored + stable: bind before refresh; refreshed state preserves the selector.
- dynamic + flip: evaluate after refresh; refreshed state changes the selector.
- dynamic + stable: evaluate after refresh; refreshed state preserves the selector.

The key diagnostic compares direct semantic resolution with interactive
tool use. If a model succeeds in direct mode but fails interactively, the error
is not just language understanding; it is identity persistence across state
updates.

## TRI-v2 upgrade

The `tri_v2` suite is a harder follow-up designed to address reviewer concerns
about artificial templates and "just save the ID" repairs. It adds:

- 8 app-style domains: mailbox, calendar, store, support console, drive, CRM,
  code host, and logistics.
- implicit anchored language without words such as `same` or `before refresh`.
- action-specific invalidity, removed entities, display-name collisions, and
  selector flips.
- conditional validity semantics: prefer the bound entity if it remains
  actionable; otherwise rebind to the refreshed target.
- collection references and nested references to owners of selected entities.
- a schema-based lifecycle controller that checks action preconditions instead
  of asking the model to guess validity.

Regenerate and evaluate the v2 deterministic suite:

```bash
python3 -m tri.v2_tasks --output data/temporal_referent_v2.jsonl
python3 -m tri.v2_ablation \
  --input data/temporal_referent_v2.jsonl \
  --output reports/v2_ablation.json
python3 -m tri.v2_tool_ablation \
  --input data/temporal_referent_v2.jsonl \
  --runs-output runs/v2_tool_ablation.jsonl \
  --report-output reports/v2_tool_ablation.json
```

Generate the scalar-only subset compatible with the existing LLM runner:

```bash
python3 -m tri.v2_api_subset --output data/temporal_referent_v2_api_scalar.jsonl
```

Run the SiliconFlow model matrix after setting the key in your shell. The key is
not stored in the repository:

```bash
export LLM_API_KEY=...
scripts/run_v2_siliconflow_matrix.sh
```

After the baseline matrix finishes, run the schema-aware compiler matrix:

```bash
scripts/run_v2_schema_siliconflow_matrix.sh
```

Generate a strict model report that counts API errors as failures:

```bash
scripts/report_v2_model_runs.sh
```

## Frozen paper evaluation

The paper-facing evaluation is frozen. Do not launch additional paid model
matrices unless a specific evidentiary gap is identified. The main experiments
are:

```text
data/temporal_referent_v3_language_clusters.jsonl
data/temporal_referent_v3_unseen_domains.jsonl
data/temporal_referent_v3_sqlite_trajectory.jsonl
data/temporal_referent_v4_policy.jsonl
```

Their preregistration, decision, and trajectory protocols are documented in:

```text
reports/TRI_v3_experiment_decision_log.md
reports/TRI_v3_preregistered_protocol.md
reports/TRI_v3_sqlite_trajectory_protocol.md
reports/TRI_v4_policy_protocol.md
```

All final run files are complete with zero API errors and zero retries. The
main results are:

```text
Qwen language clusters: generic 64.4%, lifecycle 98.1%
GLM language clusters:  generic 71.9%, lifecycle 100.0%
Qwen unseen schemas:    generic 46.2%, lifecycle 82.5%
Qwen SQLite trajectory: generic 67.5%, lifecycle 100.0%
GLM SQLite trajectory:  generic 65.0%, lifecycle 100.0%
Qwen guarded policies:  generic 52.5%, lifecycle 85.0%
```

Cluster bootstrap confidence intervals, paired tests, stage decomposition,
cost accounting, audits, and SQLite replay reports are under `reports/`. The
unseen-schema analysis isolates compound-selector grounding as a separate
bottleneck rather than counting it as evidence that reference lifecycle state
is unnecessary.

Do not aggregate every file under `runs/` with a broad glob for paper tables;
the directory intentionally retains smoke tests, endpoint failures, and
development iterations. Use the exact run files named by the v3/v4 reports.

In the anonymous archive, the current AAAI submission source is:

```text
paper/AnonymousSubmission2027.tex
```

Build it with:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error AnonymousSubmission2027.tex
```

The verified target is seven pages of main content plus references, within the
AAAI-27 nine-page total limit. The current full build is eight pages total. From the
artifact root, run:

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/pytest -q tests
```

The validated local environment is Python 3.12.13 with pytest 9.1.1; the current working
tree has 126 passing tests. Most TRI generators, deterministic evaluators, SQLite replays,
and report scripts use only the Python standard library. External-pilot tests additionally
depend on their pinned ToolSandbox/AppWorld environments and are documented separately.

## Post-primary method-upgrade decision

The frozen 20-task method-upgrade smoke combines 16 v7 scalar-core tasks with four v6
multi-refresh/role tasks. Event Graph and Executable Selector were evaluated with Qwen and
GLM after the main mechanism was selected. They did not satisfy the predeclared cross-model
schema, selector-equivalence, and direction-consistency gates, so neither replaces Exact CTA
as the paper's scalar main method. Role-Indexed Lifecycle remains a limited compositional
extension. Reproduce the unified decision report with:

```bash
PYTHONPATH=. ../../.venv-toolsandbox/bin/python \
  scripts/analyze_method_upgrade_closed_loop.py
```

The resulting files are `reports/method_upgrade_closed_loop_v1.json` and `.md`. This is an
exploratory Go/No-Go audit, not a powered confirmatory result.

## Single-turn ToolSandbox existence study

The frozen confirmatory extension is
`data/toolsandbox_tri_single_turn_2x2_v1.jsonl` (96 tasks; SHA-256
`f795031bba66d9a018b94d351930a9ed2beaaae23285925cc3a514e17f7f189d`). It crosses
Preserve/Reevaluate with Stable/Flip and contains four paraphrases of six selector clusters.
The no-op `record_binding` event makes initial identity and timing observable without mutating
the database.

After exporting `LLM_API_KEY` in the shell, run an eight-task balanced health check:

```bash
MODE=health CONTROLLERS=full_history scripts/run_toolsandbox_single_turn_2x2.sh \
  Qwen/Qwen3.5-122B-A10B
```

Run `MODE=full` only after the health file has zero API/protocol errors and all four cells have
nonzero TRI-opportunity coverage. Analyze completed files with:

```bash
PYTHONPATH=. python3 -m tri.toolsandbox_single_turn_report runs/COMPLETED.jsonl \
  --json reports/toolsandbox_single_turn_2x2.json \
  --markdown reports/toolsandbox_single_turn_2x2.md
```

`runs/toolsandbox_tri_single_turn_qwen_full_history_network_blocked_v1.jsonl` is an infrastructure
audit from a DNS-blocked sandbox: it contains no model responses and must never enter paper
statistics.

The corrected controlled-benchmark mechanism audit is generated with:

```bash
PYTHONPATH=. python3 -m tri.v3_generic_tri_audit \
  runs/20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl \
  runs/20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl \
  --json reports/v3_generic_tri_corrected_audit.json \
  --markdown reports/v3_generic_tri_corrected_audit.md
```

This analysis must read Generic Ledger's `selected_entity_id`, not Lifecycle's
`bound_target_id`. The external-validation claim boundary and all negative results are retained in
`reports/TRI_external_validation_v1_summary.md`.

## Current P0 ablation

`generic_reference_mode_ledger_then_act` is the minimal diagnostic for the remaining mechanism
question. It keeps the Generic Structured Ledger and its free actor, adding only
`reference_mode` (`preserve` or `reevaluate`). It adds no invalidity policy, guard, fallback, or
deterministic gate. Run it on the frozen 160-task v3 language-cluster set with:

```bash
scripts/run_reference_mode_ablation.sh
```

The runner requires `LLM_API_KEY` in the environment and never reads a key file. Analyze a
completed paired run with:

```bash
python3 -m tri.analyze_reference_mode_ablation \
  --generic runs/GENERIC.jsonl \
  --reference-mode runs/REFERENCE_MODE.jsonl
```

Interpretation is conditional: a high result would show that explicit mode classification
explains most of CTA's gain; a lower result would support additional value from the pre-refresh
identity/provenance record. Neither outcome establishes Lifecycle-Gated superiority by itself.
