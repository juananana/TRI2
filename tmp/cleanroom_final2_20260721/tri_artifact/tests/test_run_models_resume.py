from __future__ import annotations

import json
from pathlib import Path

from tri.run_models import completed_task_ids, truncate_partial_jsonl


def test_completed_task_ids_supports_partial_long_runs(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    rows = [
        {"task": {"id": "task-1"}, "status": "ok"},
        {"task": {"id": "task-2"}, "status": "api_error"},
    ]
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows) + '{"task":',
        encoding="utf-8",
    )

    assert completed_task_ids(path) == {"task-1", "task-2"}
    assert completed_task_ids(tmp_path / "missing.jsonl") == set()

    truncate_partial_jsonl(path)
    assert path.read_text(encoding="utf-8") == "".join(
        json.dumps(row) + "\n" for row in rows
    )
