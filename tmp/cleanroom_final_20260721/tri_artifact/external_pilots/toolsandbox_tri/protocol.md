# ToolSandbox TRI Pilot Protocol

## Claim under test

In a stateful tool environment, a lifecycle representation should reduce
wrong-entity mutations after an exogenous refresh, compared with a matched
generic controller and a matched untyped pre-refresh plan.

## Environment boundary

The pilot is a custom extension built on ToolSandbox. ToolSandbox supplies the
stateful Reminder database, stable reminder IDs, snapshot history, search, and
mutation implementation. This extension supplies the exogenous sync operation,
the lock policy, TRI task language, controller interception, and evaluator.

## Scoring

The evaluator records three database snapshots: initial, immediately after the
exogenous sync, and final. Agent writes are computed only from the post-sync to
final diff. Primary metrics are final-state success and wrong-entity write rate.
Secondary diagnostics are invalid attempts, unnecessary rejection, tool-order
success, and collateral modifications.

## Staged decision rule

1. Four deterministic development scenarios must score 4/4 with zero wrong writes.
2. An API smoke set must have zero API/parser errors and auditable tool traces.
3. Task language and transitions are frozen before controller comparisons.
4. The frozen set has 24 tasks: six selectors, paired Preserve/Reevaluate
   language, and balanced coverage of Flip, Stable, Invalidate, and Remove.
5. The paper-scale pilot is expanded only if both models can operate the tools
   without a dominant non-TRI tool-use failure mode.

No failed smoke run is silently removed. Development runs and frozen evaluation
runs are stored separately and identified by exact filenames.

## Frozen artifact hashes

- Task JSONL: `a900dbca27530b71fdf7a1cf13d1a8b90539c4ad695935acab3a405602e48268`
- Upstream ToolSandbox commit: `165848b9a78cead7ca7fe7c89c688b58e6501219`

Runner, environment, and evaluator hashes are recorded immediately before the
first frozen API call because reliability changes to the streaming runner are
still permitted during the development-smoke stage.

- Runner: `66945a9464405dff6a3e4f69f14dadf46bf0a5f6461e88c2be4f52e01c695d4a`
- Environment: `8a342a64e3c770758a809caa37ea5a57b9e4d012b3b88d2fa758617a738c9931`
- Evaluator: `67e7ad33d7885a061efdc09755a1badfbbc62de5f455f4bb4826fe9b7e700bc5`
