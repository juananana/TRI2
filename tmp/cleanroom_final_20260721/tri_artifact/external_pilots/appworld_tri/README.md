# AppWorld TRI Custom Case Study

This pilot uses AppWorld `0.1.3.post1` and the official train task world
`82e2fac_1` only as a realistic database/API substrate. It adds frozen TRI tasks,
a sidecar binding tool, and an external synchronization operator. It is **not** an
unmodified AppWorld task, TGC/SGC score, test-set result, or leaderboard submission.

The frozen Todoist MVP crosses Preserve/Reevaluate with Stable/Flip and two instruction
paraphrases (8 tasks). A separately frozen post-primary Simple Note addendum contributes
the same 8-cell design with a different application, selector, and mutation. The Agent
autonomously calls a restricted tool surface. Search, sync, and mutation delegate to native
AppWorld APIs. Scoring uses stable IDs and post-sync-to-final database snapshots; no LLM
judge defines the gold target.

Runtime prerequisites are intentionally kept outside the artifact:

```bash
python3.12 -m venv .venv-appworld312
.venv-appworld312/bin/python -m pip install appworld==0.1.3.post1
HOME="$PWD/experiments/tri_artifact/external_pilots/appworld_runtime/home" \
  .venv-appworld312/bin/appworld install
HOME="$PWD/experiments/tri_artifact/external_pilots/appworld_runtime/home" \
  .venv-appworld312/bin/appworld download data \
  --root "$PWD/experiments/tri_artifact/external_pilots/appworld_runtime"
```

See `reports/TRI_appworld_custom_protocol.md` and
`reports/TRI_appworld_simple_note_addendum_protocol.md` for inclusion and interpretation rules.
