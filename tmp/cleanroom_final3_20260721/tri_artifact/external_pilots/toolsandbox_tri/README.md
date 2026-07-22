# ToolSandbox-Based TRI Extension

This directory contains a custom external pilot for Temporal Referent Integrity.
It reuses ToolSandbox's Reminder database, snapshot semantics, native
`search_reminder`, and native `modify_reminder`. It adds two experiment-specific
tools: `sync_reminders` for an exogenous mid-trajectory transition and
`postpone_reminder` for an action-level lock policy.

This is **not an official ToolSandbox benchmark score**. Paper text and released
artifacts must call it a "ToolSandbox-based custom TRI extension."

## Frozen Upstream

- Repository: `https://github.com/apple/ToolSandbox`
- Commit: `165848b9a78cead7ca7fe7c89c688b58e6501219`
- License/copyright remain with Apple Inc.; this extension does not copy Apple
  source code.

Create a Python 3.12 environment and install the frozen upstream package:

```bash
python3.12 -m venv .venv-toolsandbox
.venv-toolsandbox/bin/pip install \
  'git+https://github.com/apple/ToolSandbox.git@165848b9a78cead7ca7fe7c89c688b58e6501219'
```

Run the deterministic environment and evaluator tests:

```bash
PYTHONPATH=. .venv-toolsandbox/bin/pytest -q tests/external_pilots/test_toolsandbox_tri.py
```

The four-scenario smoke set covers Preserve-Flip, Reevaluate-Flip,
Preserve-Invalidate, and Preserve-Remove. It is a pre-API infrastructure check,
not a paper result. Expansion and model calls are permitted only after the
oracle suite has perfect final-state, order, rejection, and collateral-write
scores.

## Frozen single-turn existence study

Generate the balanced 96-task set with:

```bash
PYTHONPATH=. python -m external_pilots.toolsandbox_tri.scenarios \
  --set single-turn-2x2 \
  --output experiments/tri_artifact/data/toolsandbox_tri_single_turn_2x2_v1.jsonl
```

It contains 24 tasks per cell of `reference_mode x transition`: Preserve/Stable,
Preserve/Flip, Reevaluate/Stable, and Reevaluate/Flip. Each task has one user
turn and an explicit no-op `record_binding` event. This event makes the
denominator auditable and does not change the database. The 96 rows are four
paraphrases of six selector clusters, so cluster-aware analysis is required;
they must not be presented as 96 independent natural user cases.

For the existence claim, report the conditional rate among rows with a correct
binding record and a successful sync. Preserve/Flip measures unauthorized
rebinding; Reevaluate/Flip measures premature locking. Stable cells are
negative controls. Tool/API/compiler failures are reported separately and are
not silently counted as evidence of TRI.

`generic_state_observed` is a versioned measurement condition for generic rewritable state. It
does not add lifecycle fields or enforce a target. When the model's own generic state contains
exactly one reminder ID, the evaluator logs that ID when the model requests sync (Preserve) or
mutation (Reevaluate). This removes the extra `record_binding` agent step while leaving target
choice and database writes under model control. Results from `generic` and
`generic_state_observed` must not be merged.
